# Improvements & Potential Additions

## Recently Fixed

### `_clean_translation()` strips non-ASCII for non-English destinations
**File:** `src/miner/translate/translate.py`

The `_clean_translation()` function unconditionally stripped all non-ASCII characters
via `ENGLISH_CLEAN.findall(text)`. This meant translating *to* Chinese, Japanese,
Korean, Russian, etc. would produce empty output because the translated result
is entirely non-ASCII.

**Fix:** Added a `dest` parameter — the ASCII-only pass is now only applied when
the destination language is English. For all other languages, the full Unicode
result is preserved.

### `romkan` broken on Python >= 3.12 — replaced with `pykakasi`
**Files:** `src/miner/text/text.py`, `pyproject.toml`, `requirements.txt`

The `romkan` package (last released 2013) uses the removed `imp` module and
cannot be installed on Python 3.12+. It was listed as a hard dependency,
breaking `pip install` entirely.

**Fix:** Removed `romkan` from `requirements.txt` and `pyproject.toml`.
Replaced with `pykakasi` (actively maintained, pre-installed on many systems).
The `get_romaji()` function now uses `pykakasi` directly.

### `pip install -e .` broken — invalid build-backend
**File:** `pyproject.toml`

The `build-backend` was set to `setuptools.backends._legacy:_Backend`, which
does not exist in modern setuptools (>75). This caused installs to fail with
`BackendUnavailable`.

**Fix:** Changed to `setuptools.build_meta` — the standard, supported backend.

### `edge-tts` TTS integration
**File:** `src/miner/translate/translate.py`

Added `speak_text(text, lang)` function with language-appropriate neural voices
for all 10 supported languages (zh, ja, ko, de, fr, es, el, pl, ru, en).
Uses `edge-tts` to generate speech and `ffplay`/`paplay` for playback.
Added to `requirements.txt` and `pyproject.toml`.

---

## Critical Issues Remaining

### `translate_text()` silently returns `""` on failure
**File:** `src/miner/translate/translate.py`

When translation fails (network error, rate limiting, etc.), the function returns
`""` which is indistinguishable from a legitimate empty translation. Callers
cannot differentiate between "no text to translate" and "something went wrong."

**Suggested fix:** Return `None` on failure, or raise a typed exception.
Update all callers to handle the new return value.

### `pyproject.toml` missing `[tool.setuptools.packages.find]`
**File:** `pyproject.toml`

The `[tool.setuptools.packages.find]` section was removed during the
build-backend fix. Verify the package still finds all subpackages correctly
after the change.

---

## Potential Improvements

### Translation

- **Better error propagation**: `translate_text()` currently returns `""` on
  failure, making it impossible to distinguish "empty translation" from "error."
  Consider returning `None` or raising typed exceptions.
- **Language auto-detection**: Use a library like `langdetect` or `fasttext`
  to reliably detect source language instead of relying on Google Translate's
  `source="auto"`, which can be inconsistent.
- **Batch translation**: Accept a list of strings and translate them in one
  call where the backend supports it.

### Pronunciation / Romaji

- **Per-word breakdown in translation output**: Combine `get_word_breakdown()`
  with translation results so the user sees word-by-word pronunciation.
- **Tone mark option for pinyin**: The `get_pinyin()` function supports
  `tone_marks=True` (e.g., `nǐ hǎo`), but `get_pronunciation()` always uses
  tone numbers. Expose this option as a parameter.
- **TTS on pronunciation**: Currently `speak_text()` only reads the translated
  text. Optionally also speak the pinyin/romaji pronunciation.

### CLI / Workflow

- **Interactive translate mode**: A REPL-style loop where you type text
  and get instant translation + pronunciation, instead of clipboard-only flow.
- **Clipboard monitoring**: Watch the clipboard and auto-translate when
  text changes (useful for reading foreign-language content).
- **Multi-language output**: Show translation in several languages at once
  (e.g., "Good morning → おはよう (ohayou), 早上好 (zǎo shang hǎo)").

### Packaging & Dependencies

- **Pin compatible versions**: Many dependencies lack version pins or use
  outdated ranges. Run `pip-compile` to generate a locked `requirements.txt`.
- **Optional dependencies**: Make `pypinyin`, `pykakasi`, `hangul_romanize`,
  and `trans` optional extras (`pip install miner[zh,ja,ko]`).

### Testing

- **More edge cases in tests**: Empty strings, mixed-script text,
  very long strings, HTML entities.
- **CI pipeline**: Add GitHub Actions to run `test_text.py` and
  `test_translate.py` on pushes.

### Documentation

- **TTS example**: Document `speak_text()` usage with language codes and
  available voices.
- **Pronunciation examples**: Add a section in `docs/text.md` showing
  example outputs for each supported language.
- **API reference**: Auto-generated docs from docstrings (Sphinx/readthedocs).
- **Quick-start translate script**: Show the 3-line Python snippet to
  translate + get pronunciation.
