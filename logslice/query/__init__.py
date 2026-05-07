"""logslice.query — query parsing, evaluation, and record processing utilities."""

from logslice.query.parser import ParsedQuery, QueryFilter, parse_query
from logslice.query.evaluator import matches
from logslice.query.builder import QueryBuilder
from logslice.query.composer import merge_queries, negate_query
from logslice.query.validator import ValidationError, validate_query
from logslice.query.highlighter import highlight_record
from logslice.query.sorter import SortError, sort_records
from logslice.query.paginator import PaginationError, PageResult, PaginatorConfig, paginate
from logslice.query.summarizer import SummaryResult, summarize
from logslice.query.sampler import SamplerError, SamplerConfig, SampleResult, sample
from logslice.query.deduplicator import DeduplicatorError, DeduplicatorConfig, DeduplicationResult, deduplicate
from logslice.query.transformer import TransformError, TransformRule, TransformConfig, apply_transforms
from logslice.query.enricher import EnrichError, EnrichRule, EnrichConfig, enrich_records
from logslice.query.router import RouterError, Route, RouterConfig, RoutingResult, route_records

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
    "PaginationError",
    "PageResult",
    "PaginatorConfig",
    "paginate",
    "SummaryResult",
    "summarize",
    "SamplerError",
    "SamplerConfig",
    "SampleResult",
    "sample",
    "DeduplicatorError",
    "DeduplicatorConfig",
    "DeduplicationResult",
    "deduplicate",
    "TransformError",
    "TransformRule",
    "TransformConfig",
    "apply_transforms",
    "EnrichError",
    "EnrichRule",
    "EnrichConfig",
    "enrich_records",
    "RouterError",
    "Route",
    "RouterConfig",
    "RoutingResult",
    "route_records",
]
