# H2O2 Research Design HTML · Visual System v1.2

## Design intent

出版感研究手记，而不是仪表盘。「90% 严谨的实验记录 + 10% 有性格的编辑设计」。以可读性和信息真实性为先，最后才添加细微装饰。

## Color & shape

- Warm paper `#faf8f4`、panel `#fff`、ink `#292b2c`、secondary `#697079`、border `#e5e1da`。
- Agent / Thinking：`#557eaf`；Tools / MCP：`#886db4`；文件 / used：`#397b67`；少数特殊注释：`#a9773b`；明确失败：`#b75b55`。
- 允许轻阴影但通常优先细分隔线；面板圆角 12–16px，内容项 7–10px。
- 减少「大卡里小卡里再套小卡」：外层 panel 界定模块，内部以留白/细线组织，而不是每一行都有重描边。
- 颜色表达事件类型或意义；另外用边框/背景表达 focus。**Used 不随焦点切换而变化。**

## Main layout

1. 极简 Header：实验归属、标题、短上下文、一行有效数字。不要把 Scenario/Case 再重复做成两张相同语义的大指标卡。
2. 有多个候选值时才展示 Scenario/Case/Model/Run 选择器。它们属于内容导航，不属于指标。
3. 桌面：Trajectory / Scene Map ~ 3:2，Evidence 在下方。窄屏上下排列；不缩成看不清的微型 SVG。
4. Footer：真实来源、限制、可选署名，避免“官方认证”等误导信息。

## Trajectory

- 顶部小型 User/Agent/Tool 泳道展现真实事件顺序；如果有真实 time span 才画非等距时间轴，并标注单位。
- 事件列表为主要阅读区域：步骤编号、类型、短标题、1–2 行中文摘要；不是日志全文。
- 合并配对 Tool Call/Result，保持前后 Thinking 在正确位置。调用异常时保留失败返回，不隐去。
- Key moment 是可选的小琥珀色边注；默认不标，最多保留真正有意义的节点。说明紧贴对应事件。
- 可选的 Evidence 小回形针必须是真实可点击的证据入口，不能成为无功能图标。

## Scene Map

- Agent 用独立的轻卡片，Tools/Skills/Workspace 主要用小标题与间隔线分组，减少视觉上所有框同权重的问题。
- Tools 的 available/used，Skills 的 configured/loaded，Files 的 read/created/modified/deleted 只依据相关真实数据。若缺少证据，显示 unknown。
- 场景资源的**整轮使用状态**与**当前选中高亮**独立；选中事件时 Scene 不隐藏其他组件。
- Scene 资源很多时可折叠长清单；不要画几十个静态节点连线以追求“炫酷”。

## Evidence / Thinking

- 区分摘要（模型生成者的压缩陈述）、原文、忠实翻译、工具入参与返回。不可把摘要标成「直译」。
- 有多段 Thinking 时，以「英文段落 ↔ 中文段落」逐行成对；中文不需要机械逐词翻译，但必须保留语义、犹豫、否定和自我修正。
- 中文与英文证据容器具有相同的视觉地位；切换单语言时更宽，保证阅读舒适。
- 很长的正文建议 max-width 约 70–90ch，或局部滚动；保留可复制的全文。

## Decoration / signature

- 英文标题少量使用系统衬线斜体；不将装饰字体用于表格、代码、日志或复杂 UI。
- 页脚 `crafted by h2o2` 落款轻巧、低对比、可选；不遮盖数据。当前主示例保留内联 SVG 落款，离线可用，不另附字体文件。
- 允许至多 2–3 个细节（例如署名、页边极细线、档案编号），装饰不能要求产生假的关键节点。

## Responsive fallback

- 930px 以下由左右变上下；640px 以下标题/选择器/双语版式重新组织。
- 泳道在窄屏改为自身可横向滚动，保留标签与点击精度；不得让整个 document 出现横向滚动。
- 触控事件行有充足点击面积，所有交互支持键盘操作和明显焦点样式。

## Two references, not one template

- `../assets/example.html`：有 Thinking + Scene Map 的 Trace-first 案例。
- `../assets/example-compact.html`：三步、无 Thinking、无 Scene Map 的最小实验，故意不塞满版面。

永远先判断用户带来的信息是否支持图形，再决定生成图形。
