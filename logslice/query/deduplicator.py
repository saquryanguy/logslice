"""Deduplication of log records based on configurable key fields."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, List, Optional, Tuple


class DeduplicatorError(Exception):
    """Raised when deduplication configuration is invalid."""


@dataclass
class DeduplicatorConfig:
    """Configuration for log record deduplication."""

    key_fields: List[str] = field(default_factory=lambda: ["message", "level", "service"])
    max_seen: Optional[int] = None  # cap memory usage; None means unlimited


@dataclass
class DeduplicationResult:
    """Result of a deduplication pass."""

    records: List[dict]
    total_input: int
    duplicates_removed: int

    def as_dict(self) -> dict:
        return {
            "total_input": self.total_input,
            "duplicates_removed": self.duplicates_removed,
            "unique_count": len(self.records),
        }


def _make_key(record: dict, key_fields: List[str]) -> Tuple[Any, ...]:
    """Build a hashable key from the specified fields of a record."""
    return tuple(record.get(f) for f in key_fields)


def _validate_config(config: DeduplicatorConfig) -> None:
    if not config.key_fields:
        raise DeduplicatorError("key_fields must contain at least one field")
    if config.max_seen is not None and config.max_seen < 1:
        raise DeduplicatorError("max_seen must be a positive integer or None")


def deduplicate(
    records: Iterable[dict],
    config: Optional[DeduplicatorConfig] = None,
) -> DeduplicationResult:
    """Remove duplicate records based on key fields.

    Args:
        records: Iterable of log record dicts.
        config: Deduplication configuration. Uses defaults if not provided.

    Returns:
        DeduplicationResult with unique records and counts.

    Raises:
        DeduplicatorError: If configuration is invalid.
    """
    if config is None:
        config = DeduplicatorConfig()

    _validate_config(config)

    seen: dict[Tuple[Any, ...], int] = {}
    unique: List[dict] = []
    total = 0
    duplicates = 0

    for record in records:
        total += 1
        key = _make_key(record, config.key_fields)

        if key in seen:
            duplicates += 1
            seen[key] += 1
        else:
            if config.max_seen is not None and len(seen) >= config.max_seen:
                # Evict oldest entry to stay within memory cap
                oldest = next(iter(seen))
                del seen[oldest]
            seen[key] = 1
            unique.append(record)

    return DeduplicationResult(
        records=unique,
        total_input=total,
        duplicates_removed=duplicates,
    )
