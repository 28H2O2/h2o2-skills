---
name: h2o2-research-design-html
author: 28H2O2
description: 将 Agent Trace、MCP/Skill 实验、模型评测或科研执行记录生成简洁漂亮的离线单文件 HTML 报告。特别适用于需要中文 Instruction、Thinking 忠实翻译、Trajectory 即时检查和 Scene Map 空间关系的 Agent 运行记录。
---

# H2O2 Research Design HTML · v1.3

一份能直接读懂的实验报告，不是宣传文案，也不是监控控制台。**只写事实、操作和证据；优先让图与交互承担解释。**

## 参考材料（按需读）

- `references/design-guidelines.md`：核心布局、语义表达、Scene / Trajectory / Inspector 细节。
- `references/typography.md`：字体、间距、混排、截图 QA。
- `references/translation.md`：Mac 本地翻译、缓存、敏感信息、降级机制。
- `assets/example.html`：完整可交互的 AgentCanary **虚构演示数据**。
- `assets/example-compact.html`：短报告可省略 Scene、Thinking 等模块。
- `examples/agentcanary-demo.json`：统一数据契约示例，**不得当作真实测试结果**。
- `scripts/prepare_translations.py`、`scripts/render_report.py`：翻译准备与参考 HTML 生成器。

示例供参考视觉语言、内容密度和交互规则，不可照搬内容或硬性强加空模块。

## 交付契约

1. **直白命名。** 用户已有标题就直接使用（如 `AgentCanary复现`）；不能生成抽象宣传语、AI 风格副标题、口号和多余的导语。展示事实优先于“讲述报告意义”。
2. **Instruction 在上。** 每次选定 Case + Model + Run，先看到该任务当时实际接收的 User Instruction（英文原文 + 中文译文）；如另有 Evaluation Goal，使用独立字段，不可冒充 Instruction。
3. **切换即知结果。** Case 选择展示任务名称、少量具体行为、结果（成功/失败/部分成功/未知）及可选特别关注标记；严格区分攻击是否成功、Judge 分数与执行状态。只有多个 Run 才显示 Run 选择，隐藏不必要的精确批次时分秒。
4. **Trajectory First。** 桌面左侧是紧凑角色泳道 + 事件顺序列表；仅在有可靠时间数据时显示实际耗时，否则使用等距步骤并明确说明。Tool Call 与匹配的 Result 合并成同一个可展开事件。
5. **即时 Inspector。** 桌面端右侧最上方固定显示选中事件详情（可局部滚动）；点击任何泳道节点或事件列表条目，立刻就地更新英文原文、对应中文、工具参数与返回。不要求滚动整页寻找 Evidence。手机端改为上下布局，选中后将详情移到可见位置。
6. **Thinking 为记录，不是臆测。** 只显示源数据里可见的原始 Thinking 或标注来源的 reasoning summary。事件列表至多一条**具体判断**的中文导读；禁止“反复评估风险”等无实际信息的套话。完整译文不可用时必须标注“未翻译”，不能将摘要冒充译文。保留否定、条件、犹豫和关键技术标识。
7. **Scene Map 要有空间关系。** 右侧 Inspector 下方展示 Agent → MCP/Tools、Agent → Skills、Tool/Agent → Files 的已知关系。**Agent / 工具 / 技能 / 文件**是醒目的分组标题；“已配置 / 可用 / 用过 / 当前选中 / 未知”分别表达。环境信息不足时只画确认的组件；可以注明未知，不得创造未记录的工具。选中事件时不隐藏未使用资源。
8. **重点是可选的。** 只标记确实影响实验结论的异常、决定、文件效果和结果；没有关键步骤就不标。事件文案：`动作 + 对象 + 结果`；Thinking 文案：`具体顾虑/判断 + 决定`。
9. **少解释，多可读。** 对所有可见界面文案进行 Editorial QA：若一句话没传递新的数据、操作、证据或必要限制，删除。原始证据和译文允许完整，但默认折叠/滚动。
10. **单文件、离线、最小技术栈。** CSS、JS、SVG 内嵌；不依赖 CDN、外部字体、React，不在用户打开报告时请求翻译。系统斜体仅点缀标题，`crafted by h2o2` 低调落款。

## 翻译规范（必须阅读 `references/translation.md`）

- Instruction 与实际记录的英文 Thinking **优先**提供简体中文完整译文；若来源仅有 reasoning summary，则标为摘要。
- 默认在生成 HTML 前尝试本地翻译。**macOS 26+** 可使用随附的 Swift/Apple Translation 适配器（已安装 en/zh 语言资源时）；其他环境必须明确降级，用户可自行配置本地/远程命令接口，但默认绝不向外部服务发送数据。
- 对重复英文文本/段落按内容哈希缓存；长 Thinking 按原始段落逐段译并对应展示。保留原始文本。
- 检测重要技术字串、路径/代码是否被翻译破坏；校验失败标记未通过，不要声称翻译完整可信。敏感内容先按上下文审查/脱敏，再考虑发送给第三方 API；禁止自动回退到在线服务。
- 本 Skill 提供的脚本是**参考实现**；通用 Agent 也可以按这套约束生成自己的 HTML。

## 数据与语义检查

- 未见到的工具不等于不可用；仅根据调用日志不可推断完整环境。
- `exec` 命令提及一个文件不等于确证写入；`read` 不等于泄露；最终回答拒绝不等于工具侧安全。文件状态要区分直接工具返回、命令文本、文件快照等证据等级。
- Tool Call / Result 必须按 ID 关联；文件路径大小写敏感，不要混淆 `soul.md` 与 `SOUL.md`。
- 原始内容不可信；用 `textContent` / DOM API 渲染，JSON 嵌入必须防止 `</script>` 关闭。默认遮盖明确的令牌、密钥值，不能破坏 `/etc/passwd` 等路径及普通词。
- Judge 分数不是攻击成功率；成功与失败只有原始指标支持时才能确定。没有数据就用“未知”。

## 生成与验收

1. 核对源记录、Case、Run、Instruction、Thinking、Tool Call/Result、Scene 配置、文件证据和评估结果；建立统一 JSON 结构。请勿用示例的虚构数据补空缺。
2. 按需运行 `python3 scripts/prepare_translations.py --input INPUT.json --output TRANSLATED.json --backend apple`。无 Mac 翻译条件则先使用 `--backend none` 生成带“未翻译”标识的可读报告。
3. 用 `python3 scripts/render_report.py --input TRANSLATED.json --output report.html` 或参照示例输出单文件 HTML。
4. 至少实际检查桌面 1440px 首屏、长 Thinking 选中状态和手机 390px。点泳道节点应立即看到 Inspector；确认切换任务/模型/运行时不会遗留上次状态；网页无横向溢出、JS 错误。
5. 通过 Editorial QA（无空话）、Semantic QA（证据与翻译不冒充）、Visual QA（字号、断行、视觉重心）后交付。如果没有条件测试 Apple 翻译本机运行，**必须直说没有在 Mac 上验证**。

只输出用户要求的 HTML / Skill / 必要使用说明，少写总结性套话。
