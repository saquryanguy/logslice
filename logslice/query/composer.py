"""Compose multiple ParsedQuery objects into a single query."""

from __future__ import annotations

from typing import Iterable, Optional

from logslice.query.parser import ParsedQuery, QueryFilter


def merge_queries(
    *queries: ParsedQuery,
    limit: Optional[int] = None,
) -> ParsedQuery:
    """Merge filters from all queries into one ParsedQuery.

    The optional *limit* overrides any limits set on individual queries.
    If *limit* is None and exactly one query carries a limit, that value
    is preserved; when multiple queries have limits the smallest wins.

    Raises:
        ValueError: If no queries are provided.
    """
    if not queries:
        raise ValueError("merge_queries requires at least one query")

    merged_filters: list[QueryFilter] = []
    limits: list[int] = []

    for q in queries:
        merged_filters.extend(q.filters)
        if q.limit is not None:
            limits.append(q.limit)

    resolved_limit: Optional[int]
    if limit is not None:
        resolved_limit = limit
    elif limits:
        resolved_limit = min(limits)
    else:
        resolved_limit = None

    return ParsedQuery(filters=merged_filters, limit=resolved_limit)


def negate_query(query: ParsedQuery) -> ParsedQuery:
    """Return a new ParsedQuery where every filter operator is negated.

    Supported negations: eq<->neq, gt<->lte, gte<->lt, regex->not_regex.
    Unrecognised operators are left unchanged.
    """
    _NEGATION_MAP = {
        "eq": "neq",
        "neq": "eq",
        "gt": "lte",
        "lte": "gt",
        "gte": "lt",
        "lt": "gte",
        "regex": "not_regex",
        "not_regex": "regex",
    }
    negated = [
        QueryFilter(
            field=f.field,
            operator=_NEGATION_MAP.get(f.operator, f.operator),
            value=f.value,
        )
        for f in query.filters
    ]
    return ParsedQuery(filters=negated, limit=query.limit)
