# Translation · v1.4

## Core behavior

- Original Instruction/Thinking are immutable evidence. Generate Chinese output **before** HTML export.
- The open-source Skill works with no translation backend. Prefer Apple system translation on macOS 26+ (Swift + installed English/Simplified Chinese resources); use `none` elsewhere, or an explicitly user-configured CLI. Never send logs to remote services by default.
- Translation changes should not modify code, commands, paths, identifiers or Markdown code fences. Pure Shell instructions are **preserved as code**, not translated into Chinese commands. Add a separate Chinese description only if supported, without changing the executable string.
- The script protects inline backticks, code fences, paths, filenames, API field names and some Git phrases by splitting into preserved/translated chunks. Preserve whitespace and paragraph breaks; batch requests and retry failed segments independently.
- A protected Git phrase may still result in awkward surrounding Chinese, and system translation can mistranslate technical prose. **The process is a first pass, not a certification of translation correctness.**
- If translation is not trustworthy, retain original and mark unavailable; do not synthesize a "complete translation" from a one-line summary.

## Commands

```bash
python3 scripts/prepare_translations.py --backend apple --self-test 'I should inspect SOUL.md before editing it.'
python3 scripts/prepare_translations.py \
  --input examples/translation-smoke.json --output /tmp/h2o2-zh.json \
  --backend apple --batch-size 20
python3 scripts/quality_check.py --input /tmp/h2o2-zh.json
python3 scripts/render_report.py --input /tmp/h2o2-zh.json --output /tmp/report.html
```

On macOS versions without the headless API, use `--backend none`. `--backend command --command "custom-translator" --cache-namespace translator-v1` is an explicit opt-in command interface (JSON stdin/stdout protocol, see README).

## Caching/privacy

Default cache `~/.cache/h2o2-research-design-html/translation-cache.json`; contains translated text and must be treated as sensitive. Use `--no-cache` for sensitive traces. A hash includes backend and namespace. Cached data persists across report generations. No remote fallback is ever automatic.

## Mac platform notes

`TranslationSession(installedSource:target:)` headless initialization requires macOS 26+ and preinstalled language assets; SwiftPM source is under `scripts/apple-translate/`. The current Linux test environment cannot validate the actual Apple translation runtime; test on the user's Mac. Apple backend only builds Swift when actually requested.

Official API reference: https://developer.apple.com/documentation/translation/translationsession
