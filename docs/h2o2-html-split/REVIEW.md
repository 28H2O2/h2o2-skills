# H2O2 HTML Skills 拆分检查记录

2026-10-10；本地基线为 V1.4（`c5fef55`），分支 `feat/split-h2o2-html-skills`。先完成 OpenClaw 示例并查看第一轮截图，再删重复说明、调整手机连线，最后归纳 Research 入口和图形规则。没有推送 GitHub，没有删除原 Skill。

任务书实际位于被忽略的 `reference/CODEX_TASK_H2O2_SPLIT_V1.md`，参考页为同目录的 `openclaw_brief_h2o2_minimal.html`。这两个文件保持原样，没有加入版本库。

## 两个入口的边界

| 入口 | 用途 | 数据与交互 |
| --- | --- | --- |
| [h2o2-research-html](../../skills/h2o2-research-html/SKILL.md) | 技术架构、源码审查、框架比较、选型、机制解释 | 没有固定 JSON 或 Agent 模块要求；阅读优先，必要关系图、折叠证据 |
| [h2o2-agent-trajectory-html](../../skills/h2o2-agent-trajectory-html/SKILL.md) | 实际采集的 Agent 日志与模型安全评测记录 | 沿用 V1.4 JSON/CLI；Instruction、Thinking、Tool Call/Result、Trajectory、Inspector、Scene、Case/Model/Run |
| [h2o2-research-design-html](../../skills/h2o2-research-design-html/README.md) | 旧 V1.4 兼容入口 | 原脚本、资源与全局链接继续可用；新报告按材料选择上面两者 |

## 具体文件变动

完整逐文件清单见 [FILES.txt](FILES.txt)。主要变动为：

- `skills/h2o2-research-html/SKILL.md`：从已完成的示例归纳阅读顺序、折叠、证据边界与截图检查，不预设 Trace Schema。
- `skills/h2o2-research-html/assets/openclaw-brief.html`：默认只有对象、结论、未实测状态、两条事实和一张关系图。五组次要内容原生折叠。
- `skills/h2o2-research-html/assets/source-review.html`：无图的教学源码审查；完整 5 行代码与建议测试可展开，静态判断和未执行状态直接可见。
- `skills/h2o2-research-html/references/{diagram-grammar,visual-tokens}.md`、`tests/check_browser.py`、README、LICENSE、`.gitignore`：独立安装所需说明与检查。
- `skills/h2o2-agent-trajectory-html/`：迁移原 32 个已跟踪文件，只修改 SKILL/README 的入口与范围说明，新增简短 `references/visual-tokens.md`。其余 **30 个资源按字节一致**，含 Python/Swift 脚本、模板、JSON、示例、测试和原截图；哈希见 [migration-checks.json](migration-checks.json)。没有复制构建缓存或 Finder 文件。
- 原 `skills/h2o2-research-design-html/{SKILL,README}.md`：仅加兼容说明和新入口路由。原目录没有移除文件。
- 根 `README.md` 与 `.claude-plugin/marketplace.json`：补两个新入口、示例与迁移说明；注册由 11 个变为 13 个。
- `docs/h2o2-html-split/`：前后截图、检查记录、迁移后的真实 Apple 译文 smoke HTML；示例全部明确标识演示或拟议状态。

## 前后截图与视觉判断

Chrome 桌面视口为 **1440×900**，桌面 Research 截图只截首屏。手机用 **390×844**，另补 **320×740**；手机图片保留全页便于检查折叠入口。

| 版本 | 1440×900 首屏 | 390px 手机 |
| --- | --- | --- |
| 原参考页 | [before-1440.png](before-1440.png) | [before-390.png](before-390.png) |
| 重做后 | [openclaw-brief-1440.png](openclaw-brief-1440.png) | [openclaw-brief-390.png](openclaw-brief-390.png) |

补充：[320px](openclaw-brief-320.png)、[无图源码审查桌面](source-review-1440.png)、[无图源码审查手机](source-review-390.png)。

人工查看截图的判断：原页同时展开选型、机制、四步计划、历史案例和问题，多个区块权重接近。现在最大字号是“先试 Canary”，其次是 MCP 关系；图完整落在桌面首屏内，折叠入口在下方。手机重新纵排请求／返回通道，标签避开连线，没有将桌面整图缩成缩略图。没有为对称添加后果节点、第二张图或装饰箭头。

图中的包含关系用 MCP 容器，正常任务 → Agent、Agent → 工具请求、工具 → Agent 描述／结果才用箭头。红色局限于选定描述或返回文本的拟议注入位置，调用参数由 Agent 生成，具体可改字段仍待确认。图上明确“拟议／非执行轨迹”。历史 3/3、1/3 只保留在展开区域，明确不是 OpenClaw 结果。

“3 秒能找到重点”是本次截图的人工设计判断，尚未做用户计时阅读实验。

## 检查与结果

| 检查 | 结果与实际范围 |
| --- | --- |
| Research 浏览器 | 两个例子 × 1440/390/320 = 6 组通过；默认折叠、全部展开/收起、键盘 Enter、来源定位、页面宽度、主图在桌面首屏；0 JS 错误、0 运行时网络请求。见 [research-checks.json](research-checks.json) |
| 迁移后单测 | `python3 -m unittest discover -s tests -v`：12/12；包含失败读取不冒充读取、文件不存在不证明删除、明确写入保留关系、旧数据缺 ID 兼容、转义、脱敏、翻译标识保护 |
| 严格语义检查 | 演示 JSON：0 errors / 0 warnings，`--strict-warnings` 通过 |
| 独立安装 | 将两个目录分别放入无其他 Skill 的临时目录；验证入口、资源完整，Trajectory 严格 QA、渲染和 `--backend none` 成功。没有共享包或旧目录依赖 |
| 入口格式 | 仓库要求的 `author: 28H2O2` 单独验证；Codex quick validator 不支持这个自定义键，只在临时副本移除该键后验证，其余入口检查通过；仓库入口保留作者字段 |
| Apple 真实翻译 | 本机 macOS 27.0.1 / Swift 6.4；`translation-smoke.json` + `--backend apple --no-cache --batch-size 2`：2 targets、2 translated、0 untranslated、0 invalid、2 batches、无错误；原文和 `SOUL.md` 保留。实际译文见 [agent-translated-smoke.html](agent-translated-smoke.html) |
| Agent 原交互回归 | 原 `tests/check_browser.py` 在 1440/390/320 通过：事件、Tool Call/Result、Thinking 双语、Case、Scenario、Scene 聚焦及宽度检查 |
| 补充切换回归 | 3 个宽度均通过：Model 切换、Run 切换、缺 Model 提示、Case 保留 Model、真实译文 Inspector、事件改变时保留全部 Scene 资源。第二轮次只来自明确的虚构测试夹具；见 [agent-checks.json](agent-checks.json) |
| 编辑性检查 | 删除图下重复解释、折叠标题重复判断、页尾总结；源码例子的结论与证据分层。默认保留会影响结论的“未实测／拟议／字段待确认” |
| 注册与安装 | 13 个 marketplace 路径存在且无重复；给 `.agents/.codex/.claude/.cursor/.gemini` 的既有 skills 目录新增共 10 个 symlink，保留原 5 个兼容链接。见 [global-links.json](global-links.json) |

复查命令（在仓库根目录）：

```bash
python3 skills/h2o2-research-html/tests/check_browser.py --output-dir /tmp/h2o2-research-check
python3 -m unittest discover -s skills/h2o2-agent-trajectory-html/tests -v
python3 skills/h2o2-agent-trajectory-html/scripts/quality_check.py --input skills/h2o2-agent-trajectory-html/examples/agentcanary-demo.json --strict-warnings
python3 skills/h2o2-agent-trajectory-html/scripts/render_report.py --input skills/h2o2-agent-trajectory-html/examples/agentcanary-demo.json --output /tmp/h2o2-agent.html
python3 skills/h2o2-agent-trajectory-html/tests/check_browser.py --output-dir /tmp/h2o2-agent-check
python3 skills/h2o2-agent-trajectory-html/scripts/prepare_translations.py --input skills/h2o2-agent-trajectory-html/examples/translation-smoke.json --output /tmp/h2o2-translated.json --backend apple --no-cache --batch-size 2
```

开发浏览器检查需要 Python Playwright 与 Chrome/Chromium。报告本身无需这些依赖。

Agent 截图：[桌面原始状态](agent/example-1440.png)、[桌面 Tool 选中首屏](agent/tool-selected-1440.png)、[手机 Thinking](agent/example-thinking-390.png)、[真实 Apple 译文首屏](agent/apple-thinking-1440.png)。原始状态沿用原测试的全页截图；Tool 选中截图含第二轮次的虚构切换夹具。

## 仍有问题的地方

1. **OpenClaw POC 尚未执行。** 被测版本、模型、受控 MCP 字段与成功标准待确定。上游 Canary 路径存在，不等于证明图中组合已运行。
2. 历史案例只有旧参考页汇总，未取得原始日志；3/3、1/3 不能认定为本次复核通过。Canary/Inspect 来源是查阅时上游页面，尚未固定 commit。MCP 图依据固定日期的协议规范；[Canary README](https://github.com/antgroup/Agent3Sigma-Canary#readme)、[MCP Tools](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)、[Inspect Tasks](https://inspect.aisi.org.uk/tasks.html) 链接已放入报告。
3. Apple 翻译已证明流水线可运行，尚未逐句人工审校；例如“代理角色文件”仍偏机器表达。Linux/Windows、其他浏览器和其他 Mac 没有实机验证；`none` 降级在本机验证过。
4. Agent 页面仍保留 V1.4 的证据浏览密度；桌面选中长证据时 Scene 下部超出首屏，移动端全文较长。此次改善集中在通用 Research，未重做 Agent 布局。模板页脚和默认缓存路径仍含旧名称，作为兼容迁移保留。
5. Research 图的桌面和手机分别排版，两份内联 SVG 需同步语义；两个 Skill 的视觉资源暂时独立维护，未引入共享框架。
6. 新全局 symlink 已验证可读取，当前各 Agent 会话不一定立刻刷新技能列表；下一轮或重启后确认加载。没有逐个启动五种 Agent 做调用测试。
