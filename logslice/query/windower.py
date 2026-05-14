"""Time-window bucketing for log records."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class WindowError(Exception):
    """Raised when windowing configuration or input is invalid."""


@dataclass
class WindowerConfig:
    """Configuration for time-window bucketing."""

    window_seconds: int = 60
    timestamp_field: str = "timestamp"
    # If True, records missing the timestamp field are dropped; otherwise raise.
    skip_missing: bool = False

    def __post_init__(self) -> None:
        if self.window_seconds <= 0:
            raise WindowError("window_seconds must be a positive integer")


@dataclass
class WindowResult:
    """Result of a windowing operation."""

    windows: Dict[int, List[Dict[str, Any]]] = field(default_factory=dict)
    total: int = 0
    dropped: int = 0

    def as_dict(self) -> Dict[str, Any]:
        return {
            "windows": {str(k): v for k, v in self.windows.items()},
            "total": self.total,
            "dropped": self.dropped,
            "window_count": len(self.windows),
        }


def _bucket_key(timestamp: float, window_seconds: int) -> int:
    """Return the epoch-second start of the window containing *timestamp*."""
    ts = int(timestamp)
    return ts - (ts % window_seconds)


def window_records(
    records: List[Dict[str, Any]],
    config: Optional[WindowerConfig] = None,
) -> WindowResult:
    """Bucket *records* into fixed-size time windows.

    Args:
        records: Sequence of log record dicts.
        config:  Windowing configuration; defaults to 60-second windows.

    Returns:
        A :class:`WindowResult` mapping window-start timestamps to record lists.

    Raises:
        WindowError: If a record is missing the timestamp field and
            ``skip_missing`` is *False*.
    """
    if config is None:
        config = WindowerConfig()

    result: WindowResult = WindowResult()

    for record in records:
        result.total += 1
        raw = record.get(config.timestamp_field)
        if raw is None:
            if config.skip_missing:
                result.dropped += 1
                continue
            raise WindowError(
                f"Record missing timestamp field '{config.timestamp_field}'"
            )
        try:
            ts = float(raw)
        except (TypeError, ValueError) as exc:
            if config.skip_missing:
                result.dropped += 1
                continue
            raise WindowError(
                f"Cannot parse timestamp value {raw!r} as a number"
            ) from exc

        key = _bucket_key(ts, config.window_seconds)
        result.windows.setdefault(key, []).append(record)

    return result
