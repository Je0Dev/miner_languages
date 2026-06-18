# User Interfaces

Provides three distinct user interfaces: a Tkinter live OCR overlay (primary), Flask web dashboards (secondary), and a Tkinter hover overlay (for Yomitan integration).

## Files

### `overlay.py` — Live OCR Overlay (Primary UI)

Depends on: `config`, `ocr`, `translate`, `text`, `text/replace`, `stability`, `dictionary`, `profiles`, `multiline`, `storage/universal_log`, `coordinates`

Class: **`LiveOCROverlay`**

A draggable Tkinter window for interactive sentence mining. This is the most feature-rich interface.

**UI Components:**
- **Select Region** button — launches `slurp` to choose capture area
- **Start/Stop Live** toggle — begins auto-OCR loop at 2-second intervals
- **Text display** — editable text widget showing OCR output
- **Translation display** — editable translation widget
- **Pronunciation area** — shows pinyin/romaji + word breakdown with dictionary definitions
- **Language selector** — radio buttons for all 10 languages
- **Mine button** — saves current text + translation + audio
- **Split Preview** — shows how text will split into multiple entries
- **Discard button** — clears current capture
- **Auto-hide** — window hides after 10 seconds of inactivity

**Key Methods:**

| Method | Description |
|--------|-------------|
| `__init__(ocr_lang, translate_to, source_name)` | Auto-detects game via window class, loads profile, builds UI. |
| `_select_region()` | Launches `slurp`, stores geometry, flash overlay corner to confirm. |
| `_toggle_live()` | Starts/stops the auto-OCR timer loop. |
| `_start_loop()` | Timer callback: captures region → OCR → translate → update display. Uses `MSSIMStabilityDetector` to skip OCR during animations. Uses `MultiLineBuffer` to merge consecutive OCR results. |
| `_update_text(text, tr, pron)` | Updates the UI widgets with new OCR results. |
| `_mine()` | Saves current entry: writes to files, records audio, notifies. |
| `_update_lang()` | Called when language changes; updates OCR/translation language. |

### `dashboard.py` — Stats Dashboard

Depends on: `config`, `stats`

| Function | Description |
|----------|-------------|
| `run_dashboard(port)` | Starts Flask server (default port 5001) showing mining statistics: total mined, OCR failures, per-language breakdown, recent activity. Single-page HTML with dark theme. |

### `web_viewer.py` — Sentence Browser

Depends on: `config`, `text`

| Function | Description |
|----------|-------------|
| `index()` | Main page: table of all mined sentences with search and language filter. |
| `get_sentences()` | JSON endpoint returning filtered/paginated sentence list. |
| `export_csv()` | Download all sentences as Anki-compatible CSV. |

A single-page Flask app (port 5000) for browsing mined sentences with search/filter and CSV export.

### `hover.py` — Yomitan Hover Overlay

Depends on: `ocr`, `translate`, `text`, `config`, `log`

A small semi-transparent Tkinter window (250x60px) that OCRs whatever screen area it covers, copies the text to clipboard, and sends it to the Yomitan sentence server. Designed for use with the Yomitan browser extension — hover over game text, and Yomitan automatically shows the definition.

### `debug_monitor.py` — Yomitan Debug Monitor

Depends on: `config`

A Tkinter window showing real-time OCR/translation/clipboard activity from the Yomitan hover tool. Reads from `yomitan_clipboard.json` and `yomitan_debug.log`. Useful for debugging Yomitan integration.

### How They Connect

- `main.py` dispatches to overlay (`--live`), dashboard (`--dashboard`), web_viewer (via server)
- `scripts/mine.sh` with `--live` flag launches the overlay
- `scripts/yomitan-hover.sh` launches the hover overlay
- All UIs share the same core services (capture, OCR, translate, text, storage)
