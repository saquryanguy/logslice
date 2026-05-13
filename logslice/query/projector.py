"""Field projection — include or exclude specific fields from log records."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class ProjectionError(Exception):
    """Raised when projection configuration is invalid."""


@dataclass
class ProjectorConfig:
    include: Optional[List[str]] = None  # whitelist of dot-separated field paths
    exclude: Optional[List[str]] = None  # blacklist of dot-separated field paths

    def __post_init__(self) -> None:
        if self.include and self.exclude:
            raise ProjectionError(
                "'include' and 'exclude' are mutually exclusive; specify only one."
            )


@dataclass
class ProjectionResult:
    records: List[Dict[str, Any]]
    total: int
    fields_applied: List[str]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "total": self.total,
            "fields_applied": self.fields_applied,
            "records": self.records,
        }


def _get_nested(record: Dict[str, Any], path: str) -> Any:
    parts = path.split(".")
    node: Any = record
    for part in parts:
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def _pick_fields(record: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
    """Return a new record containing only the specified dot-path fields."""
    result: Dict[str, Any] = {}
    for path in fields:
        parts = path.split(".")
        src: Any = record
        dst = result
        for i, part in enumerate(parts):
            if not isinstance(src, dict) or part not in src:
                break
            if i == len(parts) - 1:
                dst[part] = src[part]
            else:
                dst.setdefault(part, {})
                dst = dst[part]
                src = src[part]
    return result


def _drop_fields(record: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
    """Return a shallow-copied record with specified dot-path fields removed."""
    import copy
    result = copy.deepcopy(record)
    for path in fields:
        parts = path.split(".")
        node: Any = result
        for part in parts[:-1]:
            if not isinstance(node, dict) or part not in node:
                node = None
                break
            node = node[part]
        if isinstance(node, dict):
            node.pop(parts[-1], None)
    return result


def project(
    records: List[Dict[str, Any]],
    config: Optional[ProjectorConfig] = None,
) -> ProjectionResult:
    """Apply field projection to a list of records."""
    if config is None:
        config = ProjectorConfig()

    if config.include:
        projected = [_pick_fields(r, config.include) for r in records]
        applied = list(config.include)
    elif config.exclude:
        projected = [_drop_fields(r, config.exclude) for r in records]
        applied = list(config.exclude)
    else:
        projected = [dict(r) for r in records]
        applied = []

    return ProjectionResult(
        records=projected,
        total=len(projected),
        fields_applied=applied,
    )
