# Changelog

## 场景优先文档更新 — 2026-10-10

- 中文任务和关键 Scene 同屏，先说明运行空间、参与对象与实际后果，再查看过程和证据。
- 调整电脑端空间优先级、关键对象字号、语义配色及次要清单折叠要求。
- 增加概览入口与实际 Case/Model/Run/Event ID 的一致性检查。
- 本次仅更新文档；HTML、渲染器、翻译、输入结构与测试保留 V1.4。

## v1.4 — 2026-10-10

- Removed decorative/fictitious Scene branches and introduced explicit `resource → relation → resource` cards backed by `environment.links[]`, retaining all known edges and highlighting current event.
- Reduced Inspector height on desktop to make Scene Map visible earlier; hid inactive language controls on Tool events.
- Preserved the selected model across Case changes where records exist; where unavailable, displays a change notice.
- Tightened File lane marks to observed reads/writes/creates/deletes/modifications with suitable evidence.
- Added `scripts/quality_check.py`: schema reference checks, weak Thinking-summary warnings, translation anomalies, and file evidence warnings.
- Reworked translation preparation to protect shell commands, inline code, paths and technical terms, with bounded batches, local caching and per-segment retry.
- Added optional v1.3 HTML embedded-data importer for migration and semantic regression. It does not invent Thinking summaries.
- Maintained single-file offline HTML; design reference uses fictional sample data, not actual study results.

### Known limitations

- Automated source text translation still requires human review for nuanced technical meanings. This repository has additionally tested the Apple runtime, protected technical identifiers and cached batches on macOS 27.0.1 / Swift 6.4.
- The repository retains the validated Swift 6 CLI and macOS browser-test fixes, and adds regression coverage for missing source IDs and failed read/delete evidence.
- The importer only supports the old AgentCanary `script#report-data` export shape. Other trace formats require a separate normalizer.
- Inferred shell-command file effects are deliberately conservative; partial shell commands, aliases and state changes not observable through results require additional file snapshots.
- The Scene Map uses compact relation cards rather than a free-form directed graph to stay lightweight.
