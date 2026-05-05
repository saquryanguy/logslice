"""Sort parsed query results by a specified field and direction."""

from __future__ import annotations

from typing import Any, Iterable

SORTABLE_DIRECTIONS = ("asc", "desc")


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
