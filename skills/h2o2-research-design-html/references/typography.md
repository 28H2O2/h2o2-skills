# H2O2 Typography & Visual QA · v1.2

目的：像设计师一样检查字、行、数字、留白与阅读节奏，而不是仅套一套 CSS Token。

## Font roles

| Role | Recommendation | Why |
| --- | --- | --- |
| 中文正文 + UI | PingFang SC / Microsoft YaHei / 系统无衬线，15px 左右 | 抗干扰、长期阅读 |
| 英文展示标题 | 少量 Iowan Old Style / Baskerville / Palatino / Georgia Italic | 编辑感与亲近感 |
| 英文工具名 / 路径 | UI font / 必要时等宽字体 | 容易准确辨认 |
| 数字（Step、Duration） | `font-variant-numeric:tabular-nums` | 不同长度保持列对齐 |
| 手写署名 | 页脚少量内联 SVG 字标或系统 fallback | 有作者特征，但不依赖网络 |

不同系统的可用字体不同；不要为了模仿一个截图加载不可访问的在线资源。禁止分发字体二进制文件。英文装饰字形只在 1–2 个位置使用。

## Type scale (guidance, not pixel-law)

- 英文主标题 30–40px，必要时通过 `clamp()` 适配；`letter-spacing` 可略微收紧。
- 章节标题 16–19px；事件标题 14–15px；中文正文 15px 左右。
- 事件摘要 / 说明 13–14px；不影响理解的档案编号与元信息 11–12px。
- 不把小字号当成“高级感”；当前主示例刻意把 v1.1 中 11–12px 的重要信息提高到 12–13px。

## Micro-typography checklist

1. 中英混排自然：`Agent`、`Thinking`、`report.md` 与中文之间的视觉空隙恰当。可以用浏览器支持的 `text-autospace: normal`，不支持时保持正常文字空格；不要改变原始证据字符。
2. 短标题 `text-wrap: balance`，避免尾端剩一两个孤字；正文不要强行 balance。
3. 较短模型名或 Tool 名尽量保持完整；很长标识允许 `overflow-wrap: anywhere`，绝不撑破屏幕。
4. 数字 tabular；百分比、耗时、步骤不混用比例尺。
5. 使用视觉中心而非绝对数学中心：图标、签名、标题斜体可做极轻微光学校正。
6. 控制大写英文的 tracking；不要把所有标签都变成字距很大的 uppercase。
7. 避免双语块形成一边很长一边很短的大空洞。长 Thinking 适合段落成对排版，移动端顺序变为英文段→中文段。
8. 观察全页边框密度：如果信息层次可以通过间隔区分，不要再多加一道盒子。

## Visual QA: screenshot then revise

在环境允许时，至少看桌面初始、长 Thinking 选中、手机 390px 截图，并真实执行交互测试。

- 截图第一眼能找到主要图吗？主图是否压缩得太小？
- Header、指标、选择器是否表达了同一件事三遍？
- 字号是否可读、段落行长是否适中？是否存在孤行、奇怪的硬折行？
- 是否有不必要的高饱和颜色、阴影和复杂边框？
- 是否能看到当前事件位置，同时仍看清 Scene 中未使用的工具？
- 触控/键盘是否能选择所有事件和语言模式？
- 截图是否包含横向溢出、文字裁剪、重叠、异常空白？

原则：修正渲染后才交付；不要用“看起来应该没问题”代替浏览器检查。
