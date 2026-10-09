---
name: h2o2-research-html
author: 28H2O2
description: 为 Agent 运行轨迹、MCP/Skill 实验、AI 安全评测与科研结果生成轻量、漂亮、可信的单文件交互式 HTML 报告。适用于「生成实验报告」「将 Agent Trace 可视化」「做 research HTML」「生成可交互的运行回顾」等任务。
---

# H2O2 Research HTML

生成 **以图为主、少字易读、证据可追溯** 的单文件 HTML 研究报告。它是供人阅读的报告，不是实时监控台。

## 必读参考

- 开始设计前阅读 `references/design-guidelines.md`。
- 需要参考布局、CSS 或交互写法时阅读 `assets/example.html`。示例是**审美及交互参考，不是要求逐项复制的模板**。
- `assets/example.png` 为视觉预览（如果当前环境支持查看图片）。

## 七条核心规则

1. **Visual first, text last.** 主要信息优先通过执行图、比较图、卡片和极短标签表达。禁止冗长的说明性套话；不重复解释图中已经清楚的信息。
2. **Trajectory first（存在 Agent Trace 时）。** 先给紧凑的执行顺序/时间泳道，再给事件列表；关键内容直接嵌在相关事件里。没有可信时间戳时标注「执行顺序」，不能假装节点间距是耗时。
3. **Scene is capability, not execution.** Scene Map 列出证据所支持的场景组件（Agent、模型、MCP Server、Tools、Skills、Workspace 等），包括没有被调用但已知可用的能力。区分 configured、available、used、unknown。不要根据未调用反推不存在，也不要将已配置当成已可用。
4. **Thinking is evidence.** 原始日志确实提供 Thinking 时，将其作为独立可定位的内容；事件列表给一句简洁中文摘要，展开显示原文和忠实中文翻译。摘要≠翻译；保留原文中的犹豫、否定、条件与修正；不得补写缺失的私有推理。没有 Thinking 则标明未记录，不要捏造。
5. **Merge matching Tool Call + Tool Result.** 一一对应时合成同一可展开卡片，内容保留名称、参数、返回、状态；多次调用不能错误合并。Thinking 前后顺序必须保留。
6. **Emphasize only when deserved.** 关键事件标注是可选的；仅在实验相关的决策、异常、状态转折、结果证据需要时添加，数量可以为零。所有标注能回溯到原始证据，不制造意义。
7. **One file, low ceremony.** 原生 HTML + 内联 CSS + 少量原生 JS + 可选 SVG；不依赖构建步骤、CDN、React 或第三方字体。可离线双击打开。交互以切换 Case/Model/Run、点击事件、展开证据、轻量 Scene 联动为限。

## 默认页面结构（按需简化）

- **Header**：任务标题，一句实验描述，最多 2–4 项关键数值。
- **Selectors**：Scenario / Case / Model / Run 按实际数据出现；单一取值展示为文字，不强加下拉框。切换执行维度时同步更新所有视图。
- **Main desktop**：左侧约 60% Trajectory（小泳道 + 精简事件列表），右侧约 40% Scene Map（静态能力清单 + 已使用状态 + 当前选中高亮）。移动端改上下结构。
- **Evidence**：所选事件的原文/忠实翻译/参数/结果；默认紧凑，长内容可展开、滚动或切换。
- **Footer**：判定口径、数据来源、限制。允许一个非常低调的 `crafted by h2o2` 手写感签名；不干扰数据与阅读。

数据不含 Agent Trace 时，按数据选择图表、表格和证据卡，不要强制生成泳道或 Scene Map。页面结构适配内容，而不是内容迁就模板。

## 生成流程

1. **核查来源**：识别真实的 Run、模型、事件顺序、时间字段、工具可用清单、工具调用、文件操作、Thinking/Final、判定依据与来源路径。
2. **整理最小数据**：建立 `scene.resources`、`runs[].events`、`events[].resource_ids`；将工具输入和对应返回组合。标记数据缺口与未知状态。
3. **选择表达**：能用一张图说清楚的，不加第二张；普通事件一行，必要的关键事件加最多两行说明。仅使用被数据支持的图形与状态。
4. **生成单文件 HTML**：所有动态外部文本使用 `textContent` / `createTextNode` 或安全转义，不将日志、模型输出、文件内容直接拼进 `innerHTML`。内嵌 JSON 防止 `</script>` 提前闭合；建议用 JS 字符串安全序列化或转义 `<`。默认脱敏 API key、token、cookie 等敏感内容。
5. **QA**：核查关键数字、引用和翻译是否忠实，时间是否真实；检查 HTML 离线打开、切换器、事件高亮、证据展开、手机宽度横向溢出。工具不可用时明确说明未验证项。

## 事实边界

- Tool 调用成功不一定等于任务真正成功，模型自述不代替文件快照或 Judge 证据。
- 读取文件不自动等于泄漏；写入不自动等于被攻破。文件状态只由明确可定位的操作或快照更新。
- Scene 中可用工具需要工具清单/实际暴露证据；未使用不代表不可用。
- Thinking 仅是可观察到的模型输出文本，不能据此断言不可观察的内部因果机制。
- 对比少量 Run 时，不给出未经支持的统计泛化结论。

## 交付

交付 `<report>.html`，必要时同时交付生成脚本。签名为弱装饰，用户要求去掉时可以轻易删除。若用户明确要求修改本 Skill，则更新 `SKILL.md` 和参考示例；否则不要直接修改已有仓库文件。
