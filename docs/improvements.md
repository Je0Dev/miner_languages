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

### `romkan` broken on Python >= 3.12
**File:** `src/miner/text/text.py`

The `romkan` package (last released 2013) uses the removed `imp` module and
cannot be installed on Python 3.12+. Japanese romaji conversion silently
returned empty strings.

**Fix:** Added a `pykakasi` fallback (new API) when `romkan` import fails.
`pykakasi` is pre-installed on most modern systems and actively maintained.

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
  tone numbers. Expose this option.
- **Audio pronunciation**: TTS integration (e.g., `espeak-ng`, `piper-tts`,
  or `edge-tts`) to play the pronunciation aloud.

### CLI / Workflow

- **Interactive translate mode**: A REPL-style loop where you type text
  and get instant translation + pronunciation, instead of clipboard-only flow.
- **Clipboard monitoring**: Watch the clipboard and auto-translate when
  text changes (useful for reading foreign-language content).
- **Multi-language output**: Show translation in several languages at once
  (e.g., "Good morning → おはよう (ohayou), 早上好 (zǎo shang hǎo)").

### Packaging & Dependencies

- **Replace `romkan` with `pykakasi`**: Since `romkan` is unmaintained and
  broken, swap it in `requirements.txt` and `pyproject.toml`.
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

- **Pronunciation examples**: Add a section in `docs/text.md` showing
  example outputs for each supported language.
- **API reference**: Auto-generated docs from docstrings (Sphinx/readthedocs).
- **Quick-start translate script**: Show the 3-line Python snippet to
  translate + get pronunciation.
