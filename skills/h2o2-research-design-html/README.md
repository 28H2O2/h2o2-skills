# H2O2 Research Design HTML Skill · v1.3

开源友好的 **单文件 Agent 研究报告**生成规范与最小参考实现。

- 标题只写任务名（示例：**AgentCanary复现**）；不写 AI 风格口号。
- Scenario/Case/Model/Run 选择，选 Case 时能看到结果与关注原因。
- 英文 Instruction + 中文译文固定在 Trajectory 上方。
- 左侧泳道与执行列表，右侧立即更新的 Inspector + 带资源关系的 Scene Map。
- Thinking 保留完整原文与忠实中文，工具调用与返回合并。
- HTML 打开时完全离线；Mac 翻译只在报告生成阶段运行。

## 安装

本仓库将此 skill 放在 `skills/h2o2-research-design-html/`，可通过仓库 README 中的安装方式安装。全局安装使用指向该目录的 symlink，后续仓库更新会直接生效。

可以直接双击 `assets/example.html` 查看交互范例。所有示例数据都是**虚构设计数据**，并非 AgentCanary 的真实结果。

## Mac 本地翻译（最先做这一步）

**要求：macOS 26.0+，Swift 工具链，系统英语/简体中文翻译语言包。** M 系列 CPU 不是版本要求的替代品。

在你的 Mac 终端中：

```bash
sw_vers -productVersion
swift --version
# 在系统设置 → 通用 → 语言与地区 → 翻译语言 安装英语、简体中文
cd /你的路径/h2o2-research-design-html
python3 scripts/prepare_translations.py --backend apple --self-test 'I should inspect the file before editing it.'
```

首次运行会在本地编译附带的 Swift 小工具，后续会复用编译产物。成功时应输出含中文字符串的 JSON；失败会显示原因，不会自动把数据发送到在线翻译 API。

### 真实测试：缺少翻译的示例

`examples/translation-smoke.json` 中故意拿掉了 1 个 Instruction 中文和 1 个 Thinking 中文，以测试 Apple 翻译能力：

```bash
python3 scripts/prepare_translations.py \
  --input examples/translation-smoke.json \
  --output /tmp/h2o2-translated.json \
  --backend apple

python3 scripts/render_report.py \
  --input /tmp/h2o2-translated.json \
  --output /tmp/AgentCanary复现.html

open /tmp/AgentCanary复现.html
```

如果本机不是 macOS 26+，暂时用 `--backend none` 测试 UI（缺失译文会显式显示“未翻译”）。不应默默调用第三方服务。若有自建翻译工具，可以使用 `--backend command --command '你的翻译CLI'`，但 CLI 必须遵循如下 JSON 协议：

```json
{"requests":[{"id":"0","text":"Hello"}]}
```

输出：

```json
{"translations":[{"id":"0","text":"你好"}]}
```

## 翻译缓存和隐私

翻译按段落批量处理，默认缓存到 `~/.cache/h2o2-research-design-html/translation-cache.json`，缓存键是文本哈希、后端及版本。缓存包含中文译文，可能有私密数据；必要时使用 `--no-cache`。原英文仍作为证据留在本地 JSON，不会被替换。

生成器对 `API_KEY=...` 等常见明文凭据进行**保守的值级脱敏**（不替换 `/etc/passwd`、`bypass` 等普通字符串），但它不是通用 DLP，分享前仍应人工检查。原始输入文件不会被修改。不要不经授权把真实日志发送给第三方翻译服务。

## 项目结构

```text
h2o2-research-design-html/
├── SKILL.md
├── README.md
├── LICENSE
├── references/
│   ├── design-guidelines.md
│   ├── typography.md
│   └── translation.md
├── assets/
│   ├── report-template.html
│   ├── example.html
│   ├── example-compact.html
│   ├── signature.html
│   └── example-1440.png / example-390.png
├── examples/
│   ├── agentcanary-demo.json
│   └── translation-smoke.json
├── scripts/
│   ├── prepare_translations.py
│   ├── render_report.py
│   └── apple-translate/ (SwiftPM)
└── tests/
    ├── test_pipeline.py
    └── check_browser.py
```

## Mac 兼容性说明

- **macOS 26+**：使用 Swift 命令行 `TranslationSession(installedSource:target:)`，系统翻译语言包必须已安装。
- **macOS 15–25**：框架能在 SwiftUI App 中用，但本项目当前**没有**打包 GUI Helper。Apple CLI 不可用。仍可以用已有译文、`--backend none` 或用户自主配置的外部翻译命令。
- **其他平台**：HTML 生成器完全可用；Apple 翻译后端不可用。

Swift 源码在 Linux 只能做语法检查；实际调用系统翻译必须在符合条件的 Mac 上验证。若报错，请提供 `sw_vers -productVersion`、`swift --version` 和终端错误（记得去掉敏感内容）。

## 资料

- Apple TranslationSession: https://developer.apple.com/documentation/translation/translationsession
- Apple installedSource 初始化：https://developer.apple.com/documentation/translation/translationsession/init%28installedsource%3Atarget%3A%29
- Apple 语言包准备：https://developer.apple.com/documentation/translation/translating-text-within-your-app

## 本仓库验证

已在 macOS 27.0.1 / Swift 6.4 上完成 Apple 真实翻译测试：1 个 Instruction 与 1 个双段 Thinking 均翻译成功，原文及已有译文未改动，缓存复用输出一致。生成的离线 HTML 已检查 1440px、390px、320px 布局及双语／模型切换。

```bash
python3 -m unittest discover -s tests -p test_pipeline.py -v
# 需安装 Python Playwright；Mac 自动使用 /Applications 中的 Google Chrome
python3 tests/check_browser.py --output-dir /tmp/h2o2-report-browser
```

Apple 翻译 CLI 将框架请求放在非主线程隔离的异步辅助函数中，以通过 Swift 6 并发检查。截图检查也支持 `--browser-executable` 指定浏览器，默认不会覆盖包内截图。
