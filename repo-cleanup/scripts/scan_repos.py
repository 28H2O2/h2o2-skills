#!/usr/bin/env python3
"""
scan_repos.py — Scan a directory of code repos and output structured JSON.

Usage:
    python3 scan_repos.py <target-directory>

Output: JSON to stdout with full inventory of every item, git metadata,
size breakdowns, and quick-win flags.
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path


def run(cmd, cwd=None):
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, cwd=cwd, timeout=15
        )
        return result.stdout.strip()
    except Exception:
        return ""


def du_mb(path):
    """Return size in MB using du. Uses list invocation to avoid shell injection."""
    try:
        result = subprocess.run(
            ["du", "-sm", str(path)],
            capture_output=True, text=True, timeout=15
        )
        return float(result.stdout.split()[0])
    except Exception:
        return 0.0


def human(mb):
    if mb >= 1024:
        return f"{mb/1024:.1f} GB"
    return f"{mb:.0f} MB"


def scan_item(path: Path):
    total_mb = du_mb(path)
    item = {
        "name": path.name,
        "path": str(path),
        "total_mb": total_mb,
        "total_human": human(total_mb),
        "last_modified": int(path.stat().st_mtime),
        "last_modified_iso": time.strftime(
            "%Y-%m-%d", time.localtime(path.stat().st_mtime)
        ),
        "is_git_repo": False,
        "git_size_mb": 0,
        "git_ratio": 0.0,
        "remote_url": None,
        "local_changes": 0,
        "local_change_files": [],
        "flags": [],
    }

    git_dir = path / ".git"
    if git_dir.exists():
        item["is_git_repo"] = True
        item["git_size_mb"] = du_mb(git_dir)
        if item["total_mb"] > 0:
            item["git_ratio"] = round(item["git_size_mb"] / item["total_mb"], 2)

        item["remote_url"] = run("git remote get-url origin 2>/dev/null", cwd=path)

        # local changes
        status = run("git status --porcelain 2>/dev/null", cwd=path)
        lines = [l for l in status.splitlines() if l.strip()]
        # Exclude .DS_Store — macOS noise
        real_changes = [l for l in lines if ".DS_Store" not in l]
        item["local_changes"] = len(real_changes)
        item["local_change_files"] = real_changes[:10]  # cap at 10

    # Flag: .git dominates (re-clone candidate; threshold 0.4 to catch near-majority cases)
    if item["is_git_repo"] and item["git_ratio"] >= 0.4 and item["total_mb"] > 50:
        item["flags"].append("git_heavy")

    # Flag: safe to re-clone (no meaningful local changes, has remote)
    if item["is_git_repo"] and item["local_changes"] == 0 and item["remote_url"]:
        item["flags"].append("safe_reclone")

    # Flag: has local changes that need review
    if item["is_git_repo"] and item["local_changes"] > 0:
        item["flags"].append("has_local_changes")

    # Flag: SSH remote (needs SSH key for re-clone)
    if item["remote_url"] and item["remote_url"].startswith("git@"):
        item["flags"].append("ssh_remote")

    return item


def scan_files(target: Path):
    """Scan loose files (non-directories) for quick wins."""
    files = []
    dir_names = {d.name for d in target.iterdir() if d.is_dir()}

    for f in target.iterdir():
        if not f.is_file():
            continue
        size_mb = f.stat().st_size / (1024 * 1024)
        entry = {
            "name": f.name,
            "path": str(f),
            "size_mb": round(size_mb, 1),
            "flags": [],
        }

        # Flag: zip file whose stem matches an existing directory
        if f.suffix == ".zip":
            stem = f.stem
            # Handle "Name 2.zip" style duplicates
            stem_clean = stem.rstrip(" 0123456789").strip()
            if stem in dir_names or stem_clean in dir_names:
                entry["flags"].append("redundant_zip")
            else:
                entry["flags"].append("zip")

        if size_mb > 50:
            entry["flags"].append("large_file")

        files.append(entry)

    return files


def main():
    if len(sys.argv) < 2:
        print("Usage: scan_repos.py <target-directory>", file=sys.stderr)
        sys.exit(1)

    target = Path(sys.argv[1]).expanduser().resolve()
    if not target.is_dir():
        print(f"Not a directory: {target}", file=sys.stderr)
        sys.exit(1)

    dirs = sorted(
        [d for d in target.iterdir() if d.is_dir() and not d.name.startswith(".")],
        key=lambda d: d.name,
    )

    print(f"Scanning {len(dirs)} directories in {target} ...", file=sys.stderr)

    items = []
    for i, d in enumerate(dirs):
        print(f"  [{i+1}/{len(dirs)}] {d.name}", file=sys.stderr)
        items.append(scan_item(d))

    # Sort by size descending
    items.sort(key=lambda x: x["total_mb"], reverse=True)

    files = scan_files(target)
    files.sort(key=lambda x: x["size_mb"], reverse=True)

    total_mb = sum(i["total_mb"] for i in items) + sum(
        f["size_mb"] for f in files
    )

    # Summary
    redundant_zips = [f for f in files if "redundant_zip" in f["flags"]]
    git_heavy_no_changes = [
        i for i in items
        if "git_heavy" in i["flags"] and "safe_reclone" in i["flags"]
    ]
    has_changes = [i for i in items if "has_local_changes" in i["flags"]]

    output = {
        "target": str(target),
        "total_mb": round(total_mb, 1),
        "total_human": human(total_mb),
        "item_count": len(items),
        "summary": {
            "redundant_zip_count": len(redundant_zips),
            "redundant_zip_mb": round(sum(f["size_mb"] for f in redundant_zips), 1),
            "reclone_candidates": len(git_heavy_no_changes),
            "reclone_savings_mb": round(
                sum(i["git_size_mb"] for i in git_heavy_no_changes), 1
            ),
            "repos_with_local_changes": len(has_changes),
        },
        "directories": items,
        "files": files,
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
