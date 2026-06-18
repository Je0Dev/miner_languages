#!/usr/bin/env python3
"""Game Sentence Miner v2 - CLI entry point."""
import sys, argparse
from pathlib import Path

from miner.config import LANG_REGISTRY
from miner.zones import list_zones, save_zone, delete_zone
from miner.health import run_health_check, format_health_report
from miner.stats import load_stats, format_stats_report
from miner.backup import create_backup, recover_from_backup, list_backups
from miner.log import log

def main():
    parser = argparse.ArgumentParser(description="Game Sentence Miner v2")
    parser.add_argument("-l", "--lang", choices=LANG_REGISTRY.keys(), default="zh",
                        help="OCR language")
    parser.add_argument("-t", "--translate-to", default="en", help="Translate to")
    parser.add_argument("-a", "--audio-duration", type=int, default=5, help="Audio duration")
    parser.add_argument("-s", "--source", default="Game", help="Source name")
    parser.add_argument("--live", action="store_true", help="Live OCR overlay")
    parser.add_argument("--parallel", action="store_true", help="Multi-engine parallel translation")
    parser.add_argument("--no-clipboard", action="store_true", help="No clipboard")
    parser.add_argument("--long-text", action="store_true", help="Long text mode")
    parser.add_argument("--no-stability", action="store_true", help="Disable MSSIM stability check")
    parser.add_argument("--zone", help="Use saved zone")
    parser.add_argument("--save-zone", metavar="NAME", help="Save zone")
    parser.add_argument("--list-zones", action="store_true", help="List zones")
    parser.add_argument("--delete-zone", metavar="NAME", help="Delete zone")
    parser.add_argument("--multi-region", nargs="+", metavar="ZONE", help="Multi-zone capture")
    parser.add_argument("--health", action="store_true", help="Run health check")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--backup", action="store_true", help="Create backup")
    parser.add_argument("--recover", action="store_true", help="Recover from backup")
    parser.add_argument("--list-backups", action="store_true", help="List backups")
    parser.add_argument("--batch", metavar="DIR", help="Batch process directory")
    parser.add_argument("--export-json", action="store_true", help="Export JSON")
    parser.add_argument("--export-excel", action="store_true", help="Export Excel CSV")
    parser.add_argument("--dashboard", action="store_true", help="Start stats dashboard")
    parser.add_argument("--profiles", action="store_true", help="List game profiles")
    parser.add_argument("--detect-game", action="store_true", help="Detect current game")
    parser.add_argument("--bridge", action="store_true", help="Start Yomitan WebSocket bridge")
    parser.add_argument("--clipboard", action="store_true", help="Start clipboard monitor")
    args = parser.parse_args()

    if args.health:
        checks = run_health_check()
        print(format_health_report(checks))
        return
    if args.stats:
        print(format_stats_report())
        return
    if args.backup:
        create_backup()
        return
    if args.recover:
        recover_from_backup()
        return
    if args.list_backups:
        for b in list_backups(): print(b)
        return
    if args.list_zones:
        for z in list_zones(): print(z)
        return
    if args.save_zone:
        import subprocess
        geom = subprocess.run(["slurp"], capture_output=True, text=True).stdout.strip()
        if geom:
            save_zone(args.save_zone, geom, args.lang)
            print(f"Zone '{args.save_zone}' saved: {geom}")
        return
    if args.delete_zone:
        delete_zone(args.delete_zone)
        return
    if args.batch:
        from miner.pipeline.batch import batch_process
        results = batch_process(Path(args.batch), args.lang, args.translate_to)
        print(f"Processed {len(results)} images")
        return
    if args.export_json:
        from miner.storage.export import export_json
        export_json(); print("JSON exported")
        return
    if args.export_excel:
        from miner.storage.export import export_excel
        export_excel(); print("Excel CSV exported")
        return
    if args.dashboard:
        from miner.ui.dashboard import run_dashboard
        run_dashboard()
        return
    if args.profiles:
        from miner.profiles import list_profiles
        for p in list_profiles():
            print(f"  {p['window_class']}: lang={p['ocr_lang']}, zone={p.get('zone', 'none')}")
        return
    if args.detect_game:
        from miner.profiles import auto_detect_and_apply
        profile = auto_detect_and_apply()
        print(f"Detected: {profile}")
        return
    if args.bridge:
        from miner.yomitan.bridge import run_bridge
        print("Starting Yomitan Bridge on ws://localhost:8766")
        run_bridge()
        return
    if args.clipboard:
        from miner.yomitan.clipboard import monitor_clipboard
        monitor_clipboard(lang=args.lang if args.lang != "zh" else None)
        return

    if args.live:
        from miner.ui.overlay import LiveOCROverlay
        overlay = LiveOCROverlay(ocr_lang=args.lang, translate_to=args.translate_to,
                                  source_name=args.source)
        if args.parallel:
            overlay._parallel_translate = True
        if args.no_stability:
            overlay._stability = None
        overlay.run()
    elif args.multi_region:
        from miner.pipeline.mine import mine_multi_region
        mine_multi_region(ocr_lang=args.lang, translate_to=args.translate_to,
                          audio_duration=args.audio_duration, source_name=args.source,
                          auto_clipboard=not args.no_clipboard, long_text=args.long_text,
                          zones=args.multi_region)
    else:
        from miner.pipeline.mine import mine_sentence
        mine_sentence(ocr_lang=args.lang, translate_to=args.translate_to,
                      audio_duration=args.audio_duration, source_name=args.source,
                      auto_clipboard=not args.no_clipboard, long_text=args.long_text,
                      zone_name=args.zone)

if __name__ == "__main__":
    main()
