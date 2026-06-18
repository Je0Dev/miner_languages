# Game Sentence Miner

A Wayland-native (Hyprland) language learning sentence mining toolkit for gamers. Capture on-screen text from games — press a key, select a region, and the tool OCRs the text, translates it, records audio, copies to clipboard, and saves everything for Anki import.

## Quick Start

```bash
# Check dependencies are installed
python main.py --health

# Quick capture — select region with crosshair, get OCR + translate + audio
bash scripts/mine.sh -l zh -t en

# Live OCR overlay — draggable window, auto-OCRs every 2s, mine button
bash scripts/mine.sh --live -l zh -t en

# Yomitan hover — semi-transparent window, drag over text, auto-OCR + clipboard
bash scripts/yomitan-hover.sh chi_sim
```

## How It Works

The project is a pipeline of modular stages. Each stage is a separate subpackage under `src/miner/`:

```
       Keybind
          │
          ▼
  ┌────────────────┐
  │ scripts/       │  Shell wrappers that set PYTHONPATH and dispatch to Python
  │ mine.sh        │
  └────────┬───────┘
           │
  ┌────────▼───────┐
  │ main.py        │  argparse CLI entry point — dispatches to the right module
  │ (CLI)          │  based on flags: --live, --bridge, --health, etc.
  └────────┬───────┘
           │
  ┌────────▼───────┐
  │ pipeline/      │  Orchestrates the full mining flow:
  │ mine.py        │  1. capture_region()  → grim + slurp screenshot
  │ quick.py       │  2. ocr_image()       → Tesseract OCR
  │ batch.py       │  3. clean_text()      → sanitize + validate
  └────────┬───────┘  4. translate_text() → Google Translate
           │          5. get_pronunciation() → pinyin/romaji
           │          6. record_audio()    → ffmpeg MP3
           │          7. _save_entry()     → sentences.json
           │          8. _append_to_anki_csv() → Anki CSV
           │          9. copy_to_clipboard() → wl-copy
           │          10. notify()         → desktop notification
           │
           │  ┌──────────────┐  ┌──────────────┐
           │  │ capture/     │  │ ocr/          │
           │  │ grim + slurp │─▶│ Tesseract     │
           │  │ display scale│  │ ± EasyOCR     │
           │  └──────────────┘  │ ± confidence  │
           │                    └──────┬───────┘
           │                           │
           │  ┌──────────────┐  ┌──────▼───────┐
           │  │ translate/   │  │ text/         │
           │  │ Google       │◀─│ cleaning      │
           │  │ ± parallel   │  │ validation    │
           │  │ ± fallback   │  │ pinyin/romaji │
           │  └──────────────┘  │ segmentation  │
           │                    │ duplicates    │
           │                    └──────────────┘
           │
           ▼
  ┌────────────────┐
  │ storage/       │  sentences.json, anki_export.csv, universal_log
  │ server.py      │  Optional Flask + SQLite API for browsing
  └────────────────┘
```

**Separate UIs** run alongside the pipeline:
- **`ui/overlay.py`** — Tkinter window: select region, auto-OCR loop, edit text, add word definitions, mine with audio
- **`ui/hover.py`** — Tiny Tkinter window that OCRs whatever it covers, copies to clipboard for Yomitan
- **`yomitan/bridge.py`** — WebSocket server that Yomitan browser extension connects to for finding mined sentences and word definitions

## Workflows

### Quick Capture — `SUPER+X`
The default mining mode. Press the keybinding, a crosshair appears for you to drag-select any screen region. The tool captures the screenshot, runs Tesseract OCR, cleans the text, translates it (default: Chinese → English), looks up pronunciation, records 5 seconds of game audio via ffmpeg, copies the text to your clipboard, and saves everything. A desktop notification shows you the result.

### Live OCR Overlay — `SUPER+O`
Opens a frameless Tkinter window. Click "Select Region" to choose what area of the screen to monitor, then click "Start Live". The overlay auto-OCRs that region every 2 seconds, showing the raw text and translation in editable text boxes. It uses MSSIM stability detection to skip OCR during animations and a multi-line buffer to merge consecutive captures. Click "Mine" to save the current text with audio. The overlay supports all 10 languages, word-by-word breakdown with dictionary definitions (Chinese CC-CEDict, Japanese Jisho), per-game profiles (auto-detects the game window and loads its settings), and auto-hides after inactivity.

### Quick Instant Capture — `SUPER+ALT+CTRL+Q`
Same as quick capture but no region selection — captures the full screen immediately. Designed for fast NPC dialogue where the entire screen contains text. Bound per-language like quick capture.

### Extended Capture — `SUPER+CTRL+E`
Same as quick capture but records 15 seconds of audio instead of 5. Useful for dialogue sequences.

### Yomitan Hover — `SUPER+Y`
Opens a tiny 250x60px semi-transparent Tkinter window. Drag this window over any text on screen — it auto-OCRs every 2 seconds and copies the result to your clipboard. If you have the Yomitan browser extension open, Yomitan picks up the clipboard text and shows dictionary definitions automatically.

### Sentence Server — `SUPER+CTRL+V`
Starts a Flask web server at `http://localhost:5002` with a SQLite database. Browse all mined sentences, search by term or language, download as CSV. Also serves Yomitan-compatible API endpoints (`/api/yomitan/find`, `/api/yomitan/term`) and a bridge web page at `/bridge`.

### Yomitan Bridge — `SUPER+CTRL+J`
Starts a WebSocket server on port 8766. The `bridge.js` content script connects to it from your browser, enabling Yomitan to search your mined sentence collection and look up word definitions directly from the tool's dictionaries.

### Clipboard Monitor — `SUPER+CTRL+C`
Polls the Wayland clipboard every 0.5 seconds. When new text appears, auto-detects the language, translates it, and saves it as a mined sentence. Useful for capturing text from sources that don't need OCR (e.g. visual novels with text extraction).

### Health Check — `SUPER+CTRL+H`
Verifies all dependencies are installed: grim, slurp, tesseract, ffmpeg, wl-copy, PulseAudio sources.

### Statistics — `SUPER+CTRL+S`
Shows mining stats: total sentences mined, OCR failures, translation failures, per-language breakdown, average confidence.

### Backup — `SUPER+CTRL+B`
Creates a timestamped backup of all data files (sentences.json, anki_export.csv, universal_log) in `mining/backups/`. Keeps the last 10 backups.

### Kill All — `SUPER+CTRL+K`
Kills all running miner-v2 and yomitan-hover processes.

## Hyprland Keybindings

To use the keybindings, add this line to your `~/.config/hypr/hyprland.conf`:

```
source = ~/miner-v2/scripts/mining_bindings.conf
```

### Quick Capture — Region Select + OCR + Translate + Audio

| Keybinding | Language |
|------------|----------|
| `SUPER` + `X` | Chinese → English |
| `SUPER` + `SHIFT` + `X` | Japanese → English |
| `SUPER` + `ALT` + `X` | German → English |
| `SUPER` + `CTRL` + `X` | Korean → English |
| `SUPER` + `ALT` + `SHIFT` + `X` | Spanish → English |
| `SUPER` + `CTRL` + `ALT` + `X` | Greek → English |
| `SUPER` + `CTRL` + `ALT` + `SHIFT` + `X` | French → English |
| `SUPER` + `ALT` + `CTRL` + `M` | Polish → English |
| `SUPER` + `ALT` + `CTRL` + `SHIFT` + `M` | Russian → English |
| `SUPER` + `CTRL` + `SHIFT` + `M` | English → English |

### Extended Capture — 15s Audio for Dialogue Sequences

| Keybinding | Language |
|------------|----------|
| `SUPER` + `CTRL` + `E` | Chinese |
| `SUPER` + `CTRL` + `SHIFT` + `E` | Japanese |
| `SUPER` + `CTRL` + `ALT` + `E` | German |
| `SUPER` + `CTRL` + `ALT` + `SHIFT` + `E` | Korean |

### Quick Instant Capture — Full Screen (No Region Select)

| Keybinding | Language |
|------------|----------|
| `SUPER` + `ALT` + `CTRL` + `Q` | Chinese |
| `SUPER` + `ALT` + `CTRL` + `SHIFT` + `Q` | Japanese |
| `SUPER` + `CTRL` + `SHIFT` + `Q` | German |
| `SUPER` + `CTRL` + `ALT` + `Q` | Korean |

### Live OCR Overlay — Draggable Auto-OCR Window

| Keybinding | Language |
|------------|----------|
| `SUPER` + `O` | Chinese |
| `SUPER` + `SHIFT` + `O` | Japanese |
| `SUPER` + `ALT` + `O` | German |
| `SUPER` + `CTRL` + `O` | Korean |
| `SUPER` + `ALT` + `SHIFT` + `O` | Spanish |
| `SUPER` + `CTRL` + `ALT` + `O` | Greek |

### Yomitan Hover — OCR + Clipboard for Yomitan

| Keybinding | Language |
|------------|----------|
| `SUPER` + `Y` | Chinese (chi_sim) |
| `SUPER` + `SHIFT` + `Y` | Japanese (jpn) |
| `SUPER` + `ALT` + `Y` | German (deu) |
| `SUPER` + `CTRL` + `Y` | Korean (kor) |

### Utilities

| Keybinding | Action |
|------------|--------|
| `SUPER` + `CTRL` + `K` | Kill all miner processes |
| `SUPER` + `CTRL` + `H` | Show health check notification |
| `SUPER` + `CTRL` + `S` | Show mining stats notification |
| `SUPER` + `CTRL` + `B` | Create backup |
| `SUPER` + `CTRL` + `D` | Open Yomitan debug monitor |
| `SUPER` + `CTRL` + `V` | Start sentence server |
| `SUPER` + `CTRL` + `J` | Start Yomitan WebSocket bridge |
| `SUPER` + `CTRL` + `W` | Start sentence server + bridge + open browser |
| `SUPER` + `CTRL` + `C` | Start clipboard monitor |
| `SUPER` + `ALT` + `P` | Live OCR with parallel translation (Chinese) |
| `SUPER` + `ALT` + `SHIFT` + `P` | Live OCR with parallel translation (Japanese) |

## Project Structure

```
miner-v2/
├── main.py                    # Thin entry point — adds src/ to path, calls src/miner/main.py
├── pyproject.toml             # Package metadata + dependency list
├── requirements.txt           # pip installable dependencies
│
├── scripts/                   # Shell wrappers and Hyprland config
│   ├── mine.sh                # Quick capture / live OCR dispatcher
│   ├── quick.sh               # Full-screen instant capture dispatcher
│   ├── sentence_server.sh     # Flask API server launcher with PID management
│   ├── yomitan-hover.sh       # Hover overlay launcher with language mapping
│   └── mining_bindings.conf   # Complete Hyprland keybinding configuration
│
├── src/miner/                 # All Python source code
│   ├── main.py                # argparse CLI dispatcher
│   ├── config.py              # Paths, language registry, constants
│   ├── log.py                 # Logging (file + console)
│   │
│   ├── capture/               # Wayland screen capture via grim + slurp
│   ├── ocr/                   # Tesseract OCR + EasyOCR fallback + confidence scoring
│   ├── text/                  # Text cleaning, validation, pinyin, word segmentation
│   ├── translate/             # Google Translate + parallel engines + audio recording
│   ├── pipeline/              # Mining orchestration (mine_sentence, quick_capture, batch)
│   ├── storage/               # sentences.json, Anki CSV, Flask API, universal log
│   ├── ui/                    # Tkinter overlays, Flask dashboards, web viewer
│   └── yomitan/               # WebSocket bridge, clipboard monitor, browser content script
│
├── tests/                     # 147 unit tests across all modules
├── mining/                    # Runtime data (sentences, stats, audio, backups)
├── tessdata/                  # Local Tesseract language data
└── docs/                      # Architecture and module documentation
```

## CLI Commands

```bash
python main.py -l zh -t en              # Quick capture (region select)
python main.py -l ja -t en --long-text  # Quick capture, multi-line mode
python main.py --zone intro_zone        # Use a saved capture zone
python main.py --live -l zh -t en       # Live OCR overlay
python main.py --multi-region zone1 zone2  # Mine multiple zones sequentially
python main.py --health                 # Dependency check
python main.py --stats                  # Show mining statistics
python main.py --backup                 # Create data backup
python main.py --list-backups           # List available backups
python main.py --list-zones             # List saved regions
python main.py --save-zone name         # Save current selection as named zone
python main.py --delete-zone name       # Delete a saved zone
python main.py --profiles               # List game profiles
python main.py --detect-game            # Auto-detect current game window
python main.py --export-json            # Export sentences as JSON
python main.py --export-excel           # Export sentences as CSV
python main.py --dashboard              # Start stats web dashboard
python main.py --bridge                 # Start Yomitan WebSocket bridge
python main.py --clipboard              # Start clipboard monitor
python main.py --batch /path/to/images  # Batch OCR images in directory
```

## Dependencies

### System (install via your package manager)
- `grim` — Wayland screenshot utility
- `slurp` — Wayland region selection
- `tesseract` + language packs — OCR engine (install `tesseract-data-*` or use bundled `tessdata/`)
- `ffmpeg` — Audio recording
- `wl-clipboard` — Wayland clipboard (`wl-copy` / `wl-paste`)
- `pipewire` or `pulseaudio` — Audio system

### Python (install via pip)
```
pip install -r requirements.txt
```

Or install the package for development:
```
pip install -e .
miner --health
```

## Supported Languages

| Code | Language | Tesseract Model | Google Code | Script Type | Romanization |
|------|----------|----------------|-------------|-------------|-------------|
| zh | Chinese | chi_sim | zh-CN | CJK | pinyin |
| ja | Japanese | jpn | ja | CJK | romaji |
| ko | Korean | kor | ko | CJK | romanization |
| de | German | deu | de | Latin | — |
| es | Spanish | spa | es | Latin | — |
| fr | French | fra | fr | Latin | — |
| pl | Polish | pol | pl | Latin | — |
| el | Greek | ell | el | Greek | transliteration |
| ru | Russian | rus | ru | Cyrillic | transliteration |
| en | English | eng | en | Latin | — |


## Special Credits

This project is a rewrite and combination of concepts from two outstanding open-source projects:

**GameSentenceMiner** — Contributed the core mining workflow design, Yomitan WebSocket bridge architecture and some other things not too good to explain here really.

**LunaTranslator** — Contributed also to this nice simple personal project.


The architecture, module structure, and implementation in this repository were done mostly with their original work (unless otherwise noted in individual file headers). Neither GameSentenceMiner nor LunaTranslator are affiliated with or endorse this project(although i personally would not mind of course).


## License

Copyright © 2026 Je0Dev

This project is free for personal and non-commercial use. You may use, modify, and distribute this software for non-commercial purposes only, provided that:

1. **Attribution is required** — Any use, distribution, or derivative work must give appropriate credit to the original author (Je0Dev), GameSentenceMiner, and LunaTranslator. This includes any application, website, or product that incorporates or is derived from this code.

2. **Commercial use is prohibited without permission** — You may not use this software, in whole or in part, to generate revenue or for any commercial purpose without explicit written permission from the author. This includes but is not limited to: selling, licensing, or bundling the software as part of a paid product; using it in a commercial service; or accepting donations specifically for this software.

3. **No warranty** — This software is provided "as is" without warranty of any kind, express or implied.

> In other words just keep it Open Source please!


---


