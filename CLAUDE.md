# h2o2-skills 仓库规范

## 命名规则

所有 skill 目录名和 SKILL.md 中的 `name` 字段必须以 `h2o2-` 开头：

```
h2o2-<skill-name>/
└── SKILL.md   ←  name: h2o2-<skill-name>
```

## 作者标注

每个 SKILL.md 的 frontmatter 必须包含 `author: 28H2O2`：

```yaml
---
name: h2o2-<skill-name>
author: 28H2O2
description: ...
---
```

## 安装方式

使用 symlink 安装到 `~/.claude/skills/`，不要用 `cp`：

```bash
ln -sf /Users/h2o2/Desktop/Project/h2o2-skills/h2o2-<skill-name> ~/.claude/skills/h2o2-<skill-name>
```

或统一执行：

```bash
bash install.sh
```

symlink 的好处：仓库里修改后直接生效，无需重新安装。
