# Storage

Persists mined sentences and supporting data to disk. Supports multiple output formats and a Flask web API for runtime access.

## Files

### `server.py` — Flask + SQLite API

Depends on: `config`, `dictionary`

| Function | Description |
|----------|-------------|
| `run_server(port)` | Starts Flask app on given port (default 5002). |
| `add_sentence(original, lang, translation, ...)` | Inserts into SQLite. |
| `api_add()` | POST endpoint `/api/add` — accepts JSON with `original`, `lang`, `translation`, etc. |
| `api_sentences()` | GET `/api/sentences` — list sentences with pagination, language filter, search. |
| `api_sentence(sid)` | GET `/api/sentences/<id>` — single sentence detail. |
| `api_stats()` | GET `/api/stats` — aggregate statistics. |
| `yomitan_find()` | POST `/api/yomitan/find` — find sentences containing a term (for Yomitan browser extension). |
| `yomitan_term()` | POST `/api/yomitan/term` — get word definitions (for Yomitan). |
| `yomitan_recent()` | GET `/api/yomitan/recent` — most recent sentences. |
| `export_csv()` | GET `/api/export/csv` — download all as CSV. |
| `bridge_page()` | GET `/bridge` — Yomitan bridge web interface. |

### `universal_log.py` — Dual-Format Log

Depends on: `config`

| Function | Description |
|----------|-------------|
| `log_capture(sentence, translation, pronunciation, source, lang, audio)` | Appends to both `universal_log.txt` (human-readable formatted) and `universal_log.json` (machine-readable). Each entry includes timestamp, language, source, and all text fields. |

### `export.py` — JSON/CSV Export

Depends on: `config`, `text`, `log`

| Function | Description |
|----------|-------------|
| `export_json(output_path)` | Exports all sentences from `sentences.json` to a separate JSON file. |
| `export_excel(output_path)` | Exports to Excel-compatible CSV (quoted fields, UTF-8 BOM). |

### `anki.py` — Anki CSV Export

Depends on: `config`, `text`, `log`

| Function | Description |
|----------|-------------|
| `export_to_anki_csv(anki_csv_path)` | Exports all sentences to Anki-compatible CSV. Columns: Sentence, Translation, Pronunciation, Audio, Source, Timestamp, Language. Audio field uses `[sound:filename.mp3]` format. |
| `append_to_anki_csv(entry, anki_csv_path)` | Appends a single entry to the Anki CSV. Called by `mine.py` after each capture. |

### Storage Layout

```
mining/
├── sentences.json            # Master list of all entries (JSON array)
├── sentences.db              # SQLite database (server.py, optional)
├── anki_export.csv           # Cumulative Anki CSV
├── history_sentences.txt     # Human-readable one-line-per-entry log
├── universal_log.json        # Machine-readable log
├── universal_log.txt         # Human-readable formatted log
├── stats.json                # Mining statistics
├── zones.json                # Saved capture zones
├── game_profiles.json        # Per-game profiles
├── yomitan_clipboard.json    # Clipboard history
├── miner.log                 # Application log
├── backups/                  # Timestamped backup archives
└── YYYYMMDD_HHMMSS/          # Per-session folders
    ├── entry.json            # Entry metadata
    ├── images/capture.png    # OCR source screenshot
    └── audio/audio.mp3       # Recorded audio
```

### How They Connect

Used by:
- `pipeline/mine.py` — calls `universal_log.log_capture()`, directly writes to `sentences.json` and `anki_export.csv`
- `pipeline/quick.py` — same
- `main.py` — dispatches to `export_json()`, `export_excel()`, `run_server()`
- `scripts/sentence_server.sh` — starts `server.py` as background process
- `ui/overlay.py` — calls `universal_log.log_capture()`
