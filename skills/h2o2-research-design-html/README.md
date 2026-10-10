# H2O2 Research Design HTML · v1.4

开源、跨平台、离线单文件的 Agent Trajectory / 研究报告 Skill。

- 任务名作标题，不写“从判分回到执行证据”式宣传语
- Case 选择显示攻击结果；同 Case 的 Model/Run 状态尽量保持
- Instruction 英中并排，左侧 Trajectory + 右侧即时 Inspector
- Scene Map 分清**资源有哪些**和**哪些关系有证据**
- Thinking 一条具体中文判断摘要 + 完整英文与可选中文；Tool Call/Result 合并
- Apple Translation 可选；Linux/Windows 可在不安装任何依赖的情况下生成报告
- 文件底部留一个轻量 `crafted by h2o2` 签名

## 安装

本仓库将此 skill 放在 `skills/h2o2-research-design-html/`，可通过仓库 README 中的安装方式安装。`SKILL.md` 是入口；本地全局安装使用指向正式目录的 symlink，仓库更新会直接生效。

`assets/example.html` 是**虚构数据示例**；可以直接用浏览器打开。不需 `npm install`。

## 最短运行路径

```bash
cd h2o2-research-design-html
python3 scripts/quality_check.py --input examples/agentcanary-demo.json
python3 scripts/render_report.py --input examples/agentcanary-demo.json --output /tmp/h2o2-report.html
open /tmp/h2o2-report.html  # macOS
```

### Apple 系统翻译（可选，仅 macOS 26+）

使用前准备 Swift 和英语/简体中文翻译资源：系统设置 → 通用 → 语言与地区 → 翻译语言。

```bash
sw_vers -productVersion
swift --version
python3 scripts/prepare_translations.py \
  --backend apple --self-test 'I should inspect the file before editing it.'

python3 scripts/prepare_translations.py \
  --input examples/translation-smoke.json \
  --output /tmp/h2o2-translated.json \
  --backend apple --batch-size 20
python3 scripts/render_report.py \
  --input /tmp/h2o2-translated.json \
  --output /tmp/h2o2-translated.html
open /tmp/h2o2-translated.html
```

Apple 翻译在生成时运行；打开报告无需联网。本仓库已在 macOS 27.0.1 / Swift 6.4 上验证 Apple 单句、分批翻译及缓存复用；其他 Mac 仍需满足系统版本和语言包要求。保留 V1.3 的 Swift 6 并发兼容修复。

其他系统用 `--backend none`，或者自己**显式**配置 `--backend command --command '/path/to/translator' --cache-namespace custom-v1`。不会自动请求云 API。

自定义命令读取 stdin：

```json
{"requests":[{"id":"0","text":"Hello"}]}
```

向 stdout 输出：

```json
{"translations":[{"id":"0","text":"你好"}]}
```

默认每批 20 条；批次失败会单条尝试，失败者保留原文。`--no-cache` 可避免敏感译文落盘。

## 导入旧版 AgentCanary HTML（测试用途）

附带**可选的**迁移工具，仅解析 `script#report-data` 里的 JSON，不执行旧 HTML：

```bash
python3 scripts/import_v13_html.py \
  --input /path/to/agentcanary-results-v1.3.html \
  --output /tmp/cases-v14.json --cases 23,54,56,74
python3 scripts/quality_check.py --input /tmp/cases-v14.json
```

它会保留 Thinking 原文与已有译文，按 Tool/Result 提取明确关系；但**不会凭第一句自动生成 Thinking 决策摘要**。迁移后需由有原始 Trace 的 Agent 阅读并补 `summary_zh`，再运行 `quality_check.py`。命令提及文件默认只标 `mentions`；目标不存在的错误不能证明删除成功，因此不会升级为删除关系；失败的读取也不会标为实际读取。

## QA 与局限

本仓库已通过 12 项流水线／迁移回归测试、示例严格语义检查，以及 1440px、390px、320px 浏览器交互检查。保留 macOS 浏览器自动发现和临时截图输出适配；可用 `--browser-executable` 指定 Chrome/Chromium。

```bash
python3 -m unittest discover -s tests -v
python3 tests/check_browser.py --output-dir /tmp/h2o2-v14-browser  # 需 Python Playwright；Mac 默认使用 Google Chrome
python3 scripts/quality_check.py --input /tmp/cases-v14.json --strict-warnings
```

- 结构错误（未知资源 ID、重复事件 ID 等）会阻止生成。
- 弱 Thinking 摘要、可疑翻译、文件证据不充分等输出 Warning，默认不阻断生成；`--strict-warnings` 可用作 CI 门禁。
- QA 不能证明机器翻译语义完全准确，也不能替代对原始 JSON / 实际文件快照的验证。
- 渲染器提供保守的常见密钥值脱敏，但不是通用 DLP。对外分享前人工检查本地路径、隐私和凭据。
- 若只拥有执行日志，Scene Map 只展示**已观察到**的工具，不能推断全套可用 Tool/MCP/Skill。

## 结构

```text
h2o2-research-design-html/
├── SKILL.md
├── README.md
├── LICENSE
├── references/
│   ├── design-guidelines.md
│   ├── typography.md
│   ├── translation.md
│   └── scene-semantics.md
├── assets/
│   ├── report-template.html
│   ├── example.html
│   ├── example-compact.html
│   ├── signature.html
│   └── example-*.png
├── examples/
│   ├── agentcanary-demo.json
│   └── translation-smoke.json
├── scripts/
│   ├── quality_check.py
│   ├── prepare_translations.py
│   ├── render_report.py
│   ├── import_v13_html.py
│   └── apple-translate/  (SwiftPM)
└── tests/
    ├── test_pipeline.py
    ├── test_import.py
    └── check_browser.py
```

MIT License；字体不打包、不分发。示例 JSON 均为虚构数据，`crafted by h2o2` 落款可移除。
