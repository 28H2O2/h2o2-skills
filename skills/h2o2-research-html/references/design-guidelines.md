# H2O2 视觉与交互规范 · v1.1

## 目标

阅读型实验报告，观感像精心排版的研究手记。让一个第一次打开报告的人在十几秒内看出“任务、轨迹、环境、结果”。**图中已有的信息不用再写一段解释。**

## 视觉语言

- 默认浅暖纸背景 `#faf8f4`，白色面板 `#fff`，线 `#e6e2dc`，文字 `#23282d`，次级 `#72777e`。
- Agent/Thinking：蓝 `#4e7ab8`；Tool/MCP：紫 `#8c6bc1`；文件/成功：绿 `#35866e`；关键强调：琥珀 `#b9823f`；失败：红 `#c45b53`。
- 颜色有状态语义，当前选中用边框或浅底强调；**“整轮已使用”和“当前事件涉及”分别表达**。
- 圆角 10–16px；轻边框优先于重阴影；留白清楚，避免大片花哨渐变、霓虹、动画。
- 标题 22–26px，正文 14–15px，辅助 11–13px；轨迹普通事件约 48–60px，关键事件略展开；数字大卡不必每页都有。
- **品牌小签名**：右下 Footer 可以用低对比小号 `crafted by h2o2 ✳`，字体可略带字距；绝不占据标题或遮挡正文。不要写“官方认证”之类误导文本。

## Trajectory

- 第一段使用小幅泳道概览：User / Agent / Tool（如需要加 Sub-Agent）；横轴如果只记录顺序，必须写“step order”。
- 第二段是紧凑事件列表：编号、图标/事件类型、极短中文说明。仅特殊案例标注 Decision/Action/Observation/Outcome，允许完全没有标注。
- Thinking 与前后工具事件保持顺序；相匹配的 tool call + result 组合成一条。
- 每个事件可选中，选中后在 Evidence 显示原文、翻译或调用参数与返回。

## Scene Map

- 以**卡片式资源清单**呈现，而非必须画连线拓扑：Agent 基本信息；MCP/Tools；Skills；Workspace。
- 已知配置 ≠ 实际暴露；已暴露未使用应当与未知分开；已使用保持绿色标识，当前选中关联节点再加蓝色淡底或描边。
- 切换 Model / Run 后更新 used 状态；切换当前事件只改变 focus，不删去未使用节点。
- 当某类资源未知或没有可靠数据时显示 `未知` 或省略模块，不编造完整列表。

## Thinking 与双语

- 事件中的一句中文摘要标记为“摘要”，尽量客观（例如“判断配置修改可以执行，随后调用 write”）。
- Evidence 提供原文 / 中文 / 双语切换。简洁但忠实地翻译完整原文；**不要将压缩摘要冒充直译**。
- 输出很长时容器最大高度 + 内部滚动；用户仍可复制全文。
- 无原始 Thinking 就标“无可用 Thinking 记录”，不可生成想象的思考文字。

## 选择器与适配

- Scenario > Case 是内容选择；Model > Run 是执行实例选择。随数据按需显示，不限制必须四个选择器。
- Desktop 左 60–65%、右 35–40%；Evidence 放下面。不超过 850px 变成纵向堆叠。
- 资源很多时卡片内部折叠/滚动，不让整页横向溢出。

## 安全与测试

- 外部数据文本 `textContent`；若模板生成 HTML，先完整进行 HTML 和 JS 上下文转义。
- 报告默认脱敏密钥与个人信息，保持来源线索与 hash/行号，避免将隐私复制到可分享的 HTML。
- 检查切换 Case、Model、Run 之后图表、选中事件、Scene 和 Evidence 都更新。
- `scrollWidth <= clientWidth` 在桌面及窄屏都成立。对缺失时间字段不生成虚构的精确持续时间。

示例 `../assets/example.html` 提供视觉与行为参照；真实报告应当按数据裁剪模块。


## Typography & gentle details · v1.1

- 维持正文系统无衬线，数据仍以对比度和对齐为先。
- **英文展示标题**：仅小范围应用优雅斜体衬线，如 `Iowan Old Style / Baskerville / Palatino / Georgia Italic`；参考在线字体 [Instrument Serif](https://github.com/Instrument/instrument-serif)。
- **页脚落款**：`a field note, crafted by` 采用极小斜体，`h2o2` 使用内联 SVG 手写轮廓，带一条近似铅笔的收尾线；不引用线上 CDN，也不附带字体文件。当前示例的字形轮廓取自开源 Lobster Two (SIL OFL 1.1)，仅四个字形的矢量轮廓用于显示，参见 [许可](https://fontsource.org/fonts/lobster-two/about)。可参考 [Caveat](https://fonts.google.com/specimen/Caveat) 进一步探索笔记手写感。
- **边注**：只有明确的关键事件才有细琥珀边线，不为了装饰强行生成事件标签。
- **克制原则**：每页不超过三处纯装饰；禁用遮挡文字的水印、漂浮动画或闪烁。
