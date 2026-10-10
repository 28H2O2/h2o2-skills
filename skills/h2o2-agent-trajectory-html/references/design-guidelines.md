# H2O2 v1.4 · Information Design

## Desktop (primary)

```
Title: AgentCanary复现                brief verified totals
Scenario / Case (status in options) / Model / Run (only if >1)
User Instruction: full English + Chinese (directly visible)
┌──────────────────────────┬────────────────────────┐
│ TRAJECTORY (56%)         │ EVENT INSPECTOR (44%)  │
│ compact User/Agent/Tool  │ chosen event evidence  │
│ step swimlane            │ original / translation │
│ concise event list       │ in-panel scrolling     │
│                          ├────────────────────────┤
│                          │ SCENE MAP              │
│                          │ inventory + observed relations│
└──────────────────────────┴────────────────────────┘
```

- Case selection should preview **task title, result, and one concrete reason to inspect**, without turning dropdown into an entire dashboard. Use a native select for small counts; custom picker only if value is clear.
- Model selection updates visible result; no inaccurate cross-run summary in the Case dropdown.
- Show raw User Instruction above Trajectory, not a model-made evaluation paraphrase. Source language may be followed by a complete faithful Chinese translation. Never rename a summary to "全文译文".
- Timeline SVG conveys sequence; only label duration if timestamps exist. Click nodes to select corresponding event. Tool Call+Result one inspectable row. No mandatory key events.
- Event list: one line `verb → target`, optional second line `actual observed result`; Thinking: an objective decision in <= 1 sentence. Important events may have amber left hairline / evidence clip icon.
- Inspector directly adjacent to selected trace, not at the end of a long page. Fixed/scrollable independent panel when room allows. Expand original Thinking and faithful paragraph-by-paragraph translation. Control language view (`双语` / `原文` / `中文`), use clear `未翻译` state.
- Scene Map separates capability inventory from observed relations. Use prominent **工具 / 技能 / 文件** headings. Draw `Tool → file` only from recorded `links[]` with evidence; never fake relationships with decorative branches. Keep all known available-but-unused components visible while focusing related edges. Fit Inspector (~250px scrollable evidence) and the Scene Map heading/main groups into the initial 1440×900 desktop viewport where content allows.
- Timestamp, file hashes, full JSON paths belong behind a small `运行元数据` disclosure, not the primary UI.
- In mobile layouts, use stacked Inspector below trajectory (scroll into view on event selection), horizontal-locally-scrollable SVG, readable full-size text.

## Visual language

- Page background warm off-white (#F7F6F2); ink #222623; muted #70766F; accent blue #4779AA, violet #9069AF, green #2F896D, amber #AD7940.
- 15–16px default Chinese, 13–14px compact event summary, 14–15px event headers, 16–18px Scene group headings. Technical text monospace only where appropriate.
- Typography system stack first, Georgia/Palatino italic for small editorial touches; avoid decorative/AI-generated subtitles. `crafted by h2o2` as optional low-contrast signature footer.
- Fewer boxes; intentional whitespace, thin rules; do not multiply explanatory captions.
- Meaningful interactions 1) case/model/run switch, 2) event select, 3) evidence view toggle, 4) Scene focus highlight.

## Content checklist

- Each visible sentence says a fact, action, necessary caveat, or concrete model judgment, not design intent.
- Scores do not automatically imply outcome. Failures/no Judge scores can be `未知` or `未完成`.
- Source trace and translated text remain separately accessible; redaction cannot alter benign paths/identifiers or turn a normal shell `find` into file modification.
- Think of "readable in 20 seconds", not "a long introduction".

## Visual QA (v1.4 additions)

- Remove generic hero slogans; the report title should be the actual experiment name.
- If clicking a Trace step only changes a panel below the fold, that is a failure.
- Inspect Scene in a selected Tool event **and** in a plain Thinking event; connection rows stay visible, focus changes only.
- Do not mark every file reference in the swimlane with an identical green state node. Mark only observed file operations.
- Limit Inspector height and enable its own scrolling rather than pushing the Scene Map off-screen.
- Translate commands as non-executable descriptive text only in an additional field; never edit the original command.
