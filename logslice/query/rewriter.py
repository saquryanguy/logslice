"""Query rewriting utilities for logslice.

Provides functions to normalize, optimize, and transform ParsedQuery
objects before execution — e.g. collapsing redundant filters, injecting
default constraints, or rewriting field aliases.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from logslice.query.parser import ParsedQuery, QueryFilter


class RewriteError(Exception):
    """Raised when a query cannot be rewritten."""


# ---------------------------------------------------------------------------
# Field alias map
# ---------------------------------------------------------------------------

_FIELD_ALIASES: Dict[str, str] = {
    "lvl": "level",
    "svc": "service",
    "msg": "message",
    "ts": "timestamp",
}


@dataclass
class RewriteConfig:
    """Controls which rewriting passes are applied."""

    resolve_aliases: bool = True
    deduplicate_filters: bool = True
    inject_defaults: Dict[str, object] = field(default_factory=dict)
    max_limit: Optional[int] = None


# ---------------------------------------------------------------------------
# Rewriting passes
# ---------------------------------------------------------------------------


def _resolve_aliases(filters: List[QueryFilter]) -> List[QueryFilter]:
    """Replace known field aliases with their canonical names."""
    result = []
    for f in filters:
        canonical = _FIELD_ALIASES.get(f.field, f.field)
        if canonical != f.field:
            result.append(QueryFilter(field=canonical, operator=f.operator, value=f.value))
        else:
            result.append(f)
    return result


def _deduplicate_filters(filters: List[QueryFilter]) -> List[QueryFilter]:
    """Remove exact duplicate filters, preserving order."""
    seen: set = set()
    result = []
    for f in filters:
        key = (f.field, f.operator, str(f.value))
        if key not in seen:
            seen.add(key)
            result.append(f)
    return result


def _inject_defaults(
    filters: List[QueryFilter], defaults: Dict[str, object]
) -> List[QueryFilter]:
    """Add equality filters for fields not already constrained."""
    existing_fields = {f.field for f in filters}
    injected = [
        QueryFilter(field=k, operator="eq", value=v)
        for k, v in defaults.items()
        if k not in existing_fields
    ]
    return filters + injected


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def rewrite_query(query: ParsedQuery, config: Optional[RewriteConfig] = None) -> ParsedQuery:
    """Apply configured rewriting passes to *query* and return a new instance.

    The original query is never mutated.
    """
    if config is None:
        config = RewriteConfig()

    filters: List[QueryFilter] = list(query.filters)

    if config.resolve_aliases:
        filters = _resolve_aliases(filters)

    if config.inject_defaults:
        filters = _inject_defaults(filters, config.inject_defaults)

    if config.deduplicate_filters:
        filters = _deduplicate_filters(filters)

    limit = query.limit
    if config.max_limit is not None:
        if limit is None:
            limit = config.max_limit
        else:
            limit = min(limit, config.max_limit)

    return ParsedQuery(filters=filters, limit=limit)
