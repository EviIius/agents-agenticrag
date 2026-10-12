"""One native invocation. Interactive preference with bounded background starvation."""

import asyncio
import fcntl
import os
from collections import deque
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path


class Capacity:
    def __init__(self, path: Path | None = None) -> None:
        self.interactive: deque[asyncio.Future[None]] = deque()
        self.background: deque[asyncio.Future[None]] = deque()
        self.busy = False
        self.streak = 0
        self.path = path
        self.fd: int | None = None

    def advance(self) -> None:
        if self.busy:
            return
        for queue in (self.interactive, self.background):
            while queue and queue[0].cancelled():
                queue.popleft()
        background = self.background and (not self.interactive or self.streak >= 3)
        queue = self.background if background else self.interactive
        if not queue:
            return
        future = queue.popleft()
        self.busy = True
        self.streak = 0 if background else self.streak + 1
        future.set_result(None)

    @asynccontextmanager
    async def lease(self, *, background: bool = False) -> AsyncIterator[None]:
        future: asyncio.Future[None] = asyncio.get_running_loop().create_future()
        queue = self.background if background else self.interactive
        queue.append(future)
        self.advance()
        acquired = False
        try:
            await future
            acquired = True
            if self.path:
                self.fd = os.open(self.path, os.O_CREAT | os.O_RDWR, 0o600)
                while True:
                    try:
                        fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        break
                    except BlockingIOError:
                        # Cross-process resource lock, never job/status polling.
                        await asyncio.sleep(0.05)
            yield
        finally:
            # Cancellation can arrive after admission but before await resumes.
            if acquired or (future.done() and not future.cancelled()):
                if self.fd is not None:
                    os.close(self.fd)
                    self.fd = None
                self.busy = False
            else:
                future.cancel()
                if future in queue:
                    queue.remove(future)
            self.advance()
