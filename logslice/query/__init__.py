"""logslice.query — query parsing, evaluation, and record processing utilities."""

from logslice.query.parser import ParsedQuery, QueryFilter, parse_query
from logslice.query.evaluator import matches
from logslice.query.builder import QueryBuilder
from logslice.query.composer import merge_queries, negate_query
from logslice.query.validator import ValidationError, validate_query
from logslice.query.highlighter import highlight_record
from logslice.query.sorter import SortError, sort_records
from logslice.query.paginator import PageResult, PaginatorConfig, PaginationError, paginate
from logslice.query.summarizer import SummaryResult, summarize
from logslice.query.sampler import SamplerConfig, SamplerError, SampleResult, sample
from logslice.query.deduplicator import DeduplicatorConfig, DeduplicatorError, DeduplicationResult, deduplicate
from logslice.query.transformer import (
    TransformConfig,
    TransformError,
    TransformRule,
    transform_record,
    transform_records,
)

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
    "SortError",
    "sort_records",
    "PageResult",
    "PaginatorConfig",
    "PaginationError",
    "paginate",
    "SummaryResult",
    "summarize",
    "SamplerConfig",
    "SamplerError",
    "SampleResult",
    "sample",
    "DeduplicatorConfig",
    "DeduplicatorError",
    "DeduplicationResult",
    "deduplicate",
    "TransformConfig",
    "TransformError",
    "TransformRule",
    "transform_record",
    "transform_records",
]
