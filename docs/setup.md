# Setup & Running Instructions

## System Requirements

- **OS:** Arch Linux (or any Linux with Wayland)
- **Display Server:** Wayland (Hyprland recommended)
- **Python:** >= 3.10

---

## 1. Install System Dependencies

```bash
# Core tools
sudo pacman -S grim slurp tesseract tesseract-data-{eng,chi_sim,jpn,kor,deu,fra,spa,ell,pol,rus} \
  ffmpeg wl-clipboard pipewire wireplumber pulseaudio-utils

# Optional but recommended
sudo pacman -S python-pip python-pillow python-numpy tk
```

### Verify system dependencies

```bash
python3 -m miner --health
```

This checks that all external commands (`grim`, `slurp`, `tesseract`, `ffmpeg`,
`wl-copy`, `pactl`) are available and working.

---

## 2. Install the Python Package

### From cloned repo (development install)

```bash
git clone https://github.com/Je0Dev/miner_languages.git
cd miner_languages

# Install with pip (recommended)
pip install -e . --break-system-packages

# Or install dependencies only
pip install -r requirements.txt --break-system-packages
```

### Verify Python dependencies

```bash
python3 -c "from miner.translate import translate_text, speak_text; from miner.text import get_pronunciation; print('OK')"
```

> **Note:** `--break-system-packages` is required on modern Arch Linux
> (PEP 668). Use a virtualenv if you prefer:
> ```bash
> python3 -m venv .venv
> source .venv/bin/activate
> pip install -e .
> ```

---

## 3. Run the Tests

```bash
cd miner_languages
PYTHONPATH=src python3 tests/run_tests.py
```

This runs 147+ tests across all modules (OCR, translation, text processing,
capture zones, Anki export, etc.). Tests that require a Wayland session
(`wl-copy`) will be skipped gracefully.

---

## 4. Basic Usage

### Health check

```bash
python3 main.py --health
```

### Capture a region and mine a sentence

1. Press the keybinding for your language (e.g. `SUPER+N` for Chinese)
2. Click and drag to select a screen region
3. The tool will: capture → OCR → clean → translate → save → notify

### Quick full-screen capture

```bash
python3 main.py --quick
```

### Live OCR overlay

```bash
python3 main.py --live
```

Opens a draggable Tkinter window that continuously OCRs the area behind it.

---

## 5. Keybindings (Hyprland)

The `scripts/mining_bindings.conf` file contains 50+ Hyprland keybindings
for all mining workflows. Source it from your Hyprland config:

```conf
# In ~/.config/hypr/hyprland.conf
source = ~/miner_languages/scripts/mining_bindings.conf
```

### Default keybinding categories

| Prefix | Action |
|--------|--------|
| `SUPER+N` | Mine sentence (current language) |
| `SUPER+SHIFT+N` | Quick capture |
| `SUPER+CTRL+N` | Live OCR overlay |
| `SUPER+ALT+N` | Multi-region capture |
| `SUPER+B` | Toggle Yomitan bridge |
| `SUPER+M` | Toggle clipboard monitor |
| `SUPER+K` | Start/stop sentence server |

Per-language variants use the language initial:
- `SUPER+Z` = Chinese, `SUPER+J` = Japanese, `SUPER+K` = Korean
- `SUPER+E` = English, `SUPER+F` = French, `SUPER+D` = German
- `SUPER+R` = Russian, `SUPER+S` = Spanish

---

## 6. Running Without Hyprland

The tool works with any Wayland compositor, but you'll need to:

1. Bind the CLI commands to your own keybindings
2. Ensure `grim` and `slurp` work in your environment

Example standalone commands:

```bash
# Capture & mine a sentence (Chinese)
cd ~/miner_languages
python3 main.py --lang zh

# Translate clipboard text
echo "你好世界" | wl-copy
python3 -c "
import sys; sys.path.insert(0, 'src')
from miner.translate import translate_text, speak_text
from miner.text import get_pronunciation
t = translate_text('你好世界', 'zh', 'en')
print('Translation:', t)
speak_text(t, 'en')
"
```

---

## 7. Using the Translate + TTS Pipeline

```python
from miner.translate import translate_text, speak_text
from miner.text import get_pronunciation

# Translate English to Chinese
result = translate_text("Good morning", "auto", "zh-CN")
print(result)  # 早上好

# Get pinyin pronunciation
pinyin = get_pronunciation(result, "zh")
print(pinyin)  # zao3 shang4 hao3

# Hear it spoken aloud
speak_text(result, "zh")  # Xiaoxiao voice (Chinese)
```

### Supported TTS Voices

| Language | Code | Voice |
|----------|------|-------|
| Chinese  | zh   | XiaoxiaoNeural |
| Japanese | ja   | NanamiNeural |
| Korean   | ko   | SunHiNeural |
| German   | de   | KatjaNeural |
| French   | fr   | DeniseNeural |
| Spanish  | es   | ElviraNeural |
| Greek    | el   | AthinaNeural |
| Polish   | pl   | ZofiaNeural |
| Russian  | ru   | SvetlanaNeural |
| English  | en   | AriaNeural |

---

## 8. Exporting to Anki

```bash
# Export all mined sentences to CSV
python3 main.py --export-anki

# Export as JSON
python3 main.py --export-json

# Export as Excel
python3 main.py --export-excel
```

---

## 9. Running the Sentence Server

```bash
python3 main.py --server
```

Opens a Flask web server at `http://localhost:5000` with:
- Sentence browser with search/filter
- Per-language views
- Yomitan integration API
- Audio playback of recorded game audio

---

## 10. Troubleshooting

### "wl-copy not found"
Install `wl-clipboard`: `sudo pacman -S wl-clipboard`

### "Tesseract not found"
Install tesseract and language data:
```bash
sudo pacman -S tesseract tesseract-data-eng tesseract-data-chi_sim
```

### "deep-translator translation returns empty"
The `_clean_translation()` function previously stripped non-ASCII characters
for all destinations. Update to the latest version (fix included).

### "edge-tts command not found"
```bash
pip install edge-tts --break-system-packages
```

### "pip install fails with PEP 668"
Use `--break-system-packages` flag or set up a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Tests fail on clipboard operations
The `wl-copy` command requires a Wayland session. Tests that use it will
timeout in non-Wayland environments. This is expected.
