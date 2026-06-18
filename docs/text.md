# Text Processing

Cleans, validates, and enriches OCR output. Handles all 10 supported languages with script-specific logic for CJK, Latin, Greek, and Cyrillic text.

## Files

### `text.py` — Core Processing

Depends on: `config`, `log`

| Function | Description |
|----------|-------------|
| `sanitize_unicode(text)` | Decodes unicode escape sequences (`\u4f60` → `你`), normalizes to NFC form. |
| `clean_text(text)` | Strips whitespace, removes zero-width characters, normalizes spaces. |
| `is_valid_text(text)` | Validates: length ≥ 2, not a garbage string like `[No text detected]`, contains real content. |
| `split_sentences(text)` | Splits on sentence boundaries: `。！？!?；;.\n\r` for CJK and Western text. |
| `is_duplicate(new_text, history, threshold)` | Character-set-overlap based duplicate check against existing mined sentences. |
| `load_history(max_entries)` | Loads recent sentences from `sentences.json` for duplicate comparison. |
| `filter_garbage(text, lang)` | Removes purely numeric/symbolic text and single repeated characters. Script-aware: CJK, Latin, Greek, Cyrillic. |
| `normalize_repeating_chars(text)` | Collapses repeated characters (e.g. `"aaaa"` → `"a"`). |
| `remove_line_duplicates(text)` | Deduplicates repeated lines from OCR flicker. |
| `get_pronunciation(text, lang)` | Dispatches to language-appropriate romanization: pinyin (zh), romaji (ja), romanization (ko), transliteration (el, ru), or identity (latin). |
| `get_pinyin(text, tone_marks)` | Chinese pinyin via `pypinyin`. Optional tone marks. |
| `get_romaji(text)` | Japanese romaji via `romkan`. |
| `get_transliteration(text, lang)` | Greek/Russian transliteration via `trans` library. |
| `format_with_pronunciation(text, lang)` | Returns string with pronunciation appended. |
| `get_word_breakdown(text, lang)` | Segments text into words using `jieba` (Chinese) or `mecab` (Japanese). Returns list of `{word, pinyin/romaji}` dicts. |
| `format_word_breakdown(text, lang)` | Formats word breakdown as a display string. |
| `text_similarity(a, b)` | Character-level similarity score (0.0–1.0) using set overlap. |
| `strip_punctuation(text)` | Removes all punctuation via Unicode category matching (`regex` module). |
| `count_words_mixed(text)` | Estimates word count accounting for CJK (characters = words) vs Latin (space-separated). |

### `replace.py` — Text Replacement

Depends on: `config`, `log`

| Function | Description |
|----------|-------------|
| `apply_text_processing(text, lang)` | Runs text through configurable regex and plain-text replacement rules. Rules are loaded from a JSON config file. Used to fix common OCR errors (e.g. `"0"` → `"O"`, `"rn"` → `"m"`). |

### How They Connect

Used by every pipeline and UI component:
- `pipeline/mine.py` — `clean_text`, `is_duplicate`, `load_history`, `get_pronunciation`, `split_sentences`, `filter_garbage`
- `pipeline/quick.py` — same set
- `pipeline/batch.py` — `get_pronunciation`
- `ui/overlay.py` — `clean_text`, `sanitize_unicode`, `get_pronunciation`, `split_sentences`, word breakdown
- `ui/hover.py` — `clean_text`, `get_pronunciation`
- `storage/anki.py` — `get_pronunciation`
- `storage/export.py` — `get_pronunciation`
- `storage/server.py` — `get_pronunciation` (web viewer CSV export)
- `yomitan/bridge.py` — `get_pronunciation`, `get_word_breakdown`
- `yomitan/clipboard.py` — `clean_text`, `filter_garbage`, `get_pronunciation`
- `dictionary.py` — `get_word_breakdown`, `get_pronunciation`
- `profiles.py` — `clean_text`, `is_valid_text`
