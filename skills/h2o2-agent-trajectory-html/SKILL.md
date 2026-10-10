---
name: h2o2-agent-trajectory-html
author: 28H2O2
description: 把实际采集的 Agent 执行日志与安全评测记录整理为场景清楚、中文任务优先的离线 HTML。电脑端同时呈现任务和关键环境，再按事件查看轨迹、工具及文件证据；支持可选本地翻译。通用技术研究使用 h2o2-research-html。
---

# H2O2 Agent Trajectory HTML

**先让读者认清场景和任务，再看执行过程与证据。** 打开页面应能回答：用户想做什么、Agent 在哪里运行、哪些工具／技能／文件参与、实际发生了什么。用具体任务和后果吸引读者，不靠空泛口号或堆指标。

此 Skill 处理实际 Agent 日志；通用架构、源码审查和选型用 `h2o2-research-html`。输入与脚本接口兼容 V1.4，不要求材料补齐不存在的事件或环境。

## 场景与任务先讲清

- 用任务本名作标题。需要概览时，先给正常任务、关键参与对象和有证据的结果；读者不应先解码 Case ID、JSON、分数或术语。历史结果、当前实测、拟议流程在对应标题或结果附近标明。
- **Instruction 中文全文在前，字号和权重高于辅助信息。** 保留 Agent 实际收到的完整原文，英文可展开对照；摘要不能冒充全文翻译。Shell／代码指令原样显示，中文说明另列。Judge Goal 与用户任务分开。
- **场景地图与 Instruction 同时可读。** 优先显示关键 Agent、工具、技能和文件，用中文用途名辅助真实标识，例如「查询员工记录 / get_employee_record」。不要只给一串 API 名或路径。
- 把空间边界说清：宿主、容器、工作区、MCP 服务等仅按已知材料标注。把过程说清：谁准备材料、说明在哪里被读取、谁执行调用、结果回到哪里；未记录的阶段明确未知。归属用分组或容器，真实调用／返回才用有方向的关系。
- 每个关键数字说明含义与来源，区分传入参数、工具返回、最终答案和评分。不能把「传入工资」下的数字写成返回的奖金；结果差异不能自动归因于框架差异。

## 电脑端优先的阅读布局

- 先完成 1440×900 桌面布局。推荐上方任务与场景并排，下方执行过程与即时 Inspector 并排；布局服从内容，不强制等高卡片、固定比例、四个页签或多个图。
- **优先给场景分配空间。** 默认就能看到关键工具／技能／文件及必要关系；不要靠固定小高度、内部滚动或缩小字号把它们藏起来。长清单和原始证据可折叠／局部滚动，主内容可以向下延伸。
- 工具、技能、文件分组对齐，标题、用途与技术标识层次清楚。已知未使用资源可放「其他已知资源」中，完整清单仍可访问；选中事件涉及的折叠资源应显露。切换事件只改变焦点，不移除其他已知组件。
- 颜色帮助认识对象和风险，避免整页只有黑白灰；颜色语义一致，配置／使用／失败等状态另有文字或标记，不靠颜色证明攻击成功。具体字体与配色见 `references/typography.md`、`references/visual-tokens.md`。
- Case／Model／Run 按材料需要出现，显示可理解的任务名和当前运行结果，隐藏无关批次信息。移动端随后适配为任务 → 场景 → 过程 → 证据，保持可读字号。

排版与截图验收时读 `references/design-guidelines.md`。兼容示例可用于核对功能，不能作为新布局的固定模板。

## 执行过程与证据

- 用事件列表或紧凑的 User／Agent／Tool／File 泳道表达真实顺序；无时间戳写「执行顺序」，不编耗时。对应 Tool Call 与 Result 按调用 ID 合成一条可查看事件；无法匹配时标明不确定。
- 工具事件写「动作 → 对象」，下一行只写观察到的结果。Thinking 摘要说出具体判断或决定，不能复述用户任务或泛写「反复评估风险」；没有可靠摘要时省略，Inspector 保留实际采集的原文。不可补造未记录的内在推理。
- 选中步骤时，旁边 Inspector 立即显示中文证据、工具参数／返回和可追溯原文。长 Thinking 中文全文优先，原文可展开或切换；不重复铺满已经可见的 Instruction。关键步骤标记仅在证据支持时使用。
- 从概览跳转必须使用实际 Case／Model／Run／Event ID，不能用显示名猜 ID。核对入口打开的轮次与所讲结果一致；记录缺失时提示，不能静默展示另一个运行。切换 Case 尽量保留 Model，缺记录时说明变化。
- 可见文字必须增加事实、操作、证据或必要限制；删除重复解释，不给每段信息套卡片。

## Translation：参考 `references/translation.md`

- 优先提供 Instruction 和**实际采集到的** Thinking 的完整中文译文；中文先读，原始英文可对照。不把摘要叫作「直译」。
- 生成阶段优先可选 Apple Translation（macOS 26+ 且已安装翻译语言包）；其他系统用 `--backend none` 或用户**主动配置**的 CLI 翻译器。不得自动调用第三方在线 API。生成的 HTML 离线运行。
- `scripts/prepare_translations.py` 在翻译前保护代码块、反引号、Shell 命令、路径和技术标识；分批、缓存并局部重试。发现保留标识丢失、替换字符 `�` 等问题时保留原文并标注失败；技术语义仍可能出错，不能把机器译文视为人工审核通过。
- 中文读书摘要与全文翻译分开处理；读书摘要应由生成 Agent 依据 Thinking 写出，再经 `scripts/quality_check.py` 检查低质模式。
- 不覆盖已存在的人工译文；对**已有译文**仍进行翻译 QA，不因 `translation_status=translated_apple` 就认定可信。

## Scene 事实边界：参考 `references/scene-semantics.md`

- 区分 `declared/configured`、`available`、`observed used`、`unknown`，严禁用「工具未调用」推断「工具不可用」。
- 区分 `mentions`（命令文本出现路径）、`reads`、`writes`、`deletes`。`rm file` 出现在命令中不是删除成功；仅当明确工具返回或快照支持时提升证据等级。
- `memory_search` 不等于读取 `MEMORY.md`；`exec` 不代表所涉及文件全部被修改；Tool 进程结束不等于内部命令成功。
- 连线依据真实 `environment.links[]` 逐条画出，完整关系可展开，选中时改变焦点。**不能画固定连线冒充数据关系**。文件名大小写与真实路径不得无证据合并。

## 最小实现与自检

- 原生 HTML + 内联 CSS / JS / SVG；不依赖 CDN、React、远程字体或运行时 API。
- 渲染不可信源文本时使用 DOM `textContent`；JSON 以安全转义嵌入。机密字符串默认脱敏，不能把 `/etc/passwd`、`bypass` 之类的普通文本误删。
- 数据：顶层 `scenarios[]` 与 `cases[]`，Case 有 `runs[]`，Run 有 `events[]`；环境沿用 `agent / servers / tools / skills / files / links`。详见 `examples/agentcanary-demo.json`，不为排版改动兼容输入。
- 先执行：`python3 scripts/quality_check.py --input data.json`；修正 errors，逐条检查 warnings（警告不保证发现所有语义错误）。
- 如缺翻译：`python3 scripts/prepare_translations.py --input data.json --output translated.json --backend apple`；非兼容平台使用 `--backend none`。
- 兼容生成：`python3 scripts/render_report.py --input translated.json --output report.html`。现有模板保留 V1.4 布局；制作新报告时复用安全数据嵌入与事件逻辑，再按上述场景优先要求调整输出排版，不能把直接运行旧渲染器当作新视觉规范已实现。
- **视觉 QA**：实际查看 1440×900 首屏，先判断任务、运行空间和关键资源是否容易认出，再测入口轮次、事件／Inspector／Scene 联动及长译文；最后检查 390px / 320px。现有 `python3 tests/check_browser.py` 验证兼容功能，不替代新报告的阅读与截图验收。

### 参考文件

- `references/visual-tokens.md`：独立安装的视觉起点与可选落款
- `references/design-guidelines.md`：场景优先布局、信息密度与视觉 QA
- `references/translation.md`：Apple Swift、其他平台降级、缓存与翻译保护
- `references/scene-semantics.md`：边与证据等级
- `assets/report-template.html`、`assets/example.html`：V1.4 兼容功能参考（示例为**虚构数据**，排版未随文档更新）
- `scripts/import_v13_html.py`：可选的旧版 AgentCanary HTML 数据迁移器；**不会自动生成可靠 Thinking 摘要**

示例是视觉参考，不是固定模块清单。源材料缺什么就省略或标未知；不要补造。
