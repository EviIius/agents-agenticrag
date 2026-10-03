"""Watched folder: audio dropped in the inbox comes out transcribed in done.

    inbox/meeting.wav  ->  done/meeting.wav
                           done/meeting.txt   plain text
                           done/meeting.srt   timestamped
                           done/meeting.json  everything, incl. raw Whisper text

A file that cannot be transcribed is moved to failed/ with a .log beside it.
The audio itself is only ever read and moved, never changed or deleted.
"""
from __future__ import annotations

import fcntl
import logging
import logging.handlers
import shutil
import signal
import sys
import tempfile
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, Set, Tuple

from . import audio, doctor, proc
from .config import AUDIO_EXTENSIONS, Config
from .pipeline import OUTPUT_SUFFIXES, transcribe_file

log = logging.getLogger("localtranscribe")

TEMP_SUFFIXES = (".part", ".partial", ".tmp", ".crdownload", ".download",
                 ".icloud", ".!sync", ".filepart")


class Seen(NamedTuple):
    signature: Tuple[int, int]  # (size, mtime_ns)
    since: float                # when this signature was first observed


def unique_stem(folder: Path, stem: str, suffixes) -> str:
    """A stem that collides with nothing already in folder (adds -2, -3, ...)."""
    candidate, n = stem, 1
    while any((folder / (candidate + s)).exists() for s in suffixes):
        n += 1
        candidate = "%s-%d" % (stem, n)
    return candidate


class Watcher:
    def __init__(self, cfg: Config, clock=time.monotonic):
        self.cfg = cfg
        self.clock = clock
        self.seen: Dict[Path, Seen] = {}
        self.stopping = False
        self._skipped: Set[Path] = set()   # logged-once notices
        self._stuck: Set[Path] = set()     # could not be moved; left alone
        self._last_problem_log = 0.0

    # -- finding files that are ready --------------------------------------
    def _is_candidate(self, entry: Path) -> bool:
        name = entry.name
        if name.startswith((".", "~")) or name.lower().endswith(TEMP_SUFFIXES):
            return False
        if entry.suffix.lower() not in AUDIO_EXTENSIONS:
            if entry not in self._skipped:
                self._skipped.add(entry)
                log.info("Ignoring %s: not a recognised audio type", name)
            return False
        return True

    def scan(self) -> List[Tuple[Path, List[str]]]:
        """Files that have finished arriving, oldest first, with any warnings."""
        watcher_cfg = self.cfg["watcher"]
        settle = float(watcher_cfg["settle_seconds"])
        stalled = float(watcher_cfg["stalled_seconds"])
        now = self.clock()
        present: Dict[Path, Seen] = {}
        try:
            entries = sorted(self.cfg.inbox_dir.iterdir())
        except FileNotFoundError:
            self.cfg.ensure_dirs()
            entries = []
        for entry in entries:
            try:
                if not entry.is_file() or entry in self._stuck or not self._is_candidate(entry):
                    continue
                st = entry.stat()
            except OSError:
                continue
            signature = (st.st_size, st.st_mtime_ns)
            previous = self.seen.get(entry)
            if previous is None or previous.signature != signature:
                present[entry] = Seen(signature, now)
            else:
                present[entry] = previous
        self.seen = present

        ready: List[Tuple[Path, List[str]]] = []
        for entry, state in present.items():
            unchanged_for = now - state.since
            if unchanged_for < settle:
                continue
            size = state.signature[0]
            missing = audio.wav_missing_bytes(entry) if size else 0
            if (size == 0 or missing) and unchanged_for < stalled:
                if entry not in self._skipped:
                    self._skipped.add(entry)
                    log.info("%s looks incomplete (%s); waiting for the rest",
                             entry.name, "empty" if size == 0 else "%d bytes short" % missing)
                continue
            warnings = []
            if missing:
                warnings.append(
                    "The WAV header promises %d more bytes than arrived; the "
                    "recording may be cut short. Transcribed what was there." % missing)
            ready.append((entry, warnings))
        ready.sort(key=lambda item: present[item[0]].signature[1])
        return ready

    # -- handling one file -------------------------------------------------
    def process(self, src: Path, warnings: Optional[List[str]] = None) -> bool:
        cfg = self.cfg
        log.info("Transcribing %s", src.name)
        staging = Path(tempfile.mkdtemp(prefix="out-", dir=str(cfg.work_dir)))
        try:
            try:
                result = transcribe_file(src, staging, cfg, warnings=warnings)
            except Exception as exc:  # noqa: BLE001 - every failure is reported
                if self.stopping:
                    log.info("Stopped while transcribing %s; it stays in the inbox", src.name)
                    return False
                self._fail(src, exc, traceback.format_exc())
                return False

            suffixes = (src.suffix,) + OUTPUT_SUFFIXES
            stem = unique_stem(cfg.done_dir, src.stem, suffixes)
            # Transcripts first, audio last: if this is interrupted, the audio
            # is still in the inbox and simply gets transcribed again.
            for suffix in OUTPUT_SUFFIXES:
                shutil.move(str(result.files[suffix]), str(cfg.done_dir / (stem + suffix)))
            shutil.move(str(src), str(cfg.done_dir / (stem + src.suffix)))
        except OSError as exc:
            log.error("Could not file %s into done: %s. Leaving it in the inbox.", src.name, exc)
            self._stuck.add(src)
            return False
        finally:
            shutil.rmtree(staging, ignore_errors=True)
            self.seen.pop(src, None)

        speed = result.duration_seconds / result.elapsed_seconds if result.elapsed_seconds else 0
        log.info("Done %s -> done/%s.txt  (%.1f min of audio in %.0f s, %.1fx realtime)",
                 src.name, stem, result.duration_seconds / 60, result.elapsed_seconds, speed)
        for warning in result.warnings:
            log.warning("%s: %s", src.name, warning)
        return True

    def _fail(self, src: Path, exc: Exception, trace: str) -> None:
        cfg = self.cfg
        log.error("Failed %s: %s", src.name, exc)
        if not src.exists():
            log.error("%s is no longer in the inbox; nothing to move", src.name)
            return
        stem = unique_stem(cfg.failed_dir, src.stem, (src.suffix, ".log"))
        report = (
            "File:   %s\nWhen:   %s\nError:  %s\n\n"
            "The audio was not changed. Fix the cause and move it back into\n"
            "the inbox to try again.\n\nDetails:\n%s"
            % (src.name, datetime.now().astimezone().isoformat(timespec="seconds"), exc, trace))
        try:
            (cfg.failed_dir / (stem + ".log")).write_text(report, encoding="utf-8")
            shutil.move(str(src), str(cfg.failed_dir / (stem + src.suffix)))
        except OSError as move_exc:
            log.error("Could not move %s to failed: %s. Leaving it in the inbox.",
                      src.name, move_exc)
            self._stuck.add(src)

    # -- main loop ---------------------------------------------------------
    def _environment_ok(self) -> bool:
        problems = doctor.blocking_problems(self.cfg)
        if not problems:
            return True
        if self.clock() - self._last_problem_log >= 600 or not self._last_problem_log:
            self._last_problem_log = self.clock()
            log.error("Not transcribing until this is fixed (files wait in the inbox): %s",
                      "; ".join(problems))
        return False

    def run_once(self) -> int:
        """One pass: transcribe everything that is ready. Returns the count."""
        ready = self.scan()
        if not ready or not self._environment_ok():
            return 0
        handled = 0
        for src, warnings in ready:
            if self.stopping:
                break
            self.process(src, warnings)
            handled += 1
        return handled

    def run_forever(self) -> None:
        cfg = self.cfg
        cfg.ensure_dirs()
        self._clear_stale_work()
        log.info("Watching %s", cfg.inbox_dir)
        poll = float(cfg["watcher"]["poll_seconds"])
        while not self.stopping:
            try:
                handled = self.run_once()
            except Exception:  # noqa: BLE001 - keep the watcher alive
                log.exception("Unexpected error; continuing")
                handled = 0
            if not handled:
                self._sleep(poll)
        log.info("Watcher stopped")

    def _sleep(self, seconds: float) -> None:
        end = time.monotonic() + seconds
        while not self.stopping and time.monotonic() < end:
            time.sleep(min(0.5, seconds))

    def _clear_stale_work(self) -> None:
        """Remove scratch left by an interrupted run, unless a job is live."""
        with open(self.cfg.lock_file, "w") as fh:
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                return
            for child in self.cfg.work_dir.iterdir():
                shutil.rmtree(child, ignore_errors=True)
            fcntl.flock(fh, fcntl.LOCK_UN)

    def stop(self, *_args) -> None:
        self.stopping = True
        proc.request_stop()


def setup_logging(cfg: Config) -> None:
    cfg.ensure_dirs()
    fmt = logging.Formatter("%(asctime)s %(levelname)-7s %(message)s", "%Y-%m-%d %H:%M:%S")
    root = logging.getLogger("localtranscribe")
    root.setLevel(logging.INFO)
    root.handlers.clear()
    file_handler = logging.handlers.RotatingFileHandler(
        cfg.logs_dir / "watcher.log", maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(fmt)
    root.addHandler(file_handler)
    if sys.stderr.isatty():
        console = logging.StreamHandler()
        console.setFormatter(fmt)
        root.addHandler(console)


def main(cfg: Config, once: bool = False) -> int:
    setup_logging(cfg)
    # One watcher per data folder: a second copy would only queue behind it.
    instance_lock = open(cfg.data_dir / ".watcher.lock", "w")
    try:
        fcntl.flock(instance_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        message = "Another watcher is already running for %s" % cfg.data_dir
        log.error(message)
        print(message, file=sys.stderr)
        return 1
    watcher = Watcher(cfg)
    signal.signal(signal.SIGTERM, watcher.stop)
    signal.signal(signal.SIGINT, watcher.stop)
    if once:
        # Handle whatever is in the inbox now, then exit.
        cfg.ensure_dirs()
        problems = doctor.blocking_problems(cfg)
        if problems:
            log.error("Cannot transcribe: %s", "; ".join(problems))
            return 1
        poll = float(cfg["watcher"]["poll_seconds"])
        watcher.run_once()
        while watcher.seen and not watcher.stopping:
            watcher._sleep(poll)
            watcher.run_once()
    else:
        watcher.run_forever()
    return 0
