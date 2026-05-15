---
name: h2o2-youtube-transcript-extractor
author: 28H2O2
description: Extract YouTube video transcript/script via youtube-transcript-api, with CDP fallback to discover available caption tracks. Use when the user wants YouTube视频文字稿、口播语料、演讲全文，尤其是需要把视频内容落地成可分析的纯文本时。
---

# YouTube Transcript Extractor

用于从 YouTube 视频提取字幕/文字稿，适合"要视频内真实口播语料"的任务。

## 适用场景

- 用户要 YouTube 视频的演讲全文、口播文案
- 用户要保存字幕纯文本用于分析、翻译、引用
- B 站搬运视频没有字幕轨，需要找 YouTube 原版
- 批量提取某频道/系列视频的文字语料

## 前提

- Python 3 环境（`/opt/anaconda3/bin/python3` 或系统 python3）
- `youtube-transcript-api` 库（不存在时自动安装）
- 需要找视频 ID 时，加载 `web-access` skill 用 CDP 操作

## 工作流

### 1. 确认视频 ID

YouTube 视频 ID 是 URL 中 `?v=` 后面的 11 位字符串：

```
https://www.youtube.com/watch?v=3Fx5Q8xGU8k
                                ^^^^^^^^^^^
                                video_id = 3Fx5Q8xGU8k
```

如果用户给的是 B 站链接，先判断是否是搬运视频（标题含原版来源），用 WebSearch 找对应的 YouTube 原版。

### 2. 检查并安装依赖

```bash
python3 -c "from youtube_transcript_api import YouTubeTranscriptApi" 2>/dev/null || \
  pip3 install youtube-transcript-api -q && echo "ready"
```

### 3. 查询可用字幕轨

先查这个视频有哪些字幕轨（语言、是否自动生成）：

```bash
python3 -c "
from youtube_transcript_api import YouTubeTranscriptApi
api = YouTubeTranscriptApi()
# list_transcripts 返回可用轨列表
transcripts = api.list('VIDEO_ID')
for t in transcripts:
    print(t.language_code, t.language, '自动生成' if t.is_generated else '人工')
"
```

### 4. 下载字幕并保存纯文本

```bash
python3 -c "
from youtube_transcript_api import YouTubeTranscriptApi

video_id = 'VIDEO_ID'
api = YouTubeTranscriptApi()

# 优先拿人工字幕，没有则拿自动生成
transcript = api.fetch(video_id, languages=['en'])  # 按需改语言代码

# 拼成纯文本（去掉时间戳）
lines = [s.text.strip() for s in transcript.snippets if s.text.strip()]
full_text = ' '.join(lines)

# 保存
output_path = './VIDEO_TITLE.txt'
with open(output_path, 'w') as f:
    f.write(full_text)

print(f'共 {len(transcript.snippets)} 段，{len(full_text.split())} 词')
print(f'已保存到 {output_path}')
"
```

### 5. 保留带时间戳版本（可选）

用于需要对照视频位置的场景：

```bash
python3 -c "
from youtube_transcript_api import YouTubeTranscriptApi

api = YouTubeTranscriptApi()
transcript = api.fetch('VIDEO_ID', languages=['en'])

with open('./VIDEO_TITLE_timestamped.txt', 'w') as f:
    for s in transcript.snippets:
        mins = int(s.start // 60)
        secs = int(s.start % 60)
        f.write(f'[{mins:02d}:{secs:02d}] {s.text}\n')

print('带时间戳版本已保存')
"
```

## 关键判断

- **有人工字幕**：质量高，有标点，直接用
- **只有自动字幕（is_generated=True）**：全小写无标点，专有名词易错，使用时需标注来源是 ASR
- **无任何字幕**：视频可能是私有的、刚上传的，或不支持字幕；考虑音频转写方案
- **只有目标语言之外的字幕**：用 `languages=['zh-Hans', 'zh-TW', 'en']` 按优先级列举

## 语言代码参考

| 语言 | 代码 |
|------|------|
| 英语 | `en` |
| 简体中文 | `zh-Hans` |
| 繁体中文 | `zh-TW` |
| 日语 | `ja` |
| 韩语 | `ko` |

## 已验证的事实

（2026-04-30 实测）

- `YouTubeTranscriptApi()` 新版实例化后调 `.fetch(video_id)` 和 `.list(video_id)`，旧版的 `get_transcript` 类方法已不存在
- YouTube 的 timedtext URL（从 `ytInitialPlayerResponse` 里读出来的）在 CDP 页面内 `fetch()` 会返回空字符串——CORS 拦截，不要走这条路
- `youtube-transcript-api` 走的是服务器端请求，绕过 CORS，是最可靠的方式
- `transcript.snippets` 是字幕片段列表，每个片段有 `.text`、`.start`（秒）、`.duration`
- 自动字幕（ASR）常见问题：全小写、无标点、专有名词错字（如 `silica valley` = Silicon Valley，`paler` = Palantir）

## CDP 辅助：发现字幕轨（备用）

当需要确认 YouTube 页面上有哪些字幕轨时（不依赖 python 库），可用 CDP 读页面状态：

```bash
# 打开视频页
curl -s "http://localhost:3456/new?url=https://www.youtube.com/watch?v=VIDEO_ID"

# 等 5 秒后读字幕轨列表
sleep 5 && curl -s -X POST "http://localhost:3456/eval?target=TARGET_ID" -d '(()=>{
  const pr = window.ytInitialPlayerResponse;
  const tracks = pr?.captions?.playerCaptionsTracklistRenderer?.captionTracks || [];
  return JSON.stringify(tracks.map(t => ({
    lang: t.languageCode,
    name: t.name?.simpleText,
    isAsr: !!t.kind
  })), null, 2);
})()'
```

注意：只用于**查询**有哪些轨，不用于下载——下载必须走 `youtube-transcript-api`。

## 注意事项

- 自动字幕质量参差：口音重、专业术语多的视频识别误差大
- 视频若设置了字幕禁用，`youtube-transcript-api` 会抛 `TranscriptsDisabled` 异常
- 私人视频无法访问，会抛 `VideoUnavailable`
- 不要用于版权内容的大规模批量采集
