"""Query parser for logslice unified query syntax."""

import re
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class QueryFilter:
    field: str
    operator: str
    value: Any


@dataclass
class ParsedQuery:
    filters: list[QueryFilter] = field(default_factory=list)
    level: Optional[str] = None
    service: Optional[str] = None
    limit: int = 100
    raw: str = ""


OPERATORS = ["==", "!=", ">=", "<=", ">", "<", "~="]
LEVEL_KEYWORDS = {"DEBUG", "INFO", "WARN", "WARNING", "ERROR", "FATAL"}

TOKEN_RE = re.compile(
    r'(?P<field>[\w\.]+)\s*(?P<op>==|!=|>=|<=|>|<|~=)\s*(?P<value>"[^"]*"|\S+)'
)


def _coerce(value: str) -> Any:
    value = value.strip('"')
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    return value


def parse_query(raw: str) -> ParsedQuery:
    """Parse a query string into a ParsedQuery object."""
    query = ParsedQuery(raw=raw)
    remaining = raw.strip()

    limit_match = re.search(r'\blimit\s+(\d+)', remaining, re.IGNORECASE)
    if limit_match:
        query.limit = int(limit_match.group(1))
        remaining = remaining[:limit_match.start()] + remaining[limit_match.end():]

    for match in TOKEN_RE.finditer(remaining):
        f = match.group("field")
        op = match.group("op")
        val = _coerce(match.group("value"))

        if f == "level" and op == "==":
            query.level = str(val).upper()
        elif f == "service" and op == "==":
            query.service = str(val)
        else:
            query.filters.append(QueryFilter(field=f, operator=op, value=val))

    return query
