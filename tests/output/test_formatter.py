"""Tests for logslice.output.formatter."""

import json
import pytest

from logslice.output.formatter import format_record


SAMPLE = {
    "timestamp": "2024-01-15T10:00:00Z",
    "level": "info",
    "service": "api",
    "message": "request handled",
    "status": 200,
}


def test_format_json_roundtrip():
    result = format_record(SAMPLE, fmt="json")
    parsed = json.loads(result)
    assert parsed == SAMPLE


def test_format_json_non_serializable_does_not_raise():
    record = {**SAMPLE, "extra": object()}
    result = format_record(record, fmt="json")
    assert "extra" in result


def test_format_compact_contains_key_fields():
    result = format_record(SAMPLE, fmt="compact")
    assert "2024-01-15T10:00:00Z" in result
    assert "INFO" in result
    assert "[api]" in result
    assert "request handled" in result


def test_format_compact_no_service():
    record = {k: v for k, v in SAMPLE.items() if k != "service"}
    result = format_record(record, fmt="compact")
    assert "[" not in result
    assert "request handled" in result


def test_format_pretty_contains_message():
    result = format_record(SAMPLE, fmt="pretty", color=False)
    assert "request handled" in result
    assert "INFO" in result
    assert "api" in result


def test_format_pretty_color_disabled():
    result = format_record(SAMPLE, fmt="pretty", color=False)
    assert "\033[" not in result


def test_format_pretty_color_enabled():
    result = format_record(SAMPLE, fmt="pretty", color=True)
    assert "\033[" in result


def test_format_pretty_extra_fields_included():
    result = format_record(SAMPLE, fmt="pretty", color=False)
    assert "status" in result
    assert "200" in result


def test_format_pretty_alternate_field_names():
    record = {
        "ts": "2024-01-15T10:00:00Z",
        "severity": "error",
        "app": "worker",
        "msg": "job failed",
    }
    result = format_record(record, fmt="pretty", color=False)
    assert "job failed" in result
    assert "ERROR" in result
    assert "worker" in result


def test_format_pretty_unknown_level_no_color():
    record = {**SAMPLE, "level": "trace"}
    result = format_record(record, fmt="pretty", color=True)
    assert "TRACE" in result
