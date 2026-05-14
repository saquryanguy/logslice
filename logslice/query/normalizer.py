"""Normalize log records by standardizing field names and values."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


class NormalizeError(Exception):
    """Raised when normalization configuration is invalid."""


@dataclass
class NormalizeRule:
    """A single normalization rule mapping a source field to a canonical form."""

    source: str
    target: str
    transform: Optional[Callable[[Any], Any]] = None

    def __post_init__(self) -> None:
        if not self.source:
            raise NormalizeError("source field name must not be empty")
        if not self.target:
            raise NormalizeError("target field name must not be empty")


@dataclass
class NormalizeConfig:
    """Configuration for the normalizer."""

    rules: List[NormalizeRule] = field(default_factory=list)
    drop_source: bool = True


@dataclass
class NormalizeResult:
    """Result of a normalization pass."""

    records: List[Dict[str, Any]]
    total: int
    rules_applied: int

    def as_dict(self) -> Dict[str, Any]:
        return {
            "total": self.total,
            "rules_applied": self.rules_applied,
            "records": self.records,
        }


def _apply_rule(record: Dict[str, Any], rule: NormalizeRule, drop_source: bool) -> tuple[Dict[str, Any], bool]:
    """Apply a single rule to a record. Returns (new_record, was_applied)."""
    if rule.source not in record:
        return record, False

    result = dict(record)
    value = result[rule.source]

    if rule.transform is not None:
        value = rule.transform(value)

    result[rule.target] = value

    if drop_source and rule.source != rule.target:
        del result[rule.source]

    return result, True


def normalize(records: List[Dict[str, Any]], config: NormalizeConfig) -> NormalizeResult:
    """Apply all normalization rules to each record."""
    if not config.rules:
        return NormalizeResult(records=list(records), total=len(records), rules_applied=0)

    normalized: List[Dict[str, Any]] = []
    total_applied = 0

    for record in records:
        current = record
        for rule in config.rules:
            current, applied = _apply_rule(current, rule, config.drop_source)
            if applied:
                total_applied += 1
        normalized.append(current)

    return NormalizeResult(records=normalized, total=len(normalized), rules_applied=total_applied)
