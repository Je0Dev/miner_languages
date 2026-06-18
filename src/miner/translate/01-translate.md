# 01 — Translate Module

**`src/miner/translate/`** — `translate.py`, `parallel.py`, `fallback.py`, `__init__.py`

Translates text (Google Translate via `deep-translator`), records game audio via `ffmpeg`, copies to Wayland clipboard via `wl-copy`, and sends desktop notifications via `notify-send`.

## What each file does

### `translate.py` — Core translate + utilities

| Function | What it does |
|----------|-------------|
| `translate_text(text, src, dest)` | Cleans text before translation (remove garbage per script), runs Google Translate via `deep_translator`, cleans result to ASCII-only for English output. Caches results (max 1000). |
| `record_audio(path, duration, source)` | Finds best PulseAudio monitor source (`pactl list short sources`), tests it with ffmpeg, then records MP3 via `ffmpeg -f pulse -i source -acodec libmp3lame`. Returns gracefully if no audio source (doesn't crash). |
| `copy_to_clipboard(text)` | Pipes text to `wl-copy` for Wayland clipboard. |
| `notify(title, body, timeout)` | Runs `notify-send` with title, body, and timeout. |
| `_clean_for_translation(text, lang)` | Strips non-matching script chars. For CJK: keeps only CJK + CJK punctuation. Rejects if <50% valid chars. |
| `_is_valid_for_translation(text, lang)` | Checks min 2 script-specific chars, ≥60% script chars. Latin: needs ≥2 words or accents. |
| `_find_best_audio_source()` | Finds PulseAudio monitor source (the one that captures desktop audio). |
| `_test_audio_source(source)` | Quick ffmpeg test to check if the source is working. |

### `parallel.py` — Multi-engine parallel translation

| Function | What it does |
|----------|-------------|
| `translate_google(text, src, dest)` | Google Translate via `deep_translator`. |
| `translate_libre(text, src, dest)` | LibreTranslate via `curl POST` to `localhost:5000`. |
| `translate_mymemory(text, src, dest)` | MyMemory API via `urllib.request` (free, no auth). |
| `translate_parallel(text, src, dest, engines)` | Runs all 3 engines in separate threads (daemon), waits up to 8 seconds, ranks results by length similarity to source (closer to 1.5× source length = better). Returns `{results, best, all}`. |
| `translate_text(text, src, dest, parallel)` | Top-level. If `parallel=True` uses multi-engine, otherwise Google only. Caches both. |

### `fallback.py` — Graceful degradation

| Function | What it does |
|----------|-------------|
| `translate_libretranslate(text, src, dest)` | LibreTranslate via `curl`. |
| `translate_with_fallback(text, src, dest)` | Tries Google first. If that fails, falls back to LibreTranslate. If both fail, returns empty string. |

### `__init__.py`

Exports from `translate.py`: `translate_text`, `copy_to_clipboard`, `record_audio`, `notify`, `_is_valid_for_translation`, `_find_best_audio_source`, `_clean_translation`, `_clean_for_translation`

## Audio recording flow

```
record_audio(path, 5)
  │
  ├── _find_best_audio_source()
  │     pactl list short sources → find "monitor" source
  │
  ├── _test_audio_source(source)
  │     ffmpeg -t 1 -f pulse -i source → test
  │
  └── ffmpeg -y -f pulse -i source -t 5 -acodec libmp3lame -q:a 2 out.mp3
        │
        └── Waits in 1-second sleeps for duration seconds
```

## Translation quality checks

Before sending text to Google Translate, `_clean_for_translation()` and `_is_valid_for_translation()` filter out garbage:
- CJK text must be ≥50% CJK characters and have ≥2 CJK chars
- Greek text must be ≥50% Greek characters
- Latin text needs ≥2 words or accented characters
- Result is cleaned to ASCII-only for English translation
