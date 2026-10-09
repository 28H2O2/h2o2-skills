# H2O2 Research Design HTML · v1.2

将本目录复制到 Agent 的 Skills 目录；加载 `SKILL.md` 即可。

## Contents

- `SKILL.md` — 简明生成规范、事实边界、浏览器视觉 QA
- `references/design-guidelines.md` — 轻量报告视觉系统与交互规则
- `references/typography.md` — Apple 式微排版思路与视觉检查清单
- `assets/example.html` — Trajectory + Scene Map + 逐段中英对照的可交互 HTML
- `assets/example-compact.html` — 无 Thinking/Scene Map 的最小报告示例
- `assets/example.png` — 桌面截图
- `assets/example-thinking.png` — 长 Thinking 选中状态截图
- `assets/example-mobile.png` — 手机截图
- `assets/example-compact.png` — Compact 示例截图

## Example prompt

> 使用 h2o2-research-design-html，将这些真实 Agent 运行数据整理成**一份单文件 HTML 研究手记**：以轨迹为主、Scene Map 为辅；关键步骤只在有真实研究意义时标注；有 Thinking 则提供中文摘要和忠实双语原文；少解释、重可视化。生成后请截图自检。

## Design notes

- 两份 HTML 都纯离线、无 CDN、无外部脚本、无构建步骤。
- 示例数据全部为 **synthetic / 虚构演示**，不代表真实评测结论。
- `crafted by h2o2` 是可删除的视觉署名，不代表报告事实来源或研究作者。
- 不附带字体文件；主示例沿用内联 SVG 字标。

## v1.2 changes

1. 删除 Header 中重复的 Scenario/Case 指标卡，采用更克制的标题与一行数据概览。
2. 提升事件与辅助信息字号，优化字体层级、数字对齐与断行。
3. Scene Map 减少嵌套卡片边框，将焦点与已使用状态分开。
4. Thinking 英中段落对齐，证据模式切换更易阅读。
5. 泳道使用窄屏内部横向滚动，不压缩至不可读。
6. 新增极简示例与 visual screenshot QA 流程。

**Signature provenance:** 主示例保留 v1.1 的手写字标：源自开源字体 [Lobster Two](https://fonts.google.com/specimen/Lobster+Two) 字形轮廓（SIL Open Font License 1.1）。它以 SVG 图形内嵌，不包含字体文件。
