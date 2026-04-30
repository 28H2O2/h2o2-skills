---
name: h2o2-ai-process-auditor
author: 28H2O2
description: 诊断 macOS/Linux 上可能残留的 AI 编程助手、开发服务器、Node.js、Python、Playwright、MCP、浏览器自动化及端口监听进程。当用户询问 Claude Code、Codex、Cursor、VS Code、Agent、npm 开发服务器、Python 脚本、MCP 服务器、Playwright/Chrome 或后台进程是否仍在运行、是否占用 CPU/端口、是否需要清理时，使用此 Skill。
metadata:
  short-description: 审查残留的 AI/开发进程
---

# AI 进程审查器

使用此 Skill 检查 AI 编程工具和开发服务器遗留的本地后台进程。

## 核心规则

- 始终使用用户所用的语言进行交流。
- 默认只读检查，不做任何修改。
- 除非用户明确要求并确认具体清理目标，否则不得终止任何进程。
- 不要首先建议 `killall node`、`pkill -f python` 等批量终止命令。
- 进程命令行可能包含密钥等敏感信息；内置扫描器已对常见 token/key/password 模式进行脱敏，但避免在最终回答中粘贴不必要的完整命令行。
- 除非有明确证据，否则以下进程应视为用户重要进程，不得随意终止：数据库、Docker、代理/VPN、使用正常用户配置的浏览器、IDE、聊天应用、同步工具及系统进程。
- 优先使用温和终止：`kill <PID>` / `SIGTERM`；只有在用户确认后，且仅针对特定 PID，才使用 `kill -9`。

## 快速扫描

运行内置扫描脚本：

```bash
python3 “$CLAUDE_SKILL_DIR/scripts/ai_process_audit.py”
```

输出 JSON 格式：

```bash
python3 “$CLAUDE_SKILL_DIR/scripts/ai_process_audit.py” --json
```

如果进程列表因沙盒权限被拦截，请以提升权限重试同一命令，并向用户说明这是只读操作。

## 结果解读

按以下优先级排查：

1. 与 Agent、开发服务器、Node、Python、MCP、Playwright 或浏览器自动化相关的高 CPU 进程。
2. `PPID=1` 的长期孤儿进程，尤其是 `node`、`python`、`npm`、`next`、`vite`、`playwright`、`claude`、MCP 服务器，或位于项目/工作区目录下的脚本。
3. 监听常见开发端口的进程：`3000`、`3001`、`5173`、`8000`、`8080`、`8787`、`9009` 以及 Agent/浏览器端口。
4. 重复存在的 MCP、Playwright、浏览器自动化或 Claude Code 会话。
5. 命令行中包含当前工作目录路径的项目专属命令。

标签说明：

- `建议确认`：可能是残留进程，或值得向用户确认。
- `可疑但低负载`：目前可能无害，但可能已过期。
- `看起来正常`：可能与当前打开的应用/会话关联。
- `不要动`：系统/服务/应用进程，不应随意终止。

## 清理流程

当用户要求清理时：

1. 按风险分组列出简短的 PID 列表。
2. 终止任何进程前必须获得用户的明确确认。
3. 只终止已确认的 PID。
4. 重新运行扫描，汇报变化情况。

示例：

```bash
kill 47333
```

若短暂等待后进程仍存活：

```bash
kill -9 47333
```

只有在用户确认后才使用 `kill -9`。

## 报告风格

保持实用简洁：

- 说明是否存在真实的 CPU 占用大户。
- 列出最可疑的进程，包含 PID、CPU、运行时长、命令摘要及判断原因。
- 区分”正在占用 CPU”和”仅仅还在运行”。
- 只针对具体 PID 给出精确命令。
- 说明重启通常会停止普通进程，但 launchd/systemd/brew 服务及登录项可能会自动重启。
