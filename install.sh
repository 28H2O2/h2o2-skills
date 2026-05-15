#!/bin/bash
# 用法：bash install.sh [--force]

SKILLS_DIR="$HOME/.claude/skills"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
FORCE=0
[[ "$1" == "--force" ]] && FORCE=1

mkdir -p "$SKILLS_DIR"

for skill_dir in "$REPO_DIR/skills"/*/; do
  skill_name=$(basename "$skill_dir")
  [[ ! -f "$skill_dir/SKILL.md" ]] && continue

  target="$SKILLS_DIR/$skill_name"
  if [[ -e "$target" || -L "$target" ]]; then
    if [[ $FORCE -eq 1 ]]; then
      rm -rf "$target"
    else
      echo "已存在，跳过: $skill_name  (--force 覆盖)"
      continue
    fi
  fi

  ln -s "$skill_dir" "$target"
  echo "已安装: $skill_name -> $target"
done

echo ""
echo "完成。重启 Claude Code 后新 skill 生效。"
