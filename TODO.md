# TODO & Changelog

## 2026-07-22 — Critical fixes + documentation overhaul

### What was done

- **`translate_text()` now returns `None` on failure instead of `""`**
  - Why: Callers couldn't distinguish "translation failed" from "empty translation".
    Network errors, rate limiting, and invalid input all returned `""` silently.
    Now they get `None` (error) vs `""` (valid empty result).

- **Updated all callers to handle `None` safely**
  - Why: `overlay.py`, `hover.py`, `clipboard.py`, `bridge.py`, `quick.py`,
    `mine.py`, `batch.py` all called `translate_text()` and would crash or
    misbehave with `None` in string operations like `tr[:60]`.

- **Updated test suite to match new `None` return**
  - Why: Tests checked `assertEqual("")` and `assertGreater(len(result), 0)`
    which would fail on `None`. Added `_check_translation()` helper.

- **Fixed `record_audio()` type hint** (`source: str = None` → `source: str | None = None`)
  - Why: Type mismatch caused LSP errors. The function explicitly handles `None`.

- **Added comprehensive docs**
  - `docs/overview.md` — Architecture, data flow, subpackage map, language matrix
  - `docs/setup.md` — Install guide, run instructions, troubleshooting
  - `README.md` now references `docs/` and separate `LICENSE` file

- **Added `LICENSE` file** (MIT)
  - Why: License was embedded in README only. Now it's a proper standalone file.

- **Fixed packaging** (`pyproject.toml`, `requirements.txt`)
  - Why: `pip install -e .` was broken (invalid build-backend, `romkan` uninstallable)
  - Replaced `romkan` with `pykakasi`, fixed build-backend, added `edge-tts`

- **Added missing docstrings** to `coordinates.py` and 4 empty `__init__.py` files
  - Why: These were the only undocumented modules in the project.

- **All 147 tests pass** (clipboard test times out in non-Wayland — expected)

### Remaining improvements

#### High priority

- **CI pipeline** — Add GitHub Actions to auto-run tests on push
- **`translate_text()` rate limiting** — Google Translate API has no built-in
  rate limiting. Long mining sessions may get temporarily blocked.
- **Better error propagation in parallel.py** — `translate_parallel()` wraps
  errors silently too. Should surface them like `translate_text()` now does.

#### Medium priority

- **Pin dependency versions** — `requirements.txt` uses minimum versions only.
  Run `pip-compile` to generate a locked `requirements.txt` for reproducible builds.
- **Optional dependency groups** — Make `pypinyin`, `pykakasi`, `hangul_romanize`,
  `trans` optional extras (`pip install miner[zh,ja,ko]`).
- **Tone marks in pinyin** — `get_pinyin()` supports `tone_marks=True` but
  `get_pronunciation()` doesn't expose it. Add parameter.

#### Low priority

- **Batch translation** — Accept a list of strings to translate in one API call.
- **Language auto-detection** — Use `langdetect` or `fasttext` instead of
  Google Translate's `source="auto"`.
- **TTS on pronunciation** — `speak_text()` only reads the translated text.
  Optionally also speak pinyin/romaji.
- **Per-word breakdown in translation output** — Combine `get_word_breakdown()`
  with translation results.
- **Interactive translate mode** — REPL-style loop for instant translate + TTS.
