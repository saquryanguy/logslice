"""Summarize a list of log records into human-readable statistics."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class SummaryResult:
    total: int = 0
    by_level: Dict[str, int] = field(default_factory=dict)
    by_service: Dict[str, int] = field(default_factory=dict)
    first_timestamp: str | None = None
    last_timestamp: str | None = None
    unique_fields: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "total": self.total,
            "by_level": self.by_level,
            "by_service": self.by_service,
            "first_timestamp": self.first_timestamp,
            "last_timestamp": self.last_timestamp,
            "unique_fields": self.unique_fields,
        }


def _update_timestamp(result: SummaryResult, ts: str | None) -> None:
    if ts is None:
        return
    if result.first_timestamp is None or ts < result.first_timestamp:
        result.first_timestamp = ts
    if result.last_timestamp is None or ts > result.last_timestamp:
        result.last_timestamp = ts


def summarize(records: List[Dict[str, Any]]) -> SummaryResult:
    """Return a SummaryResult describing *records*."""
    result = SummaryResult()
    fields_seen: set[str] = set()

    for record in records:
        result.total += 1

        level = record.get("level") or record.get("severity")
        if level:
            key = str(level).upper()
            result.by_level[key] = result.by_level.get(key, 0) + 1

        service = record.get("service")
        if service:
            key = str(service)
            result.by_service[key] = result.by_service.get(key, 0) + 1

        _update_timestamp(result, record.get("timestamp") or record.get("ts"))

        fields_seen.update(record.keys())

    result.unique_fields = sorted(fields_seen)
    return result
