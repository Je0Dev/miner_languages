# Architecture

Game Sentence Miner v2 is a modular pipeline: capture screen text → OCR → translate → save. Each stage is a separate subpackage under `src/miner/`.

## High-Level Data Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACES                                │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────┐  ┌────────────┐  │
│  │  mine.sh     │  │  overlay.py   │  │  yomitan-    │  │  sentence  │  │
│  │  (CLI)       │  │  (Live OCR)   │  │  hover.py    │  │  server.py │  │
│  └──────┬───────┘  └───────┬───────┘  └──────┬───────┘  └─────┬──────┘  │
└─────────┼──────────────────┼──────────────────┼────────────────┼─────────┘
          │                  │                  │                │
          ▼                  ▼                  ▼                ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                          PIPELINE LAYER                                  │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  mine.py       │  quick.py       │  batch.py                    │    │
│  │  mine_sentence  │  quick_capture  │  batch_process              │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                          CORE SERVICES                                   │
│                                                                          │
│  ┌──────────┐  ┌──────────┐  ┌────────────┐  ┌─────────────────────┐   │
│  │ capture/ │  │  ocr/    │  │ translate/ │  │ text/               │   │
│  │ grim+    │─▶│ Tesseract│─▶│ Google     │─▶│ cleaning, pinyin,   │   │
│  │ slurp    │  │ EasyOCR  │  │ + fallback │  │ validation, split   │   │
│  └──────────┘  └──────────┘  └────────────┘  └─────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  UTILITY MODULES (top-level in src/miner/)                       │    │
│  │  zones.py ─ profiles.py ─ dictionary.py ─ stability.py ─        │    │
│  │  multiline.py ─ duplicates.py ─ compare.py ─ coordinates.py ─   │    │
│  │  health.py ─ stats.py ─ backup.py ─ auto_detect.py ─           │    │
│  │  preprocess.py                                                  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                          STORAGE LAYER                                   │
│                                                                          │
│  ┌─────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────────────┐  │
│  │ sentences   │  │ anki_export│  │ universal_ │  │ sentence_server  │  │
│  │ .json       │  │ .csv       │  │ log.json   │  │ (Flask + SQLite) │  │
│  └─────────────┘  └────────────┘  └────────────┘  └──────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
```

## Package Structure

```
src/miner/               # All Python source lives here
├── __init__.py          # Package docstring
├── __main__.py          # python -m miner support
├── main.py              # CLI dispatcher (argparse)
├── config.py            # Central configuration (paths, language registry, constants)
├── log.py               # Logging setup (file + console via logging module)
│
├── capture/             # Wayland screen capture
│   ├── __init__.py      # Exports: capture_region, capture_screenshot, get_display_scale, parse_slurp_geom
│   └── capture.py       # grim/slurp implementation
│
├── ocr/                 # OCR engines
│   ├── __init__.py      # Exports: ocr_image, ocr_long_text, prewarm_tesseract, etc.
│   ├── ocr.py           # Tesseract OCR with preprocessing, caching, multi-PSM fallback
│   ├── confidence.py    # Per-word confidence scoring + auto-retry
│   └── easyocr.py       # EasyOCR fallback engine (lazy-loaded)
│
├── text/                # Text processing
│   ├── __init__.py      # Exports: clean_text, sanitize_unicode, get_pronunciation, etc.
│   ├── text.py          # Cleaning, validation, CJK/Latin/Greek/Cyrillic support, jieba/Mecab
│   └── replace.py       # Configurable regex/plain text replacement pipeline
│
├── translate/           # Translation engines
│   ├── __init__.py      # Exports: translate_text, copy_to_clipboard, record_audio, notify
│   ├── translate.py     # Google Translate + ffmpeg audio + wl-copy clipboard + notify-send
│   ├── parallel.py      # Multi-engine parallel translation (Google + Libre + MyMemory)
│   └── fallback.py      # Fallback chain: Google → LibreTranslate
│
├── pipeline/            # Mining pipelines (orchestrates capture → OCR → translate → save)
│   ├── __init__.py
│   ├── mine.py          # mine_sentence() + mine_multi_region() — full pipeline
│   ├── quick.py         # quick_capture() — full-screen fast path
│   └── batch.py         # batch_process() — directory of images
│
├── storage/             # Data persistence
│   ├── __init__.py
│   ├── server.py        # Flask + SQLite: sentence API + Yomitan bridge endpoints + web viewer
│   ├── universal_log.py # Dual-format (JSON + TXT) capture log
│   ├── export.py        # JSON + CSV export from sentences.json
│   └── anki.py          # Anki-compatible CSV export
│
├── ui/                  # User interfaces
│   ├── __init__.py
│   ├── overlay.py       # LiveOCR Tkinter overlay (select region, auto-OCR, edit, mine, split)
│   ├── dashboard.py     # Flask mini-dashboard for mining stats
│   ├── web_viewer.py    # Flask web browser for mined sentences
│   ├── hover.py         # Yomitan floating hover overlay (Tkinter, semi-transparent)
│   └── debug_monitor.py # Yomitan debug Tkinter monitor
│
├── yomitan/             # Yomitan browser extension integration
│   ├── __init__.py
│   ├── bridge.py        # WebSocket server (port 8766) — find sentences, word info, translate
│   ├── bridge.js        # Browser content script — connects to WebSocket, shows popups
│   └── clipboard.py     # Polling clipboard watcher with auto-detect + auto-translate
│
├── zones.py             # Named capture regions (save/load/delete geometry + language)
├── profiles.py          # Per-game config via Hyprland window class detection
├── dictionary.py        # Word lookups: CC-CEDict (Chinese), Jisho (Japanese), Naver (Korean)
├── stability.py         # MSSIM image stability detection (skip OCR during animations)
├── multiline.py         # Thread-safe deque buffer for live OCR text merging
├── coordinates.py       # Coordinate math: ceil/floor to multiples, percentage scaling
├── duplicates.py        # Levenshtein-based duplicate detection
├── compare.py           # Advanced OCR text comparison (evolving prefix, chunk coverage)
├── stats.py             # Mining statistics (sessions, OCR failures, per-language)
├── health.py            # Dependency health checks (grim, slurp, tesseract, ffmpeg, audio)
├── backup.py            # Timestamped backup/restore of sentences.json, anki.csv, logs
├── auto_detect.py       # Edge-density-based text region detection on images
└── preprocess.py        # Advanced image preprocessing (deblur, deskew, adaptive binarize)
```

## Dependency Graph

```
main.py (CLI entry)
  ├── config.py              ← imported by everything
  ├── log.py                 ← imported by everything
  ├── zones.py               uses nothing
  ├── health.py              uses config
  ├── stats.py               uses config, log
  ├── backup.py              uses config, log
  │
  ├── pipeline/mine.py       ← orchestrates capture → ocr → text → translate → storage
  │     uses: capture, ocr, text, text/replace, translate, zones, compare, storage/universal_log
  │
  ├── pipeline/quick.py      ← same as mine but full-screen
  │     uses: capture, ocr, text, text/replace, translate, zones, stats, storage/universal_log
  │
  ├── pipeline/batch.py      ← processes directory of images
  │     uses: ocr, text, translate, storage/universal_log
  │
  ├── ui/overlay.py          ← depends on almost everything
  │     uses: ocr, text, text/replace, translate, stability, dictionary, profiles,
  │            multiline, storage/universal_log, coordinates
  │
  ├── yomitan/bridge.py      uses: config, text, translate, log
  ├── yomitan/clipboard.py   uses: config, text, translate, log
  ├── storage/server.py      uses: config, dictionary
  └── ui/hover.py            uses: ocr, text, translate, config, log

Independent modules (no internal deps beyond config/log):
  coordinates.py, duplicates.py, preprocess.py, auto_detect.py
```

## Entry Points

1. **`main.py` (root)** — Thin 6-line wrapper, adds `src/` to `sys.path`, delegates to `src/miner/main.py`. Supports both `python main.py` and `PYTHONPATH=src python -m miner`.

2. **Shell scripts in `scripts/`** — Each sets `PYTHONPATH`, then calls `python -m miner <command>` or directly invokes a module.

3. **`__main__.py`** — Allows `python -m miner` when package is installed or `PYTHONPATH` is set.

## Config System

`config.py` is the single source of truth:
- **Paths**: `MINING_DIR`, `LOCAL_TESSDATA`, all subdirectory names
- **Language registry**: 10 languages with Tesseract/Google codes, script type, romanization method
- **Timing**: Live OCR interval, audio duration, VAD settings
- **All constants** are module-level, imported directly where needed

Project root is resolved dynamically: `Path(__file__).resolve().parent.parent.parent` (up from `src/miner/config.py`).

## Threading Model

- **OCR caching** uses a `threading.Lock` in `ocr.py`
- **MultiLineBuffer** uses a `threading.RLock` for thread-safe deque access
- **Translation fallback** uses `concurrent.futures.ThreadPoolExecutor` for parallel engine calls
- **Live OCR overlay** runs OCR in the main tkinter event loop via `after()` scheduling
- **Clipboard monitor** polls on a daemon thread
- **Yomitan bridge** runs an `asyncio` event loop on a separate thread
