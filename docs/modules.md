# Top-Level Utility Modules

Standalone modules in `src/miner/` that provide supporting functionality. Most are independent of each other and depend only on `config` and `log`.

## Core Infrastructure

### `config.py`

The single source of truth for all project configuration. Defines:

- **Project paths**: `MINING_DIR`, `LOCAL_TESSDATA`, subdirectory names
- **Language registry**: `LANG_REGISTRY` — 10 languages with Tesseract/Google codes, script type, romanization
- **Runtime constants**: timing intervals, recording settings, VAD parameters, text length limits
- **Anki settings**: `ANKICONNECT_URL`, Anki field names

Project root is resolved dynamically: `Path(__file__).resolve().parent.parent.parent` (from `src/miner/config.py` to project root). This ensures paths work regardless of how the package is invoked (installed, PYTHONPATH, or relative).

Imported by virtually every module in the project.

### `log.py`

Configures Python's `logging` module. Sets up two handlers:
- **File handler**: writes to `mining/miner.log`
- **Stream handler**: writes to stderr

Format: `timestamp [LEVEL] message`. Exposes a single `log` logger instance.

Imported by virtually every module.

## Configuration & State

### `zones.py`

Manages named capture regions. Zones store geometry + language, saved as JSON in `mining/zones.json`.

| Function | Description |
|----------|-------------|
| `save_zone(name, geom, lang)` | Saves a named zone. |
| `get_zone(name)` | Returns zone dict or `None`. |
| `list_zones()` | Returns list of zone names. |
| `delete_zone(name)` | Removes a zone. |

Used by: `main.py`, `pipeline/mine.py`, `pipeline/quick.py`

### `profiles.py`

Per-game configuration via Hyprland window class detection. When you mine from a game, the profile remembers the language, translation target, zone, and MSSIM settings for that game's window class.

| Function | Description |
|----------|-------------|
| `load_profiles()` | Loads from `game_profiles.json`. |
| `get_profile(window_class)` | Returns profile for a window class (or default). |
| `create_profile(window_class, **kwargs)` | Creates or updates a profile. |
| `delete_profile(window_class)` | Removes a profile. |
| `list_profiles()` | Lists all profiles. |
| `auto_detect_and_apply()` | Detects current game window, loads its profile. |

Used by: `main.py`, `ui/overlay.py`

### `stats.py`

Tracks mining statistics: total mined, OCR failures, translation failures, per-language breakdown, average OCR confidence. Persisted as JSON in `mining/stats.json`.

| Function | Description |
|----------|-------------|
| `load_stats()` | Loads stats from disk. |
| `save_stats(stats)` | Saves stats to disk. |
| `record_mining(lang, success, ocr_confidence, translation_success)` | Records one mining event. |
| `format_stats_report()` | Returns a formatted string for CLI display. |

Used by: `main.py`, `pipeline/quick.py`

### `backup.py`

Creates timestamped backups of key data files: `sentences.json`, `anki_export.csv`, `universal_log.txt`. Stores in `mining/backups/`. Keeps last 10 backups, auto-cleans older ones.

| Function | Description |
|----------|-------------|
| `create_backup()` | Creates a timestamped backup directory with copies of all data files. |
| `list_backups()` | Lists available backups. |
| `recover_from_backup(backup_path)` | Restores data from a backup. |

Used by: `main.py`

## Text Quality

### `dictionary.py`

Word definition lookups for Chinese (CC-CEDict), Japanese (Jisho API), and Korean (Naver/Krdict API). Downloads dictionary data on first use.

| Function | Description |
|----------|-------------|
| `get_definition(word, lang)` | Returns short definitions for a word. Dispatches to language-specific lookup. |
| `lookup_chinese(word)` | Searches CC-CEDict for Chinese word definitions. |
| `lookup_japanese(word)` | Searches Jisho API for Japanese word definitions. |
| `lookup_korean(word)` | Searches Naver/Krdict for Korean word definitions. |
| `enrich_word_breakdown(text, lang)` | Takes word segmentation output and adds definitions to each word. |
| `format_definition_display(text, lang)` | Formats word breakdown + definitions for display in the overlay. |

Used by: `ui/overlay.py`, `storage/server.py`

### `duplicates.py`

Levenshtein distance-based duplicate detection. Simpler and more lenient than `compare.py`.

| Function | Description |
|----------|-------------|
| `normalize_for_comparison(text)` | Lowercase, strip punctuation, collapse whitespace. |
| `levenshtein_distance(s1, s2)` | Standard Levenshtein edit distance. |
| `is_similar(text1, text2, threshold)` | Checks if two texts are similar (distance-based). |
| `is_duplicate_smart(new_text, history, threshold)` | Checks new text against all history entries. |
| `load_history_smart(max_entries)` | Loads history from sentences.json. |

### `compare.py`

Advanced OCR text comparison from GameSentenceMiner. Detects evolving text (text that grows as more of it appears on screen), partial overlaps, and chunk coverage.

| Function | Description |
|----------|-------------|
| `compare_ocr_results(prev_text, new_text, lang)` | Full comparison: checks for evolving prefix, identical text, anchored truncation, and chunk coverage. Returns `"skip"`, `"update"`, `"new"`, or `"reset"`. |
| `normalize_for_comparison(text)` | Language-aware normalization. |
| `is_evolving_text(shorter, longer, ...)` | Checks if shorter is a prefix of longer (text appearing character by character). |

Used by: `pipeline/mine.py` — determines whether to skip, update, or save new OCR results.

### `multiline.py`

Thread-safe deque buffer that accumulates consecutive OCR captures. Used in live mode to merge partial OCR results into a complete sentence.

| Class | Description |
|-------|-------------|
| `MultiLineBuffer(max_lines, window_sec)` | Circular buffer with timestamps. Methods: `add(text)`, `get_recent()`, `get_combined()`, `clear()`. |

Used by: `ui/overlay.py`

## Image Processing

### `stability.py`

MSSIM (Multi-Scale Structural Similarity) image stability detector. Compares consecutive frames and skips OCR if the scene hasn't stabilized (e.g. during UI animations or scene transitions).

| Class | Description |
|-------|-------------|
| `MSSIMStabilityDetector(threshold, cooldown)` | Holds reference frame. `is_stable(frame)` compares current frame to reference via `scipy.signal.correlate2d`. Returns `True` when similarity exceeds threshold. |

Used by: `ui/overlay.py`

### `preprocess.py`

Advanced image preprocessing for difficult OCR scenarios. Not used by the main OCR pipeline by default — provides these as optional enhancements.

| Function | Description |
|----------|-------------|
| `deblur_image(img, strength)` | Unsharp mask for motion blur. |
| `deskew_image(img)` | Corrects rotated text via Hough transform. |
| `adaptive_binarize(img)` | Local threshold binarization for uneven lighting. |
| `preprocess_advanced(image_path, lang)` | Applies all three in sequence. |

### `auto_detect.py`

Edge-density-based text region detection. Scans an image for areas with high vertical edge density (indicating text) and returns bounding boxes.

| Function | Description |
|----------|-------------|
| `detect_text_regions(image_path, min_area)` | Returns list of `(x, y, w, h)` regions with high text probability. |
| `auto_capture(output_path)` | Captures screen, detects best text region, saves cropped image. |

### `coordinates.py`

Coordinate math utilities for converting between logical and physical screen coordinates.

| Function | Description |
|----------|-------------|
| `ceil_to_multiple(value, multiple)` | Rounds up to nearest multiple. |
| `floor_to_multiple(value, multiple)` | Rounds down to nearest multiple. |
| `ceil_to_even(value)` | Rounds up to even number (for ffmpeg compatibility). |
| `scale_percentage_rectangle_to_even_pixels(...)` | Converts percentage-based regions to pixel coordinates. |
| `logical_box_to_even_physical_box(...)` | Applies display scale and rounds to even dimensions. |

## System

### `health.py`

Dependency health checker. Verifies that all required system commands and resources are available.

| Function | Description |
|----------|-------------|
| `run_health_check()` | Returns dict with status for: grim, slurp, ffmpeg, wl-copy, tesseract, audio source, mining directory. |
| `format_health_report(checks)` | Formats results as a human-readable string. |
| `check_command(cmd)` | Tests if a command exists and is executable. |
| `check_tesseract()` | Verifies tesseract is installed and has language data. |
| `check_audio()` | Checks PulseAudio for available recording sources. |

Used by: `main.py` (via `--health` flag)
