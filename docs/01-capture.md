# 01 — Capture Module

**Location:** `src/miner/capture/`

**Files:** `__init__.py`, `capture.py`

**Purpose:** Frontend of the mining pipeline. Handles all Wayland screen capture — launching `slurp` for interactive region selection, running `grim` for screenshots, querying `hyprctl` for display scaling, and parsing geometry strings into usable coordinates.

**Platform:** Wayland-only. Designed for Hyprland (uses `hyprctl` for scale detection, `grim`/`slurp` which are wlroots-based tools). Will not work on X11.

---

## `__init__.py`

Single re-export of all 4 public functions from `capture.py`:

```python
from miner.capture.capture import capture_region, capture_screenshot, get_display_scale, parse_slurp_geom
```

Callers import from the package level:

```python
from miner.capture import capture_region, capture_screenshot
```

---

## `capture.py` — Full Breakdown

### Imports and Module-Level Constants

```python
import subprocess, json, time
from pathlib import Path
from miner.log import log
```

`subprocess` is the core — every capture operation spawns an external process. No Python-native screenshot library (no `mss`, `PIL.ImageGrab`, etc.) since Wayland does not allow cross-process pixel reading without portal APIs.

`json` is used only in `get_display_scale()` to parse the `hyprctl monitors -j` JSON array.

`time.sleep` is used for a 150ms compositor settle delay after `slurp` exits before calling `grim` — without this, `grim` sometimes captures a frame that still shows the slurp crosshair overlay.

```python
MAX_RETRIES = 1
```

Defined but **not used** anywhere in the current code. Likely a leftover from an earlier design where capture was retried on failure. Could be removed or repurposed for a retry loop.

---

### `get_display_scale()`

```python
def get_display_scale() -> float:
```

**Purpose:** Queries Hyprland for the focused monitor's display scale factor.

**Why needed:** Hyprland runs at a logical resolution, but `grim` captures at physical pixel resolution. If the display is scaled (e.g. 1.5x or 2.0x on a HiDPI screen), coordinates returned by Hyprland APIs might be in logical pixels, while `grim -g` expects physical pixels. This function retrieves the scale so callers can multiply coordinates if needed.

**How it works:**

1. Runs `hyprctl monitors -j` — this returns a JSON array of all monitors with their properties.
2. Iterates over the array looking for the monitor where `"focused": true`.
3. Reads the `"scale"` field and returns it as a `float`.
4. If anything fails (subprocess error, JSON parse error, missing key, no focused monitor), silently catches the exception and returns `1.0` (no scaling).

**Return value:** `float` — typically `1.0`, `1.5`, or `2.0`.

**Edge cases:**
- No monitors? Returns `1.0`.
- No focused monitor? Returns `1.0` (multi-monitor setups where focus is on another workspace).
- `hyprctl` not installed? Returns `1.0`.
- JSON malformed? Returns `1.0`.

**Note:** Currently, `capture_region()` and `capture_screenshot()` do **not** call this function. The coordinates passed to `grim` are assumed to already be in physical pixels. The scaling function is available for callers (like `overlay.py` region selection) that need to convert between logical and physical coordinates.

---

### `parse_slurp_geom()`

```python
def parse_slurp_geom(geom_str: str) -> tuple | None:
```

**Purpose:** Parses a geometry string into a `(x, y, width, height)` tuple of integers. Handles three different formats because geometry strings come from multiple sources.

**Supported formats:**

| Format | Example | Source |
|--------|---------|--------|
| Slurp default | `"100,200 300x150"` | Direct output from `slurp` |
| Comma-separated | `"100,200,300,150"` | Saved zones, user config files |
| ImageMagick | `"300x150+100+200"` | Some external tools, manual input |
| Dimensions only | `"300x150"` | Fallback with origin at (0,0) |

**Parsing logic step by step:**

1. **Strip whitespace** from the input string.
2. **Format detection — slurp default:** If the string contains both `,` and a space (e.g. `"100,200 300x150"`), split on the space into `xy` and `wh` parts. Parse the `x,y` part by splitting on `,`, and the `wxh` part by splitting on `x`.
3. **Format detection — comma-separated:** If the string contains `,` but no space (e.g. `"100,200,300,150"`), split on `,` and map all 4 parts to ints.
4. **Format detection — ImageMagick:** Remove any spaces. Look for the pattern `WxH+X+Y` (a `x` and at least one `+`). Split on the first `+` to separate `WxH` from the offset. Parse `WxH` by splitting on `x`. Parse the offset by splitting the remainder on `+` (which handles `+X+Y` format where there are two parts).
5. **Format — dimensions only:** Has a `x` but no `+`. Treat as width x height with origin at (0,0).
6. If none of these patterns match, returns `None`.

**Edge cases:**
- Empty string → returns `None`.
- Non-numeric characters → exception caught, returns `None`.
- Wrong number of parts → returns `None`.
- Negative coordinates (possible on multi-monitor setups) → works fine since they parse to negative ints.
- `IM` format with extra plus signs → handled by splitting on `+` and taking the first two parts.

**Return value:** `(x: int, y: int, w: int, h: int) | None`

---

### `capture_region()`

```python
def capture_region(output_path: Path, geom: str = None) -> str | None:
```

**Purpose:** Captures a screen region. The primary capture entry point used by the mining pipeline.

**Parameters:**

- `output_path: Path` — Where to save the PNG screenshot. Must be a writeable path. Typically something like `mining/20250101_120000/images/abc123.png`.
- `geom: str | None` — If provided, captures this region directly. If `None`, launches `slurp` for interactive selection.

**Return value:** `str | None` — The geometry string of the captured region (as returned by `slurp`), or `None` if capture failed or was cancelled.

**Full call flow when `geom=None` (interactive mode):**

1. **Launch `slurp`** with visual styling flags:
   ```
   slurp -b 333333cc -c ff0000ff -s ff000044 -w 3
   ```
   - `-b 333333cc` — Background color (semi-transparent dark gray, 80% opacity). This dims the area outside the selection rectangle.
   - `-c ff0000ff` — Border color (solid red). Draws the selection rectangle border.
   - `-s ff000044` — Selection color (semi-transparent red, ~27% opacity). Tints the selected region.
   - `-w 3` — Border width in pixels.

2. **Wait** up to 30 seconds for `slurp` to complete (user might take a while selecting a region, or press Escape to cancel).

3. **Check return code:** If `slurp` exited non-zero (user pressed Escape or clicked outside), return `None` — no capture happened.

4. **Check output:** If `slurp` produced empty output, return `None`.

5. **Parse geometry:** Call `parse_slurp_geom()` on the raw slurp output.

6. **Small delay:** `time.sleep(0.1)` — 100ms pause to let the compositor finish removing the slurp overlay. Without this, `grim` sometimes captures the frame where the slurp crosshair is still being removed, resulting in artifacts.

7. **Launch `grim`** with the geometry:
   ```
   grim -g "100,200 300x150" /path/to/output.png
   ```

8. **Log result** at `info` level with the geometry string.

**Full call flow when `geom` is provided (non-interactive mode):**

1. Parse the geometry string.
2. If parsing fails, return `None`.
3. Extract `x, y, w, h` from the parsed tuple.
4. 100ms delay.
5. Run `grim` with the parsed geometry.

**Error handling:**

- `subprocess.CalledProcessError` — `grim` or `slurp` returned non-zero. Logged at `error` level. Returns `None`.
- `subprocess.TimeoutExpired` — User took longer than 30 seconds to select a region. Logged at `error` level. Returns `None`.
- Exception in geometry parsing — Any unexpected format triggers an exception caught by the `try/except` in `parse_slurp_geom`, returning `None` up the chain.

**Notable behavior:**
- **Single attempt only.** No retry logic despite `MAX_RETRIES = 1` being defined.
- **Always overwrites** the output file if it exists.
- **Does not validate** that the captured image has non-zero dimensions or actual content. If `grim` produces an empty/black image (e.g. capturing a region outside all monitors), it still returns the geometry string as if successful.

---

### `capture_screenshot()`

```python
def capture_screenshot(output_path: Path, geom: str = None) -> bool:
```

**Purpose:** Captures a full-screen screenshot, optionally cropped to a region. Used by the quick capture workflow (`quick.py`) where no region selection is needed.

**Parameters:**

- `output_path: Path` — Where to save the PNG.
- `geom: str | None` — Optional geometry string. If provided, crops to this region. If `None`, captures the entire screen.

**Return value:** `bool` — `True` if the screenshot was captured successfully, `False` otherwise.

**Call flow:**

1. **If `geom` is provided:**
   - Parse the geometry string.
   - If parsing succeeds, run `grim -g "x,y wxh" output_path`.
   - If parsing fails, fall through to full-screen capture.

2. **If `geom` is `None` or parsing failed:**
   - Run `grim output_path` — captures the entire composite desktop.

**Differences from `capture_region()`:**

| Aspect | `capture_region()` | `capture_screenshot()` |
|--------|-------------------|----------------------|
| Interactive selection | Yes (launches `slurp`) | No |
| Returns | Geometry string | Boolean success |
| Delay after slurp | 100ms | None (no slurp involved) |
| Use case | Mining pipeline | Quick/instant capture |
| Logging | Logs geometry | Silent on success |

**Error handling:**

- `subprocess.CalledProcessError` — Logged at `error` level. Returns `False`.
- Geometry parsing failure — Falls through to full-screen capture instead of returning failure.

**Note:** This function silently redirects `grim`'s stdout/stderr to `/dev/null` via `capture_output=True`, so error messages from `grim` are swallowed. Only subprocess-level errors (non-zero exit) are detected.

---

## How Other Modules Use Capture

### `pipeline/mine.py` — Standard mining

```python
from miner.capture import capture_region

# In mine_sentence():
geom = capture_region(screenshot_path)
if not geom:
    return None  # User cancelled or capture failed
```

The mining pipeline calls `capture_region()` without a geometry, forcing interactive selection. The returned geometry is stored in the sentence entry metadata for potential re-capture.

### `pipeline/quick.py` — Quick/instant capture

```python
from miner.capture import capture_screenshot

# In quick_capture():
success = capture_screenshot(screenshot_path, geom=zone_geom if zone_mode else None)
```

Quick capture calls `capture_screenshot()` with an optional pre-defined geometry (from saved zones or command-line `--zone` flag). No interactive selection.

### `ui/overlay.py` — Live OCR overlay

```python
from miner.capture import capture_region, get_display_scale

# When user clicks "Select Region":
geom = capture_region(screenshot_path)
if geom:
    scale = get_display_scale()  # For coordinate conversion
```

The overlay lets the user select a region once, then continuously captures that region in a loop (every 2 seconds) for live OCR. The scale factor is used to position overlay elements correctly on HiDPI displays.

### `main.py` — Zone management

```python
# In --save-zone handler:
subprocess.run(["slurp"], ...)  # Calls slurp directly, not through capture module
```

Zone saving uses `slurp` directly rather than going through the capture module, since it only needs the geometry string (not a screenshot).

---

## Data Flow Diagram

```
User presses SUPER+X
        │
        ▼
  mine.sh (shell wrapper)
        │
        ▼
  pipeline/mine.py :: mine_sentence()
        │
        ├── capture_region(None)     ← no geom → launches slurp
        │       │
        │       ├── slurp -b ...     ← user selects region
        │       │       │
        │       │       └── Returns "100,200 300x150"  (or None if cancelled)
        │       │
        │       ├── parse_slurp_geom("100,200 300x150")
        │       │       │
        │       │       └── (100, 200, 300, 150)
        │       │
        │       ├── time.sleep(0.1)  ← compositor settle
        │       │
        │       └── grim -g "100,200 300x150" /path/img.png
        │
        └── Returns geom for entry metadata

User presses SUPER+ALT+CTRL+Q
        │
        ▼
  pipeline/quick.py :: quick_capture()
        │
        └── capture_screenshot(path, geom=None)
                │
                └── grim /path/img.png    ← full screen, no selection
```

---

## Geometry Format Reference

### Slurp output format: `"X,Y WxH"`

```
"560,340 600x400"
│    │   │   │
│    │   │   └── height in pixels
│    │   └────── width in pixels
│    └────────── Y coordinate (from top of screen)
└─────────────── X coordinate (from left of screen)
```

### Comma-separated format: `"X,Y,W,H"`

```
"560,340,600,400"
```

Used in saved zone files and some config options. Easier to parse programmatically.

### ImageMagick format: `"WxH+X+Y"`

```
"600x400+560+340"
```

The plus signs indicate positive offsets from the top-left. Could also be `-` for negative offsets on multi-monitor setups.

---

## Hyprland Monitor Detection

`get_display_scale()` parses `hyprctl monitors -j` output. The relevant JSON structure:

```json
[
  {
    "name": "DP-1",
    "focused": true,
    "scale": 1.5,
    "x": 0,
    "y": 0,
    "width": 2560,
    "height": 1440
  }
]
```

The function finds the focused monitor by iterating the array. If no monitor has `"focused": true`, the entire screen composite may span multiple monitors — grim captures all of them, but the scale factor for any individual monitor may not represent the full capture.

---

## Known Limitations

1. **`MAX_RETRIES` is dead code** — Defined but never referenced. Could be removed.
2. **No content validation** — `capture_region()` does not check if the captured PNG has non-zero size or actual content. A region that's completely off-screen or covered by other windows still returns success.
3. **No retry on failure** — If `grim` fails (e.g. the output directory doesn't exist), the error is logged and `None` is returned. The caller chooses what to do (most abort the pipeline).
4. **Display scale not automatically applied** — `get_display_scale()` is available but `capture_region()` and `capture_screenshot()` do not call it. Callers must apply scaling themselves if needed. This is intentional — different callers have different coordinate systems.
5. **Wayland-only** — No fallback for X11. On X11, `grim`/`slurp` will not be found, and capture will always fail. X11 support would require `import` or `maim`.
