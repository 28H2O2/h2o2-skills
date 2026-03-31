#!/usr/bin/env python3
import argparse
import glob
import json
from pathlib import Path


def load_text(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    body = data.get("body", [])
    lines = [seg.get("content", "").strip() for seg in body]
    lines = [line for line in lines if line]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", help="subtitle json paths or globs")
    parser.add_argument("--output", help="write first input as plain text")
    parser.add_argument("--merge-output", help="write merged corpus for all inputs")
    args = parser.parse_args()

    paths = []
    for pattern in args.inputs:
        matches = sorted(glob.glob(pattern))
        if matches:
            paths.extend(matches)
        else:
            paths.append(pattern)
    files = [Path(p) for p in paths]

    texts = []
    for path in files:
        text = load_text(path)
        texts.append((path, text))

    if args.output:
        if not texts:
            raise SystemExit("no input files")
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(texts[0][1], encoding="utf-8")

    if args.merge_output:
        merge_path = Path(args.merge_output)
        merge_path.parent.mkdir(parents=True, exist_ok=True)
        merged = []
        for path, text in texts:
            merged.append(f"# {path.name}\n\n{text}\n")
        merge_path.write_text("\n".join(merged), encoding="utf-8")

    if not args.output and not args.merge_output:
        for path, text in texts:
            print(f"# {path.name}\n")
            print(text)
            print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
