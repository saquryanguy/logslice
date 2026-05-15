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
from logslice.query.transformer import TransformError, TransformRule, TransformConfig, apply_rules
from logslice.query.enricher import EnrichError, EnrichRule, EnrichConfig, enrich
from logslice.query.router import RouterError, Route, RouterConfig, RoutingResult, route
from logslice.query.throttler import ThrottlerError, ThrottlerConfig, ThrottleResult, throttle
from logslice.query.splitter import SplitterError, SplitterConfig, SplitResult, split
from logslice.query.rewriter import RewriteError, RewriteConfig, rewrite_query
from logslice.query.grouper import GrouperError, GrouperConfig, GroupResult, group
from logslice.query.flattener import FlattenerError, FlattenerConfig, FlattenResult, flatten
from logslice.query.projector import ProjectionError, ProjectorConfig, ProjectionResult, project
from logslice.query.redactor import RedactError, RedactConfig, RedactResult, redact
from logslice.query.merger import MergerError, MergerConfig, MergeResult, merge
from logslice.query.tagger import TaggerError, TaggerConfig, TagResult, tag
from logslice.query.windower import WindowError, WindowerConfig, WindowResult, window
from logslice.query.scorer import ScorerError, ScorerConfig, ScoreResult, score
from logslice.query.alerter import AlertError, AlertRule, AlertEvent, evaluate_alerts
from logslice.query.normalizer import NormalizeError, NormalizeConfig, NormalizeResult, normalize
from logslice.query.correlator import CorrelatorError, CorrelatorConfig, CorrelationGroup, correlate
from logslice.query.censor import CensorError, CensorConfig, CensorResult, censor
from logslice.query.dispatcher import DispatchError, DispatchConfig, dispatch
from logslice.query.buffer import BufferError, BufferConfig, BufferResult, buffer_records

__all__ = [
    # parser
    "QueryFilter", "ParsedQuery", "parse_query",
    # evaluator
    "matches",
    # builder
    "QueryBuilder",
    # composer
    "merge_queries", "negate_query",
    # validator
    "ValidationError", "validate_query",
    # highlighter
    "highlight_record",
    # sorter
    "SortError", "sort_records", "sort_records_multi",
    # paginator
    "PaginationError", "PageResult", "PaginatorConfig", "paginate",
    # summarizer
    "SummaryResult", "summarize",
    # sampler
    "SamplerError", "SamplerConfig", "SampleResult", "sample",
    # deduplicator
    "DeduplicatorError", "DeduplicatorConfig", "DeduplicationResult", "deduplicate",
    # transformer
    "TransformError", "TransformRule", "TransformConfig", "apply_rules",
    # enricher
    "EnrichError", "EnrichRule", "EnrichConfig", "enrich",
    # router
    "RouterError", "Route", "RouterConfig", "RoutingResult", "route",
    # throttler
    "ThrottlerError", "ThrottlerConfig", "ThrottleResult", "throttle",
    # splitter
    "SplitterError", "SplitterConfig", "SplitResult", "split",
    # rewriter
    "RewriteError", "RewriteConfig", "rewrite_query",
    # grouper
    "GrouperError", "GrouperConfig", "GroupResult", "group",
    # flattener
    "FlattenerError", "FlattenerConfig", "FlattenResult", "flatten",
    # projector
    "ProjectionError", "ProjectorConfig", "ProjectionResult", "project",
    # redactor
    "RedactError", "RedactConfig", "RedactResult", "redact",
    # merger
    "MergerError", "MergerConfig", "MergeResult", "merge",
    # tagger
    "TaggerError", "TaggerConfig", "TagResult", "tag",
    # windower
    "WindowError", "WindowerConfig", "WindowResult", "window",
    # scorer
    "ScorerError", "ScorerConfig", "ScoreResult", "score",
    # alerter
    "AlertError", "AlertRule", "AlertEvent", "evaluate_alerts",
    # normalizer
    "NormalizeError", "NormalizeConfig", "NormalizeResult", "normalize",
    # correlator
    "CorrelatorError", "CorrelatorConfig", "CorrelationGroup", "correlate",
    # censor
    "CensorError", "CensorConfig", "CensorResult", "censor",
    # dispatcher
    "DispatchError", "DispatchConfig", "dispatch",
    # buffer
    "BufferError", "BufferConfig", "BufferResult", "buffer_records",
]
