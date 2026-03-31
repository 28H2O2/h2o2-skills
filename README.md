# h2o2-skills

我的 Claude Code 自建 skill 集合。

## 安装

```bash
bash install.sh          # 首次安装（symlink 到 ~/.claude/skills/）
bash install.sh --force  # 覆盖已有版本
```

重启 Claude Code 后生效。

## Skills

| Skill | 用途 |
|-------|------|
| [bilibili-subtitle-extractor](./bilibili-subtitle-extractor/) | 从 B 站视频页提取 AI 字幕轨，转存 JSON 并生成纯文本语料 |
| [arxiv-paper](./arxiv-paper/) | 搜索/下载 arXiv 论文 TeX 源码，生成结构化中文摘要（实验、基线、关键数字） |
| [make-ppt](./make-ppt/) | 基于已下载的 arXiv 论文生成 3 张 PPT + 讲稿，含溢出检测 |
| [repo-cleanup](./repo-cleanup/) | 扫描本地代码目录，识别可回收空间（巨型 .git、冗余 zip、模型权重文件），生成可执行的清理脚本。macOS only |

## Quick Start

### bilibili-subtitle-extractor

在任意目录下，告诉 Claude：

> 帮我提取这个 B 站视频的字幕：https://www.bilibili.com/video/BVxxxxxxxx/

skill 会通过已登录的 Chrome 获取字幕 JSON，并转成可读文本。

---

### arxiv-paper + make-ppt（两段式工作流）

两个 skill 共享同一个**项目根目录**，在同一目录下依次使用即可自动对齐。

```
my-research/          ← 在这里打开 Claude Code
├── archives/         ← arxiv-paper 自动创建，存放 tar.gz
├── papers/           ← arxiv-paper 自动创建，存放 TeX 源码 + summary.md
└── ppts/             ← make-ppt 自动创建，存放 PPT + 讲稿
    └── META_PPT.md   ← 可选：自定义 PPT 样式规范
```

**第一步：下载并总结论文**

> 帮我下载这篇论文并生成摘要：Attention Is All You Need

`arxiv-paper` 会搜索 arXiv、确认 ID、下载 TeX 源码，并在 `papers/paper_{ID}/summary.md` 生成结构化摘要。

**第二步：制作 PPT**

> 帮我为 Attention Is All You Need 制作 PPT

`make-ppt` 会读取 summary.md 和 TeX 原文、规划 3 张 Slide、转换图片、计算尺寸、生成 `.pptx` 和讲稿，并自动做溢出检测。

## 目录结构

```
h2o2-skills/
├── README.md
├── install.sh
├── bilibili-subtitle-extractor/
│   ├── SKILL.md
│   └── scripts/
│       └── subtitle_json_to_text.py
├── arxiv-paper/
│   └── SKILL.md
└── make-ppt/
    └── SKILL.md
```
