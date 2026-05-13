"""Group log records by one or more fields into named buckets."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


class GrouperError(Exception):
    """Raised when grouping configuration or input is invalid."""


@dataclass
class GrouperConfig:
    """Configuration for the grouper."""

    keys: List[str]
    missing_value: str = "<unknown>"
    max_groups: Optional[int] = None


@dataclass
class GroupResult:
    """Result of a grouping operation."""

    groups: Dict[Tuple[str, ...], List[Dict[str, Any]]] = field(default_factory=dict)
    total: int = 0
    group_count: int = 0
    truncated: bool = False

    def as_dict(self) -> Dict[str, Any]:
        return {
            "groups": {
                "|".join(k): v for k, v in self.groups.items()
            },
            "total": self.total,
            "group_count": self.group_count,
            "truncated": self.truncated,
        }


def _get_field(record: Dict[str, Any], key: str, missing: str) -> str:
    """Retrieve a (possibly nested) field value as a string."""
    parts = key.split(".")
    value: Any = record
    for part in parts:
        if not isinstance(value, dict):
            return missing
        value = value.get(part)
        if value is None:
            return missing
    return str(value)


def group_records(
    records: List[Dict[str, Any]],
    config: GrouperConfig,
) -> GroupResult:
    """Group *records* by the fields specified in *config*.

    Args:
        records: Log records to group.
        config: Grouping configuration.

    Returns:
        A :class:`GroupResult` with records partitioned into buckets.

    Raises:
        GrouperError: If *config.keys* is empty.
    """
    if not config.keys:
        raise GrouperError("GrouperConfig.keys must contain at least one field.")

    groups: Dict[Tuple[str, ...], List[Dict[str, Any]]] = {}
    truncated = False

    for record in records:
        bucket: Tuple[str, ...] = tuple(
            _get_field(record, k, config.missing_value) for k in config.keys
        )
        if bucket not in groups:
            if config.max_groups is not None and len(groups) >= config.max_groups:
                truncated = True
                continue
            groups[bucket] = []
        groups[bucket].append(record)

    return GroupResult(
        groups=groups,
        total=sum(len(v) for v in groups.values()),
        group_count=len(groups),
        truncated=truncated,
    )
