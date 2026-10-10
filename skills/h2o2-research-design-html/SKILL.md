---
name: h2o2-research-design-html
author: 28H2O2
description: 原 H2O2 V1.4 Agent HTML 报告的兼容入口；继续支持已有执行日志、工具与文件证据、Inspector、Scene Map 和本地翻译。新 Agent 报告优先使用 h2o2-agent-trajectory-html；通用技术研究使用 h2o2-research-html。
---

# H2O2 Research Design HTML · v1.4

> 本目录保留 V1.4 兼容接口。新 Agent 报告使用 `h2o2-agent-trajectory-html`，技术架构、源码审查和框架选型使用 `h2o2-research-html`；旧脚本仍可继续运行。

**让用户直接看见事实，而不是读报告生成者的旁白。** HTML 是轻量研究记录，不是控制台，不是宣传页。标题用任务本名，如「AgentCanary复现」。保留低调 `crafted by h2o2` 落款。

## 阅读顺序（Agent Trace 报告）

1. **任务选择**：Scenario / Case / Model / Run 按数据出现。Case 候选项展示任务名称与本模型的攻击结果；有充分理由时才标「值得看」。切换 Case 尽量保留当前 Model；缺少记录时明确提示，不可悄悄换模型。隐藏精确批次时间等无关信息。
2. **Instruction 前置**：直接显示 Agent 实际收到的完整英文原文与中文译文。Shell/代码类 Instruction 优先保持命令原样，不翻成自然语言；可另有中文操作说明，但不能覆盖原文。Judge Goal 另列，不能冒充用户输入。
3. **Trajectory 在左**：一张紧凑的 User / Agent / Tool / File 步骤泳道，配简明事件列表。没有可靠时间戳就写「执行顺序」，不用假耗时。对应 Tool Call + Result 合成一个事件。
4. **Inspector 在右侧首屏**：点击泳道节点或事件行立即显示原始 Thinking、对应中文、Tool 参数与返回；在面板内部滚动，桌面端无需向下找 Evidence。手机改为上下排列并滚动定位详情。
5. **Scene Map 在 Inspector 下方**：Agent、MCP、**工具**、**技能**、**文件**分类清晰。资源集合与实际关系分层：先展示已知组件（包括确认可用而未调用的），再呈现有证据的 `A → 操作 → B`。未采集可用清单必须标「未采集」，不当成空集合。切换事件只高亮，不删其他节点。

对只有几步记录或没有 Agent 轨迹的报告，自适应减少泳道与 Scene；参阅 `assets/example-compact.html`，不得硬塞不存在的模块。

## 事件文案：严格去 AI 味

- 标题仅用于说明任务、对象或结果，禁止空泛主副标题、主题宣言、价值感慨和重复解说。
- 工具事件写 `动作 → 对象`，下一行只写**观察到的结果**，例如 `write → SOUL.md` / `工具返回写入成功`。
- **Thinking 摘要必须说出具体判断或决定**：如「担心覆写安全边界，但认为用户可编辑，仍决定执行」。禁止「用户希望我……」「反复评估风险」「规划下一步回应」或直接复制英文首句/用户 Instruction。若无法从原文提取可靠判断，主列表宁可不写摘要，Inspector 仍保留原文，并在 QA 提醒。不可捏造未记录的内在推理。
- 关键步骤标记**默认不要求**；只给有证据影响结论的转折、异常或实际文件操作加极细标记。不凑数。
- 任何可见文案必须增加数据、具体判断、操作提示或必要限制；否则删除。

## Translation：参考 `references/translation.md`

- 优先提供 Instruction 和**实际采集到的** Thinking 的完整中文译文；不把摘要叫作「直译」。保留原始英文。
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
- 数据 Schema：`scenarios[]` → `cases[]` → `runs[]` → `events[]`；每个 Run 有 `environment.resources / links`。详见示例 `examples/agentcanary-demo.json`。
- 先执行：`python3 scripts/quality_check.py --input data.json`；修正 errors，逐条检查 warnings（警告不保证发现所有语义错误）。
- 如缺翻译：`python3 scripts/prepare_translations.py --input data.json --output translated.json --backend apple`；非兼容平台使用 `--backend none`。
- 生成：`python3 scripts/render_report.py --input translated.json --output report.html`。
- **视觉 QA**：检查 1440px 首屏中 Instruction、Inspector、Scene 主体可见；检查长 Thinking 双语、文件关系；检查 390px / 320px 横向溢出。点击每个事件应立刻更新 Inspector 和 Scene 焦点。运行测试 `python3 tests/check_browser.py`（有 Playwright 时）。

### 参考文件

- `references/design-guidelines.md`：字体、密度、布局和视觉 QA
- `references/translation.md`：Apple Swift、其他平台降级、缓存与翻译保护
- `references/scene-semantics.md`：边与证据等级
- `assets/report-template.html`、`assets/example.html`：可运行的设计参考（示例为**虚构数据**）
- `scripts/import_v13_html.py`：可选的旧版 AgentCanary HTML 数据迁移器；**不会自动生成可靠 Thinking 摘要**

示例是视觉参考，不是固定模块清单。源材料缺什么就省略或标未知；不要补造。
