"""Redact sensitive fields from log records before output."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


class RedactError(Exception):
    """Raised when redaction configuration is invalid."""


@dataclass
class RedactRule:
    """A single redaction rule targeting one field."""

    field: str
    replacement: str = "***REDACTED***"
    pattern: Optional[str] = None  # if set, only matching substring is replaced
    mask_fn: Optional[Callable[[Any], Any]] = None  # custom masking callable

    def __post_init__(self) -> None:
        if self.pattern is not None and self.mask_fn is not None:
            raise RedactError("Specify either 'pattern' or 'mask_fn', not both.")


@dataclass
class RedactConfig:
    """Configuration for the redactor."""

    rules: List[RedactRule] = field(default_factory=list)
    redact_keys: List[str] = field(default_factory=list)  # shorthand: full-value redact


@dataclass
class RedactResult:
    """Result of a redaction pass."""

    records: List[Dict[str, Any]]
    redacted_count: int  # number of records that had at least one field redacted

    def as_dict(self) -> Dict[str, Any]:
        return {"records": self.records, "redacted_count": self.redacted_count}


def _get_field(record: Dict[str, Any], key: str) -> Any:
    parts = key.split(".", 1)
    value = record.get(parts[0])
    if len(parts) == 2 and isinstance(value, dict):
        return _get_field(value, parts[1])
    return value


def _set_field(record: Dict[str, Any], key: str, value: Any) -> None:
    parts = key.split(".", 1)
    if len(parts) == 2:
        nested = record.setdefault(parts[0], {})
        if isinstance(nested, dict):
            _set_field(nested, parts[1], value)
    else:
        record[parts[0]] = value


def _apply_rule(record: Dict[str, Any], rule: RedactRule) -> bool:
    original = _get_field(record, rule.field)
    if original is None:
        return False
    if rule.mask_fn is not None:
        _set_field(record, rule.field, rule.mask_fn(original))
        return True
    if rule.pattern is not None:
        redacted = re.sub(rule.pattern, rule.replacement, str(original))
        _set_field(record, rule.field, redacted)
        return redacted != str(original)
    _set_field(record, rule.field, rule.replacement)
    return True


def redact(records: List[Dict[str, Any]], config: RedactConfig) -> RedactResult:
    """Apply redaction rules to a list of records."""
    if not config.rules and not config.redact_keys:
        return RedactResult(records=[dict(r) for r in records], redacted_count=0)

    shorthand_rules = [RedactRule(field=k) for k in config.redact_keys]
    all_rules = config.rules + shorthand_rules

    output: List[Dict[str, Any]] = []
    redacted_count = 0

    for record in records:
        copy = dict(record)
        touched = False
        for rule in all_rules:
            if _apply_rule(copy, rule):
                touched = True
        output.append(copy)
        if touched:
            redacted_count += 1

    return RedactResult(records=output, redacted_count=redacted_count)
