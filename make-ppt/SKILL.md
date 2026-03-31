---
name: make-ppt
description: Create PowerPoint presentation slides and speaker notes from a downloaded arXiv paper. Use when the user wants to make a PPT for an arXiv paper that has already been processed by the arxiv-paper skill (i.e., summary.md and TeX source exist under papers/). Input is a paper name or arXiv ID.
---

## 前提

在你的**论文项目根目录**下使用，该目录需已通过 arxiv-paper skill 下载并生成了 `papers/paper_{ID}/summary.md`。skill 会自动创建：
- `ppts/{PaperName}/image_png/` — 转换后的 PNG 图片
- `ppts/{PaperName}/make_ppt.js` — 生成脚本
- `ppts/{PaperName}/{PaperName}.pptx` — 最终 PPT
- `ppts/{PaperName}/script.md` — 讲稿

如需自定义 PPT 样式（配色、字体、布局），在根目录创建 `ppts/META_PPT.md` 并写入规范；若不存在则使用默认样式。

---

你正在为一篇已下载的 arXiv 论文制作 PPT 和讲稿。

用户提供的论文名称或 arXiv ID 作为输入。

在开始之前，检查根目录是否存在 `ppts/META_PPT.md`；若存在，必须完整阅读，本次制作的所有规范以该文件为准。

---

## Phase 1：准备素材（自动化，不需要推理）

### 1.1 确认 summary.md

检查 `papers/` 目录，找到与用户输入匹配的论文目录（按名称或 ID 匹配），确认存在 `summary.md`。

```bash
ls papers/
```

若 summary.md 不存在，告知用户需要先运行 arxiv-paper skill 生成摘要，然后停止。

### 1.2 确认图片目录与 TeX 源码

```bash
ls papers/paper_{ID}/          # 找到图片目录（images/ 或 image/）
ls papers/paper_{ID}/images/   # 列出所有 PDF 图片
```

### 1.3 创建 PPT 工作目录

```bash
mkdir -p ppts/{PaperName}/image_png
```

PaperName 使用论文的短名称（框架名，如 MirrorGuard、GUIGuard）。

### 1.4 将论文图片 PDF 转为高清 PNG，并记录尺寸

**只转换计划放入 PPT 的图片**（在 Phase 2.1 阅读论文后再决定选哪些，但为节省时间可以先转换所有主图）。

```python
import fitz, os

figures = {
    "fig_XXX": "XXX.pdf",   # 按图号命名，Phase 2 决定后填入
}
base = "papers/paper_{ID}/images"
out  = "ppts/{PaperName}/image_png"

for name, fname in figures.items():
    doc = fitz.open(os.path.join(base, fname))
    for i, page in enumerate(doc):
        pix = page.get_pixmap(matrix=fitz.Matrix(3.0, 3.0))
        path = os.path.join(out, f"{name}_p{i}.png")
        pix.save(path)
        print(f"{name}_p{i}: {pix.width}×{pix.height}  ratio={pix.width/pix.height:.3f}")
```

**将每张图的像素尺寸和 ratio 记录下来**，后续计算必须用到。

---

## Phase 2：AI 核心工作（需要推理）

### 2.1 阅读论文，理解内容

按以下顺序阅读（summary 只做索引，关键数字必须回到原文核实）：

1. `papers/paper_{ID}/summary.md` — 获取整体结构
2. 论文 TeX 主文件的 Abstract + Introduction — 提取背景、问题、核心洞察
3. 方法章节 — 理解关键设计，记录图的编号和内容
4. 实验章节 — 提取主表关键数字、消融结论

同时确认：
- 使用哪个 style 文件（判断会议）
- 论文的框架/系统名称（`\newcommand` 或 `\textsc{}`）
- 图片目录中哪些图是主图、哪些是附录图

### 2.2 规划 Slide 结构

根据 `ppts/META_PPT.md` 第三节的标准布局，确定：

| Slide | 主题 | 选用的图 | 布局方案 |
|-------|------|---------|---------|
| 1 | 背景+问题+方法概览 | 总览图（Overview/Framework） | 布局 A（左文右图）|
| 2 | 方法细节 / Benchmark | 流水线图 / 数据集图 | 布局 B 或 D |
| 3 | 实验结果 | 结果图 / Case Study | 布局 C 或 B |

**在选图时说明理由**（为什么选这张而不是其他）。

### 2.3 计算图片 PPT 尺寸

对每张选用的图，使用公式计算：

```
可用内容高度 = 6.00"（CONTENT_Y=1.10 到 FOOTER_Y=7.10）

已知 ratio = 图片像素宽 / 图片像素高

若目标宽度为 w：  h = w / ratio
若目标高度为 h：  w = h * ratio

约束：
  - 单图最大宽度：11.5"
  - 单图最大高度：3.97"（CONTENT_H × 0.65）
  - 同一 Slide 多图：sum(各图 h) + 间距总和 ≤ 6.00"
```

**列出每个 Slide 的元素高度累加验算**，确认不超出 6.00" 才进入下一步。

示例：
```
Slide 2 高度验算：
  top margin:    0.05"
  dataset fig:   2.74"  (w=7.0, ratio=2.557)
  caption:       0.23"
  separator gap: 0.40"
  label text:    0.28"
  recog fig:     2.07"  (w=10.5, ratio=5.074)
  caption:       0.23"
  合计:          6.00" ✓
```

### 2.4 撰写 Slide 正文文字

每张 Slide 的中文内容，遵循：
- Section label：≤15 字，加粗
- Bullet points：简洁，每条 ≤40 字
- 关键数字直接引用（如"Unsafe Rate 从 66.5% 降至 13.0%"）
- 专业术语、模型名、指标名保留英文

### 2.5 撰写讲稿

共 3～4 段，每段 250～350 字（约 1.5～2 分钟），结构：
- 背景铺垫（1～2 句）
- 论文方案介绍（2～3 句，必须引用具体 Section/Figure/Table）
- 关键数字解读（1～2 句）
- 一句评价或过渡

最后一段末尾：一句话点出全文核心亮点。

### 2.6 编写 make_ppt.js

基于以上所有信息，编写完整的 `ppts/{PaperName}/make_ppt.js`，要求：

1. **所有路径相对 `__dirname`**：
   ```javascript
   const IMG_DIR = path.join(__dirname, "image_png");
   ```

2. **图片尺寸注释**（像素宽高 + ratio）：
   ```javascript
   // 2041×1148, ratio=1.778
   addFig(s, figFramework, RX, RY, 7.95, 7.95/1.778, "Figure 1 — ...");
   ```

3. **每张 Slide 结束前必须调用 `s.addNotes(讲稿文字)`**

4. 图注中文，包含 Figure 编号和核心描述

5. 输出文件：`path.join(__dirname, "{PaperName}.pptx")`

如果 `ppts/` 下已有其他论文的 `make_ppt.js`，可以参考其中的 helper 函数（addTitle、addFooter、addFig、booktabsTable 等）；否则从头编写。

---

## Phase 3：生成与验证（自动化）

### 3.1 运行脚本

```bash
NODE_PATH=$(npm root -g) node ppts/{PaperName}/make_ppt.js
```

### 3.2 溢出检测（必须执行，不可跳过）

```python
from pptx import Presentation
prs = Presentation('ppts/{PaperName}/{PaperName}.pptx')
sw = prs.slide_width.inches
sh = prs.slide_height.inches
overflows = []
for i, slide in enumerate(prs.slides):
    for shape in slide.shapes:
        x = shape.left / 914400
        y = shape.top / 914400
        w = shape.width / 914400
        h = shape.height / 914400
        if (x + w) > sw + 0.05 or (y + h) > sh + 0.05:
            overflows.append(
                f"Slide {i+1} [{shape.name}]: right={x+w:.2f}\" bot={y+h:.2f}\""
            )
print("溢出检测：", overflows if overflows else "无溢出 ✓")
```

**如有溢出**：回到 2.3，缩小对应图片的目标宽度，重新计算高度，修改 make_ppt.js，重新运行。

### 3.3 内容 QA

```bash
python3 -m markitdown ppts/{PaperName}/{PaperName}.pptx | head -80
```

确认：每张 Slide 的标题、正文、图注、Notes 均正确输出。

### 3.4 保存讲稿文件

将讲稿写入 `ppts/{PaperName}/script.md`，格式：

```markdown
# {PaperName} 讲稿

**论文**：{完整标题}
**时长**：5～6 分钟

---

## Slide 1：{Slide 标题}（~X 分钟）

{讲稿正文，引用论文 Section/Figure/Table}

---

## Slide 2：{Slide 标题}（~X 分钟）

...

---

## Slide 3：{Slide 标题}（~X 分钟）

...（最后一句为全文亮点）
```

---

## 完成标准

以下所有条件满足后，本次制作完成：

- [ ] `ppts/{PaperName}/image_png/` 包含所有使用的 PNG 图片
- [ ] `ppts/{PaperName}/make_ppt.js` 已编写，路径用 `__dirname`
- [ ] `ppts/{PaperName}/{PaperName}.pptx` 已生成
- [ ] 溢出检测结果：**无溢出**
- [ ] markitdown QA：文字和 Notes 均正确
- [ ] `ppts/{PaperName}/script.md` 已生成，每段引用论文原文，末尾有亮点总结
