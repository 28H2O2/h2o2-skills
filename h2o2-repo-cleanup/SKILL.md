---
name: h2o2-repo-cleanup
author: 28H2O2
description: >
  Audit and clean up a local directory full of code repositories — especially
  useful for researchers who clone many repos to read/experiment with and then
  need to reclaim disk space. Use this skill whenever the user says things like
  "my repos are taking up too much space", "help me clean up my code folder",
  "which repos can I delete", "re-clone with depth 1", or "generate a disk usage
  report for my projects directory". Also trigger for any combination of: large
  .git directories, redundant zip files, cloned repos with no local changes,
  VM images or model weights sitting inside repo folders.
platform: macOS
---

# Repo Cleanup Skill

You are helping a developer reclaim disk space from a directory containing a mix
of their own repos and third-party repos they cloned for reference.

The workflow has four phases. Work through them in order, but stay flexible —
if the user has already done some steps (e.g. they just want a fresh report),
jump to where they are.

---

## Phase 1: Scan

Run the scan script to collect raw data about every item in the target directory:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/scan_repos.py" <target-directory>
```

The script outputs JSON. Parse it to understand the full picture before saying
anything to the user. At minimum, note:
- Total directory size
- The top 5–10 items by size (these almost always explain 80%+ of usage)
- Any items in the "quick wins" category (redundant zips, regenerable dirs)

---

## Phase 2: Report

Present a ranked size table, grouped into three sections:

**Section A — Your own repos** (has local commits not pushed, or no remote)
**Section B — Cloned repos** (has a remote; may or may not have local changes)
**Section C — Non-git items** (data, results, zips, weights, etc.)

For each cloned repo, show:
- Total size / `.git` size / ratio
- Whether it has local changes (`git status`)
- Remote URL (for re-cloning)
- Last-modified date of the directory

Call out the "unusual suspects" explicitly:
- `.git` taking >50% of total size → strong re-clone candidate
- Zip file whose name matches an existing directory → pure redundancy
- Directories named `vmware_vm_data`, `__pycache__`, `node_modules`,
  `.venv`, `env`, `checkpoints`, `weights`, `*.pth`, `*.bin`, `*.ckpt`
  → almost always safe to delete or regenerate

---

## Phase 3: Recommendations

Produce a prioritized action list in three tiers:

**Tier 1 — Safe, immediate wins** (no local changes, clearly redundant)
Examples: duplicate zips, VM images, `node_modules/`, `__pycache__/`

**Tier 2 — Re-clone with `--depth 1`** (cloned repos, no local changes,
large `.git`)
Explain `--depth 1` briefly if the user hasn't heard it: it keeps only
the latest snapshot, discarding all git history. Fine for read-only reference
repos. Saves the full `.git` size.

**Tier 3 — Review before acting** (repos with local changes)
For each, offer to show what the local changes actually are (`git diff`,
`git status --short`) so the user can decide whether they matter.

Always state the estimated space savings clearly per item and in total.

---

## Phase 4: Generate Commands

Because permanent deletion cannot be executed on behalf of the user, generate
a ready-to-run shell script they can review and execute themselves. Structure it
as a commented script:

```bash
#!/bin/bash
# Repo Cleanup Commands
# Generated: <date>
# Estimated savings: X GB
#
# Review each section before running.
# Each block is independent — comment out anything you want to skip.

TARGET="<path>"

# ── TIER 1: Immediate wins ─────────────────────────────────────────
# <explanation>
rm -rf "$TARGET/<item>"

# ── TIER 2: Re-clone with --depth 1 ───────────────────────────────
# Saves ~X GB. No local changes detected.
rm -rf "$TARGET/<repo>" && git clone --depth 1 <url> "$TARGET/<repo>"

# ── TIER 3: Manual review needed ──────────────────────────────────
# <repo> has N local changes — review before deciding.
# git -C "$TARGET/<repo>" diff   # uncomment to inspect
```

Save this script to the target directory as `cleanup_commands.sh` and tell the
user the path.

---

## Extended Checks (run if user wants deeper analysis)

These take longer but surface more savings. All commands are macOS (BSD) syntax.

```bash
# Large files anywhere in the tree (>50MB)
find <dir> -size +50M -not -path '*/.git/*' -exec du -sh {} \; | sort -rh

# Regenerable Python artifacts
find <dir> -type d -name '__pycache__' -not -path '*/.git/*'
find <dir> -type d -name '.venv' -not -path '*/.git/*'
find <dir> -type d -name 'node_modules' -not -path '*/.git/*'

# Model weight files
find <dir> -type f \( -name '*.pth' -o -name '*.bin' -o -name '*.ckpt' \
  -o -name '*.safetensors' \) -not -path '*/.git/*' -exec du -sh {} \; | sort -rh

# Stale repos (not touched in >90 days) — macOS stat + date
find <dir> -maxdepth 1 -type d -not -name '.*' \
  -exec stat -f "%m %N" {} \; | \
  awk -v cutoff=$(date -v-90d +%s) '$1 < cutoff {print $2}' | sort
```

Surface findings naturally — don't dump raw output at the user.

---

## Notes on Safety

- Never execute `rm` commands yourself. Always give them to the user to run.
- Before recommending deletion of a repo with local changes, show what those
  changes are and let the user decide.
- For repos where the upstream URL uses SSH (`git@github.com:...`), flag this —
  the user needs their SSH key available to re-clone.
- A repo with no `.git` directory might still be important (it could be a
  hand-downloaded archive or a data directory). Don't treat no-.git as
  automatically disposable.
