---
name: arxiv-paper
description: Download, extract, and summarize arXiv papers from TeX source. Use when the user wants to fetch an arXiv paper by title or ID, download its TeX source, and generate a structured Chinese summary covering background, contributions, experiments, baselines, and key results.
---

## 前提

在你的**论文项目根目录**下使用（任意空目录均可）。skill 会自动创建所需子目录：
- `archives/` — 原始 tar.gz 下载缓存
- `papers/paper_{ID}/` — 解压后的 TeX 源码 + 生成的 summary.md

与 make-ppt skill 配合使用时，保持在同一根目录下即可，两者自动对齐。

---

You are helping the user download, extract, and summarize arXiv papers from their TeX source.

The user will provide one or more paper titles or arXiv IDs as input.

Follow these steps carefully for EACH paper provided:

---

## Step 1: Search arXiv for the paper ID

Use the arXiv API to find the paper:
```
curl -s "https://export.arxiv.org/api/query?search_query=ti:{TITLE_KEYWORDS}&max_results=5"
```
Parse the XML response to find the arXiv ID (format: `YYMM.NNNNN`) and confirm the title matches. If multiple results are returned, pick the best match and tell the user which one you selected.

---

## Step 2: Confirm before downloading

Tell the user:
- The paper title found
- The arXiv ID
- The download URL: `https://arxiv.org/src/{ID}`
- The save path: current working directory

Then ask: "Please confirm to proceed with downloading."

Wait for user confirmation before continuing.

---

## Step 3: Download and extract

Once confirmed:
1. Download: `curl -L -o archives/paper_{ID}.tar.gz "https://arxiv.org/src/{ID}"`
2. Create directory: `mkdir -p papers/paper_{ID}`
3. Extract: `tar -xzf archives/paper_{ID}.tar.gz -C papers/paper_{ID}/`
4. List the extracted files so the user can see what's inside.

---

## Step 4: Read the paper content

Locate the main TeX file (usually `main.tex`, or named after the paper). Also look for a `sections/` subdirectory with individual section files.

Read the following in order (use `offset` and `limit` parameters to avoid token limits):
1. The abstract and introduction (first ~300 lines of main.tex)
2. The method/system design section
3. The experiments section (setup, baselines, metrics, results)
4. The conclusion

If there is a `sections/` directory, read each file individually:
- `00_abstract.tex`, `01_introduction.tex`, etc.

---

## Step 5: Generate and save a structured summary

Create a file at `papers/paper_{ID}/summary.md` with the following structure:

```markdown
# Paper Summary: {SHORT_TITLE}

## Metadata
- **arXiv ID**: {ID}
- **Title**: {FULL_TITLE}
- **Authors**: {AUTHORS}
- **Affiliations**: {AFFILIATIONS}
- **Venue**: {CONFERENCE} (inferred from style file: icml/iclr/neurips/usenix/acl/emnlp/etc.)
- **Submission Date**: {YYMM from arXiv ID}
- **\iclrfinalcopy / accepted flag**: {YES/NO — indicates camera-ready}
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

## Step 6: If multiple papers were provided

After processing all papers individually, generate a comparison table at `papers_comparison.md` in the root working directory (or append to it if it already exists). Scan `papers/` to find all existing `summary.md` files to include in the comparison.

The table should compare across:
- Basic metadata (venue, date, affiliation)
- Research problem & threat model
- Method type (attack / defense / evaluation)
- Benchmark & dataset
- Baselines
- Metrics
- Key results
- Paper structure (which sections exist: ablation, case study, benchmark chapter, etc.)

Also include a "Structural Patterns" section at the end summarizing recurring patterns you observe across all papers (e.g., how baselines are selected, how metrics are justified, how human evaluation is used).

---

## Notes for reading TeX files

- Style file name reveals the venue:
  - `icml2026.sty` → ICML 2026
  - `iclr2026_conference.sty` → ICLR 2026
  - `neurips_2025.sty` → NeurIPS 2025
  - `usenix.sty` → USENIX Security
  - `acl_natbib.sty` → ACL/EMNLP/NAACL
- `\iclrfinalcopy` present → paper accepted (camera-ready)
- `.bbl` file length ≈ proxy for citation count
- `arXiv ID YYMM` → submission month (e.g., 2602 = Feb 2026, 2509 = Sep 2025)
- `\newcommand{\NAME}{...}` reveals the system/framework name
- Authors listed in `\icmlauthor{}{}` or `\author{}` blocks
