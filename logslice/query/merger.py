"""Merge multiple streams of log records into a single ordered sequence."""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from typing import Iterable, Iterator, List, Optional


class MergerError(Exception):
    """Raised when merger configuration or input is invalid."""


@dataclass
class MergerConfig:
    """Configuration for merging log record streams."""

    sort_key: str = "timestamp"
    descending: bool = False
    skip_missing_key: bool = True


@dataclass
class MergeResult:
    """Result of a merge operation."""

    records: List[dict] = field(default_factory=list)
    total: int = 0
    stream_count: int = 0

    def as_dict(self) -> dict:
        return {
            "total": self.total,
            "stream_count": self.stream_count,
            "records": self.records,
        }


def _get_key(record: dict, key: str, descending: bool) -> tuple:
    """Return a sortable tuple for heap comparison."""
    value = record.get(key)
    if value is None:
        # Push records with missing keys to the end
        return (1, None) if not descending else (0, None)
    try:
        comparable = (0, str(value))
    except Exception:
        comparable = (1, None)
    if descending:
        # Invert ordering by negating the tier and wrapping value
        return (comparable[0], value)
    return comparable


def iter_merged(
    streams: Iterable[Iterable[dict]],
    config: Optional[MergerConfig] = None,
) -> Iterator[dict]:
    """Lazily yield records from multiple streams in sorted order.

    Uses a min-heap over stream iterators so only one record per stream
    is held in memory at a time.
    """
    if config is None:
        config = MergerConfig()

    heap: list = []
    iters = [iter(s) for s in streams]

    for stream_idx, it in enumerate(iters):
        try:
            record = next(it)
            sort_val = _get_key(record, config.sort_key, config.descending)
            heapq.heappush(heap, (sort_val, stream_idx, record, it))
        except StopIteration:
            pass

    while heap:
        sort_val, stream_idx, record, it = heapq.heappop(heap)
        if config.skip_missing_key or record.get(config.sort_key) is not None:
            yield record
        try:
            next_record = next(it)
            next_val = _get_key(next_record, config.sort_key, config.descending)
            heapq.heappush(heap, (next_val, stream_idx, next_record, it))
        except StopIteration:
            pass


def merge(
    streams: Iterable[Iterable[dict]],
    config: Optional[MergerConfig] = None,
) -> MergeResult:
    """Merge multiple record streams into a MergeResult."""
    stream_list = list(streams)
    if not stream_list:
        raise MergerError("At least one stream must be provided.")

    records = list(iter_merged(stream_list, config))
    return MergeResult(
        records=records,
        total=len(records),
        stream_count=len(stream_list),
    )
