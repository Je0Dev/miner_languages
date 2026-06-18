#!/bin/bash
# Game Sentence Miner v2 wrapper
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYTHON="${PYTHON:-python3}"

# Prevent multiple instances using lock file
LOCK_FILE="/tmp/miner-v2.lock"
if [ -f "$LOCK_FILE" ]; then
    exit 0
fi
touch "$LOCK_FILE"
trap "rm -f $LOCK_FILE" EXIT

OCR_LANG="zh"; TRANSLATE_TO="en"; AUDIO_DURATION=5
LIVE=false; LONG_TEXT=false; EXTENDED=false; ZONE=""
PARALLEL=false; NO_STABILITY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -l) OCR_LANG="$2"; shift 2 ;;
        -t) TRANSLATE_TO="$2"; shift 2 ;;
        -a) AUDIO_DURATION="$2"; shift 2 ;;
        --live) LIVE=true; shift ;;
        --long-text) LONG_TEXT=true; shift ;;
        --extended) EXTENDED=true; AUDIO_DURATION=15; shift ;;
        --zone) ZONE="$2"; shift 2 ;;
        --parallel) PARALLEL=true; shift ;;
        --no-stability) NO_STABILITY=true; shift ;;
        --list-zones) PYTHONPATH="$PROJECT_ROOT/src" $PYTHON -m miner --list-zones; exit 0 ;;
        --save-zone) PYTHONPATH="$PROJECT_ROOT/src" $PYTHON -m miner --save-zone "$2"; exit 0 ;;
        --delete-zone) PYTHONPATH="$PROJECT_ROOT/src" $PYTHON -m miner --delete-zone "$2"; exit 0 ;;
        -h) echo "Usage: $0 [-l LANG] [-t LANG] [-a SEC] [--live] [--parallel] [--long-text] [--extended] [--zone NAME]"; exit 0 ;;
        *) echo "Unknown: $1"; exit 1 ;;
    esac
done

for cmd in grim slurp tesseract ffmpeg wl-copy; do
    command -v "$cmd" &>/dev/null || { echo "ERROR: $cmd required"; exit 1; }
done

PYTHONPATH="$PROJECT_ROOT/src" $PYTHON -m miner \
    -l $OCR_LANG -t $TRANSLATE_TO -a $AUDIO_DURATION \
    $([ "$LIVE" = true ] && echo "--live") \
    $([ "$LONG_TEXT" = true ] && echo "--long-text") \
    $([ "$PARALLEL" = true ] && echo "--parallel") \
    $([ "$NO_STABILITY" = true ] && echo "--no-stability") \
    $([ -n "$ZONE" ] && echo "--zone $ZONE")
