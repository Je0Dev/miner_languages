# Yomitan Integration

Connects the mining toolkit to the [Yomitan](https://github.com/themoeway/yomitan) browser extension (a dictionary popup tool for language learners). Provides three integration points: a WebSocket bridge, a clipboard monitor, and a browser content script.

## Files

### `bridge.py` — WebSocket Server

Depends on: `config`, `text`, `translate`, `log`

Runs a WebSocket server on port 8766. The Yomitan browser extension connects via a content script, enabling real-time dictionary lookups against mined sentences.

| Function | Description |
|----------|-------------|
| `run_bridge(port)` | Starts the WebSocket server. Handles client connections, parses JSON messages, dispatches actions. |
| `start_bridge(port)` | Runs `run_bridge` in a background thread. |
| `load_sentences()` | Loads all mined sentences from `sentences.json`. |
| `find_sentences_with_term(term, lang)` | Searches mined sentences for a specific term. Returns matching entries with surrounding context. |
| `get_word_info(term, lang)` | Gets pronunciation, word breakdown, and definitions for a term. Combines `text.get_word_breakdown()` and `dictionary` lookups. |

**WebSocket Actions:**

| Action | Request | Response |
|--------|---------|----------|
| `find_sentences` | `{"action": "find_sentences", "term": "...", "lang": "zh"}` | `{"sentences": [...]}` |
| `word_info` | `{"action": "word_info", "term": "...", "lang": "zh"}` | `{"pronunciation": "...", "breakdown": [...], "definitions": [...]}` |
| `translate` | `{"action": "translate", "text": "...", "src": "zh", "dest": "en"}` | `{"translation": "..."}` |
| `ping` | `{"action": "ping"}` | `{"pong": true}` |

### `bridge.js` — Browser Content Script

A JavaScript file that runs in the browser (via Yomitan's popup or a userscript manager like Tampermonkey). Connects to the WebSocket bridge at `ws://localhost:8766` and exposes `window.MinerBridge` API:

```javascript
window.MinerBridge.findSentences("term")  // → [...]
window.MinerBridge.getWordInfo("term")    // → {...}
window.MinerBridge.translate("text")      // → "..."
```

### `clipboard.py` — Clipboard Monitor

Depends on: `config`, `text`, `translate`, `log`

Polling clipboard watcher that auto-processes copied text for Yomitan integration.

| Function | Description |
|----------|-------------|
| `monitor_clipboard(interval, lang, auto_save)` | Main loop. Polls `wl-paste` every 0.5s. When new text is detected, auto-detects language, translates, saves to history, optionally sends to sentence server. |
| `get_clipboard()` | Returns current clipboard content via `wl-paste`. |
| `send_to_server(original, lang, translation, pronunciation)` | POSTs to the sentence server API. |
| `save_entry(entry)` | Appends to `yomitan_clipboard.json`. |
| `auto_detect_lang(text)` | Heuristic language detection (CJK character ranges → language code). |

### How They Connect

- `main.py` — `--bridge` flag starts the WebSocket bridge; `--clipboard` starts the clipboard monitor
- `scripts/mine.sh` — `--list-zones` and `--save-zone` call main.py which uses the bridge
- `mining_bindings.conf` — SUPER+CTRL+J starts bridge, SUPER+CTRL+C starts clipboard monitor
- `ui/hover.py` — the hover overlay copies OCR'd text to clipboard, which Yomitan picks up via the bridge
- `storage/server.py` — serves the `/bridge` web page and `/api/yomitan/*` endpoints for Yomitan HTTP fallback

### System Architecture

```
┌──────────────────┐     WebSocket      ┌─────────────────┐
│  Browser         │◄──────────────────►│  bridge.py       │
│  (Yomitan ext)   │   ws://localhost   │  (port 8766)     │
│  bridge.js       │       :8766        │                  │
└──────────────────┘                    └────────┬────────┘
                                                 │
                                                 ▼
                                          ┌─────────────────┐
                                          │  sentences.json  │
                                          │  dictionary.py   │
                                          │  text.py         │
                                          │  translate.py    │
                                          └─────────────────┘

┌──────────────────┐     clipboard      ┌─────────────────┐
│  Hover Overlay   │──────────────────►│  Browser         │
│  (hover.py)      │   wl-copy         │  (Yomitan)       │
└──────────────────┘                    └─────────────────┘

┌──────────────────┐     HTTP POST      ┌─────────────────┐
│  clipboard.py    │──────────────────►│  sentence_server │
│  (monitor)       │   /api/add        │  (port 5002)     │
└──────────────────┘                    └─────────────────┘
```
