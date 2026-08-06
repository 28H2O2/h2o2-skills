#!/usr/bin/env python3
"""Store and use a Feishu custom-bot webhook without exposing it in prompts."""

from __future__ import annotations

import argparse
import getpass
import json
import os
import stat
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


APP_NAME = "h2o2-fdu-badminton-booker"
ALLOWED_HOSTS = {"open.feishu.cn", "open.larksuite.com"}


def default_config_path() -> Path:
    base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / APP_NAME / "feishu-webhook"


def validate_webhook(value: str) -> str:
    value = value.strip()
    parsed = urllib.parse.urlparse(value)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        allowed = ", ".join(sorted(ALLOWED_HOSTS))
        raise ValueError(f"webhook must use HTTPS and one of these hosts: {allowed}")
    if not parsed.path.startswith("/open-apis/bot/"):
        raise ValueError("webhook path does not look like a Feishu custom-bot endpoint")
    return value


def read_webhook(config_path: Path) -> str:
    if not config_path.is_file():
        raise FileNotFoundError(
            f"Feishu webhook is not configured; run: {sys.argv[0]} configure"
        )
    if os.name != "nt":
        mode = stat.S_IMODE(config_path.stat().st_mode)
        if mode & 0o077:
            raise PermissionError(
                f"config permissions are too broad ({mode:o}); run chmod 600 on the file"
            )
    return validate_webhook(config_path.read_text(encoding="utf-8"))


def configure(config_path: Path) -> int:
    webhook = validate_webhook(getpass.getpass("Feishu webhook URL (hidden): "))
    config_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if os.name != "nt":
        os.chmod(config_path.parent, 0o700)
    config_path.write_text(webhook + "\n", encoding="utf-8")
    if os.name != "nt":
        os.chmod(config_path, 0o600)
    print(f"Configured Feishu webhook at {config_path}")
    return 0


def check(config_path: Path) -> int:
    read_webhook(config_path)
    print(f"Feishu configuration is valid: {config_path}")
    return 0


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        raise urllib.error.HTTPError(req.full_url, code, msg, headers, fp)


def send(config_path: Path, text: str, dry_run: bool = False) -> int:
    webhook = read_webhook(config_path)
    payload = json.dumps(
        {"msg_type": "text", "content": {"text": text}},
        ensure_ascii=False,
    ).encode("utf-8")

    if dry_run:
        print(f"Dry run passed; payload bytes={len(payload)}; config={config_path}")
        return 0

    request = urllib.request.Request(
        webhook,
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    opener = urllib.request.build_opener(NoRedirectHandler())
    try:
        with opener.open(request, timeout=15) as response:
            raw = response.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        print(f"Feishu request failed: {exc.reason}", file=sys.stderr)
        return 1

    try:
        body = json.loads(raw)
    except json.JSONDecodeError:
        print("Feishu returned a non-JSON response", file=sys.stderr)
        return 1

    success = body.get("code") == 0 or body.get("StatusCode") == 0
    if not success:
        message = body.get("msg") or body.get("StatusMessage") or "unknown error"
        print(f"Feishu rejected the message: {message}", file=sys.stderr)
        return 1

    print("Feishu message delivered successfully")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=default_config_path(),
        help="webhook config path (default: user config directory)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("configure", help="securely prompt for and store the webhook")
    subparsers.add_parser("check", help="validate the stored webhook and permissions")
    send_parser = subparsers.add_parser("send", help="send a text notification")
    send_parser.add_argument("--text", required=True)
    send_parser.add_argument("--dry-run", action="store_true")
    subparsers.add_parser("test", help="send a harmless test notification")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "configure":
            return configure(args.config)
        if args.command == "check":
            return check(args.config)
        if args.command == "send":
            return send(args.config, args.text, args.dry_run)
        if args.command == "test":
            return send(args.config, "【复旦羽毛球监控】飞书通知测试成功。")
    except (FileNotFoundError, PermissionError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
