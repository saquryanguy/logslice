"""Evaluate parsed queries against log records."""

import re
from typing import Any

from logslice.query.parser import ParsedQuery, QueryFilter


def _get_nested(record: dict, field: str) -> Any:
    """Retrieve a nested field using dot notation."""
    keys = field.split(".")
    value = record
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def _apply_operator(record_val: Any, operator: str, query_val: Any) -> bool:
    if record_val is None:
        return False
    try:
        if operator == "==":
            return record_val == query_val
        elif operator == "!=":
            return record_val != query_val
        elif operator == ">":
            return record_val > query_val
        elif operator == ">=":
            return record_val >= query_val
        elif operator == "<":
            return record_val < query_val
        elif operator == "<=":
            return record_val <= query_val
        elif operator == "~=":
            return bool(re.search(str(query_val), str(record_val)))
    except TypeError:
        return False
    return False


def _filter_matches(record: dict, f: QueryFilter) -> bool:
    val = _get_nested(record, f.field)
    return _apply_operator(val, f.operator, f.value)


def matches(record: dict, query: ParsedQuery) -> bool:
    """Return True if a log record satisfies the parsed query."""
    if query.level is not None:
        rec_level = str(record.get("level", "")).upper()
        if rec_level != query.level:
            return False

    if query.service is not None:
        rec_service = record.get("service", "")
        if rec_service != query.service:
            return False

    return all(_filter_matches(record, f) for f in query.filters)
