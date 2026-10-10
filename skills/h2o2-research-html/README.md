# h2o2-research-html

技术架构、源码审查、框架比较、方案选型和机制解释的离线阅读页。没有固定 JSON 格式或 Agent Trace 模块要求。

- `assets/openclaw-brief.html`：一张拟议 MCP 关系图，默认折叠比较、POC、历史案例和证据。
- `assets/source-review.html`：无架构图的教学源码审查例子。
- `references/diagram-grammar.md`：关系、箭头和容器的使用边界。
- `references/visual-tokens.md`：两个例子的视觉起点。

直接打开 HTML 即可。外部引用只在用户点击时访问，页面加载与展开完全离线。历史案例来自旧参考页汇总，本次未取得原始日志；新示例没有执行 OpenClaw 评测。

浏览器检查：`python3 tests/check_browser.py --output-dir /tmp/h2o2-research-check`。需 Python Playwright 与 Chrome/Chromium，仅为开发检查依赖；阅读输出 HTML 不需安装任何依赖。

真实运行日志、工具调用、Thinking 和 Inspector 浏览使用独立的 `h2o2-agent-trajectory-html`。两者均能单独安装，不共享运行时包。
