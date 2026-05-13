"""logslice.query public API."""

from logslice.query.builder import QueryBuilder
from logslice.query.composer import merge_queries, negate_query
from logslice.query.deduplicator import DeduplicatorConfig, DeduplicationResult, deduplicate
from logslice.query.enricher import EnrichConfig, EnrichRule, enrich
from logslice.query.evaluator import matches
from logslice.query.highlighter import highlight_record
from logslice.query.paginator import PaginationError, PaginatorConfig, PageResult, paginate
from logslice.query.parser import ParsedQuery, QueryFilter, parse_query
from logslice.query.rewriter import RewriteConfig, RewriteError, rewrite_query
from logslice.query.router import RouterConfig, RoutingResult, route
from logslice.query.sampler import SamplerConfig, SampleResult, sample
from logslice.query.sorter import SortError, sort_records
from logslice.query.splitter import SplitterConfig, SplitResult, split
from logslice.query.summarizer import SummaryResult, summarize
from logslice.query.throttler import ThrottlerConfig, ThrottleResult, throttle
from logslice.query.transformer import TransformConfig, TransformRule, apply_transforms
from logslice.query.validator import ValidationError, validate_query

__all__ = [
    # parser
    "ParsedQuery",
    "QueryFilter",
    "parse_query",
    # builder
    "QueryBuilder",
    # evaluator
    "matches",
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
    # paginator
    "PaginationError",
    "PaginatorConfig",
    "PageResult",
    "paginate",
    # summarizer
    "SummaryResult",
    "summarize",
    # sampler
    "SamplerConfig",
    "SampleResult",
    "sample",
    # deduplicator
    "DeduplicatorConfig",
    "DeduplicationResult",
    "deduplicate",
    # transformer
    "TransformConfig",
    "TransformRule",
    "apply_transforms",
    # enricher
    "EnrichConfig",
    "EnrichRule",
    "enrich",
    # router
    "RouterConfig",
    "RoutingResult",
    "route",
    # throttler
    "ThrottlerConfig",
    "ThrottleResult",
    "throttle",
    # splitter
    "SplitterConfig",
    "SplitResult",
    "split",
    # rewriter
    "RewriteConfig",
    "RewriteError",
    "rewrite_query",
]
