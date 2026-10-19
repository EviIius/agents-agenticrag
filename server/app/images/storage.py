"""Observe private case storage; logical and inode allocation are distinct."""

import os
import stat
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any


class StorageMeter:
    """Sample one private case tree. This is diagnostic accounting, not a sandbox.

    Logical bytes count every pathname; unique bytes deduplicate hard-linked
    inodes. st_blocks is the kernel's allocation report, not APFS shared extents.
    Sampling can miss short-lived files: reports explicitly say observed peak.
    Call sample at durable write/rename barriers as well as on a bounded timer.
    """

    def __init__(
        self, root: Path, *, clock: Callable[[], float] = time.monotonic, limit: int = 4096
    ) -> None:
        if root.is_symlink() or not root.is_dir() or limit < 1:
            raise ValueError("A private case directory and positive sample limit are required")
        self.root = root.resolve(strict=True)
        self.clock, self.limit = clock, limit
        self.started = clock()
        self.samples: list[dict[str, int | float]] = []

    def sample(self) -> dict[str, int | float]:
        if len(self.samples) >= self.limit:
            raise ValueError("Storage sample budget exhausted")
        logical, unique, allocated, files = 0, 0, 0, 0
        inodes: set[tuple[int, int]] = set()
        pending = [self.root]
        while pending:
            directory = pending.pop()
            if directory.is_symlink():
                raise ValueError("Storage measurement refuses symlinks")
            with os.scandir(directory) as entries:
                for entry in entries:
                    try:
                        info = entry.stat(follow_symlinks=False)
                    except FileNotFoundError:
                        # Concurrent atomic rename; next barrier sample repairs it.
                        continue
                    if stat.S_ISLNK(info.st_mode):
                        raise ValueError("Storage measurement refuses symlinks")
                    if stat.S_ISDIR(info.st_mode):
                        pending.append(Path(entry.path))
                    elif stat.S_ISREG(info.st_mode):
                        files += 1
                        if files > 10000:
                            raise ValueError("Storage file budget exhausted")
                        logical += info.st_size
                        inode = (info.st_dev, info.st_ino)
                        if inode not in inodes:
                            inodes.add(inode)
                            unique += info.st_size
                            allocated += info.st_blocks * 512
                    else:
                        raise ValueError("Unexpected non-regular case file")
        row = {
            "seconds": self.clock() - self.started,
            "logical_bytes": logical,
            "unique_inode_bytes": unique,
            "reported_allocated_bytes": allocated,
            "file_count": files,
            "unique_inode_count": len(inodes),
        }
        self.samples.append(row)
        return row

    def report(self) -> dict[str, Any]:
        if not self.samples:
            raise ValueError("No storage observations were recorded")
        return {
            "samples": list(self.samples),
            "peak_observed_logical_bytes": max(s["logical_bytes"] for s in self.samples),
            "peak_observed_unique_inode_bytes": max(s["unique_inode_bytes"] for s in self.samples),
            "peak_observed_reported_allocated_bytes": max(
                s["reported_allocated_bytes"] for s in self.samples
            ),
            "largest_sample_gap_seconds": max(
                (
                    b["seconds"] - a["seconds"]
                    for a, b in zip(self.samples, self.samples[1:], strict=False)
                ),
                default=0,
            ),
            "limits": (
                "Observed samples, not a proven absolute peak. Logical bytes are not physical "
                "APFS storage; kernel st_blocks does not deduplicate shared clone extents. "
                "No file contents, filenames, paths or model calls are recorded."
            ),
        }
