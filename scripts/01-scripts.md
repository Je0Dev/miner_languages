# 01 — Scripts

**`scripts/`** — Shell wrappers and Hyprland config.

All scripts resolve `PROJECT_ROOT` from their own location so they work regardless of `$PWD`. They set `PYTHONPATH` to include `src/` and call `python -m miner` (or specific modules).

## Files

### `mine.sh` — Main mining dispatcher

Wraps `python -m miner` for crop-region mining and live OCR.

| Flag | Default | What it does |
|------|---------|-------------|
| `-l LANG` | `zh` | OCR language code |
| `-t LANG` | `en` | Translate-to language code |
| `-a SEC` | `5` | Audio duration in seconds |
| `--live` | off | Opens live OCR overlay |
| `--long-text` | off | Use long-text OCR mode (PSM 3) |
| `--extended` | off | Sets audio to 15s |
| `--zone NAME` | — | Use a saved capture zone |
| `--parallel` | off | Run all 3 translation engines |
| `--no-stability` | off | Disable MSSIM stability detection |
| `--list-zones` | — | List saved zones and exit |
| `--save-zone NAME` | — | Save current selection as zone |
| `--delete-zone NAME` | — | Delete a saved zone |

**Lock file:** Uses `/tmp/miner-v2.lock` to prevent multiple instances.

**Dep check:** Verifies `grim`, `slurp`, `tesseract`, `ffmpeg`, `wl-copy` before running.

### `quick.sh` — Quick capture wrapper

Same as `mine.sh` but calls `python -m miner` without slurp (instant full-screen capture). Flags: `-l`, `-t`, `--zone`, `--long-text`. Lock at `/tmp/miner-quick.lock`.

### `sentence_server.sh` — Flask server launcher

Starts `python -m miner.storage.server` on port 5002 (or custom `$1`). Manages PID at `/tmp/miner-v2-server.pid` — kills existing instance before starting new one.

### `yomitan-hover.sh` — Hover overlay launcher

Maps Tesseract language codes (`chi_sim`, `jpn`, `deu`, etc.) to short codes (`zh`, `ja`, `de`), kills existing hover instance, launches `python -m miner.ui.hover` in background via `nohup`. Logs to `/tmp/yomitan-hover.log`.

### `mining_bindings.conf` — Hyprland keybindings

53 keybindings. Source in `~/.config/hypr/hyprland.conf`:

```
source = ~/miner-v2/scripts/mining_bindings.conf
```

**Binding groups:**

| Group | Key | Combos | What it does |
|-------|-----|--------|-------------|
| Quick Capture | `X` | 10 variants (SUPER + modifiers for each language) | Region select → OCR → translate → audio → save |
| Extended Capture | `E` | 4 variants | Same but 15s audio |
| Quick Instant | `Q` | 4 variants | Full-screen, no region select |
| Live OCR | `O` | 6 variants | Open live overlay window |
| Yomitan Hover | `Y` | 4 variants | Open tiny OCR hover window |
| Parallel Live | `P` | 2 variants | Live OCR with multi-engine translation |
| Kill All | `K` | 1 | `pkill -f miner-v2 && pkill -f yomitan` |
| Health | `H` | 1 | Run health check, show notification |
| Stats | `S` | 1 | Show mining stats notification |
| Backup | `B` | 1 | Create backup |
| Debug | `D` | 1 | Open debug monitor |
| Server | `V` | 1 | Start Flask sentence server |
| Bridge | `J` | 1 | Start WebSocket Yomitan bridge |
| Open Bridge | `W` | 1 | Server + bridge + open browser |
| Clipboard | `C` | 1 | Start clipboard monitor |

**Window rules** (Hyprland 0.53+ syntax):
- `^Live OCR Miner$` — float, pin, no animation, 0.95 opacity
- `^Yomitan Hover$` — float, pin, no animation, 0.85 opacity
