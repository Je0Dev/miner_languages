# 01 — Tests

**`tests/`** — 11 test files, 147 tests.

Run: `python tests/run_tests.py` or `python -m unittest discover tests`

## Test files

| File | Tests | What it tests |
|------|-------|-------------|
| `test_capture.py` | 6 | `parse_slurp_geom()` in 3 formats, invalid input, `get_display_scale()`, import check |
| `test_ocr.py` | 13 | Tesseract pre-warm, OCR for all 10 languages with generated test images, `filter_garbage` per script, `ensure_utf8`, empty image handling, image preprocessing |
| `test_text.py` | 15 | `sanitize_unicode` (normal + escapes), `clean_text` (CJK spacing), `is_valid_text`, `split_sentences` for CJK/Western/mixed, `text_similarity`, `is_duplicate`, `get_pinyin`, `format_with_pronunciation` per script |
| `test_translate.py` | 15 | Translation for all 10 languages (zh→en, ja→en, etc.), empty/garbage rejection, `is_valid_for_translation` per script, clipboard/notification/audio source tests |
| `test_config.py` | 11 | `LANG_REGISTRY` structure, per-script checks (CJK/Latin/Greek/Cyrillic), romaji field mapping, OCR/Google code backward compat, mining dir existence |
| `test_zones.py` | 4 | Save/load/list zones, delete nonexistent zone, get nonexistent zone |
| `test_multiline.py` | 6 | `MultiLineBuffer` add/get, max lines, combined output, clear, empty buffer |
| `test_anki_export.py` | 2 | `export_to_anki_csv`, `append_to_anki_csv` with temp files |
| `test_universal_log.py` | 4 | `log_capture` writes to both `.txt` and `.json`, content correctness, multiple entries |
| `test_new_modules.py` | 5 | `health` check import, `stats` record+load, `backup` create, `duplicates` normalize+similarity |
| `test_comprehensive.py` | — | Larger integration tests |

## Test structure

Each test file:
1. Adds `src/` to `sys.path` so imports work
2. Uses `unittest.TestCase`
3. Creates temp files/images where needed (tests don't depend on Wayland or Tesseract for unit tests — they mock or skip when the external tool isn't available)

## `run_tests.py`

Auto-discovers all `test_*.py` files, loads them as test modules, runs with `unittest.TextTestRunner(verbosity=2)`. Prints summary: total, passed, failed, errors.

```bash
cd ~/miner-v2 && python tests/run_tests.py
```
