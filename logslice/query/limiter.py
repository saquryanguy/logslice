"""Rate-based record limiter: keeps at most N records per time bucket."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


class LimiterError(Exception):
    """Raised when limiter configuration or input is invalid."""


@dataclass
class LimiterConfig:
    """Configuration for the record limiter."""

    max_records: int = 100
    """Maximum total records to keep."""

    bucket_field: str = "level"
    """Field used to group records into buckets."""

    max_per_bucket: int | None = None
    """Optional per-bucket cap; if None, only the global cap applies."""

    def __post_init__(self) -> None:
        if self.max_records <= 0:
            raise LimiterError("max_records must be a positive integer")
        if self.max_per_bucket is not None and self.max_per_bucket <= 0:
            raise LimiterError("max_per_bucket must be a positive integer when set")


@dataclass
class LimitResult:
    """Result produced by :func:`limit`."""

    kept: List[dict] = field(default_factory=list)
    dropped: int = 0
    total: int = 0
    by_bucket: Dict[str, int] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "kept": len(self.kept),
            "dropped": self.dropped,
            "total": self.total,
            "by_bucket": self.by_bucket,
        }


def _get_bucket(record: dict, field_name: str) -> str:
    value = record.get(field_name)
    return str(value) if value is not None else "__unknown__"


def limit(records: List[dict], config: LimiterConfig | None = None) -> LimitResult:
    """Apply global and per-bucket caps to *records*.

    Records are evaluated in order; the first ones that fit within both
    the global ``max_records`` cap and the optional ``max_per_bucket``
    cap are kept.  All others are counted as dropped.
    """
    if config is None:
        config = LimiterConfig()

    result = LimitResult(total=len(records))
    bucket_counts: Dict[str, int] = {}

    for record in records:
        if len(result.kept) >= config.max_records:
            result.dropped += 1
            continue

        bucket = _get_bucket(record, config.bucket_field)
        bucket_counts.setdefault(bucket, 0)

        if config.max_per_bucket is not None and bucket_counts[bucket] >= config.max_per_bucket:
            result.dropped += 1
            continue

        result.kept.append(record)
        bucket_counts[bucket] += 1

    result.by_bucket = dict(bucket_counts)
    return result
