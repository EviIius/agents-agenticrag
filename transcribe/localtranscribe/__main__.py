"""Command line: transcribe one file, run the watcher, or check the setup."""
from __future__ import annotations

import argparse
import signal
import sys
from pathlib import Path

from . import __version__, doctor, launchd, proc, watcher
from .config import load_config
from .pipeline import transcribe_file


EXIT_CANCELLED = 130  # `run` was stopped by SIGTERM or Ctrl-C


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="transcribe", description="Local, offline transcription with whisper.cpp.")
    parser.add_argument("--config", help="path to config.json (default: repo root)")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="transcribe one audio file")
    run.add_argument("file")
    run.add_argument("--out-dir", help="where to write the transcript "
                     "(default: next to the audio file)")
    run.add_argument("--channels", choices=("mix", "split"),
                     help="override the config: mix all channels, or one speaker per channel")
    run.add_argument("--quiet", action="store_true", help="do not print the transcript")

    watch = sub.add_parser("watch", help="watch the inbox folder (what launchd runs)")
    watch.add_argument("--once", action="store_true",
                       help="transcribe what is in the inbox now, then exit")

    doc = sub.add_parser("doctor", help="check binaries, models and folders")
    doc.add_argument("--json", action="store_true",
                     help="print the checks as JSON (for other programs)")
    agent = sub.add_parser("install-agent", help="install and start the launchd watcher")
    agent.add_argument("--plist-only", metavar="PATH",
                       help="write the plist to PATH without loading it")
    sub.add_parser("uninstall-agent", help="stop and remove the launchd watcher")
    sub.add_parser("status", help="show whether the launchd watcher is running")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    cfg = load_config(args.config)

    if args.command == "run":
        src = Path(args.file).expanduser()
        out_dir = Path(args.out_dir).expanduser() if args.out_dir else src.parent
        # SIGTERM / Ctrl-C stop ffmpeg and whisper-cli too, and clean up
        # scratch files, instead of leaving them running in the background.
        for signum in (signal.SIGTERM, signal.SIGINT):
            signal.signal(signum, lambda *_: proc.request_stop())
        try:
            result = transcribe_file(src, out_dir, cfg, channels=args.channels)
        except proc.Stopped:
            print("Transcription cancelled.", file=sys.stderr)
            return EXIT_CANCELLED
        except Exception as exc:  # noqa: BLE001 - report plainly, exit non-zero
            print("Transcription failed: %s" % exc, file=sys.stderr)
            return 1
        if not args.quiet:
            sys.stdout.write(result.text)
        for warning in result.warnings:
            print("Warning: %s" % warning, file=sys.stderr)
        print("Wrote %s (.txt, .srt, .json) in %.0f s"
              % (out_dir / result.stem, result.elapsed_seconds), file=sys.stderr)
        return 0
    if args.command == "watch":
        return watcher.main(cfg, once=args.once)
    if args.command == "doctor":
        cfg.ensure_dirs()
        return doctor.report_json(cfg) if args.json else doctor.report(cfg)
    if args.command == "install-agent":
        if args.plist_only:
            print(launchd.write_plist(cfg, Path(args.plist_only).expanduser()))
            return 0
        return launchd.install(cfg)
    if args.command == "uninstall-agent":
        return launchd.uninstall()
    if args.command == "status":
        return launchd.status()
    return 2


if __name__ == "__main__":
    sys.exit(main())
