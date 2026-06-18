# Translation

Handles text translation, audio recording, clipboard operations, and desktop notifications. The primary engine is Google Translate via `deep-translator`, with fallback and parallel engine options.

## Files

### `translate.py` — Primary Engine

Depends on: `config`, `log`

| Function | Description |
|----------|-------------|
| `translate_text(text, src, dest)` | Translates via Google Translate (`deep-translator`). Pre-cleaning strips whitespace and rejects garbage. Returns empty string for invalid input or translation failure. |
| `record_audio(output_path, duration, source)` | Records system audio via `ffmpeg` from PulseAudio. Auto-detects best audio source (HDMI monitor, analog stereo). Saves as MP3. Returns success boolean. |
| `copy_to_clipboard(text)` | Copies text to Wayland clipboard via `wl-copy`. |
| `notify(title, body, timeout)` | Sends desktop notification via `notify-send`. |

### `parallel.py` — Multi-Engine Translation

Depends on: `config`, `log`

| Function | Description |
|----------|-------------|
| `translate_parallel(text, src, dest)` | Runs Google + LibreTranslate + MyMemory simultaneously via `ThreadPoolExecutor`. Returns the result with the closest length match to the source text. Each engine has a 5-second timeout. |

### `fallback.py` — Fallback Chain

Depends on: `config`, `log`

| Function | Description |
|----------|-------------|
| `translate_text(text, src, dest)` | Drop-in replacement for `translate.translate_text`. Tries Google first; if that fails, falls back to LibreTranslate (self-hosted or public API). |

### How They Connect

Used by:
- `pipeline/mine.py` — `translate_text` for translation, `record_audio` for audio, `copy_to_clipboard` for clipboard
- `pipeline/quick.py` — same set
- `pipeline/batch.py` — `translate_text` only
- `ui/overlay.py` — all four functions; also uses `translate_parallel` for multi-engine mode
- `ui/hover.py` — `translate_text`, `copy_to_clipboard`, `notify`
- `yomitan/bridge.py` — `translate_text`
- `yomitan/clipboard.py` — `translate_text`, `notify`

### Translation Pipeline

```
received text
  → clean_for_translation (strip whitespace, normalize)
  → is_valid_for_translation (reject empty, garbage, single chars)
  → translate via Google (deep-translator)
  → clean_translation (strip leading/trailing whitespace)
  → return result (or empty string on failure)
```

### Audio Pipeline

```
record_audio(path, duration)
  → enumerate PulseAudio sources via pactl
  → find best source (prioritize monitor sources)
  → run ffmpeg: parec → mp3 (64kbps, 22kHz)
  → return success/failure
```

### Language Support

Translation maps short codes to Google language codes via `config.LANG_REGISTRY`:
- `zh` → `zh-CN`, `ja` → `ja`, `ko` → `ko`, `de` → `de`, etc.
- All 10 supported languages can translate to any language Google supports (typically English).
