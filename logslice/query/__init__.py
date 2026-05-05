"""Query sub-package: parsing, evaluation, building, composition, validation, highlighting."""

from logslice.query.parser import ParsedQuery, QueryFilter, parse_query
from logslice.query.evaluator import matches
from logslice.query.builder import QueryBuilder
from logslice.query.composer import merge_queries, negate_query
from logslice.query.validator import ValidationError, validate_query
from logslice.query.highlighter import highlight_record

__all__ = [
    "ParsedQuery",
    "QueryFilter",
    "parse_query",
    "matches",
    "QueryBuilder",
    "merge_queries",
    "negate_query",
    "ValidationError",
    "validate_query",
    "highlight_record",
]
