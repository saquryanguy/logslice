"""Archive log records to a structured store, keyed by time bucket and optional tag."""
from __future__ import annotations

import copy
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional


class ArchiveError(Exception):
    """Raised when archival configuration or input is invalid."""


@dataclass
class ArchiveConfig:
    bucket_field: str = "timestamp"
    tag_field: Optional[str] = None
    bucket_fn: Optional[Callable[[str], str]] = None  # maps raw value -> bucket key
    max_buckets: int = 0  # 0 = unlimited

    def __post_init__(self) -> None:
        if not self.bucket_field:
            raise ArchiveError("bucket_field must not be empty")
        if self.max_buckets < 0:
            raise ArchiveError("max_buckets must be >= 0")


@dataclass
class ArchiveResult:
    buckets: Dict[str, List[dict]] = field(default_factory=dict)
    total: int = 0
    bucket_count: int = 0
    dropped: int = 0

    def as_dict(self) -> dict:
        return {
            "total": self.total,
            "bucket_count": self.bucket_count,
            "dropped": self.dropped,
            "buckets": {k: list(v) for k, v in self.buckets.items()},
        }


def _get_field(record: dict, field_name: str) -> Optional[str]:
    """Return a top-level or dot-separated nested field as a string, or None."""
    parts = field_name.split(".")
    cur = record
    for part in parts:
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return str(cur) if cur is not None else None


def archive(
    records: Iterable[dict],
    config: Optional[ArchiveConfig] = None,
) -> ArchiveResult:
    """Group records into named buckets determined by bucket_field (and optional tag_field)."""
    if config is None:
        config = ArchiveConfig()

    buckets: Dict[str, List[dict]] = defaultdict(list)
    total = 0
    dropped = 0

    for record in records:
        total += 1
        raw_bucket = _get_field(record, config.bucket_field)
        if raw_bucket is None:
            dropped += 1
            continue

        bucket_key = config.bucket_fn(raw_bucket) if config.bucket_fn else raw_bucket

        if config.tag_field:
            tag = _get_field(record, config.tag_field) or "_untagged"
            bucket_key = f"{bucket_key}::{tag}"

        if config.max_buckets and bucket_key not in buckets:
            if len(buckets) >= config.max_buckets:
                dropped += 1
                continue

        buckets[bucket_key].append(copy.deepcopy(record))

    return ArchiveResult(
        buckets=dict(buckets),
        total=total,
        bucket_count=len(buckets),
        dropped=dropped,
    )
