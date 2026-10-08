"""Private SQLite online backups; a daily local-time timer, never run-state polling."""

import asyncio
import os
import shutil
from collections.abc import Callable
from datetime import datetime, time, timedelta
from pathlib import Path

import aiosqlite

from .db.core import Store
from .schemas import BackupStatus


def next_delay(current: datetime) -> float:
    target = datetime.combine(current.date(), time(3, 30), tzinfo=current.tzinfo)
    if target <= current:
        target += timedelta(days=1)
    # timestamp accounts for the local DST offset when current/target are naive.
    return max(1, target.timestamp() - current.timestamp())


class Backups:
    def __init__(
        self,
        store: Store,
        data: Path,
        clock: Callable[[], datetime] = datetime.now,
        free: Callable[[Path], int] | None = None,
    ) -> None:
        self.store, self.data, self.clock = store, data, clock
        self.free = free or (lambda path: shutil.disk_usage(path).free)
        self.folder = data / "backups"
        self.folder.mkdir(mode=0o700, exist_ok=True)
        self.folder.chmod(0o700)
        self.lock = asyncio.Lock()
        self.warning: str | None = None
        self.task: asyncio.Task[None] | None = None

    def files(self) -> list[Path]:
        return sorted(self.folder.glob("auto-*.db"), key=lambda p: (p.stat().st_mtime, p.name))

    def status(self) -> BackupStatus:
        files = self.files()
        return BackupStatus(
            last_at=datetime.fromtimestamp(files[-1].stat().st_mtime).astimezone().isoformat()
            if files
            else None,
            count=len(files),
            bytes=sum(p.stat().st_size for p in files),
            warning=self.warning,
        )

    async def make(self) -> BackupStatus:
        async with self.lock:
            current = self.clock()
            target = self.folder / current.strftime("auto-%Y%m%d-%H%M.db")
            part = target.with_suffix(".part")
            try:
                size = sum(
                    p.stat().st_size
                    for p in (self.data / "workbench.db", self.data / "workbench.db-wal")
                    if p.exists()
                )
                if self.free(self.data) < 2 * size:
                    self.warning = (
                        "Backup skipped: not enough free disk space. Free space and try again."
                    )
                    return self.status()
                part.touch(mode=0o600, exist_ok=True)
                part.chmod(0o600)
                async with self.store.lock, aiosqlite.connect(part) as destination:
                    copying = asyncio.create_task(self.store.db.backup(destination))
                    try:
                        await asyncio.shield(copying)
                    except asyncio.CancelledError:
                        await copying
                        raise
                # Only expose a complete, durable backup; failed copies stay private.
                with part.open("rb") as handle:
                    os.fsync(handle.fileno())
                os.replace(part, target)
                os.utime(target, (current.timestamp(), current.timestamp()))
                for old in self.files()[:-7]:
                    old.unlink()
                self.warning = None
            except (OSError, aiosqlite.Error):
                self.warning = "Couldn't make a backup. Your chats are unchanged. Try again."
            finally:
                part.unlink(missing_ok=True)
            return self.status()

    async def start(self) -> None:
        for part in self.folder.glob("auto-*.part"):
            part.unlink(missing_ok=True)
        files = self.files()
        if not files or self.clock().timestamp() - files[-1].stat().st_mtime >= 86400:
            await self.make()
        self.task = asyncio.create_task(self.daily())

    async def daily(self) -> None:
        while True:
            await asyncio.sleep(next_delay(self.clock()))
            await self.make()

    async def close(self) -> None:
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
