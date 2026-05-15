---
name: h2o2-arxiv-paper
author: 28H2O2
description: 从 TeX 源码下载、解压并结构化摘要 arXiv 论文。当用户想通过标题或 ID 获取 arXiv 论文、下载其 TeX 源码，并生成涵盖背景、贡献、实验、基线及主要结果的中文结构化摘要时，使用此 Skill。
---

## 前提

在你的**论文项目根目录**下使用（任意空目录均可）。skill 会自动创建所需子目录：
- `archives/` — 原始 tar.gz 下载缓存
- `papers/paper_{ID}/` — 解压后的 TeX 源码 + 生成的 summary.md

与 make-ppt skill 配合使用时，保持在同一根目录下即可，两者自动对齐。

---

你正在帮助用户从 TeX 源码下载、解压并摘要 arXiv 论文。

用户将提供一篇或多篇论文的标题或 arXiv ID 作为输入。

**对用户提供的每篇论文**，按以下步骤操作：

---

## 第一步：在 arXiv 上搜索论文 ID

使用 arXiv API 查找论文：
```
curl -s "https://export.arxiv.org/api/query?search_query=ti:{TITLE_KEYWORDS}&max_results=5"
```
解析 XML 响应，找到 arXiv ID（格式：`YYMM.NNNNN`），并确认标题匹配。若返回多个结果，选择最佳匹配项并告知用户选择了哪篇。

---

## 第二步：下载前确认

告知用户：
- 找到的论文标题
- arXiv ID
- 下载链接：`https://arxiv.org/src/{ID}`
- 保存路径：当前工作目录

然后询问："请确认是否继续下载。"

**等待用户确认后再继续。**

---

## 第三步：下载并解压

确认后执行：
1. 下载：`curl -L -o archives/paper_{ID}.tar.gz "https://arxiv.org/src/{ID}"`
2. 创建目录：`mkdir -p papers/paper_{ID}`
3. 解压：`tar -xzf archives/paper_{ID}.tar.gz -C papers/paper_{ID}/`
4. 列出解压后的文件，让用户了解内容结构。

---

## 第四步：阅读论文内容

找到主 TeX 文件（通常为 `main.tex`，或以论文命名）。同时查找包含各节单独文件的 `sections/` 子目录。

按以下顺序阅读（使用 `offset` 和 `limit` 参数避免超出 token 限制）：
1. 摘要与引言（main.tex 前约 300 行）
2. 方法/系统设计章节
3. 实验章节（设置、基线、指标、结果）
4. 结论

若存在 `sections/` 目录，逐个读取每个文件：
- `00_abstract.tex`、`01_introduction.tex` 等

---

## 第五步：生成并保存结构化摘要

在 `papers/paper_{ID}/summary.md` 创建摘要文件，结构如下：

```markdown
# Paper Summary: {SHORT_TITLE}

## Metadata
- **arXiv ID**: {ID}
- **Title**: {FULL_TITLE}
- **Authors**: {AUTHORS}
- **Affiliations**: {AFFILIATIONS}
- **Venue**: {CONFERENCE}（从 style 文件推断：icml/iclr/neurips/usenix/acl/emnlp 等）
- **Submission Date**: {YYMM from arXiv ID}
- **\iclrfinalcopy / accepted flag**: {YES/NO — 表示是否为 camera-ready}
- **Code/Project**: {URL if found}

## 研究背景与问题
{2–3 sentences describing the problem and motivation}

## 核心贡献
{Bullet points for each main contribution}

## 实验结构

### 实验设置
- **基础数据集/Benchmark**: ...
- **实验规模**: ...
- **迭代/重复次数**: ...
- **温度设置**: ...

### 被测模型
{List of models evaluated}

### Baselines
| 基线 | 类型 |
|------|------|
| ... | ... |

### Benchmark / 数据集
{Name, size, construction method, domains covered}

### Metrics
- **主要指标**: ...
- **辅助指标**: ...
- **人工验证**: ...

### 主要结果
{Key numbers in a table or bullet points}

## 关键发现
{3–5 bullet points}
```

---

## 第六步：多篇论文时生成对比表

逐一处理完所有论文后，在根目录生成 `papers_comparison.md`（若已存在则追加）。扫描 `papers/` 下所有已有的 `summary.md` 文件纳入对比。

对比维度：
- 基本元数据（venue、日期、机构）
- 研究问题与威胁模型
- 方法类型（攻击 / 防御 / 评估）
- Benchmark 与数据集
- 基线
- 指标
- 主要结果
- 论文结构（存在哪些章节：消融实验、案例分析、Benchmark 章节等）

最后附一节"结构性规律"，总结跨论文观察到的共性模式（如基线选取方式、指标论证逻辑、人工评估的使用方式）。

---

## 阅读 TeX 文件的注意事项

- Style 文件名揭示发表 Venue：
  - `icml2026.sty` → ICML 2026
  - `iclr2026_conference.sty` → ICLR 2026
  - `neurips_2025.sty` → NeurIPS 2025
  - `usenix.sty` → USENIX Security
  - `acl_natbib.sty` → ACL/EMNLP/NAACL
- 存在 `\iclrfinalcopy` → 论文已接收（camera-ready）
- `.bbl` 文件长度 ≈ 引用数量的代理指标
- `arXiv ID YYMM` → 投稿月份（如 2602 = 2026年2月，2509 = 2025年9月）
- `\newcommand{\NAME}{...}` 揭示系统/框架名称
- 作者信息在 `\icmlauthor{}{}` 或 `\author{}` 块中
