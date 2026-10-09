#!/usr/bin/env python3
"""Offline-by-default, opt-in Apple Translation / custom CLI, no pip dependencies.

The script fills *only missing* Chinese translations in H2O2 report JSON.
On any failure it retains the original English and records translation status.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shlex
import subprocess
import sys

HERE = Path(__file__).resolve().parent
DEFAULT_CACHE = Path.home() / ".cache" / "h2o2-research-design-html" / "translation-cache.json"
VALID_BACKENDS = {"apple", "none", "command"}


def digest(text, backend):
    return hashlib.sha256(("v1.3|en>zh-Hans|" + backend + "|" + text).encode("utf-8")).hexdigest()


def check_identifiers(original, translation):
    """Conservative quality gate: never silently corrupt code/path markers."""
    tokens = set(re.findall(r"`[^`\n]+`|(?<!\w)/(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+|\b[A-Za-z0-9_.-]+\.(?:md|txt|json|py|sh|yaml|yml)\b|\b[A-Z][A-Z0-9_]{2,}\b", original))
    return all(t in translation for t in tokens)


def mac_version_ok():
    if platform.system() != "Darwin":
        return False
    parts = platform.mac_ver()[0].split(".")
    return bool(parts and parts[0].isdigit() and int(parts[0]) >= 26)


def apple_command():
    if not mac_version_ok():
        raise RuntimeError("Apple CLI requires macOS 26+ (see sw_vers -productVersion).")
    package = HERE / "apple-translate"
    result = subprocess.run(["swift", "build", "--package-path", str(package), "-c", "release"],
                            text=True, capture_output=True, timeout=240, check=False)
    if result.returncode:
        diagnostics = result.stdout + "\n" + result.stderr
        errors = [line for line in diagnostics.splitlines() if "error:" in line]
        raise RuntimeError("Swift build failed: " + ("\n".join(errors) or diagnostics[-1000:]))
    binary = package / ".build" / "release" / "h2o2-apple-translate"
    if not binary.exists():
        raise RuntimeError("Swift build finished but executable was not found")
    return [str(binary)]


def run_batch(requests, backend, command=None):
    if backend == "none":
        return {}
    argv = apple_command() if backend == "apple" else shlex.split(command or "")
    if not argv:
        raise RuntimeError("--command must specify a translation program")
    payload = json.dumps({"requests": [{"id": str(i), "text": txt} for i, txt in enumerate(requests)]}, ensure_ascii=False)
    proc = subprocess.run(argv, input=payload, text=True, capture_output=True, timeout=240, check=False)
    if proc.returncode:
        raise RuntimeError(f"Translator failed ({proc.returncode}): {proc.stderr[-700:]}")
    obj = json.loads(proc.stdout)
    returned = obj.get("translations", [])
    if len(returned) != len(requests):
        raise RuntimeError("Translator response count mismatch")
    mapping = {row["id"]: row["text"] for row in returned}
    if set(mapping) != {str(i) for i in range(len(requests))}:
        raise RuntimeError("Translator response IDs mismatch")
    return {txt: mapping[str(i)] for i, txt in enumerate(requests)}


def segments(text):
    """Preserve blank lines and original paragraph boundaries."""
    return [s for s in re.split(r"(\n\s*\n)", text) if s]


def translatable(part):
    return bool(part.strip() and re.search(r"[A-Za-z]{3,}", part)) and not re.fullmatch(r"\s+", part)


def targets_of(data):
    for case in data.get("cases", []):
        instruction = case.get("instruction") or {}
        if instruction.get("en") and not instruction.get("zh"):
            yield instruction, "zh", instruction["en"]
        for run in case.get("runs", []):
            for event in run.get("events", []):
                if event.get("kind") == "thinking" and event.get("original") and not event.get("translation_zh"):
                    yield event, "translation_zh", event["original"]


def prepare(data, backend, command=None, cache_path=DEFAULT_CACHE, use_cache=True):
    result = copy.deepcopy(data)
    targets = list(targets_of(result))
    cache = {}
    if use_cache and cache_path.exists():
        try:
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            cache = {}
    missing = []
    for _, _, source in targets:
        for part in segments(source):
            if translatable(part) and digest(part, backend) not in cache and part not in missing:
                missing.append(part)
    translations = {}
    error = None
    try:
        translations = run_batch(missing, backend, command) if missing else {}
    except (RuntimeError, OSError, subprocess.TimeoutExpired, ValueError) as e:
        error = str(e)
    for text, translated in translations.items():
        if isinstance(translated, str) and translated.strip() and check_identifiers(text, translated):
            cache[digest(text, backend)] = translated
    translated_items = 0
    failed_items = 0
    for target, field, source in targets:
        parts = segments(source)
        output = []
        bad = False
        for part in parts:
            if not translatable(part):
                output.append(part)
            elif digest(part, backend) in cache and check_identifiers(part, cache[digest(part, backend)]):
                output.append(cache[digest(part, backend)])
            else:
                bad = True
                break
        if not bad and output and backend != "none":
            target[field] = "".join(output)
            target["translation_status"] = "translated_" + backend
            translated_items += 1
        else:
            target["translation_status"] = "untranslated" if backend == "none" else "failed_or_unavailable"
            failed_items += 1
    if use_cache and translations:
        cache_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        temp = cache_path.with_name(cache_path.name + ".tmp")
        with temp.open("w", encoding="utf-8") as f:
            os.chmod(temp, 0o600)
            json.dump(cache, f, ensure_ascii=False, indent=1)
        temp.replace(cache_path)
    return result, {"targets": len(targets), "translated": translated_items, "untranslated": failed_items, "error": error}


def main():
    p = argparse.ArgumentParser(description="Prepare en→zh-Hans translations in H2O2 report JSON (offline by default)")
    p.add_argument("--input", type=Path)
    p.add_argument("--output", type=Path)
    p.add_argument("--backend", choices=sorted(VALID_BACKENDS), default="apple")
    p.add_argument("--command", help="Explicit custom translator command, same JSON protocol as Apple Swift tool")
    p.add_argument("--no-cache", action="store_true")
    p.add_argument("--cache-path", type=Path, default=DEFAULT_CACHE)
    p.add_argument("--self-test", metavar="ENGLISH_TEXT", help="Translate a single string (requires backend)")
    args = p.parse_args()
    if args.self_test is not None:
        try:
            print(json.dumps(run_batch([args.self_test], args.backend, args.command), ensure_ascii=False))
        except Exception as exc:
            print(f"Translation unavailable: {exc}", file=sys.stderr)
            sys.exit(2)
        return
    if not args.input or not args.output:
        p.error("--input and --output are required unless --self-test is used")
    if args.backend == "command" and not args.command:
        p.error("--backend command requires --command")
    raw = json.loads(args.input.read_text(encoding="utf-8"))
    out, status = prepare(raw, args.backend, args.command, args.cache_path, not args.no_cache)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(status, ensure_ascii=False))
    if status["error"]:
        print("Notice: untranslated original retained. " + status["error"], file=sys.stderr)


if __name__ == "__main__":
    main()
