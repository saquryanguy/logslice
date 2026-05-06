"""Enricher: attach derived or static fields to log records."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


class EnrichError(Exception):
    """Raised when enrichment configuration or execution fails."""


@dataclass
class EnrichRule:
    """A single enrichment rule.

    Attributes:
        target_field: Dot-separated path to write the derived value into.
        value: Static value to assign, or None if *fn* is provided.
        fn: Callable that receives the record and returns the value to assign.
        overwrite: If False, skip the rule when *target_field* already exists.
    """

    target_field: str
    value: Optional[Any] = None
    fn: Optional[Callable[[Dict[str, Any]], Any]] = None
    overwrite: bool = True

    def __post_init__(self) -> None:
        if self.value is None and self.fn is None:
            raise EnrichError(
                f"EnrichRule for '{self.target_field}' must specify either "
                "'value' or 'fn'."
            )
        if self.value is not None and self.fn is not None:
            raise EnrichError(
                f"EnrichRule for '{self.target_field}' must specify either "
                "'value' or 'fn', not both."
            )


@dataclass
class EnrichConfig:
    rules: List[EnrichRule] = field(default_factory=list)


def _set_nested(record: Dict[str, Any], path: str, value: Any) -> None:
    """Write *value* into *record* at the dot-separated *path*."""
    parts = path.split(".")
    node: Any = record
    for part in parts[:-1]:
        if not isinstance(node.get(part), dict):
            node[part] = {}
        node = node[part]
    node[parts[-1]] = value


def _has_nested(record: Dict[str, Any], path: str) -> bool:
    """Return True if *path* exists (even if the value is None)."""
    parts = path.split(".")
    node: Any = record
    for part in parts:
        if not isinstance(node, dict) or part not in node:
            return False
        node = node[part]
    return True


def apply_rule(
    record: Dict[str, Any], rule: EnrichRule
) -> Dict[str, Any]:
    """Return a new record with *rule* applied (original is not mutated)."""
    if not rule.overwrite and _has_nested(record, rule.target_field):
        return dict(record)
    result = dict(record)
    resolved = rule.fn(record) if rule.fn is not None else rule.value
    _set_nested(result, rule.target_field, resolved)
    return result


def enrich_records(
    records: List[Dict[str, Any]], config: EnrichConfig
) -> List[Dict[str, Any]]:
    """Apply all rules in *config* to every record and return new list."""
    enriched: List[Dict[str, Any]] = []
    for record in records:
        current = record
        for rule in config.rules:
            current = apply_rule(current, rule)
        enriched.append(current)
    return enriched
