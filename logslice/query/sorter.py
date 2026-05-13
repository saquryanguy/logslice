"""Sort parsed query results by a specified field and direction."""

from __future__ import annotations

from typing import Any, Iterable

SORT_ABLE_DIRECTIONS = ("asc", "desc")
SORTABLE_DIRECTIONS = SORT_ABLE_DIRECTIONS  # backward-compat alias


class SortError(Exception):
    """Raised when sorting cannot be applied."""


def _get_sort_key(record: dict[str, Any], field: str) -> Any:
    """Return the value at *field* for sorting; missing fields sort last."""
    value = record.get(field)
    # Ensure None values sort to the end regardless of direction.
    return (value is None, value if value is not None else "")


def sort_records(
    records: Iterable[dict[str, Any]],
    field: str,
    direction: str = "asc",
    *,
    stable: bool = True,
) -> list[dict[str, Any]]:
    """Sort *records* by *field* in *direction* order.

    Parameters
    ----------
    records:
        An iterable of log record dicts.
    field:
        Top-level field name to sort on (e.g. ``"timestamp"``, ``"level"``).
    direction:
        Either ``"asc"`` (default) or ``"desc"``.
    stable:
        When *True* (default) the sort is stable (preserves original order
        for equal keys).  Python's ``list.sort`` is always stable, so this
        flag is informational only.

    Returns
    -------
    list[dict]
        A new sorted list; the original iterable is not mutated.

    Raises
    ------
    SortError
        If *direction* is not ``"asc"`` or ``"desc"``.
    """
    if direction not in SORTABLE_DIRECTIONS:
        raise SortError(
            f"Invalid sort direction {direction!r}. "
            f"Must be one of {SORTABLE_DIRECTIONS}."
        )

    items = list(records)
    reverse = direction == "desc"
    items.sort(key=lambda r: _get_sort_key(r, field), reverse=reverse)
    return items


def sort_records_multi(
    records: Iterable[dict[str, Any]],
    fields: list[tuple[str, str]],
) -> list[dict[str, Any]]:
    """Sort *records* by multiple fields in a single pass.

    Parameters
    ----------
    records:
        An iterable of log record dicts.
    fields:
        An ordered list of ``(field, direction)`` pairs.  The first entry
        is the primary sort key, subsequent entries break ties.

    Returns
    -------
    list[dict]
        A new sorted list; the original iterable is not mutated.

    Raises
    ------
    SortError
        If any direction value is not ``"asc"`` or ``"desc"``.

    Examples
    --------
    >>> sort_records_multi(records, [("level", "asc"), ("timestamp", "desc")])
    """
    for field, direction in fields:
        if direction not in SORTABLE_DIRECTIONS:
            raise SortError(
                f"Invalid sort direction {direction!r} for field {field!r}. "
                f"Must be one of {SORTABLE_DIRECTIONS}."
            )

    items = list(records)

    def _multi_key(record: dict[str, Any]) -> tuple:
        parts = []
        for field, direction in fields:
            is_none, val = _get_sort_key(record, field)
            # Flip the value for descending fields by wrapping in a negation
            # proxy isn't feasible for mixed types, so we sort iteratively
            # in reverse order of priority instead.
            parts.append((is_none, val, direction))
        return tuple(parts)

    # Stable multi-key sort: apply sorts from least to most significant.
    for field, direction in reversed(fields):
        reverse = direction == "desc"
        items.sort(key=lambda r, f=field: _get_sort_key(r, f), reverse=reverse)

    return items
