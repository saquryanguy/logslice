"""Buffered log record accumulation with size and time-based flushing."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional


class BufferError(Exception):
    """Raised when buffer configuration or operation is invalid."""


@dataclass
class BufferConfig:
    max_size: int = 100
    flush_on_full: bool = True
    on_flush: Optional[Callable[[List[Dict]], None]] = None

    def __post_init__(self) -> None:
        if self.max_size < 1:
            raise BufferError("max_size must be at least 1")


@dataclass
class BufferResult:
    flushed_batches: int
    total_flushed: int
    remaining: List[Dict] = field(default_factory=list)

    def as_dict(self) -> Dict:
        return {
            "flushed_batches": self.flushed_batches,
            "total_flushed": self.total_flushed,
            "remaining_count": len(self.remaining),
        }


def buffer_records(
    records: Iterable[Dict],
    config: Optional[BufferConfig] = None,
) -> BufferResult:
    """Accumulate records into batches, flushing when the buffer is full.

    If *flush_on_full* is True, every time the internal buffer reaches
    *max_size* the *on_flush* callback is invoked (if provided) and the
    buffer is cleared.  Records that did not fill a complete batch are
    returned in *BufferResult.remaining*.
    """
    if config is None:
        config = BufferConfig()

    buf: List[Dict] = []
    flushed_batches = 0
    total_flushed = 0

    for record in records:
        buf.append(record)
        if config.flush_on_full and len(buf) >= config.max_size:
            if config.on_flush is not None:
                config.on_flush(list(buf))
            flushed_batches += 1
            total_flushed += len(buf)
            buf = []

    return BufferResult(
        flushed_batches=flushed_batches,
        total_flushed=total_flushed,
        remaining=buf,
    )
