---
name: h2o2-paper-submission-audit
author: 28H2O2
description: 对要投安全/AI 顶会的英文 LaTeX 论文做投稿前深度审查，纯只读产出一份分级中文审查报告。当用户给出一个 LaTeX 投稿论文的 zip 或源码目录，想在投稿/rebuttal 前以审稿人视角做 desk-reject 排查、数学推导核查、数据可复算性核查、claim 对齐核查时使用。触发词：投稿审查、论文审查、审稿人视角、desk reject 检查、latex 投稿检查、paper audit、submission review、帮我审一下这篇论文。
---

## 定位与铁律

你在帮用户**投稿前审查一份英文 LaTeX 论文**（典型是安全 / AI 顶会：S&P、USENIX、NDSS、CCS、NeurIPS 等）。

三条不可动摇的铁律，违反任何一条这次审查就作废：

1. **纯只读。** 绝不修改、移动、删除论文的任何源文件。zip 一律解压到副本目录。产出只有一份报告。
2. **证据纪律。** 每条问题必须标注证据状态——**已确认**（可由活跃源码 / 公式 / 表格 / 文本直接证明）或**需核验**（须看实现代码、raw data、日志等本目录中不存在的材料）。**绝不把无法从静态源码证实的东西写成确定结论。** 这是本 skill 区别于"瞎喷一通"的命门。
3. **show-your-work（尤其数学）。** 任何数学 / 推导质疑必须：(a) 引用具体公式的 `file:line`；(b) 完整写出你认为正确的推导链；(c) 以"请核对你的实现 / loss"收尾。宁可写"这一步看起来需要二阶项才非零，推导如下……请核对"，也绝不写"你的近似是错的"这种无法复核的判决。

---

## 输入处理

用户给出一个 **LaTeX zip** 或**已解压目录**。

- zip：解压到一个**副本目录**（如 `<scratchpad>/audit_unzip_<name>/`），绝不在原 zip 旁边原地解压污染。
- 目录：直接用，但仍然只读。

确认根目录里能找到 `main.tex`（或用户指定的主文件）。找不到主文件就问用户哪个是入口。

可选开关（用户可在调用时说明）：
- `--no-web`：跳过外部事实核验（第三步），报告里明确标"外部事实未核验"。
- `--second-opinion`：在 Claude 审完后，额外编排 `codex` 跑一份独立第二审并合并（第四步）。

---

## 第一步：识别"活跃源码"

**这是价值最高、也最容易翻车的一步——审错文件，整份报告作废。**

主路径：从主文件**递归解析 `\input` / `\include` 链**，不依赖编译。解析铁律：

1. **剔除注释。** 整行 `%` 注释、行内 `%` 之后的内容一律不算（注意 `\%` 是转义百分号，不是注释）。被注释掉的 `\input` 视为**不活跃**。
2. **两种语法都认。** `\input{file}`、`\input{file.tex}`、以及无花括号无后缀的 `\input file`、`\include{file}`、`\subfile{...}` 都要识别。补全 `.tex` 后缀解析。
3. **递归。** 进入每个活跃子文件继续解析，直到没有新文件。
4. **块级排除。** `\begin{comment}...\end{comment}`、`\iffalse...\fi`、`\if0...\fi` 块内的 input 算**不活跃**。条件块（`\ifsomeflag`）若无法判断真假，保守纳入但在报告里标注"条件编译，请确认是否活跃"。
5. **物理存在 ≠ 活跃。** 不在活跃链里的文件——哪怕物理存在（`do_no_use/`、`old_*.tex`、`exp_0201.tex`、被注释的旧 section）——**一律不读、不审、不引用**。
6. 同样只看活跃链实际 `\input` 的 table、实际 `\includegraphics` 引用的 fig、实际 `\cite` 的 bib 条目。

**报告第 0 段必须显式列出"判定为活跃的文件清单"和"忽略的可疑文件"**，让作者一眼核对你审对了没有。若作者反馈审错，重审。

---

## 第二步：逐维度审查（固化 rubric）

**逐项走完下面每个维度**，不要靠临场发挥东查一点西查一点。每发现一个问题，按报告模板的条目格式记录（位置 / 证据状态 / 影响 / 修复建议），并定级 P0–P3。

### 维度 A — 数学 / 推导正确性
公式推导是否成立、近似是否合理、符号是否前后一致、定义的对象（如"一个 neuron"指 up/gate/down 哪个坐标）是否唯一可复现。**严格 show-your-work**。这是审稿人最致命的攻击点，也是你最容易自信地错的地方——摊开推理让作者能反驳。

### 维度 B — 数据一致性与可复算
- 表格里的 Accuracy / FPR / FNR / ASR / SR 能否由声明的样本量与定义**反算成立**？亲自代入公式算一遍。
- 同一个量在 abstract / intro / 各 section / 表格 / 图之间**有没有数字冲突**（模型名、准确率、延迟、样本数、应用数）。
- 聚合方式（micro / macro / dataset-equal）是否定义；"Overall"是等权还是加权。
- 样本量单位是否定义清楚（screenshots vs pairs vs queries vs 过滤后样本）。
- `mean ±` 到底是 std / SE / CI。

### 维度 C — claim 对齐与严谨度
- abstract / intro / evaluation / conclusion 是否用**同一套** headline 数字和模型。
- 因果性表述是否超过实验设计能支持的程度（有没有 matched control、random intervention control）。
- "first / most popular / highest / unseen" 类声明是否有明确范围与证据。
- 百分点 vs 百分比是否混用。

### 维度 D — 实验严谨性
- 控制组是否缺失。
- 统计不确定性 / 重复运行协议 / CI 是否报告。
- **数据集 shortcut**：clean 与 injected 是否来自不同来源，使分类器可能只在分辨数据集来源而非真任务。
- threat model 与各实验的 adversary capability（black-box / defense-aware / white-box）是否对应清楚。
- 超参数（如某个 ratio）是否被引用的 pilot 表直接支持。

### 维度 E — 投稿卫生（通用，跨会议，硬抓）
扫活跃源码与（若存在）`main.log` / `main.pdf`：
- 未解析引用 `??` / `Sec.xx` / undefined reference / duplicate label。
- 残留 review 宏：`\TODO`、`\sout`、`\new`、`\revise`、彩色编辑标记、可见删除线。
- 标题页 `Anonymous Authors` 这类占位，或匿名稿里出现真实作者名。
- **作者身份泄露**：致谢、自托管 URL/路径、非匿名自引、含真实姓名的 artifact 链接。
- 编译告警（若有 log）：font-shape substitution、大量 underfull box、font 未嵌入。

### 维度 F — 参考文献与可复现性
- broken cite、缺失条目、bib 风格明显异常（具体哪种风格属会议特定，留到第 11 段提醒，不在此下断言）。
- 论文引用的 prompt templates / parsers / artifact 路径**是否在本目录中存在**（不存在标"需核验：是否在独立 artifact 中"）。
- 模型 checkpoint / API identifier / 数据集 version 是否明确到可复现。

---

## 第三步：外部事实核验（默认开，`--no-web` 可关）

对**可被外部证实**的事实做联网核验，每条**强制带 URL + 核验日期**：

- 模型名 / checkpoint 是否真实存在、是否官方名（如 Gemini 3.1 Pro、Qwen3-VL-2B-Instruct）。
- benchmark 规模与本文用量是否一致（如本文是否用了完整 benchmark 还是子集）。
- GitHub stars / 下载量 —— **特别小心 model repo 与 product/desktop repo 混用**导致 star 数虚高。
- 优先权 / 流行度类声明的可辩护性。

联网用 `web-access` skill 或 WebSearch/WebFetch。核验结果写进报告第 8 段，时间敏感数据提醒作者在论文中记录快照日期。

若 `--no-web`：跳过本步，第 8 段写"外部事实未核验"，并把上述各项列成**需作者自行核验的清单**。

---

## 第四步（可选）：第二审 `--second-opinion`

仅当用户要求。Claude 审完后，用 `codex` skill / CLI 跑一份独立审查（同样喂活跃文件清单和 rubric），然后**由 Claude 合并两份**：相同发现去重、各自独有的发现保留并注明来源、结论冲突处显式标"两边分歧：Claude 认为… / codex 认为…"。不自动采信任何一方。

---

## 产出报告

严格按 `references/report_template.md` 的**七段式骨架**填充（实际是 0–12 段，"七段式"指其主干结构，不要删段、不要改段序）。

- **语言：** 报告主体用简体中文；所有可直接替换进论文的修订句用**英文**（论文是英文，patch 必须能直接粘贴）。术语 / 模型名 / 命令保持原文。
- **写到：** `<论文目录>/audit/PAPER_AUDIT_REPORT_<YYYY-MM-DD>.md`（`audit/` 不存在则创建；这是 skill 唯一允许的写操作，且写在论文目录的子目录里，不碰任何源文件）。
- 写完把报告路径和"投稿风险结论 + P0 数量"作为一句话摘要回给用户。

---

## 不做什么（边界）

- **不内置任何会议规则。** 页数上限、必需章节名、bibliography style 全部留到报告第 11 段提醒作者对照当年 CFP 自查、并补跑该会议官方 checker（如 USENIX 的 `spacing_public.py`）。不要硬编码"13 页""必须有 Open Science 章节"这类会议特定规则。
- **不改源码。** 哪怕是显然的 typo，也只在报告里写 `错误 → 修正`，不动文件。
- **不编译 LaTeX。** 活跃文件识别靠解析 `\input` 链，不靠编译。
- **不替作者算 raw data。** 没有 raw data 的复算只能标"需核验"并给出**作者应执行的复算方法**（报告第 9 段），不要假装算出了结论。
