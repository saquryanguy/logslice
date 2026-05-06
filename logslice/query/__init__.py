"""logslice.query — query parsing, evaluation, and utilities."""

from logslice.query.parser import QueryFilter, ParsedQuery, parse_query
from logslice.query.evaluator import matches
from logslice.query.builder import QueryBuilder
from logslice.query.composer import merge_queries, negate_query
from logslice.query.validator import ValidationError, validate_query
from logslice.query.highlighter import highlight_record
from logslice.query.sorter import SortError, sort_records
from logslice.query.paginator import PaginationError, PageResult, PaginatorConfig, paginate
from logslice.query.summarizer import SummaryResult, summarize
from logslice.query.sampler import SamplerConfig, SamplerError, SampleResult, sample

__all__ = [
    "QueryFilter",
    "ParsedQuery",
    "parse_query",
    "matches",
    "QueryBuilder",
    "merge_queries",
    "negate_query",
    "ValidationError",
    "validate_query",
    "highlight_record",
    "SortError",
    "sort_records",
    "PaginationError",
    "PageResult",
    "PaginatorConfig",
    "paginate",
    "SummaryResult",
    "summarize",
    "SamplerConfig",
    "SamplerError",
    "SampleResult",
    "sample",
]
