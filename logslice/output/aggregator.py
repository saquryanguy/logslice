"""Aggregate log records and compute summary statistics."""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional


@dataclass
class AggregationResult:
    total: int = 0
    by_level: Dict[str, int] = field(default_factory=dict)
    by_service: Dict[str, int] = field(default_factory=dict)
    first_ts: Optional[str] = None
    last_ts: Optional[str] = None
    field_counts: Dict[str, Counter] = field(default_factory=lambda: defaultdict(Counter))

    def as_dict(self) -> Dict[str, Any]:
        return {
            "total": self.total,
            "by_level": dict(self.by_level),
            "by_service": dict(self.by_service),
            "first_ts": self.first_ts,
            "last_ts": self.last_ts,
        }


def aggregate(
    records: Iterable[Dict[str, Any]],
    group_by_fields: Optional[List[str]] = None,
) -> AggregationResult:
    """Consume an iterable of log records and return aggregated stats.

    Args:
        records: Iterable of parsed log dicts.
        group_by_fields: Extra top-level fields to count distinct values for.
    """
    result = AggregationResult()
    level_counter: Counter = Counter()
    service_counter: Counter = Counter()
    extra_fields = group_by_fields or []

    for record in records:
        result.total += 1

        level = record.get("level") or record.get("severity") or "unknown"
        level_counter[str(level).lower()] += 1

        service = record.get("service") or record.get("app") or "unknown"
        service_counter[str(service)] += 1

        ts = record.get("timestamp") or record.get("ts") or record.get("time")
        if ts is not None:
            ts_str = str(ts)
            if result.first_ts is None:
                result.first_ts = ts_str
            result.last_ts = ts_str

        for f in extra_fields:
            val = record.get(f)
            if val is not None:
                result.field_counts[f][str(val)] += 1

    result.by_level = dict(level_counter)
    result.by_service = dict(service_counter)
    return result
