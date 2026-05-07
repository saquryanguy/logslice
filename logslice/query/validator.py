"""Validation utilities for parsed queries and query filters."""

from __future__ import annotations

import re
from typing import List

from logslice.query.parser import ParsedQuery, QueryFilter

VALID_OPERATORS = {"eq", "neq", "gt", "gte", "lt", "lte", "regex", "contains"}
MAX_FILTERS = 20
MAX_FIELD_LENGTH = 128
MAX_VALUE_LENGTH = 1024

NUMERIC_OPERATORS = {"gt", "gte", "lt", "lte"}


class ValidationError(Exception):
    """Raised when a query fails validation."""


def _validate_filter(f: QueryFilter) -> List[str]:
    """Return a list of validation error messages for a single filter."""
    errors: List[str] = []

    if not f.field or not isinstance(f.field, str):
        errors.append("Filter field must be a non-empty string.")
    elif len(f.field) > MAX_FIELD_LENGTH:
        errors.append(
            f"Filter field '{f.field[:32]}...' exceeds max length {MAX_FIELD_LENGTH}."
        )

    if f.operator not in VALID_OPERATORS:
        errors.append(
            f"Unknown operator '{f.operator}'. Valid operators: {sorted(VALID_OPERATORS)}."
        )

    value_str = str(f.value) if f.value is not None else ""
    if len(value_str) > MAX_VALUE_LENGTH:
        errors.append(
            f"Filter value for field '{f.field}' exceeds max length {MAX_VALUE_LENGTH}."
        )

    if f.operator == "regex":
        try:
            re.compile(str(f.value))
        except re.error as exc:
            errors.append(f"Invalid regex pattern for field '{f.field}': {exc}.")

    if f.operator in NUMERIC_OPERATORS and f.value is not None:
        try:
            float(f.value)
        except (TypeError, ValueError):
            errors.append(
                f"Operator '{f.operator}' on field '{f.field}' requires a numeric value."
            )

    return errors


def validate_query(query: ParsedQuery) -> None:
    """Validate a ParsedQuery, raising ValidationError if any issues are found."""
    all_errors: List[str] = []

    if query.limit is not None:
        if not isinstance(query.limit, int) or query.limit < 1:
            all_errors.append("Query limit must be a positive integer.")

    if len(query.filters) > MAX_FILTERS:
        all_errors.append(
            f"Query contains {len(query.filters)} filters; maximum allowed is {MAX_FILTERS}."
        )

    for i, f in enumerate(query.filters):
        for err in _validate_filter(f):
            all_errors.append(f"Filter[{i}]: {err}")

    if all_errors:
        raise ValidationError("Query validation failed:\n" + "\n".join(f"  - {e}" for e in all_errors))
