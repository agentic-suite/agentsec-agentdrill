"""Filesystem + network witnesses (M23 23.2, F87).

A canary file/dir watcher (hash + inode) and a loopback sinkhole (HTTP/DNS/TCP)
with per-run tokens. An effect is seen when it happens; overhead is small.
Design: ``docs/prd/26-independent-effect-witness.md``.
"""

from __future__ import annotations

import hashlib
import os
import statistics
import time
from collections.abc import Callable

from pydantic import BaseModel, Field


class CanaryWatch(BaseModel):
    """A canary file/dir fingerprint before and after an attack."""

    path: str
    before_hash: str
    after_hash: str
    before_inode: int
    after_inode: int

    @property
    def changed(self) -> bool:
        """Whether the canary content or inode changed (the effect was seen)."""
        return self.before_hash != self.after_hash or self.before_inode != self.after_inode


def file_fingerprint(path: str) -> tuple[str, int]:
    """The ``(sha256, inode)`` fingerprint of a file (or of its absence)."""
    target = os.fspath(path)
    if not os.path.exists(target):
        return ("absent", 0)
    with open(target, "rb") as handle:
        digest = hashlib.sha256(handle.read()).hexdigest()
    return (digest, os.stat(target).st_ino)


def watch_canary(path: str, *, before: tuple[str, int], after: tuple[str, int]) -> CanaryWatch:
    """Compare a canary's before/after fingerprints."""
    return CanaryWatch(
        path=path,
        before_hash=before[0],
        after_hash=after[0],
        before_inode=before[1],
        after_inode=after[1],
    )


class Sinkhole(BaseModel):
    """A loopback sinkhole that records attempts, tagged with a per-run token."""

    token: str
    hits: list[str] = Field(default_factory=list)

    def url(self, kind: str = "http") -> str:
        """A loopback sinkhole URL for ``kind`` (http/dns/tcp) carrying the token."""
        return f"{kind}://127.0.0.1/{self.token}"

    def record(self, request: str) -> None:
        """Record a sinkhole hit."""
        self.hits.append(request)


def measure_overhead(fn: Callable[[], object], *, trials: int = 25) -> float:
    """The median wall-time overhead (seconds) of ``fn`` (a witness probe)."""
    samples: list[float] = []
    for _ in range(trials):
        start = time.perf_counter()
        fn()
        samples.append(time.perf_counter() - start)
    return statistics.median(samples)
