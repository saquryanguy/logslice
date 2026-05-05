"""Tests for logslice.pipeline.runner."""

from __future__ import annotations

import io
import json

import pytest

from logslice.pipeline.runner import PipelineConfig, run_pipeline


def _make_stream(*records: dict) -> io.StringIO:
    lines = [json.dumps(r) for r in records]
    return io.StringIO("\n".join(lines))


RECORDS = [
    {"level": "INFO", "service": "api", "message": "started"},
    {"level": "ERROR", "service": "api", "message": "boom"},
    {"level": "INFO", "service": "worker", "message": "processing"},
    {"level": "WARN", "service": "api", "message": "slow response"},
]


def test_run_pipeline_no_filter_returns_all():
    stream = _make_stream(*RECORDS)
    out = io.StringIO()
    count = run_pipeline(stream, PipelineConfig(query=""), output=out)
    assert count == len(RECORDS)


def test_run_pipeline_filter_by_level():
    stream = _make_stream(*RECORDS)
    out = io.StringIO()
    count = run_pipeline(stream, PipelineConfig(query="level=ERROR"), output=out)
    assert count == 1
    assert "boom" in out.getvalue()


def test_run_pipeline_filter_by_service():
    stream = _make_stream(*RECORDS)
    out = io.StringIO()
    count = run_pipeline(stream, PipelineConfig(query="service=worker"), output=out)
    assert count == 1
    assert "processing" in out.getvalue()


def test_run_pipeline_max_records():
    stream = _make_stream(*RECORDS)
    out = io.StringIO()
    count = run_pipeline(
        stream, PipelineConfig(query="", max_records=2), output=out
    )
    assert count == 2


def test_run_pipeline_json_output_format():
    stream = _make_stream(*RECORDS[:1])
    out = io.StringIO()
    run_pipeline(
        stream, PipelineConfig(query="", output_format="json", color=False), output=out
    )
    parsed = json.loads(out.getvalue().strip())
    assert parsed["message"] == "started"


def test_run_pipeline_skip_invalid_lines():
    raw = io.StringIO('{"level": "INFO", "message": "ok"}\nnot-json\n{"level": "ERROR", "message": "fail"}')
    out = io.StringIO()
    count = run_pipeline(raw, PipelineConfig(query="", skip_invalid=True), output=out)
    assert count == 2


def test_run_pipeline_no_match_returns_zero():
    stream = _make_stream(*RECORDS)
    out = io.StringIO()
    count = run_pipeline(stream, PipelineConfig(query="level=DEBUG"), output=out)
    assert count == 0
    assert out.getvalue() == ""
