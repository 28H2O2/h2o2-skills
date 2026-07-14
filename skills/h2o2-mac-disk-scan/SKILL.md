---
name: h2o2-mac-disk-scan
author: 28H2O2
description: 只读扫描 Mac 磁盘大文件/大目录并按可清理程度分档报告。结合 mo (Mole) 的 dry-run 与 du/find/stat，识别「放了很久且可能不需要」的东西，绝不删除任何文件。当用户说"磁盘满了"、"扫描大文件"、"哪些东西占空间"、"清理前先看看"、"disk scan"、"用 mo 查一下" 时触发。
---

# h2o2-mac-disk-scan：Mac 大文件只读扫描

## 铁律

1. **纯只读**。只用 `du` / `find` / `stat` / `ls` / `df` 和 mo 的 `--dry-run`。任何删除动作必须等用户看完报告后逐项指示。
2. 报告先行：产出三档分类报告是本 skill 的终点，清理是另一次对话的事。
3. 微信/飞书等 app 的数据**永远建议在 app 内置的存储清理入口处理**，不要直接删它们容器里的文件（会损坏聊天记录数据库）。

## 依赖：mo (Mole)

- GitHub: https://github.com/tw93/mole
- 安装: `brew install tw93/tap/mole`（注意与 homebrew/core 的 mole 重名，必须带 tap 前缀）
- 检查: `which mo`。没装就先提示用户装，或跳过 mo 步骤只用 du/find。

mo 的只读用法（本 skill 只允许这几个）：

| 命令 | 作用 | 注意 |
|---|---|---|
| `mo clean --dry-run` | 预览可清理的缓存/日志/孤立 dotfile，输出总可释放体积 | 明细落盘在 `~/.config/mole/clean-list.txt`，直接读它 |
| `mo purge --dry-run` | 预览旧项目构建产物（node_modules、__pycache__、target 等） | 搜索根路径在 `~/.config/mole/purge_paths` |
| `mo installer --dry-run` | 找遗留的 dmg/pkg 安装包 | 会进交互 TUI，用 `mo installer --dry-run 2>&1 \| sed 's/\x1b\[[0-9;]*m//g'` 抓一次输出即可，别试图交互 |
| `mo analyze` | 磁盘浏览器 | 交互式 TUI，**无人值守时不要用**，用 du 替代 |

不允许在本 skill 中运行：`mo clean`（无 dry-run）、`mo purge`（无 dry-run）、`mo uninstall`、`mo optimize`。

## 扫描流程

### 1. 概览（秒级）
```bash
df -h / /System/Volumes/Data      # 总量与剩余
tmutil listlocalsnapshots /       # APFS 本地快照（常见隐形占用）
```

### 2. mo 只读扫描（分钟级，可与步骤 3 并行）
上表三个 dry-run 命令。彩色输出用 `sed 's/\x1b\[[0-9;]*m//g'` 去转义码。

### 3. du 分层下钻（慢，用 run_in_background 并行跑）
```bash
du -x -d 1 -g ~ 2>/dev/null | sort -rn | head -30        # 家目录一级
du -x -d 0 -g /Applications /Library /private /opt /usr/local 2>/dev/null | sort -rn  # 家目录外
```
对 Top 目录再下钻 1-2 级。经验上的必查大户：
- `~/Library/Application Support`（LarkShell 飞书、Claude vm_bundles、浏览器 profile）
- `~/Library/Containers/com.tencent.xinWeChat`（微信 msg 附件，常见 20-40GB）
- `~/Library/Developer/Xcode/iOS DeviceSupport`（每个 iOS 版本 5-6GB，只需保留最近 2 个）
- `~/Desktop` 下的科研/项目目录（数据集、轨迹、压缩包）
- `~/.ollama/models`、`~/.colima`、`~/.cache`（含 huggingface）、`~/OrbStack`
- `/opt/anaconda3`（conda 包缓存可 `conda clean -a`）、`/usr/local/texlive`

部分目录会报 `Operation not permitted`（终端缺 Full Disk Access）——记录后跳过，报告里说明。

### 4. 大文件定位（慢，后台跑）
```bash
find ~ -xdev -type f -size +1G -exec du -h {} + 2>/dev/null | sort -rh | head -40
```
特别留意：磁盘镜像（.img/.raw/diffdisk）、模型权重、`.tar.gz`/`.zip` 旁边有没有同名解压目录（有则压缩包可删）。

### 5. 陈旧度判定
```bash
stat -f "%Sm|%Sa|%N" -t "%Y-%m-%d" <path>
```
阈值：>180 天未修改且未访问 → 「放了很久」；90-180 天 → 「较旧」。

## 报告格式

按三档输出，每项给：路径、体积、最后动静时间、判断理由：

1. **基本可放心清理**（删了自动重建）：mo dry-run 确认项、缓存、DerivedData、旧 DeviceSupport、Chrome 内置模型 weights.bin
2. **大概率不需要，建议过目**：桌面上的 app 副本、几个月没动的 VM 镜像（colima/ollama/浏览器 profile）、遗留安装包、孤立 dotfile
3. **只有用户能决定**（不可恢复）：科研数据集/实验轨迹、个人文档、照片库、装着的应用

结尾给「预计可释放 XX GB / 占用从 X% 降到 Y%」的估算，和建议的清理顺序（mo 三连 → app 内清理 → 第二档过目 → 第三档确认备份后处理）。明确声明：本次未删除任何文件，等用户逐项确认。
