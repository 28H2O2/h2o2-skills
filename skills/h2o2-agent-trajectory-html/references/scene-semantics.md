# Scene Map · Spatial Context, Relations and Evidence

## Context the reader can recognize

Show the key scene beside the Chinese Instruction: which Agent acts, what the normal task needs, and which tools, skills and files participate. Identify host / container / workspace / MCP boundaries only when supported by source material; unknown location stays unknown. No additional schema fields are mandatory for layout.

Explain the recorded order and data movement: preparation, exposure to tool descriptions or Skill text, invocation, return and observed effect. A spatial grouping is not a claim that every listed component was used. Use containers for membership and arrows only for evidenced direction; a proposed workflow is not a real Trace.

Keep callable Agent tools, scripts invoked through exec, Skill instructions and files distinct. Use readable purpose labels alongside original IDs / names / paths. Configured Skills do not imply loading; availability is not usage. Key resources and necessary relations should be visible while reading the task; collapse only secondary inventory / evidence, revealing selected resources when needed.

## Two layers

**Resource inventory**: known Agent, MCP Servers, Tools, Skills, Files. Key components are directly visible; the complete known list, including unused resources, remains accessible in expandable inventory. Lists may be incomplete. Resource status fields represent environment state (configured / available / observed / unknown); `used` indicates this Run has recorded usage. `used=false` does **not** mean unavailable.

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
- Relations must be visible even when no corresponding event is selected. Selection only changes emphasis and reveals related folded resources; do not remove unrelated known components. Secondary relation rows may be folded behind a clear expandable entry, while necessary scene relationships remain visible.

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

The V1.4 compatibility HTML uses inline relation rows. New reports may use groups or a small spatial diagram when that clarifies the actual environment; no graph engine or extra diagram is required. Input shape and evidence rules remain compatible.
