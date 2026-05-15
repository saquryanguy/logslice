"""logslice.query – public re-exports."""

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
from logslice.query.transformer import TransformError, TransformRule, TransformConfig, apply_rule, transform
from logslice.query.enricher import EnrichError, EnrichRule, EnrichConfig, enrich
from logslice.query.router import RouterError, Route, RouterConfig, RoutingResult, route
from logslice.query.throttler import ThrottlerError, ThrottlerConfig, ThrottleResult, throttle
from logslice.query.splitter import SplitterError, SplitterConfig, SplitResult, split
from logslice.query.rewriter import RewriteError, RewriteConfig, rewrite
from logslice.query.grouper import GrouperError, GrouperConfig, GroupResult, group
from logslice.query.flattener import FlattenerError, FlattenerConfig, FlattenResult, flatten
from logslice.query.projector import ProjectionError, ProjectorConfig, ProjectionResult, project
from logslice.query.redactor import RedactError, RedactRule, RedactConfig, RedactResult, redact
from logslice.query.merger import MergerError, MergerConfig, MergeResult, merge
from logslice.query.tagger import TaggerError, TagRule, TaggerConfig, TagResult, tag
from logslice.query.windower import WindowError, WindowerConfig, WindowResult, window
from logslice.query.scorer import ScorerError, ScorerConfig, ScoreResult, score
from logslice.query.alerter import AlertError, AlertRule, AlertEvent, alert
from logslice.query.normalizer import NormalizeError, NormalizeRule, NormalizeConfig, NormalizeResult, normalize
from logslice.query.correlator import CorrelatorError, CorrelatorConfig, CorrelationGroup, correlate
from logslice.query.censor import CensorError, CensorConfig, CensorResult, censor
from logslice.query.dispatcher import DispatchError, DispatchRule, DispatchConfig, dispatch
from logslice.query.buffer import BufferError, BufferConfig, BufferResult, buffer
from logslice.query.archiver import ArchiveError, ArchiveConfig, ArchiveResult, archive
from logslice.query.limiter import LimiterError, LimiterConfig, LimitResult, limit
from logslice.query.partitioner import PartitionError, PartitionerConfig, PartitionResult, partition

__all__ = [
    "QueryFilter", "ParsedQuery", "parse_query",
    "matches",
    "QueryBuilder",
    "merge_queries", "negate_query",
    "ValidationError", "validate_query",
    "highlight_record",
    "SortError", "sort_records", "sort_records_multi",
    "PaginationError", "PageResult", "PaginatorConfig", "paginate",
    "SummaryResult", "summarize",
    "SamplerError", "SamplerConfig", "SampleResult", "sample",
    "DeduplicatorError", "DeduplicatorConfig", "DeduplicationResult", "deduplicate",
    "TransformError", "TransformRule", "TransformConfig", "apply_rule", "transform",
    "EnrichError", "EnrichRule", "EnrichConfig", "enrich",
    "RouterError", "Route", "RouterConfig", "RoutingResult", "route",
    "ThrottlerError", "ThrottlerConfig", "ThrottleResult", "throttle",
    "SplitterError", "SplitterConfig", "SplitResult", "split",
    "RewriteError", "RewriteConfig", "rewrite",
    "GrouperError", "GrouperConfig", "GroupResult", "group",
    "FlattenerError", "FlattenerConfig", "FlattenResult", "flatten",
    "ProjectionError", "ProjectorConfig", "ProjectionResult", "project",
    "RedactError", "RedactRule", "RedactConfig", "RedactResult", "redact",
    "MergerError", "MergerConfig", "MergeResult", "merge",
    "TaggerError", "TagRule", "TaggerConfig", "TagResult", "tag",
    "WindowError", "WindowerConfig", "WindowResult", "window",
    "ScorerError", "ScorerConfig", "ScoreResult", "score",
    "AlertError", "AlertRule", "AlertEvent", "alert",
    "NormalizeError", "NormalizeRule", "NormalizeConfig", "NormalizeResult", "normalize",
    "CorrelatorError", "CorrelatorConfig", "CorrelationGroup", "correlate",
    "CensorError", "CensorConfig", "CensorResult", "censor",
    "DispatchError", "DispatchRule", "DispatchConfig", "dispatch",
    "BufferError", "BufferConfig", "BufferResult", "buffer",
    "ArchiveError", "ArchiveConfig", "ArchiveResult", "archive",
    "LimiterError", "LimiterConfig", "LimitResult", "limit",
    "PartitionError", "PartitionerConfig", "PartitionResult", "partition",
]
