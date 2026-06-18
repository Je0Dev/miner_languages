# 01 — Pipeline Module

**`src/miner/pipeline/`** — `mine.py`, `quick.py`, `batch.py`, `__init__.py`

Orchestrates the full mining flow. Each file is a different mining mode: standard (region select), quick (full-screen), and batch (folder of images).

## What each file does

### `mine.py` — Standard mining with region selection

| Function | What it does |
|----------|-------------|
| `mine_sentence(ocr_lang, translate_to, audio_duration, source_name, auto_clipboard, push_anki, long_text, zone_name, split_sentences_flag)` | The main mining pipeline. Creates session dir, captures region, OCRs, cleans text, checks duplicates, translates, records audio, saves entry + Anki CSV + universal log + sentence server, copies to clipboard, notifies. Returns list of entries (one per sentence). |
| `mine_multi_region(ocr_lang, translate_to, audio_duration, source_name, auto_clipboard, long_text, zones)` | Mines multiple zones sequentially. If no zones given, does interactive selection. Combines all text, then mines as one. |
| `_mine_single(text, ocr_lang, translate_to, source_name, audio_duration, ts, sd, af, split)` | Mines a single text block. Optionally splits into sentences. Calls translate, pronunciation, word breakdown for each. |
| `_save_entry(entry, sd, ts)` | Saves entry to session `entry.json`, appends to `sentences.json` and `history_sentences.txt`. |
| `_append_to_anki_csv(entry)` | Appends one row to `anki_export.csv` with all fields + word breakdown. Creates header if file doesn't exist. |
| `send_to_server(entry)` | Sends entry to Flask sentence server at `localhost:5002/api/add` (non-blocking, fails silently). |

**Full pipeline:**

```
mine_sentence()
  │
  ├── Create session dir: mining/YYYYMMDD_HHMMSS/
  ├── capture_region() → user selects region → screenshot.png
  ├── ocr_image() → raw text
  ├── clean_text() + filter_garbage() + normalize_repeating_chars() + remove_line_duplicates()
  ├── apply_text_processing() (user's replacement rules)
  ├── is_valid_text() → reject if garbage
  ├── is_duplicate() + compare_ocr_results() → reject if seen before
  ├── record_audio() → audio.mp3
  ├── translate_text() → English
  ├── get_pronunciation() → pinyin/romaji
  ├── get_word_breakdown() → per-word split
  ├── split_sentences() → mine each separately
  ├── _save_entry() → entry.json + sentences.json + history.txt
  ├── _append_to_anki_csv() → anki_export.csv
  ├── send_to_server() → Flask API
  ├── copy_to_clipboard() → wl-copy
  └── notify-send() → desktop notification
```

### `quick.py` — Instant full-screen capture

| Function | What it does |
|----------|-------------|
| `quick_capture(ocr_lang, translate_to, source_name, auto_clipboard, zone_name, long_text)` | Same as mine_sentence but uses `grim` directly for full-screen capture (no slurp). For fast NPC dialogue. Saves to `quick_YYYYMMDD_HHMMSS/` dirs. |
| `send_to_server(entry)` | Same as mine.py's. |

When run as a standalone script (`python quick.py -l zh`), it parses CLI args and calls `quick_capture()` directly. Uses `grim` without `slurp` — instant.

### `batch.py` — Batch process image directory

| Function | What it does |
|----------|-------------|
| `batch_process(image_dir, lang, translate_to)` | Scans dir for `*.png` and `*.jpg`, OCRs each, translates, gets pronunciation, saves to `sentences.json`. Returns list of entries. |

### `__init__.py`

Empty — no re-exports. Callers import directly:
```python
from miner.pipeline.mine import mine_sentence, mine_multi_region
from miner.pipeline.quick import quick_capture
from miner.pipeline.batch import batch_process
```

## Session directory structure

```
mining/
├── sentences.json           # All sentences ever mined (master list)
├── anki_export.csv          # Anki-compatible CSV
├── history_sentences.txt    # Plain text log
├── universal_log.txt        # Detailed per-capture log
├── universal_log.json       # Same data as JSON
├── stats.json               # Mining statistics
├── sentences.db             # SQLite database (Flask server)
├── zones.json               # Saved capture zones
├── game_profiles.json       # Per-game config profiles
├── text_replacements.json   # User's replacement rules
│
├── 20250101_120000/         # Session from mine_sentence
│   ├── images/capture.png
│   ├── audio/audio.mp3
│   └── entry.json
│
└── quick_20250101_120001/   # Session from quick_capture
    ├── images/capture.png
    └── entry.json
```
