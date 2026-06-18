# 01 — Capture Module

**`src/miner/capture/`** — `capture.py`, `__init__.py`

Screenshots the screen using `grim` and `slurp` (Wayland-only, made for Hyprland). This is step 1 of the mining pipeline.

## What each file does

### `capture.py` — 4 public functions

| Function | What it does |
|----------|-------------|
| `capture_region(path, geom)` | If no geom given, opens `slurp` so you can drag-select a region. Then runs `grim` to save a PNG. Returns the geometry string (or None if cancelled). |
| `capture_screenshot(path, geom)` | Full-screen screenshot (no interactive selection). If geom given, crops to that region. Returns True/False. |
| `get_display_scale()` | Reads `hyprctl monitors -j` to get the display scale (1.0, 1.5, 2.0). Used for HiDPI support. |
| `parse_slurp_geom(str)` | Converts geometry strings into `(x, y, w, h)` ints. Handles 3 formats: slurp default (`"100,200 300x150"`), comma-sep (`"100,200,300,150"`), ImageMagick (`"300x150+100+200"`). |

### `__init__.py`

Re-exports all 4 functions from `capture.py` so callers can do `from miner.capture import capture_region`.

## How it works

1. User presses SUPER+X and drags a region → `slurp` outputs `"560,340 600x400"`
2. `parse_slurp_geom` converts that to `(560, 340, 600, 400)`
3. Waits 100ms for compositor to settle (prevents artifacts from the disappearing crosshair)
4. Runs `grim -g "560,340 600x400" /path/to/capture.png`
5. Returns the geometry string to the pipeline for storage

## Who uses it

| Caller | What it calls | Why |
|--------|--------------|-----|
| `pipeline/mine.py` | `capture_region()` | User select region → OCR → translate → save |
| `pipeline/quick.py` | `capture_screenshot()` | Full-screen capture, no selection |
| `ui/overlay.py` | `capture_region()` + `get_display_scale()` | Select region for live OCR loop |
| `main.py` | calls `slurp` directly | Zone saving (`--save-zone`) |
