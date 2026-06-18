# Pipeline

Orchestrates the full mining workflow: capture → OCR → text processing → translation → save. These are the "main" functions that tie all the subsystems together.

## Files

### `mine.py` — Core Mining

Depends on: `config`, `text`, `text/replace`, `ocr`, `translate`, `capture`, `zones`, `compare`, `storage/universal_log`, `log`

| Function | Description |
|----------|-------------|
| `mine_sentence(ocr_lang, translate_to, audio_duration, source_name, auto_clipboard, push_anki, long_text, zone_name)` | Full mining pipeline: slurp select region → capture PNG → OCR → clean text → check duplicate → translate → get pronunciation → save entry.json → append to sentences.json → append to anki_export.csv → log → record audio → copy to clipboard → notify. This is the primary entry point for most mining. |
| `mine_multi_region(ocr_lang, translate_to, ...)` | Mines multiple saved zones in sequence. Captures each zone, OCRs, translates, and saves as separate entries. |

Pipeline flow:
```
mine_sentence()
  │
  ├── capture_region()              → region PNG, geometry
  ├── ocr_image() / ocr_long_text() → raw text
  ├── apply_text_processing()       → replacements
  ├── clean_text() + filter_garbage → clean text
  ├── is_duplicate()                → skip if already mined
  ├── split_sentences()             → optionally split into entries
  ├── translate_text()              → translation
  ├── get_pronunciation()           → pinyin/romaji
  ├── get_word_breakdown()          → word segmentation
  │
  ├── _save_entry()                 → entry.json + sentences.json + history.txt
  ├── _append_to_anki_csv()         → anki_export.csv
  ├── log_capture()                 → universal_log.json + .txt
  ├── record_audio()                → MP3
  ├── copy_to_clipboard()           → wl-copy
  ├── send_to_server()              → POST to sentence_server if running
  └── notify()                      → desktop notification
```

### `quick.py` — Instant Full-Screen Capture

Depends on: `config`, `ocr`, `translate`, `text`, `text/replace`, `zones`, `storage/universal_log`, `stats`, `log`

| Function | Description |
|----------|-------------|
| `quick_capture(ocr_lang, translate_to, ...)` | Same as `mine_sentence` but uses full-screen capture (no region selection). Designed for fast NPC dialogue where the entire screen contains the text. |

### `batch.py` — Directory Processing

Depends on: `config`, `ocr`, `translate`, `text`, `log`

| Function | Description |
|----------|-------------|
| `batch_process(image_dir, lang, translate_to)` | Processes all PNG/JPG images in a directory through OCR + translate. Returns list of entry dicts. Useful for batch-importing existing screenshots. |

### How They Connect

Used by:
- `main.py` — dispatches to `mine_sentence()`, `mine_multi_region()`, or `quick_capture()` based on CLI args
- Shell scripts (`scripts/mine.sh`, `scripts/quick.sh`) — invoke via `python -m miner`

### Entry Format

Each mined sentence produces an entry dict:
```python
{
  "sentence": str,      # cleaned OCR text
  "translation": str,   # translated text
  "audio": str,         # path to MP3 (relative to MINING_DIR)
  "pronunciation": str, # pinyin/romaji
  "lang": str,          # language code (zh, ja, etc.)
  "source": str,        # game name or "Clipboard"
  "timestamp": str,     # YYYYMMDD_HHMMSS
  "screenshot": str,    # path to captured PNG
  "words": list,        # word breakdown [{word, pinyin/romaji}]
  "tags": list,         # user-applied tags
  "character": str,     # speaking character name
}
```
