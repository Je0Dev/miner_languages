# 01 — Storage Module

**`src/miner/storage/`** — `server.py`, `anki.py`, `export.py`, `universal_log.py`, `__init__.py`

Handles everything related to saving and viewing mined sentences: SQLite database with Flask web server, Anki CSV export, JSON export, and the universal log.

## What each file does

### `server.py` — Flask web API + viewer

A Flask server that stores mined sentences in SQLite and serves them through web pages and Yomitan-compatible API endpoints.

**Database:** `mining/sentences.db` (SQLite, auto-created)

**Tables:**
- `sentences` — id, timestamp, lang, original, translation, pronunciation, source, audio_path, screenshot_path, mode, words (JSON), tags (JSON), character
- `glossary` — id, lang, term, translation (unique per lang+term)

**Web pages (rendered with inline HTML templates):**

| Route | What it shows |
|-------|-------------|
| `/` | Browse sentences. Search/filter by lang/tag. Study mode (hides translations). Delete. Export CSV. |
| `/bridge` | Yomitan Bridge page. Look up words (definition + pronunciation), find sentences containing a term. WebSocket connection status. |

**API endpoints:**

| Route | Method | What it does |
|-------|--------|-------------|
| `/api/sentences` | GET | List sentences with limit/lang/search/offset |
| `/api/sentences/<id>` | GET | Get single sentence |
| `/api/sentences/<id>` | DELETE | Delete sentence |
| `/api/add` | POST | Add new sentence (JSON body) |
| `/api/stats` | GET | Total count + per-language breakdown |
| `/api/yomitan/find` | POST | Find sentences containing a term (Yomitan format) |
| `/api/yomitan/term` | POST | Look up term in glossary (Yomitan format) |
| `/api/yomitan/recent` | GET | Recent sentences by lang |
| `/api/dictionary` | GET | Word definitions + breakdown |
| `/api/export/csv` | GET | Download all as CSV |

| Internal function | What it does |
|-----------------|-------------|
| `init_db()` | Creates tables + adds missing columns |
| `add_sentence(...)` | Inserts row, returns row ID |
| `get_sentences(limit, lang, search, offset)` | Query with filters |
| `get_sentence_by_id(sid)` | Single row lookup |
| `run_server(port)` | Starts Flask on `127.0.0.1:5002` |

### `anki.py` — Anki CSV export

| Function | What it does |
|----------|-------------|
| `export_to_anki_csv(path)` | Reads `sentences.json`, writes all entries to Anki CSV with header. Fields: Sentence, Translation, Pronunciation, Audio, Source, Timestamp, Language. Returns count exported. |
| `append_to_anki_csv(entry, path)` | Appends a single entry. Creates header if file doesn't exist. Checks pronunciation field first, falls back to regenerating it. |

### `export.py` — JSON + Excel export

| Function | What it does |
|----------|-------------|
| `export_json(path)` | Dumps `sentences.json` to a separate export file. |
| `export_excel(path)` | Writes Excel-compatible CSV with BOM (UTF-8-SIG) and fields: Language name, Sentence, Pronunciation, Translation, Source, Timestamp, Audio. |
| `get_audio_files()` | Lists all `.mp3` files in `mining/audio/`. |

### `universal_log.py` — Plain-text + JSON logging

| Function | What it does |
|----------|-------------|
| `log_capture(sentence, translation, pronunciation, source, lang, audio)` | Writes a formatted entry to `universal_log.txt` (readable plain text with `====` separators) and appends to `universal_log.json` (structured JSON array). |

### `__init__.py`

Empty — callers import directly:
```python
from miner.storage.server import run_server, add_sentence
from miner.storage.anki import export_to_anki_csv
from miner.storage.export import export_json
from miner.storage.universal_log import log_capture
```
