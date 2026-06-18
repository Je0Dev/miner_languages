# 01 — OCR Module

**`src/miner/ocr/`** — `ocr.py`, `confidence.py`, `easyocr.py`, `__init__.py`

Runs Tesseract OCR on screenshots. Cleans up the result by filtering garbage text (UI symbols, circled numbers, single letters in CJK text, etc.). Supports 10 languages with script-specific cleaning rules. Falls back to EasyOCR if Tesseract fails.

## What each file does

### `ocr.py` — Main OCR engine

| Function | What it does |
|----------|-------------|
| `prewarm_tesseract(lang)` | Warms up Tesseract once at startup (OCRs a blank 100×30 image). Fixes first-call delay. |
| `ocr_image(path, lang)` | Main entry point. Tries: preprocessed image → enhanced for dense text → raw image. Caches results for 1 hour (max 500 entries). Picks PSM modes 6, 3, 5 in order until one works. |
| `ocr_long_text(path, lang)` | Same but uses `preprocess_image_long` (wider kernel, MedianFilter) and PSM modes 3, 5. Returns text without cache. |
| `ocr_vertical_text(path, lang)` | For vertical text. Tries PSM 5, then tries rotating the image 90°, 270°, 180° and picking the longest result. |
| `preprocess_image(path, lang)` | Converts to grayscale, inverts if dark background, enhances contrast ×1.5, sharpens, then runs grey_closing background subtraction + binary threshold. |
| `preprocess_image_long(path, lang)` | Same but contrast ×1.3, MedianFilter instead of sharpen, wider kernel. |
| `_filter_garbage(text, lang)` | Removes UI symbols (circled numbers, dingbats, arrows, math), copyright marks, single letters/digits in CJK text. If CJK text has >40% non-CJK characters, returns empty string. Same for Greek/Cyrillic with script-specific filters. |

### `confidence.py` — Confidence scoring

| Function | What it does |
|----------|-------------|
| `get_ocr_confidence(path, lang, psm)` | Runs Tesseract with `image_to_data`, returns dict with `text`, `confidence` (0-100 avg), `word_count`. |
| `ocr_with_confidence(path, lang, ocr_func)` | Retries with PSM 6 → 3 → 5 until confidence >= 60. Falls back to the main OCR function if all fail. |

### `easyocr.py` — Fallback engine

| Function | What it does |
|----------|-------------|
| `ocr_easyocr(path, lang)` | Loads EasyOCR reader for the language (shareable, reused). Runs `reader.readtext()` and joins results. Returns empty string if EasyOCR not installed or fails. |

### `__init__.py`

Exports: `ocr_image`, `ocr_long_text`, `prewarm_tesseract`, `_filter_garbage`, `_ensure_utf8`, `preprocess_image`, `ocr_vertical_text`, `ocr_with_confidence`, `ocr_easyocr`

## How it works (the OCR pipeline)

```
screenshot.png
      │
      ▼
preprocess_image(path, lang)
  │  Grayscale + invert if dark
  │  Upscale ×2-3 for small text (bigger for CJK)
  │  Contrast enhance + sharpen
  │  grey_closing background removal
  │  Binary threshold
      │
      ▼
Tesseract OCR (PSM 6 → 3 → 5)
  │  --oem 3 --psm 6 -l chi_sim
      │
      ▼
_ensure_utf8(text) — fix encoding
      │
      ▼
_filter_garbage(text, lang)
  │  Remove UI symbols, circled numbers
  │  Remove lone digits/letters from CJK
  │  Reject if too much non-CJK in CJK text
      │
      ▼
Empty? → Try enhanced_for_dense_text → Try raw image
All fail? → Return ""
```

## Language-specific behavior

| Script | Upscale threshold | Filter rules |
|--------|-------------------|-------------|
| CJK (zh/ja/ko) | 3× if <1000×300 | Remove digits ≤3 chars, single letters, brackets, punctuation runs |
| Latin (de/es/fr/pl/en) | 2× if <600×150 | Remove digits ≤2 chars |
| Greek | 2× if <800×200 | Keep only Greek + ASCII |
| Cyrillic (ru) | 2× if <800×200 | Keep only Cyrillic + ASCII |
