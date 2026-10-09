---
name: h2o2-research-design-html
author: 28H2O2
description: 将 Agent 轨迹、MCP/Skill 实验、模型评测和科研数据整理为漂亮、简明、可信的离线单文件 HTML 报告。适用于 Agent Trace 可视化、实验报告、HTML 研究手记、模型运行回顾等任务。
---

# H2O2 Research Design HTML · v1.2

为人类阅读而制作的 HTML 研究手记，不是控制台。**先让数据和图说话，少解释、不重复、不伪造。**

## 参考文件（按需读取）

- `references/design-guidelines.md`：布局、组件、Trajectory / Scene Map 及交互约定。
- `references/typography.md`：中英文混排、精细排版、视觉自检。
- `assets/example.html`：有 Agent Trace、Thinking、Scene Map、四维选择器的主示例。
- `assets/example-compact.html`：没有 Thinking、没有独立 Scene Map 的短报告示例。
- `assets/example.png`、`assets/example-mobile.png`、`assets/example-compact.png`：视觉参考。

**示例是视觉语言和交互参考，不是固定模板。** 不应强行复刻示例里的模块、组件或虚构数据。

## 设计契约

1. **Visual first; language second.** 让一张图、一行短摘要或小卡片承担主要解释；禁止套话、图后重复描述、堆砌指标与装饰。首屏一眼看到任务、轨迹/关键结果。每个区域只回答一个问题。
2. **Trajectory first（存在 Agent Trace 时）。** 顶部紧凑的泳道/顺序图，下面是易扫读的事件列表；Tool Call 与其匹配的 Tool Result 合成一个事件。没有可用时间戳必须标注执行顺序，不能冒充精确时间轴。
3. **Thinking is recorded evidence.** 有采集到的原始 Thinking 时，事件表展示极短、客观的中文摘要；选中后显示完整原文与忠实中文翻译。保留不确定、否定、反复修正；摘要不是翻译；不可生成未记录的隐藏推理。没有 Thinking 时直接省略。
4. **Scene is capability, not just usage.** Scene Map 展示已知的 Agent、模型、MCP、Tools、Skills、Files；允许已配置但没调用的资源。区分 configured、available、used、unknown；当前事件只增加焦点高亮，不改变整轮使用事实。数据不足时省略部分区域，不补造。
5. **Highlight sparingly.** 默认不标关键节点。仅明确影响实验问题的决定、异常、重要状态变化或结果证据才标记；可以为零。短中文说明嵌入对应事件，不另起解释长文。
6. **One file; minimal interaction.** 离线自包含 HTML、内联 CSS、原生 JS/SVG；不依赖 CDN、前端框架或远程字体。只保留真正有用的 Case/Model/Run 切换、选择事件、查看双语证据与 Scene 高亮。避免拖拽、复杂过滤和装饰性动画。
7. **Editorial care.** 信息层级、视觉平衡、混排空隙、完整专业标识、数字对齐、精确断行都重要。正文和证据可读性优先，英文斜体与手写 h2o2 签名只用于极少的个性化细节。详见 `references/typography.md`。
8. **Evidence over narrative.** 不编造数据、时长、调用、文件状态、源码或引语。根据源数据确定事实，明确区分模型自述、工具结果、文件快照、Judge 判定与生成者推断。敏感内容默认脱敏。

## 按数据选择形态

- 少量事件：用 `example-compact.html` 式短报告；不强加 Scene、Thinking 或四个下拉框。
- 复杂 Agent 执行：用 `example.html` 式左右布局，Trajectory 主、Scene 辅。主栏约 60–65%，Scene 约 35–40%；窄屏上下布局。
- 多模型/轮次/Case：需要切换时才生成选择器；只有一个值时直接展示文字。
- 有比较数据而无 Trace：用简洁对比图/表，不生成空泳道。
- 内容长：逐步披露，用事件选择或展开保留完整证据；默认只显示一句摘要。

## 推荐信息顺序

1. **Header**：标题、实验上下文、仅有价值的 1–3 个指标；不重复下拉框里的 Scenario/Case。
2. **Selectors**：存在多个选项的维度；切换后所有可见信息同步更新。
3. **Primary**：Trajectory + 简洁事件列表；Scene Map 展示能力清单与已用/焦点状态（有数据时）。
4. **Evidence**：Thinking 原文/中文翻译按段落对应；Tool Input + Result；来源。
5. **Footer**：数据来源/限制，可选极低调 `crafted by h2o2` 落款。

## 数据准备与构建

1. 读取源数据，核查 run、step、事件顺序、模型、时间、可用工具清单、实际调用、文件操作与内容来源；不存在的信息记录为 unknown。
2. 整理最小中间结构：`scene.resources`、`runs[].events`、`events[].resource_ids`、原始证据、翻译；匹配并合并 Tool Call/Result。为文件变化标出明确发生的操作与对应事件，不靠名称猜状态。
3. **先选择表达方式，再写代码**。不为凑视觉模块构造虚假的组件或阶段。
4. 用安全 DOM API（`textContent`、`createElement`）输出来自数据源的文本；若必须内嵌 JSON，正确处理 `</script>` 和 JS/HTML 上下文。禁用未经转义的日志 `innerHTML`。不从外网取字体、脚本、图片。
5. 原始 Thinking 全文可展开与复制，翻译按原文段落配对；长证据可以在局部滚动。工具入参与结果明确分段。标明节选/摘要/译文。

## 交付前 Visual QA（重要）

在有浏览器能力时，**必须真实打开并查看截图**，而不只检查 DOM 和代码：

- 至少看「桌面初始」「桌面长 Thinking」「窄屏」三种状态；对拥挤、失衡、断行不佳或重复信息迭代修正。
- 首屏重点是否明确？是否有重复的 Header 指标/Selector 文本？小字能否阅读？边框是否过重？
- 中英文混排与标题是否自然；模型名、文件名、Step、耗时是否有不必要的断行或误导？
- 泳道在窄屏下是否能看清（局部横向滚动或改用步骤条），页面本身不允许横向溢出。
- 交互：切换 Case/Model/Run、选中事件、双语切换、Scene 高亮、文件状态、证据内容保持一致；浏览器无 JS 错误。
- 对事实/引语/判定与来源进行独立验证；不要仅凭示例逻辑认为真实数据可信。没条件完成的检查明确说出。

## 收尾

只交付必要的 HTML（或用户明确要求的脚本 / Skill 包）。签名是可移除的设计署名，不能冒充实验作者或研究成果权属。拒绝冗长的生成说明；不要让使用者花比读报告还多的时间读使用手册。
