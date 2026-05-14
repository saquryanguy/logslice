"""Correlate log records by a shared key within a time window."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class CorrelatorError(Exception):
    """Raised when correlation configuration or input is invalid."""


@dataclass
class CorrelatorConfig:
    """Configuration for record correlation."""

    key_field: str
    window_seconds: float = 60.0
    min_group_size: int = 2
    timestamp_field: str = "timestamp"

    def __post_init__(self) -> None:
        if not self.key_field:
            raise CorrelatorError("key_field must not be empty")
        if self.window_seconds <= 0:
            raise CorrelatorError("window_seconds must be positive")
        if self.min_group_size < 1:
            raise CorrelatorError("min_group_size must be at least 1")


@dataclass
class CorrelationGroup:
    """A group of correlated log records sharing the same key."""

    key: str
    records: List[Dict[str, Any]] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {"key": self.key, "count": len(self.records), "records": self.records}


@dataclass
class CorrelationResult:
    """Result of a correlation pass."""

    groups: List[CorrelationGroup] = field(default_factory=list)
    total_records: int = 0
    total_groups: int = 0

    def as_dict(self) -> Dict[str, Any]:
        return {
            "total_records": self.total_records,
            "total_groups": self.total_groups,
            "groups": [g.as_dict() for g in self.groups],
        }


def _get_field(record: Dict[str, Any], field_path: str) -> Optional[Any]:
    parts = field_path.split(".")
    node: Any = record
    for part in parts:
        if not isinstance(node, dict):
            return None
        node = node.get(part)
    return node


def correlate(
    records: List[Dict[str, Any]],
    config: Optional[CorrelatorConfig] = None,
) -> CorrelationResult:
    """Group records by key_field within a rolling time window."""
    if config is None:
        config = CorrelatorConfig(key_field="request_id")

    buckets: Dict[str, List[Dict[str, Any]]] = {}

    for record in records:
        key_val = _get_field(record, config.key_field)
        if key_val is None:
            continue
        key = str(key_val)

        ts = _get_field(record, config.timestamp_field)
        bucket = buckets.setdefault(key, [])

        if bucket and ts is not None:
            first_ts = _get_field(bucket[0], config.timestamp_field)
            if first_ts is not None:
                try:
                    if float(ts) - float(first_ts) > config.window_seconds:
                        buckets[key] = []
                        bucket = buckets[key]
                except (TypeError, ValueError):
                    pass

        bucket.append(record)

    groups = [
        CorrelationGroup(key=k, records=v)
        for k, v in buckets.items()
        if len(v) >= config.min_group_size
    ]

    return CorrelationResult(
        groups=groups,
        total_records=sum(len(g.records) for g in groups),
        total_groups=len(groups),
    )
