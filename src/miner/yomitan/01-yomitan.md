# 01 — Yomitan Module

**`src/miner/yomitan/`** — `bridge.py`, `bridge.js`, `clipboard.py`, `__init__.py`

Connects the miner to the Yomitan browser extension. Two paths: a WebSocket bridge for direct extension communication, and a clipboard monitor for polling-based integration.

## What each file does

### `bridge.py` — WebSocket server (Python)

WebSocket server on port 8766 using the `websockets` library. The Yomitan browser extension connects to it.

**Protocol:** JSON messages over WebSocket.

| Action (receive) | Response | What it does |
|-----------------|----------|-------------|
| `{"action":"find_sentences", "term":"...", "lang":"zh"}` | `{"action":"find_sentences", "results":[...]}` | Searches `sentences.json` for entries containing the term. Returns up to 50 results with sentence, translation, pronunciation, source, timestamp, words. |
| `{"action":"word_info", "term":"...", "lang":"zh"}` | `{"action":"word_info", "info":{...}}` | Gets pronunciation + word breakdown (jieba/MeCab) for the term. |
| `{"action":"translate", "text":"...", "lang":"zh"}` | `{"action":"translate", "original":"...", "translation":"..."}` | Translates the text via Google. |
| `{"action":"ping"}` | `{"action":"pong", "timestamp":"..."}` | Health check. |

| Function | What it does |
|----------|-------------|
| `run_bridge(port)` | Starts WebSocket server (blocking, uses `asyncio.run`). |
| `start_bridge(port)` | Starts bridge in a background daemon thread. Returns the thread object. |

### `bridge.js` — Content script (JavaScript)

Browser content script that connects to the WebSocket bridge. Injected by the Yomitan extension or loaded as a userscript.

**What it does:**
1. Connects to `ws://localhost:8766`
2. Auto-reconnects every 3s on disconnect
3. Exposes `window.MinerBridge` API: `findSentences(term, lang)`, `getWordInfo(term, lang)`, `translate(text, lang)`, `connect()`
4. When receives `find_sentences` response, shows a styled popup in the top-right corner listing mined sentences containing the hovered word
5. When receives `word_info`, shows a popup with per-word breakdown (word → pinyin/romaji → definition)

### `clipboard.py` — Clipboard monitor (Python)

Polling-based alternative that doesn't need browser injection. Watches Wayland clipboard via `wl-paste` every 0.5 seconds.

| Function | What it does |
|----------|-------------|
| `monitor_clipboard(interval, lang, auto_save)` | Polls clipboard. When new text appears: cleans, auto-detects language (CJK → zh/ja, Hangul → ko, Greek → el, Cyrillic → ru), translates, gets pronunciation, saves to `yomitan_clipboard.json`, sends to sentence server. |
| `auto_detect_lang(text)` | Detects language by scanning for script-specific Unicode ranges. |
| `save_entry(entry)` | Appends to `yomitan_clipboard.json`, keeps max 500 entries. |
| `send_to_server(...)` | Sends to Flask sentence server. |

**Run:**
```bash
python src/miner/yomitan/clipboard.py          # auto-detect language
python src/miner/yomitan/clipboard.py -l zh    # force Chinese
```

### `__init__.py`

Empty — callers import directly:
```python
from miner.yomitan.bridge import start_bridge, run_bridge
from miner.yomitan.clipboard import monitor_clipboard
```

## Data flow

### WebSocket path (direct browser integration):

```
Yomitan extension (browser)
       │
       │  WebSocket ws://localhost:8766
       ▼
bridge.py (Python WebSocket server)
       │
       ├── find_sentences_with_term() → search sentences.json
       ├── get_word_info() → jieba/MeCab + pronunciation
       └── translate_text() → Google Translate
```

### Clipboard path (no browser extension):

```
Any app copies text to clipboard
       │
       ▼
clipboard.py polls wl-paste every 0.5s
       │
       ├── auto_detect_lang()
       ├── clean_text() + filter_garbage()
       ├── translate_text()
       ├── get_pronunciation()
       └── save to yomitan_clipboard.json
```
