#!/bin/bash
# Quick Capture wrapper - instant full-screen capture for fast NPC dialogue
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYTHON="${PYTHON:-python3}"

# Prevent multiple instances
LOCK_FILE="/tmp/miner-quick.lock"
if [ -f "$LOCK_FILE" ]; then
    exit 0
fi
touch "$LOCK_FILE"
trap "rm -f $LOCK_FILE" EXIT

OCR_LANG="zh"; TRANSLATE_TO="en"; ZONE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -l) OCR_LANG="$2"; shift 2 ;;
        -t) TRANSLATE_TO="$2"; shift 2 ;;
        --zone) ZONE="$2"; shift 2 ;;
        --long-text) LONG_TEXT="--long-text"; shift ;;
        -h) echo "Usage: $0 [-l LANG] [-t LANG] [--zone NAME]"; exit 0 ;;
        *) echo "Unknown: $1"; exit 1 ;;
    esac
done

PYTHONPATH="$PROJECT_ROOT/src" $PYTHON -m miner \
    -l $OCR_LANG -t $TRANSLATE_TO \
    $([ -n "$ZONE" ] && echo "--zone $ZONE") \
    $([ "$LONG_TEXT" = "--long-text" ] && echo "--long-text")
