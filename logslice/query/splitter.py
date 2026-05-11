"""Split a stream of log records into named buckets based on field values."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional


class SplitterError(Exception):
    """Raised when the splitter configuration is invalid."""


@dataclass
class SplitterConfig:
    """Configuration for splitting records into buckets."""

    split_field: str
    """Top-level or dot-separated field whose value determines the bucket."""

    allowed_buckets: Optional[List[str]] = None
    """If set, only these bucket names are kept; others go to *default_bucket*."""

    default_bucket: str = "__other__"
    """Bucket name used when the field is missing or not in *allowed_buckets*."""

    max_buckets: int = 256
    """Hard upper limit on distinct buckets to prevent unbounded memory use."""


@dataclass
class SplitResult:
    """Result of a split operation."""

    buckets: Dict[str, List[dict]] = field(default_factory=dict)
    total: int = 0
    dropped: int = 0  # records beyond max_buckets that could not be placed

    def as_dict(self) -> dict:
        return {
            "buckets": {k: list(v) for k, v in self.buckets.items()},
            "total": self.total,
            "dropped": self.dropped,
            "bucket_count": len(self.buckets),
        }


def _get_field(record: dict, dotted: str) -> Optional[str]:
    """Return a string value from a (possibly nested) field path."""
    parts = dotted.split(".")
    node: object = record
    for part in parts:
        if not isinstance(node, dict):
            return None
        node = node.get(part)
    return str(node) if node is not None else None


def split_records(
    records: Iterable[dict],
    config: SplitterConfig,
) -> SplitResult:
    """Partition *records* into named buckets according to *config*.

    Args:
        records: Iterable of parsed log record dicts.
        config: Controls which field to split on and bucket constraints.

    Returns:
        A :class:`SplitResult` containing the populated buckets.

    Raises:
        SplitterError: If *config* is invalid (e.g. *max_buckets* < 1).
    """
    if config.max_buckets < 1:
        raise SplitterError("max_buckets must be >= 1")
    if not config.split_field:
        raise SplitterError("split_field must not be empty")

    result = SplitResult()

    for record in records:
        result.total += 1
        value = _get_field(record, config.split_field)

        if value is None:
            bucket_name = config.default_bucket
        elif config.allowed_buckets is not None and value not in config.allowed_buckets:
            bucket_name = config.default_bucket
        else:
            bucket_name = value

        if bucket_name not in result.buckets:
            if len(result.buckets) >= config.max_buckets:
                result.dropped += 1
                continue
            result.buckets[bucket_name] = []

        result.buckets[bucket_name].append(record)

    return result
