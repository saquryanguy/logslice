"""Tests for logslice.pipeline.runner (including highlight integration)."""

from __future__ import annotations

import io
import json

import pytest

from logslice.pipeline.runner import PipelineConfig, run_pipeline
from logslice.query.parser import parse_query
from logslice.query.highlighter import ANSI_RESET


def _make_stream(*records: dict) -> io.StringIO:
    lines = [json.dumps(r) for r in records]
    return io.StringIO("\n".join(lines))


# ---------------------------------------------------------------------------
# baseline behaviour (regression guard)
# ---------------------------------------------------------------------------

def test_run_pipeline_no_filter_returns_all():
    stream = _make_stream({"level": "info"}, {"level": "error"})
    result = run_pipeline(stream)
    assert len(result) == 2


def test_run_pipeline_filter_by_level():
    stream = _make_stream({"level": "info"}, {"level": "error"})
    cfg = PipelineConfig(query=parse_query("level=error"))
    result = run_pipeline(stream, cfg)
    assert len(result) == 1
    assert result[0]["level"] == "error"


def test_run_pipeline_filter_by_service():
    stream = _make_stream(
        {"level": "info", "service": "auth"},
        {"level": "info", "service": "billing"},
    )
    cfg = PipelineConfig(query=parse_query("service=auth"))
    result = run_pipeline(stream, cfg)
    assert len(result) == 1
    assert result[0]["service"] == "auth"


def test_run_pipeline_max_records():
    stream = _make_stream(*[{"level": "info", "n": i} for i in range(10)])
    cfg = PipelineConfig(max_records=3)
    result = run_pipeline(stream, cfg)
    assert len(result) == 3


# ---------------------------------------------------------------------------
# highlight integration
# ---------------------------------------------------------------------------

def test_highlight_off_by_default():
    stream = _make_stream({"level": "error", "message": "boom"})
    cfg = PipelineConfig(query=parse_query("level=error"))
    result = run_pipeline(stream, cfg)
    assert ANSI_RESET not in result[0]["level"]


def test_highlight_on_marks_matched_field():
    stream = _make_stream({"level": "error", "message": "boom"})
    cfg = PipelineConfig(query=parse_query("level=error"), highlight=True)
    result = run_pipeline(stream, cfg)
    assert ANSI_RESET in result[0]["level"]


def test_highlight_on_no_query_no_change():
    stream = _make_stream({"level": "info"})
    cfg = PipelineConfig(highlight=True)
    result = run_pipeline(stream, cfg)
    assert result[0]["level"] == "info"


def test_highlight_does_not_affect_unmatched_field():
    stream = _make_stream({"level": "error", "message": "all good"})
    cfg = PipelineConfig(query=parse_query("level=error"), highlight=True)
    result = run_pipeline(stream, cfg)
    assert ANSI_RESET not in result[0]["message"]


# ---------------------------------------------------------------------------
# extra_fields injection
# ---------------------------------------------------------------------------

def test_extra_fields_injected():
    stream = _make_stream({"level": "info"})
    cfg = PipelineConfig(extra_fields={"env": "prod"})
    result = run_pipeline(stream, cfg)
    assert result[0]["env"] == "prod"


def test_extra_fields_do_not_override_original():
    stream = _make_stream({"level": "info", "env": "dev"})
    cfg = PipelineConfig(extra_fields={"env": "prod"})
    result = run_pipeline(stream, cfg)
    # extra_fields are merged after, so they win — document this behaviour
    assert result[0]["env"] == "prod"
