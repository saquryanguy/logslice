"""logslice.query — query parsing, evaluation, and record processing utilities."""

from logslice.query.parser import ParsedQuery, QueryFilter, parse_query
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
from logslice.query.transformer import TransformError, TransformConfig, TransformRule, apply_transforms
from logslice.query.enricher import EnrichError, EnrichConfig, EnrichRule, enrich
from logslice.query.router import RouterError, Route, RouterConfig, RoutingResult, route
from logslice.query.throttler import ThrottlerError, ThrottlerConfig, ThrottleResult, throttle
from logslice.query.splitter import SplitterError, SplitterConfig, SplitResult, split
from logslice.query.rewriter import RewriteConfig, rewrite_query
from logslice.query.grouper import GrouperError, GrouperConfig, GroupResult, group
from logslice.query.flattener import FlattenerError, FlattenerConfig, FlattenResult, flatten
from logslice.query.projector import ProjectionError, ProjectorConfig, ProjectionResult, project
from logslice.query.redactor import RedactError, RedactConfig, RedactRule, RedactResult, redact
from logslice.query.merger import MergerError, MergerConfig, MergeResult, merge
from logslice.query.tagger import TaggerError, TaggerConfig, TagRule, TagResult, tag
from logslice.query.windower import WindowError, WindowerConfig, WindowResult, window
from logslice.query.scorer import ScorerError, ScorerConfig, ScoreResult, score
from logslice.query.alerter import AlertError, AlertRule, AlertEvent, alert
from logslice.query.normalizer import NormalizeError, NormalizeConfig, NormalizeRule, NormalizeResult, normalize
from logslice.query.correlator import CorrelatorError, CorrelatorConfig, CorrelationGroup, correlate
from logslice.query.censor import CensorError, CensorConfig, CensorResult, censor
from logslice.query.dispatcher import DispatchError, DispatchRule, DispatchConfig, DispatchResult, dispatch

__all__ = [
    "ParsedQuery", "QueryFilter", "parse_query",
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
    "TransformError", "TransformConfig", "TransformRule", "apply_transforms",
    "EnrichError", "EnrichConfig", "EnrichRule", "enrich",
    "RouterError", "Route", "RouterConfig", "RoutingResult", "route",
    "ThrottlerError", "ThrottlerConfig", "ThrottleResult", "throttle",
    "SplitterError", "SplitterConfig", "SplitResult", "split",
    "RewriteConfig", "rewrite_query",
    "GrouperError", "GrouperConfig", "GroupResult", "group",
    "FlattenerError", "FlattenerConfig", "FlattenResult", "flatten",
    "ProjectionError", "ProjectorConfig", "ProjectionResult", "project",
    "RedactError", "RedactConfig", "RedactRule", "RedactResult", "redact",
    "MergerError", "MergerConfig", "MergeResult", "merge",
    "TaggerError", "TaggerConfig", "TagRule", "TagResult", "tag",
    "WindowError", "WindowerConfig", "WindowResult", "window",
    "ScorerError", "ScorerConfig", "ScoreResult", "score",
    "AlertError", "AlertRule", "AlertEvent", "alert",
    "NormalizeError", "NormalizeConfig", "NormalizeRule", "NormalizeResult", "normalize",
    "CorrelatorError", "CorrelatorConfig", "CorrelationGroup", "correlate",
    "CensorError", "CensorConfig", "CensorResult", "censor",
    "DispatchError", "DispatchRule", "DispatchConfig", "DispatchResult", "dispatch",
]
