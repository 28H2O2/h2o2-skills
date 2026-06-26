# 论文投稿审查报告 — 七段式模板

> 这是 paper-submission-audit skill 的报告骨架。审查时**逐段填充**，不要删段、不要改段序。
> 没有内容的段也要保留标题，并写明"未发现问题"或"本次未核验（原因）"。

---

# {论文名} 论文投稿审查报告

**审查日期：** {YYYY-MM-DD}
**目标会议：** {用户指定，如未指定写"未指定，按通用安全顶会标准审查"}
**审查范围：** `main.tex` 实际 `\input` 的活跃正文、附录、表格、被引图片、参考文献
**已忽略：** 未进入活跃链的历史版本、注释内容、`do_no_use/` 等
**外部事实核验：** {已核验，截至 YYYY-MM-DD / 已用 --no-web 跳过，外部事实未核验}
**说明：** 本次审查为纯只读，未修改论文任何源文件。

## 0. 活跃文件清单（请作者先核对）

本次判定为**活跃**、纳入审查的文件（按 `\input` 顺序）：

- `main.tex`
- `sections/xxx.tex`
- …

判定为**不活跃、已忽略**的可疑文件（物理存在但未进入活跃链）：

- `do_no_use/…`、`sections/old_*.tex` …

> 若上表与你的实际投稿版本不符，说明活跃链识别有偏差，请告知后重审。

## 1. 投稿风险结论

{1–2 段。是否建议直接投稿；最致命的 3–5 条问题；对应的风险类型（正确性 / 可信度 / desk-reject）。}

**最优先修订顺序：**
1. …

## 2. 问题等级与证据定义

- **P0 — 阻断投稿：** 可能推翻核心技术论断、使主结果无法可靠解释，或违反硬性投稿要求。
- **P1 — 重大问题：** 明显削弱正确性、实验有效性、可复现性或主要结论。
- **P2 — 一般问题：** 需修复的报告、表述、一致性或次级有效性问题。
- **P3 — 语言与排版：** 投稿前应处理的语法、术语、格式、视觉问题。

证据状态：
- **已确认：** 可由活跃源码、公式、表格或文本直接证明。
- **需核验：** 须检查实现代码、raw data、日志或本目录中不存在的材料。

## 3. P0 — 阻断投稿

### P0-1. {标题}

**位置：** `file.tex:行号`
**证据：** 已确认 / 需核验

{问题描述。数学类必须遵守 show-your-work：写出完整推导链，不下不可复核的判决，以"请核对实现"收尾。}

**影响：** {审稿人会怎么用这条打你。}

**修复建议：**
1. …

{若适用，给可直接替换的英文句，用引用块。}

## 4. P1 — 重大问题
（同上条目格式）

## 5. P2 — 一般问题
（同上条目格式）

## 6. P3 — 语言、术语与排版

### P3-x. 明确的语法/措辞错误
（列 `错误 → 修正`，附位置）

### P3-x. 术语统一
（表格：概念 | 建议统一写法）

## 7. 论断对齐检查

| 论断 | Abstract/Intro | Evaluation 证据 | Conclusion | 审查结论 |
|---|---|---|---|---|
| … | … | … | … | 收敛/统一/补充… |

## 8. 外部事实与投稿合规核验

> 本节所有信息标注核验日期；时间敏感数据应在论文/artifact 中记录快照，不当作永久事实。
> 若本次 `--no-web`，整节写"未核验"，仅列出**需作者自行核验**的清单。

- {模型名/checkpoint 是否存在}：[URL]，核验日期 YYYY-MM-DD
- {benchmark 规模/子集}：[URL]，核验日期 YYYY-MM-DD
- {GitHub stars / 下载量，注意 model repo vs product repo}：[URL]，核验日期 YYYY-MM-DD

## 9. 必须生成的数据复算包（建议作者执行）

skill 无法访问 raw data，以下由作者从实验输出生成 machine-readable package，再据此自动生成表格：

1. Detector counts：按 model/dataset/split 的 TP/TN/FP/FN
2. Attack outcomes 原始计数
3. Sample manifest（task ID / hash / source / exclusion）
4. Run manifest（checkpoint/API version、commit、seed、temperature、hardware）
5. Aggregation script（同一 raw rows 自动产出 dataset-equal 与 sample-weighted）
6. Uncertainty（headline rates 的 bootstrap / 精确二项 CI）
7. Neuron ranking / approximation audit（如适用）

## 10. 投稿前验收清单

### 数学与实现
- [ ] …

### 数据与指标
- [ ] 每组指标都能由公开 confusion counts 复算
- [ ] aggregation（micro/macro/dataset-equal）已定义

### 论断
- [ ] Abstract/Intro/Eval/Conclusion 使用相同模型与数字
- [ ] Causal / first / most / unseen claim 有明确范围与证据

### 可复现性
- [ ] 精确 checkpoint/API identifier 与 access date 已记录
- [ ] 论文引用的 prompt templates / parsers 确实存在
- [ ] anonymous artifact 无需登录且不泄露身份

### 投稿卫生（通用，跨会议）
- [ ] 无 `??` / `Sec.xx` / undefined reference
- [ ] 无残留 `\TODO` / `\sout` / `\new` 等 review 宏与可见编辑痕迹
- [ ] 无 duplicate label
- [ ] 标题页无真实作者名，也无 `Anonymous Authors` 占位
- [ ] 源码不泄露作者身份（致谢 / 自托管路径 / 非匿名自引）

## 11. 会议特定格式检查（请作者自行收口）

本 skill **不内置任何会议规则**。投稿前请对照目标会议**当年 CFP** 自查并补跑官方检查：

- **页数上限 / 必需章节名 / bibliography style** —— 每家会议不同，以当年 CFP 为准。
- **官方 desk-reject checker** —— 例如 USENIX Security 的 `spacing_public.py`（检查 section/caption 间距、abstract box、Ethical Considerations / Open Science 必需章节），IEEE S&P / NDSS / CCS 各有模板与检查方式。
- 跑完把脚本报告的 violation 与本报告 P0/P3 合并处理。

## 12. 最终评价

{1 段：最该先解决的是什么（通常是核心数学/数据可复算，而非英文润色），第二优先级是什么。}
