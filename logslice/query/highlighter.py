"""Highlight matching fields in log records for display purposes."""

from __future__ import annotations

from typing import Any

from logslice.query.parser import ParsedQuery, QueryFilter

ANSI_YELLOW = "\033[33m"
ANSI_RESET = "\033[0m"


def _highlight_value(value: str, bold: bool = False) -> str:
    """Wrap a string value in ANSI highlight codes."""
    prefix = "\033[1;33m" if bold else ANSI_YELLOW
    return f"{prefix}{value}{ANSI_RESET}"


def _highlight_in_string(text: str, term: str) -> str:
    """Case-sensitive highlight of `term` inside `text`."""
    if not term or term not in text:
        return text
    return text.replace(term, _highlight_value(term))


def highlight_record(
    record: dict[str, Any],
    query: ParsedQuery,
    *,
    enabled: bool = True,
) -> dict[str, Any]:
    """Return a shallow copy of *record* with matched field values highlighted.

    Only equality and regex filters on top-level string fields are highlighted.
    Nested fields (containing ``.") are intentionally skipped to keep the
    implementation simple.
    """
    if not enabled or not query.filters:
        return record

    result = dict(record)

    for f in query.filters:
        if "." in f.field:
            continue
        raw = result.get(f.field)
        if raw is None or not isinstance(raw, str):
            continue

        if f.operator in ("=", "=="):
            if str(f.value) == raw:
                result[f.field] = _highlight_value(raw, bold=True)
        elif f.operator == "~=":
            import re

            try:
                result[f.field] = re.sub(
                    str(f.value),
                    lambda m: _highlight_value(m.group(), bold=False),
                    raw,
                )
            except re.error:
                pass
        elif f.operator == "contains":
            result[f.field] = _highlight_in_string(raw, str(f.value))

    return result
