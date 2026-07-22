# Project Overview

## What Is This?

Game Sentence Miner v2 (`miner-v2`) is a language-learning sentence mining
toolkit for the Linux desktop (Wayland/Hyprland). It captures text from
games, translates it, looks up words, records audio, and exports everything
to Anki for spaced-repetition study.

It supports 10 languages: Chinese, Japanese, Korean, German, French, Spanish,
Greek, Polish, Russian, and English.

---

## Directory Structure

```
miner_languages/
├── pyproject.toml           # Python package metadata + build config
├── requirements.txt         # pip dependencies (pinned versions)
├── README.md                # Project readme with workflows and keybindings
├── LICENSE                  # License terms
│
├── main.py                  # CLI entry point (adds src/ to PYTHONPATH)
├── test.py                  # Standalone integration test
│
├── src/miner/               # ALL Python source code
│   ├── main.py              # argparse CLI dispatcher
│   ├── config.py            # Constants, paths, language registry
│   ├── log.py               # Logging setup
│   ├── health.py            # Dependency checks
│   │
│   ├── capture/             # Screen capture (grim + slurp)
│   ├── ocr/                 # OCR engines (Tesseract, EasyOCR)
│   ├── text/                # Text processing (cleaning, pinyin, romaji)
│   ├── translate/           # Translation + TTS (Google, edge-tts)
│   ├── pipeline/            # Mining orchestration (capture→OCR→translate→save)
│   ├── storage/             # Persistence (SQLite, Anki, JSON, Excel)
│   ├── ui/                  # User interfaces (overlay, hover, web)
│   └── yomitan/             # Yomitan browser extension bridge
│
├── docs/                    # Markdown documentation
├── scripts/                 # Shell scripts for quick actions
├── tessdata/                # Tesseract language data files
├── mining/                  # Runtime data (gitignored)
└── tests/                   # Unit tests (147+ tests)
```

---

## Data Flow

```
┌─────────┐   ┌───────┐   ┌────────┐   ┌───────────┐   ┌──────────┐
│ Capture  │──▶│  OCR  │──▶│  Text  │──▶│ Translate │──▶│ Storage  │
│ (screen) │   │(image)│   │(clean) │   │  + TTS    │   │ (SQLite) │
└─────────┘   └───────┘   └────────┘   └───────────┘   └──────────┘
     │                           │                            │
     │                           │                            ▼
     │                     Pronunciation                  ┌──────────┐
     │                     (pinyin/romaji)                 │   Anki   │
     │                                                    │  Export  │
     ▼                                                    └──────────┘
┌─────────┐
│  Audio   │
│ Recording│
└─────────┘
```

### Step-by-step

1. **Capture** — `grim` + `slurp` captures a screen region (or entire screen)
2. **OCR** — Tesseract extracts text from the captured image
3. **Text** — Clean garbage, split sentences, compute pinyin/romaji
4. **Translate** — Google Translate via `deep-translator`; speak result with `edge-tts`
5. **Storage** — Save to SQLite, export to Anki CSV, record audio

### User Interfaces

```
┌─────────────────────────────────────────────────────────┐
│                    User Interfaces                       │
├────────────┬───────────┬──────────┬──────────┬─────────┤
│ Live OCR   │  Yomitan  │ Sentence │  Stats   │   Web   │
│  Overlay   │   Hover   │  Server  │Dashboard │  Viewer │
│ (tkinter)  │ (tkinter) │ (Flask)  │ (Flask)  │ (Flask) │
└────────────┴───────────┴──────────┴──────────┴─────────┘
```

---

## Subpackage Map

### `src/miner/capture/` — Screen Capture

- **`capture.py`** — `grim` (screenshot) + `slurp` (region select) wrappers
- Parses geometry strings, handles HiDPI scaling
- Called by: `pipeline/` modules, `ui/overlay.py`

### `src/miner/ocr/` — OCR Engines

- **`ocr.py`** — Tesseract OCR with per-language config, confidence scoring, caching
- **`easyocr.py`** — EasyOCR fallback when Tesseract fails
- **`confidence.py`** — Score-based retry logic
- Called by: `pipeline/` modules, `ui/overlay.py`, `ui/hover.py`

### `src/miner/text/` — Text Processing

- **`text.py`** — Unicode sanitization, validation, sentence splitting, duplicate detection,
  pinyin (Chinese), romaji (Japanese), word breakdown (jieba)
- **`replace.py`** — Configurable regex-based text replacements (OCR error correction)
- Called by: `pipeline/` modules, `translate/` (for pronunciation)

### `src/miner/translate/` — Translation + TTS

- **`translate.py`** — Google Translate via `deep-translator`, clipboard ops, notifications,
  audio recording, TTS via `edge-tts`
- **`parallel.py`** — Multi-engine parallel translation (Google + LibreTranslate + MyMemory)
- **`fallback.py`** — LibreTranslate fallback when Google fails
- Called by: `pipeline/` modules, `ui/overlay.py`, shell scripts

### `src/miner/pipeline/` — Mining Orchestration

- **`mine.py`** — `mine_sentence()`: capture → OCR → clean → translate → save → notify
- **`quick.py`** — `quick_capture()`: full-screen instant capture with fewer steps
- **`batch.py`** — `batch_process()`: process a directory of screenshot images
- Entry point for most CLI commands

### `src/miner/storage/` — Data Persistence

- **`server.py`** — Flask + SQLite web server (sentence browser + API)
- **`anki.py`** — Anki CSV export (multi-language)
- **`export.py`** — JSON and Excel export
- **`universal_log.py`** — Append-only TXT + JSON log of all mined content

### `src/miner/ui/` — User Interfaces

- **`overlay.py`** — Tkinter draggable overlay with live OCR region
- **`hover.py`** — Semi-transparent Tkinter window that OCRs under cursor
- **`dashboard.py`** — Flask web dashboard for mining stats
- **`debug_monitor.py`** — Debug view of OCR/translate/clipboard activity
- **`web_viewer.py`** — Browser-based sentence viewer

### `src/miner/yomitan/` — Yomitan Browser Extension Bridge

- **`bridge.py`** — WebSocket server that feeds Yomitan with OCR results
- **`bridge.js`** — Browser content script that connects to the WebSocket
- **`clipboard.py`** — Clipboard monitor that auto-processes copied text

---

## Dependency Graph

```
main.py
  └── src/miner/main.py              (argparse CLI)
        ├── config.py                (LANG_REGISTRY, paths)
        ├── log.py                   (logging)
        ├── health.py                (dependency checks)
        ├── stats.py                 (performance tracking)
        ├── backup.py                (data backup/recovery)
        ├── zones.py                 (capture zone management)
        ├── profiles.py              (per-game config)
        │
        ├── pipeline/mine.py         (main mining loop)
        │     ├── capture/capture.py
        │     ├── ocr/ocr.py
        │     │     └── ocr/easyocr.py
        │     ├── text/text.py
        │     │     └── text/replace.py
        │     ├── translate/translate.py
        │     │     ├── translate/parallel.py
        │     │     └── translate/fallback.py
        │     └── storage/universal_log.py
        │
        ├── pipeline/quick.py        (fast capture)
        │     └── (same deps as mine.py)
        │
        ├── pipeline/batch.py        (batch processing)
        │     └── (same deps as mine.py)
        │
        ├── ui/overlay.py            (live OCR GUI)
        │     └── (capture + ocr + text + translate)
        │
        ├── ui/hover.py              (hover overlay)
        │     └── (capture + ocr + text + translate)
        │
        ├── yomitan/bridge.py        (WebSocket server)
        │     └── (text + translate)
        │
        ├── yomitan/clipboard.py     (clipboard monitor)
        │     └── (text + translate)
        │
        ├── storage/server.py        (Flask web server)
        ├── storage/anki.py          (Anki export)
        ├── storage/export.py        (JSON/Excel export)
        ├── ui/dashboard.py          (stats dashboard)
        └── ui/web_viewer.py         (sentence viewer)
```

---

## Language Support Matrix

| Code | Language   | Script    | OCR (Tesseract) | Pronunciation | TTS Voice            |
|------|------------|-----------|-----------------|---------------|----------------------|
| zh   | Chinese    | CJK       | chi_sim         | pinyin        | zh-CN-XiaoxiaoNeural |
| ja   | Japanese   | CJK       | jpn             | romaji        | ja-JP-NanamiNeural   |
| ko   | Korean     | CJK       | kor             | romanization  | ko-KR-SunHiNeural    |
| de   | German     | latin     | deu             | —             | de-DE-KatjaNeural    |
| fr   | French     | latin     | fra             | —             | fr-FR-DeniseNeural   |
| es   | Spanish    | latin     | spa             | —             | es-ES-ElviraNeural   |
| el   | Greek      | greek     | ell             | transliteration| el-GR-AthinaNeural   |
| pl   | Polish     | latin     | pol             | —             | pl-PL-ZofiaNeural    |
| ru   | Russian    | cyrillic  | rus             | transliteration| ru-RU-SvetlanaNeural |
| en   | English    | latin     | eng             | —             | en-US-AriaNeural     |

---

## Configuration

All runtime constants live in `src/miner/config.py`:

- **`LANG_REGISTRY`** — Per-language settings (Tesseract model, Google code, script type, romanization)
- **`PATHS`** — Base directories (mining data, screenshots, backups, logs, tessdata)
- **`ZONES_DIR`** — Saved capture zone files
- **`TTS_VOICES`** — Voice mapping per language (in `translate.py`)

User configuration happens through:
1. Capture zones (saved/loaded via `--save-zone` / `--list-zones`)
2. Game profiles (via `--profiles` / `--detect-game`)
3. Hyprland keybindings (via `scripts/mining_bindings.conf`)
