# h2o2-skills

我的 Claude Code 自建 skill 集合，by 28H2O2。

## 安装

```bash
bash install.sh          # 首次安装（symlink 到 ~/.claude/skills/）
bash install.sh --force  # 覆盖已有版本
```

重启 Claude Code 后生效。

## Skills

| Skill | 用途 |
|-------|------|
| [h2o2-bilibili-subtitle-extractor](./h2o2-bilibili-subtitle-extractor/) | 从 B 站视频页提取 AI 字幕轨，转存 JSON 并生成纯文本语料 |
| [h2o2-arxiv-paper](./h2o2-arxiv-paper/) | 搜索/下载 arXiv 论文 TeX 源码，生成结构化中文摘要（实验、基线、关键数字） |
| [h2o2-make-ppt](./h2o2-make-ppt/) | 基于已下载的 arXiv 论文生成 3 张 PPT + 讲稿，含溢出检测 |
| [h2o2-repo-cleanup](./h2o2-repo-cleanup/) | 扫描本地代码目录，识别可回收空间（巨型 .git、冗余 zip、模型权重文件），生成可执行的清理脚本。macOS only |
| [h2o2-youtube-transcript-extractor](./h2o2-youtube-transcript-extractor/) | 通过 youtube-transcript-api 提取 YouTube 视频字幕/文字稿，支持多语言轨道选择和带时间戳输出 |

## Quick Start

### h2o2-bilibili-subtitle-extractor

在任意目录下，告诉 Claude：

> 帮我提取这个 B 站视频的字幕：https://www.bilibili.com/video/BVxxxxxxxx/

skill 会通过已登录的 Chrome 获取字幕 JSON，并转成可读文本。

---

### h2o2-arxiv-paper + h2o2-make-ppt（两段式工作流）

两个 skill 共享同一个**项目根目录**，在同一目录下依次使用即可自动对齐。

```
my-research/          ← 在这里打开 Claude Code
├── archives/         ← h2o2-arxiv-paper 自动创建，存放 tar.gz
├── papers/           ← h2o2-arxiv-paper 自动创建，存放 TeX 源码 + summary.md
└── ppts/             ← h2o2-make-ppt 自动创建，存放 PPT + 讲稿
    └── META_PPT.md   ← 可选：自定义 PPT 样式规范
```

**第一步：下载并总结论文**

> 帮我下载这篇论文并生成摘要：Attention Is All You Need

`h2o2-arxiv-paper` 会搜索 arXiv、确认 ID、下载 TeX 源码，并在 `papers/paper_{ID}/summary.md` 生成结构化摘要。

**第二步：制作 PPT**

> 帮我为 Attention Is All You Need 制作 PPT

`h2o2-make-ppt` 会读取 summary.md 和 TeX 原文、规划 3 张 Slide、转换图片、计算尺寸、生成 `.pptx` 和讲稿，并自动做溢出检测。

---

### h2o2-repo-cleanup

在任意目录下，告诉 Claude：

> 帮我分析一下 ~/Desktop/Project 哪些仓库可以清理，太占磁盘了

skill 会扫描目录、生成分层报告（自有仓库 / 克隆仓库 / 非 git 文件），并输出可直接执行的 `cleanup_commands.sh`。

---

### h2o2-youtube-transcript-extractor

告诉 Claude：

> 帮我提取这个 YouTube 视频的字幕：https://www.youtube.com/watch?v=xxxxxxxx

skill 会通过 `youtube-transcript-api` 查询可用字幕轨（人工/ASR、多语言），下载并保存为纯文本或带时间戳格式。

## 目录结构

```
h2o2-skills/
├── README.md
├── install.sh
├── h2o2-bilibili-subtitle-extractor/
│   ├── SKILL.md
│   └── scripts/
│       └── subtitle_json_to_text.py
├── h2o2-arxiv-paper/
│   └── SKILL.md
├── h2o2-make-ppt/
│   └── SKILL.md
├── h2o2-repo-cleanup/
│   ├── SKILL.md
│   └── scripts/
│       └── scan_repos.py
└── h2o2-youtube-transcript-extractor/
    └── SKILL.md
```
