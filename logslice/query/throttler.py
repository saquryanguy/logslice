"""Rate-based throttling for log record streams."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List


class ThrottlerError(Exception):
    """Raised when throttler configuration is invalid."""


@dataclass
class ThrottlerConfig:
    """Configuration for the throttler."""

    max_per_window: int
    """Maximum number of records to allow per window."""

    window_field: str = "timestamp"
    """Field used to determine the time window boundary (string prefix, e.g. '2024-01-01T12')."""

    window_granularity: int = 13
    """
    Number of characters from *window_field* that define a window bucket.
    Default 13 covers 'YYYY-MM-DDTHH' (hourly buckets).
    """


@dataclass
class ThrottleResult:
    """Result of a throttle operation."""

    records: List[dict]
    total_input: int
    total_dropped: int


def as_dict(result: ThrottleResult) -> dict:
    """Serialise a ThrottleResult to a plain dictionary."""
    return {
        "records": result.records,
        "total_input": result.total_input,
        "total_dropped": result.total_dropped,
    }


def _validate_config(cfg: ThrottlerConfig) -> None:
    if cfg.max_per_window < 1:
        raise ThrottlerError("max_per_window must be at least 1")
    if cfg.window_granularity < 1:
        raise ThrottlerError("window_granularity must be at least 1")


def throttle(
    records: Iterable[dict],
    config: ThrottlerConfig | None = None,
) -> ThrottleResult:
    """Return at most *max_per_window* records per window bucket.

    Records that exceed the cap for their bucket are dropped.
    Order of input is preserved.
    """
    if config is None:
        config = ThrottlerConfig(max_per_window=100)

    _validate_config(config)

    bucket_counts: dict[str, int] = {}
    kept: List[dict] = []
    total_input = 0
    total_dropped = 0

    for record in records:
        total_input += 1
        raw = record.get(config.window_field, "")
        bucket = str(raw)[: config.window_granularity]
        count = bucket_counts.get(bucket, 0)
        if count < config.max_per_window:
            bucket_counts[bucket] = count + 1
            kept.append(record)
        else:
            total_dropped += 1

    return ThrottleResult(
        records=kept,
        total_input=total_input,
        total_dropped=total_dropped,
    )
