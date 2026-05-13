"""logslice.query public API."""
from logslice.query.parser import QueryFilter, ParsedQuery, parse_query
from logslice.query.evaluator import matches
from logslice.query.builder import QueryBuilder
from logslice.query.composer import merge_queries, negate_query
from logslice.query.validator import ValidationError, validate_query
from logslice.query.highlighter import highlight_record
from logslice.query.sorter import SortError, sort_records, sort_records_multi
from logslice.query.paginator import PaginationError, PageResult, PaginatorConfig, paginate
from logslice.query.summarizer import SummaryResult, summarize
from logslice.query.sampler import SamplerError, SamplerConfig, SampleResult, sample
from logslice.query.deduplicator import DeduplicatorError, DeduplicatorConfig, DeduplicationResult, deduplicate
from logslice.query.transformer import TransformError, TransformRule, TransformConfig, apply_rules
from logslice.query.enricher import EnrichError, EnrichRule, EnrichConfig, enrich_records
from logslice.query.router import RouterError, Route, RouterConfig, RoutingResult, route_records
from logslice.query.throttler import ThrottlerError, ThrottlerConfig, ThrottleResult, throttle
from logslice.query.splitter import SplitterError, SplitterConfig, SplitResult, split_records
from logslice.query.rewriter import RewriteError, RewriteConfig, rewrite_query
from logslice.query.grouper import GrouperError, GrouperConfig, GroupResult, group_records
from logslice.query.flattener import FlattenerError, FlattenerConfig, FlattenResult, flatten_record, flatten_records

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
    "sort_records_multi",
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
    "apply_rules",
    "EnrichError",
    "EnrichRule",
    "EnrichConfig",
    "enrich_records",
    "RouterError",
    "Route",
    "RouterConfig",
    "RoutingResult",
    "route_records",
    "ThrottlerError",
    "ThrottlerConfig",
    "ThrottleResult",
    "throttle",
    "SplitterError",
    "SplitterConfig",
    "SplitResult",
    "split_records",
    "RewriteError",
    "RewriteConfig",
    "rewrite_query",
    "GrouperError",
    "GrouperConfig",
    "GroupResult",
    "group_records",
    "FlattenerError",
    "FlattenerConfig",
    "FlattenResult",
    "flatten_record",
    "flatten_records",
]
