# 01 — Text Module

**`src/miner/text/`** — `text.py`, `replace.py`, `__init__.py`

Cleans OCR text, checks for duplicates, splits sentences, and adds pronunciation (pinyin/romaji/transliteration). Has a configurable text replacement pipeline for fixing common OCR errors.

## What each file does

### `text.py` — Core text processing

| Function | What it does |
|----------|-------------|
| `sanitize_unicode(text)` | Fixes unicode escapes (`\uXXXX`), normalizes to NFC, removes zero-width chars, BOM, replacement chars, mojibake. |
| `clean_text(text)` | Sanitizes + removes spaces between CJK chars (Tesseract puts spaces between every CJK glyph) + collapses whitespace. |
| `is_valid_text(text)` | Checks length (min/max from config), rejects UI-menu-looking text (too many short words), too many numbers in CJK, copyright-only text. |
| `split_sentences(text)` | Splits on `。！？!?；;.\n\r` and validates each chunk with `is_valid_text`. |
| `text_similarity(a, b)` | Jaccard similarity of character sets (intersection / union). 0.0-1.0. |
| `is_duplicate(text, history, threshold=0.85)` | Checks if text is >85% similar to any of last 500 history entries. |
| `get_pinyin(text, tone_marks)` | Uses `pypinyin` library. Returns space-separated pinyin with tone numbers. |
| `get_romaji(text, lang)` | Japanese: `romkan` library. Korean: `hangul_romanize`. |
| `get_transliteration(text, lang)` | Greek/Russian: `trans` library. |
| `get_pronunciation(text, lang)` | Dispatches to the right function based on language config (`romaji` field in LANG_REGISTRY). |
| `format_with_pronunciation(text, lang)` | Returns `"text\npronunciation"` for CJK/Greek/Cyrillic, plain text for Latin. |
| `get_word_breakdown(text, lang)` | Chinese: `jieba.lcut()`. Japanese: `MeCab` tokenizer. Returns list of `{word, pinyin/romaji}`. |
| `format_word_breakdown(text, lang)` | Formats breakdown as `"word → pinyin | word → pinyin"` string. |
| `filter_garbage(text, lang)` | Same as OCR's `_filter_garbage` — removes UI symbols/artifacts per script type. |
| `normalize_repeating_chars(text)` | Detects repeated char patterns (game render artifacts) and deduplicates them. Ported from LunaTranslator's `_2_f`. |
| `remove_line_duplicates(text)` | Removes exact duplicate lines. Ported from LunaTranslator's `_6_fEX`. |
| `count_words_mixed(text)` | Counts CJK chars as individual words + space-delimited Latin words. |

### `LRUCache` class

Thread-safe LRU cache with configurable capacity. Used by the pipeline for caching validation states.

Methods: `get`, `put`, `test` (get-or-set), `setcap`.

### `replace.py` — Text replacement pipeline

Configurable find-and-replace rules saved to `mining/text_replacements.json`.

| Function | What it does |
|----------|-------------|
| `load_rules()` | Loads rules from JSON file. Returns empty list if file missing. |
| `save_rules(rules)` | Saves rules to JSON file. |
| `add_rule(find, replace, mode, case_sensitive, whole_word, enabled)` | Adds a rule and saves. Mode can be `"plain"` or `"regex"`. |
| `remove_rule(index)` | Removes rule by index. Returns True/False. |
| `apply_text_processing(text)` | Runs all enabled rules against the text in order. Handles regex errors gracefully — skips bad rules instead of crashing. |
| `_apply_rule(text, rule)` | Single rule application. Supports plain text, regex, whole-word matching, case sensitivity. Auto-converts `<.*>` to `/<[^>]*>/` regex. |

### `__init__.py`

Exports: `clean_text`, `sanitize_unicode`, `is_valid_text`, `is_duplicate`, `load_history`, `get_pronunciation`, `split_sentences`, `get_word_breakdown`, `format_word_breakdown`, `format_with_pronunciation`, `filter_garbage`, `normalize_repeating_chars`, `remove_line_duplicates`, `text_similarity`, `get_pinyin`

## Text processing pipeline (in order)

When you mine a sentence, these steps run in sequence:

1. `clean_text()` — fix unicode, remove CJK spacing
2. `filter_garbage()` — strip UI symbols per script
3. `normalize_repeating_chars()` — deduplicate render artifacts
4. `remove_line_duplicates()` — remove repeated lines
5. `apply_text_processing()` — run user's custom replace rules
6. `is_valid_text()` — reject garbage
7. `is_duplicate()` — reject if already mined
8. `get_pronunciation()` — add pinyin/romaji
9. `split_sentences()` — split for per-sentence storage
10. `get_word_breakdown()` — jieba/MeCab per-word split
