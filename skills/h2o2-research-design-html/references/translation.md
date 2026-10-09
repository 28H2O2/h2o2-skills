# Translation Backends · v1.3

## 目标

英文 Instruction 与记录到的 Thinking 优先翻译成简体中文。报告内嵌原文和译文，离线打开无需翻译服务。翻译来源及状态须可辨识。

## 默认本地路径：Apple Translation Framework

- 框架本身自 macOS 15 起可用；**不依赖 SwiftUI 直接构造** `TranslationSession(installedSource:target:)` 的 API 从 macOS **26** 起可用。M 系列芯片本身并不能替代版本要求。
- 首次使用前，在 **系统设置 → 通用 → 语言与地区 → 翻译语言** 中安装英语和简体中文。直接构造的 session 不会主动请求语言包下载权限，缺失时应报错。
- 需要 Xcode/Command Line Tools 提供 Swift 编译环境。Swift 命令行工具在 Mac 本机编译，来自 `scripts/apple-translate/`。此 Skill **不会下载第三方二进制文件**。
- Apple 文档声明翻译文本在设备上处理；Apple 可能收集与语言对等相关但不含文本的性能/用量指标。
- `scripts/prepare_translations.py` 默认只选择 Apple、none 或显式允许的自定义命令；**不会偷偷请求云 API**。

官方资料：
https://developer.apple.com/documentation/translation/translationsession
https://developer.apple.com/documentation/translation/translationsession/init%28installedsource%3Atarget%3A%29
https://developer.apple.com/documentation/translation/translating-text-within-your-app

## 输入与输出

将 JSON 中 `case.instruction.en` 和 `run.events[kind=thinking].original` 按段落收集；只填缺失的 `zh` / `translation_zh` 字段，不覆盖已有人工翻译。原始英文全文不变。

脚本在 `~/.cache/h2o2-research-design-html/` 中保存哈希缓存（及译文）；缓存文件权限限制为当前用户可读写。敏感任务可使用 `--no-cache`，或先人工脱敏，因缓存译文本身也可能含私密内容。

API/第三方后端按需接入 `--command`，遵循脚本帮助中的 JSON stdin/stdout 协议；仅在用户明确授权后使用。Bob、快捷指令不是依赖项。

## 质量边界

翻译不保证对抗性指令/代码/路径的逐字可靠性。对原文中的反引号代码、路径、特殊标识执行基本一致性检测；失败时**不保留错误译文**并打 `translation_status=failed_validation`。保留“未翻译”入口供查看原文，不让生成模型凭空补译。复杂思考需要额外人工复核；导读摘要与全文翻译必须有不同标记。

## Swift 支持矩阵

- macOS 26+、语言包已安装：预期可命令行批处理（需在真实 Mac 上验证 Swift 构建和运行）。
- macOS 15–25：框架可通过 SwiftUI `translationTask` 使用，但本包不提供 GUI Helper；Apple CLI 后端不可用。仍可无翻译生成，或用户接入自定义翻译命令。
- Linux/Windows：运行报告生成器，Apple 翻译不可用。可使用已有人为译文或自定义命令。
