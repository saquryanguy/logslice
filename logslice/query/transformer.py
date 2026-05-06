"""Field transformation utilities for log records."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


class TransformError(Exception):
    """Raised when a transformation cannot be applied."""


@dataclass
class TransformRule:
    """Defines a single field transformation."""

    source_field: str
    target_field: str
    fn: Callable[[Any], Any]
    skip_missing: bool = True


@dataclass
class TransformConfig:
    """Configuration for a batch of transform rules."""

    rules: List[TransformRule] = field(default_factory=list)


def _get_field(record: Dict[str, Any], key: str) -> Optional[Any]:
    """Retrieve a top-level field value, returning None if absent."""
    return record.get(key)


def _set_field(record: Dict[str, Any], key: str, value: Any) -> Dict[str, Any]:
    """Return a shallow copy of record with key set to value."""
    updated = dict(record)
    updated[key] = value
    return updated


def apply_rule(record: Dict[str, Any], rule: TransformRule) -> Dict[str, Any]:
    """Apply a single TransformRule to a record.

    Returns a new record dict; does not mutate the original.
    Raises TransformError if the field is missing and skip_missing is False.
    """
    value = _get_field(record, rule.source_field)
    if value is None:
        if rule.skip_missing:
            return dict(record)
        raise TransformError(
            f"Field '{rule.source_field}' not found in record and skip_missing=False."
        )
    try:
        transformed = rule.fn(value)
    except Exception as exc:  # noqa: BLE001
        raise TransformError(
            f"Transformation failed for field '{rule.source_field}': {exc}"
        ) from exc
    return _set_field(record, rule.target_field, transformed)


def transform_record(
    record: Dict[str, Any], config: TransformConfig
) -> Dict[str, Any]:
    """Apply all rules in *config* to *record* sequentially.

    Each rule operates on the output of the previous one.
    """
    current = record
    for rule in config.rules:
        current = apply_rule(current, rule)
    return current


def transform_records(
    records: List[Dict[str, Any]], config: TransformConfig
) -> List[Dict[str, Any]]:
    """Apply transform_record to every record in the list."""
    return [transform_record(r, config) for r in records]
