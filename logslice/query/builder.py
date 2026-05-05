"""Fluent query builder for constructing structured log queries."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional

from logslice.query.parser import QueryFilter, ParsedQuery


@dataclass
class QueryBuilder:
    """Fluent interface for building a ParsedQuery programmatically."""

    _filters: List[QueryFilter] = field(default_factory=list)
    _limit: Optional[int] = None

    def where(self, field_name: str, operator: str, value: Any) -> "QueryBuilder":
        """Add a filter condition."""
        self._filters.append(QueryFilter(field=field_name, operator=operator, value=value))
        return self

    def level(self, value: str, operator: str = "eq") -> "QueryBuilder":
        """Shorthand for filtering by log level."""
        return self.where("level", operator, value)

    def service(self, value: str, operator: str = "eq") -> "QueryBuilder":
        """Shorthand for filtering by service name."""
        return self.where("service", operator, value)

    def message_contains(self, value: str) -> "QueryBuilder":
        """Shorthand for filtering messages with a regex match."""
        return self.where("message", "regex", value)

    def limit(self, n: int) -> "QueryBuilder":
        """Set a maximum number of records to return."""
        if n < 1:
            raise ValueError("limit must be >= 1")
        self._limit = n
        return self

    def build(self) -> ParsedQuery:
        """Produce a ParsedQuery from the current builder state."""
        return ParsedQuery(filters=list(self._filters), limit=self._limit)

    @classmethod
    def from_parsed(cls, parsed: ParsedQuery) -> "QueryBuilder":
        """Initialise a builder from an existing ParsedQuery."""
        builder = cls()
        builder._filters = list(parsed.filters)
        builder._limit = parsed.limit
        return builder
