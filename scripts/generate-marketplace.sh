#!/bin/bash
# 扫描 skills/*/SKILL.md 重新生成 .claude-plugin/marketplace.json。
# 新增/删除 skill 后跑一次即可，避免与目录实际内容漂移。
# 用法：bash scripts/generate-marketplace.sh

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="$REPO_DIR/skills"
OUT="$REPO_DIR/.claude-plugin/marketplace.json"

paths=()
for skill_dir in "$SKILLS_DIR"/*/; do
  [[ -f "$skill_dir/SKILL.md" ]] || continue
  name=$(basename "$skill_dir")
  paths+=("./skills/$name")
done

skills_json=""
for i in "${!paths[@]}"; do
  [[ $i -gt 0 ]] && skills_json+=","
  skills_json+=$'\n        "'${paths[$i]}'"'
done

mkdir -p "$(dirname "$OUT")"
cat > "$OUT" <<EOF
{
  "name": "h2o2-skills",
  "owner": { "name": "28H2O2" },
  "metadata": {
    "description": "h2o2-skills: 自建 Claude Code skill 集合（arXiv 论文、B 站/YouTube 字幕、PPT、仓库清理、AI 进程巡检等）",
    "version": "0.1.0"
  },
  "plugins": [
    {
      "name": "h2o2-skills",
      "description": "h2o2-skills 全集：内容采集、论文处理、PPT 生成、本地仓库与进程巡检",
      "source": "./",
      "strict": false,
      "skills": [${skills_json}
      ]
    }
  ]
}
EOF

echo "已生成 ${OUT} (${#paths[@]} skills)"
