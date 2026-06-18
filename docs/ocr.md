# OCR

Extracts text from captured images using Tesseract, with EasyOCR as a fallback. Includes image preprocessing, result caching, and per-word confidence scoring.

## Files

### `ocr.py` — Tesseract OCR Engine

Depends on: `config`, `log`

| Function | Description |
|----------|-------------|
| `ocr_image(image_path, lang)` | Main OCR function. Preprocesses image (upscale, contrast, invert, grey closing), tries multiple PSM modes in order, filters garbage, caches results by image hash. |
| `ocr_long_text(image_path, lang)` | Same as `ocr_image` but uses PSM 6 (uniform block) for multi-line text. |
| `ocr_vertical_text(image_path, lang)` | Rotates image 90° and OCRs for vertical CJK text. |
| `preprocess_image(image_path, lang)` | Returns a preprocessed PIL Image. 3x upscale for CJK, contrast enhancement for Latin. |
| `preprocess_image_long(image_path, lang)` | Same but optimized for long/dense text blocks. |
| `prewarm_tesseract(lang)` | Loads Tesseract into memory by running one OCR pass. Called at startup to reduce first-capture latency. |

OCR pipeline: load image → hash → check cache → preprocess → try PSM modes (7, 6, 4, 3, 11) → ensure UTF-8 → filter garbage → cache result → return text.

### `confidence.py` — Confidence Scoring

Depends on: `ocr.py`

| Function | Description |
|----------|-------------|
| `ocr_with_confidence(image_path, lang)` | Runs OCR via `pytesseract.image_to_data()` to get per-word confidence scores. Auto-retries with different PSM if confidence is low (< 50). Returns `(text, avg_confidence)`. |

### `easyocr.py` — EasyOCR Fallback

Depends on: nothing internal

| Function | Description |
|----------|-------------|
| `ocr_easyocr(image_path, lang)` | Lazy-loads EasyOCR readers per language. Used as fallback when Tesseract fails or produces low-confidence results. Supports the same 10 languages. |

### How They Connect

Used by:
- `pipeline/mine.py` — calls `ocr_image()` / `ocr_long_text()` during mining
- `pipeline/quick.py` — same flow for instant capture
- `pipeline/batch.py` — calls `ocr_image()` for each image in a directory
- `ui/overlay.py` — calls `ocr_image()` in the live OCR loop
- `ui/hover.py` — calls `ocr_image()` for hover-based OCR

Language mapping: short codes (`zh`, `ja`, `de`, etc.) are converted to Tesseract codes (`chi_sim`, `jpn`, `deu`) via `config.LANG_REGISTRY`.

### Image Preprocessing

- **CJK text**: 3x bilinear upscale, contrast stretch, optional inversion for dark-on-light
- **Latin text**: 2x upscale, contrast enhancement
- **Dense text**: Additional CLAHE equalization and unsharp masking
- **All languages**: Grey-closing morphological filter to merge broken characters

### Caching

OCR results are cached in an LRU dict (keyed by SHA-256 of the image pixels). Cache is sized to the last 50 unique images. This prevents re-OCR when the same frame is captured multiple times (e.g. during live mode with a static scene).
