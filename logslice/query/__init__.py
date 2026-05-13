"""Public API for the logslice query package."""

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
from logslice.query.throttler import ThrottlerError, ThrottlerConfig, ThrottleResult, throttle_records
from logslice.query.splitter import SplitterError, SplitterConfig, SplitResult, split_records
from logslice.query.rewriter import RewriteError, RewriteConfig, rewrite_query
from logslice.query.grouper import GrouperError, GrouperConfig, GroupResult, group_records

__all__ = [
    # parser
    "QueryFilter",
    "ParsedQuery",
    "parse_query",
    # evaluator
    "matches",
    # builder
    "QueryBuilder",
    # composer
    "merge_queries",
    "negate_query",
    # validator
    "ValidationError",
    "validate_query",
    # highlighter
    "highlight_record",
    # sorter
    "SortError",
    "sort_records",
    "sort_records_multi",
    # paginator
    "PaginationError",
    "PageResult",
    "PaginatorConfig",
    "paginate",
    # summarizer
    "SummaryResult",
    "summarize",
    # sampler
    "SamplerError",
    "SamplerConfig",
    "SampleResult",
    "sample",
    # deduplicator
    "DeduplicatorError",
    "DeduplicatorConfig",
    "DeduplicationResult",
    "deduplicate",
    # transformer
    "TransformError",
    "TransformRule",
    "TransformConfig",
    "apply_rules",
    # enricher
    "EnrichError",
    "EnrichRule",
    "EnrichConfig",
    "enrich_records",
    # router
    "RouterError",
    "Route",
    "RouterConfig",
    "RoutingResult",
    "route_records",
    # throttler
    "ThrottlerError",
    "ThrottlerConfig",
    "ThrottleResult",
    "throttle_records",
    # splitter
    "SplitterError",
    "SplitterConfig",
    "SplitResult",
    "split_records",
    # rewriter
    "RewriteError",
    "RewriteConfig",
    "rewrite_query",
    # grouper
    "GrouperError",
    "GrouperConfig",
    "GroupResult",
    "group_records",
]
