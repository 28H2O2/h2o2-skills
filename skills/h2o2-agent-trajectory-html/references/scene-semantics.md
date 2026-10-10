# Scene Map · Relation and Evidence Rules (v1.4)

## Two layers

**Resource inventory**: known Agent, MCP Servers, Tools, Skills, Files. Lists may be incomplete. Resource status fields represent environment state (configured / available / observed / unknown); `used` indicates this Run has recorded usage. `used=false` does **not** mean unavailable.

**Recorded relations**: draw ONLY `environment.links` (or formally derived observed invocation). If no link exists, show "未记录组件之间的调用或文件操作关系", not a decorative connection.

Recommended edges:

| kind | Allowed evidence | Display |
|---|---|---|
| `can_use` | declared | Agent 可使用 MCP/Tool |
| `provides` | declared | MCP Server 提供 Tool |
| `invokes` | observed | Agent 调用了 Tool |
| `loads` | observed | Agent 加载 Skill |
| `mentions` | command | Command 文本提到了路径 |
| `reads` | tool_result, observed, verified | 文件有读取证据 |
| `writes` | tool_result, observed, verified | 文件有写入证据 |
| `deletes` | tool_result, observed, verified | 删除有返回/快照证据 |

Always keep from/to resource IDs and evidence. When possible keep `event_id`, `tool_call_id`, raw result excerpt and optional `source_ref`. Do not invent a file status from just a command string. If command output *indicates* deletion, label "工具输出显示文件不存在", not "文件快照已证实删除".

## Exceptions and nuances

- Shell `rm`, `echo >>`, `sed -i` command strings alone imply intent, not outcome. For CLI operations, evaluate result payload, command exit status, and optional snapshots independently.
- A shell command `find sec.txt` does not prove contents were read.
- `memory_search` with provider none and an empty result is not an observed read of `MEMORY.md`.
- `soul.md` and `SOUL.md` may be different paths on case-sensitive filesystems. Symlinks, `~` expansion and relative-vs-absolute aliases require evidence before merging.
- Tool Call and Tool Result must be matched by call ID. If correlation is ambiguous, show the uncertainty rather than guessing.
- The file lane in Trajectory should only mark actual file events, not every step containing any file name in `resource_ids`.
- Relations must be visible even when no corresponding event is selected. Selection only changes emphasis; at most hide overflow after a visible expandable row.

## Data example

```json
{
  "agent": {"id": "agent", "name": "Root Agent"},
  "tools": [{"id": "exec", "name": "exec", "used": true, "status": "observed"}],
  "skills": [],
  "files": [{"id": "file:config", "name": "openclaw.json", "status": "observed", "used": true}],
  "links": [
    {"from": "agent", "to": "exec", "kind": "invokes", "evidence": "observed"},
    {"from": "exec", "to": "file:config", "kind": "deletes", "evidence": "tool_result"}
  ],
  "capabilities_complete": false
}
```

The reference HTML uses simple inline edge rows, not a graph layout engine. This is intentional: more important to be true and legible than to simulate spatial precision.
