---
name: h2o2-bilibili-subtitle-extractor
author: 28H2O2
description: Extract Bilibili video subtitle tracks through a logged-in browser page, save AI subtitle JSON locally, and convert subtitle JSON into readable text corpora. Use when the user wants B站视频字幕、口播语料、视频内文案，尤其是要从公开视频页拿 subtitle_url 并批量落地字幕文件时。
---

# Bilibili Subtitle Extractor

用于从 B 站视频页提取字幕轨，适合“标题之外，还要视频内部真实口播语料”的任务。

## 适用场景

- 用户要 B 站视频里的真实口播文案
- 用户要保存字幕 JSON / 纯文本语料
- 用户要分析某个 UP 的语言表达，而不仅是标题和简介
- 需要批量做公开视频字幕抓取

## 前提

- 必须加载 `web-access` skill 并遵循其 CDP 流程
- 使用用户已登录的 Chrome
- 目标视频页要能正常打开

## 工作流

### 1. 打开视频页

用 CDP 新建后台 tab：

```bash
curl -s "http://localhost:3456/new?url=https://www.bilibili.com/video/<BVID>/"
```

### 2. 从页面上下文读取字幕 URL

不要直接猜接口。优先在已登录页面上下文里复用播放器已请求过的 `x/player/wbi/v2`。

示例：

```bash
curl -s -X POST "http://localhost:3456/eval?target=<TARGET_ID>" -d '(async()=>{
  const list = performance.getEntriesByType("resource").map(r => r.name);
  const url = list.find(n => n.indexOf("/x/player/wbi/v2") >= 0);
  const resp = await fetch(url, { credentials: "include" });
  const j = await resp.json();
  const sub = (j?.data?.subtitle?.subtitles || [])[0];
  return JSON.stringify({
    bvid: window.__INITIAL_STATE__?.bvid,
    title: window.__INITIAL_STATE__?.videoData?.title || document.querySelector("h1")?.textContent?.trim() || "",
    subtitle_url: sub ? `https:${sub.subtitle_url}` : null,
    need_login_subtitle: j?.data?.need_login_subtitle
  }, null, 2);
})()'
```

## 关键判断

- `subtitle_url != null`：直接下载字幕 JSON
- `need_login_subtitle: false`：通常已经拿到了可下载链接
- `subtitle_url == null`：该视频可能没有字幕轨，需要考虑音频转写

## 3. 下载字幕 JSON

拿到 `subtitle_url` 后直接下载：

```bash
curl -s '<SUBTITLE_URL>'
```

如需保存到本地：

```bash
curl -s '<SUBTITLE_URL>' > ./data/<name>.json
```

## 4. 转纯文本

用脚本把 `body[].content` 拼起来，生成可读语料：

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/subtitle_json_to_text.py" \
  ./data/example.json \
  --output ./data/example.txt
```

批量模式：

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/subtitle_json_to_text.py" \
  ./data/*.json \
  --merge-output ./data/corpus.txt
```

## 输出建议

做调研时，建议同时保留三层产物：

1. 原始字幕 JSON
2. 清洗后的纯文本
3. 调研 markdown，总结：
   - 代表句式
   - 高频表达
   - AI 字幕误差
   - 可直接引用的口播片段

## 已验证的事实

- B 站播放器接口 `x/player/wbi/v2` 在登录态页面上下文里可读到 `subtitle.subtitles[].subtitle_url`
- `subtitle_url` 指向 `aisubtitle.hdslb.com`
- 字幕 JSON 结构核心字段是：

```json
{
  "body": [
    { "from": 0.0, "to": 1.2, "content": "..." }
  ]
}
```

## 注意事项

- AI 字幕会有错字，例如音译地名、专有名词、英文段落识别错误
- 语料分析时要把“表达特征”和“字幕识别误差”分开
- `auth_key` 有时效，拿到链接后尽快下载
- 不要把 shell 里的 `!` 直接放进 zsh 表达式里，容易被 history expansion 破坏；复杂 `eval` 优先用 `bash`
