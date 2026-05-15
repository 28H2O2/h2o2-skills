#!/usr/bin/env python3
"""Audit likely leftover AI-agent and development processes."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from typing import Iterable


AI_PATTERNS = [
    r"\bclaude-code\b",
    r"\bclaude\b.*--output-format",
    r"\bcodex\b.*app-server",
    r"\bcodex\b.*sandbox",
    r"\bcursor\b.*extension-host",
    r"\bmcp\b",
    r"\bplaywright\b",
    r"\bbrowsermcp\b",
    r"remote-debugging-port",
    r"ms-playwright",
]

DEV_PATTERNS = [
    r"(^|/|\s)node(\s|$)",
    r"(^|/|\s)npm(\s|$)",
    r"(^|/|\s)pnpm(\s|$)",
    r"(^|/|\s)yarn(\s|$)",
    r"(^|/|\s)bun(\s|$)",
    r"\bnext\s+dev\b",
    r"\bvite\b",
    r"\bwebpack\b",
    r"\bturbo\b",
    r"(^|/|\s)python[0-9.]*\s",
    r"\buvicorn\b",
    r"\bgunicorn\b",
    r"\bpytest\b",
    r"\bjest\b",
]

PROTECTED_PATTERNS = [
    r"\bmysqld\b",
    r"\bpostgres\b",
    r"\bredis-server\b",
    r"\bdocker\b",
    r"\bclash\b",
    r"\brapportd\b",
    r"ControlCenter",
    r"WindowServer",
    r"\blaunchd\b",
    r"/Finder.app/",
    r"crashpad_handler",
    r"CursorUIViewService",
    r"/System/",
    r"/usr/libexec/",
]

GUI_APP_PATTERNS = [
    r"/Applications/[^ ]+\.app/Contents/MacOS/[^ ]+$",
    r"/Applications/.* Helper",
    r"Electron Framework.*crashpad_handler",
]

COMMON_DEV_PORTS = {
    "3000",
    "3001",
    "4173",
    "5173",
    "8000",
    "8001",
    "8080",
    "8787",
    "9009",
}

SECRET_PATTERNS = [
    (
        re.compile(r"(?i)(api[_-]?key|token|secret|password|passwd|auth[_-]?key)=([^&\s]+)"),
        lambda match: match.group(1) + "=[REDACTED]",
    ),
    (
        re.compile(r"(?i)(--(?:api-key|token|secret|password|auth-key))(?:=|\s+)([^\s]+)"),
        lambda match: match.group(1) + "=[REDACTED]",
    ),
    (
        re.compile(r"(?i)(bearer\s+)([a-z0-9._~+/=-]{16,})"),
        lambda match: match.group(1) + "[REDACTED]",
    ),
]


@dataclass
class Process:
    pid: int
    ppid: int
    cpu: float
    mem: float
    elapsed: str
    command: str
    ports: list[str]
    score: int
    label: str
    reasons: list[str]


PERMISSION_ERRORS: list[str] = []


def run(command: list[str]) -> str:
    try:
        return subprocess.check_output(command, text=True, stderr=subprocess.DEVNULL)
    except PermissionError as error:
        PERMISSION_ERRORS.append(f"{command[0]}: {error}")
        return ""
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def parse_ps() -> list[dict[str, str]]:
    output = run(["ps", "-axo", "pid=,ppid=,%cpu=,%mem=,etime=,command="])
    rows: list[dict[str, str]] = []
    for line in output.splitlines():
        parts = line.strip().split(None, 5)
        if len(parts) < 6:
            continue
        pid, ppid, cpu, mem, elapsed, command = parts
        if int(pid) == os.getpid():
            continue
        rows.append(
            {
                "pid": pid,
                "ppid": ppid,
                "cpu": cpu,
                "mem": mem,
                "elapsed": elapsed,
                "command": command,
            }
        )
    return rows


def parse_listeners() -> dict[int, list[str]]:
    output = run(["lsof", "-iTCP", "-sTCP:LISTEN", "-n", "-P"])
    ports: dict[int, list[str]] = {}
    for line in output.splitlines()[1:]:
        parts = line.split()
        if len(parts) < 9:
            continue
        try:
            pid = int(parts[1])
        except ValueError:
            continue
        match = re.search(r":(\d+)\s+\(LISTEN\)", line)
        if match:
            ports.setdefault(pid, []).append(match.group(1))
    return ports


def matches_any(command: str, patterns: Iterable[str]) -> bool:
    lower = command.lower()
    return any(re.search(pattern.lower(), lower) for pattern in patterns)


def redact_command(command: str) -> str:
    redacted = command
    for pattern, replacement in SECRET_PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    return redacted


def score_process(row: dict[str, str], ports: list[str], cwd: str) -> tuple[int, str, list[str]]:
    command = row["command"]
    cpu = float(row["cpu"])
    ppid = int(row["ppid"])
    elapsed = row["elapsed"]
    score = 0
    reasons: list[str] = []

    is_ai = matches_any(command, AI_PATTERNS)
    is_dev = matches_any(command, DEV_PATTERNS)
    is_protected = matches_any(command, PROTECTED_PATTERNS)
    is_gui_app = matches_any(command, GUI_APP_PATTERNS)
    is_cli_like = is_dev or "mcp" in command.lower() or "playwright" in command.lower()

    if is_ai:
        score += 25
        reasons.append("AI/agent/tooling related command")
    if is_dev:
        score += 20
        reasons.append("development runtime command")
    if ppid == 1 and (is_ai or is_dev) and is_cli_like and not is_gui_app:
        score += 25
        reasons.append("orphaned under launchd/systemd (PPID=1)")
    if cpu >= 10:
        score += 30
        reasons.append(f"high CPU ({cpu:.1f}%)")
    elif cpu >= 2:
        score += 12
        reasons.append(f"noticeable CPU ({cpu:.1f}%)")
    if ports:
        score += 10
        reasons.append("listening on TCP port(s): " + ", ".join(sorted(set(ports))))
    if COMMON_DEV_PORTS.intersection(ports):
        score += 15
        reasons.append("listening on common dev port")
    if cwd and cwd in command:
        score += 20
        reasons.append("command includes current workspace path")
    if re.match(r"\d+-", elapsed) and (is_ai or is_dev) and not is_gui_app:
        score += 12
        reasons.append("running for more than one day")
    if is_protected:
        score -= 40
        reasons.append("protected/common system or service process")
    if is_gui_app and not is_cli_like:
        score -= 20
        reasons.append("GUI app/helper; usually quit the app instead of killing child PIDs")

    if score >= 60:
        label = "建议确认"
    elif score >= 35:
        label = "可疑但低负载"
    elif score >= 15:
        label = "看起来正常"
    else:
        label = "不要动" if is_protected else "低相关"
    return score, label, reasons


def audit() -> list[Process]:
    cwd = os.getcwd()
    listener_ports = parse_listeners()
    processes: list[Process] = []
    for row in parse_ps():
        pid = int(row["pid"])
        ports = sorted(set(listener_ports.get(pid, [])), key=lambda x: int(x))
        score, label, reasons = score_process(row, ports, cwd)
        if score < 15:
            continue
        processes.append(
            Process(
                pid=pid,
                ppid=int(row["ppid"]),
                cpu=float(row["cpu"]),
                mem=float(row["mem"]),
                elapsed=row["elapsed"],
                command=row["command"],
                ports=ports,
                score=score,
                label=label,
                reasons=reasons,
            )
        )
    return sorted(processes, key=lambda proc: (proc.score, proc.cpu), reverse=True)


def short_command(command: str, width: int = 120) -> str:
    redacted = redact_command(command)
    return redacted if len(redacted) <= width else redacted[: width - 1] + "…"


def print_text(processes: list[Process]) -> None:
    if PERMISSION_ERRORS:
        print("部分系统命令被权限限制拦截，结果可能不完整：")
        for error in PERMISSION_ERRORS:
            print(f"- {error}")
        print("在 Codex 沙盒中可用只读提权重跑同一命令。")
        print()
    if not processes:
        print("未发现明显相关的 AI/dev 后台进程。")
        return
    print("AI/dev 后台进程巡检结果（只读）：")
    print()
    for proc in processes[:40]:
        port_text = ",".join(proc.ports) if proc.ports else "-"
        print(
            f"[{proc.label}] PID={proc.pid} PPID={proc.ppid} "
            f"CPU={proc.cpu:.1f}% MEM={proc.mem:.1f}% 运行={proc.elapsed} 端口={port_text}"
        )
        print(f"  分数={proc.score} 原因：{'；'.join(proc.reasons)}")
        print(f"  命令：{short_command(proc.command)}")
        print()


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit likely leftover AI/dev processes.")
    parser.add_argument("--json", action="store_true", help="print JSON")
    args = parser.parse_args()

    processes = audit()
    if args.json:
        records = []
        for proc in processes:
            record = asdict(proc)
            record["command"] = redact_command(proc.command)
            records.append(record)
        print(json.dumps(records, ensure_ascii=False, indent=2))
    else:
        print_text(processes)
    return 0


if __name__ == "__main__":
    sys.exit(main())
