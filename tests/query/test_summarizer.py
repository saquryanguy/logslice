"""Tests for logslice.query.summarizer."""
from __future__ import annotations

import pytest
from logslice.query.summarizer import summarize, SummaryResult


def _records():
    return [
        {"level": "info",  "service": "api",    "timestamp": "2024-01-01T10:00:00Z", "msg": "started"},
        {"level": "error", "service": "api",    "timestamp": "2024-01-01T10:05:00Z", "msg": "oops"},
        {"level": "info",  "service": "worker", "timestamp": "2024-01-01T09:59:00Z", "msg": "ok"},
        {"level": "warn",  "service": "worker", "timestamp": "2024-01-01T10:10:00Z", "msg": "slow"},
    ]


def test_empty_records_returns_zero_total():
    result = summarize([])
    assert result.total == 0
    assert result.by_level == {}
    assert result.by_service == {}
    assert result.first_timestamp is None
    assert result.last_timestamp is None


def test_total_count():
    result = summarize(_records())
    assert result.total == 4


def test_by_level_counts():
    result = summarize(_records())
    assert result.by_level["INFO"] == 2
    assert result.by_level["ERROR"] == 1
    assert result.by_level["WARN"] == 1


def test_by_service_counts():
    result = summarize(_records())
    assert result.by_service["api"] == 2
    assert result.by_service["worker"] == 2


def test_first_and_last_timestamp():
    result = summarize(_records())
    assert result.first_timestamp == "2024-01-01T09:59:00Z"
    assert result.last_timestamp == "2024-01-01T10:10:00Z"


def test_unique_fields_sorted():
    result = summarize(_records())
    assert result.unique_fields == sorted({"level", "service", "timestamp", "msg"})


def test_missing_level_and_service():
    records = [{"msg": "bare", "timestamp": "2024-01-02T00:00:00Z"}]
    result = summarize(records)
    assert result.by_level == {}
    assert result.by_service == {}
    assert result.total == 1


def test_severity_field_used_when_no_level():
    records = [{"severity": "debug", "msg": "x"}]
    result = summarize(records)
    assert "DEBUG" in result.by_level


def test_ts_field_used_when_no_timestamp():
    records = [{"ts": "2024-03-01T00:00:00Z", "msg": "x"}]
    result = summarize(records)
    assert result.first_timestamp == "2024-03-01T00:00:00Z"


def test_as_dict_keys():
    result = summarize(_records())
    d = result.as_dict()
    assert set(d.keys()) == {
        "total", "by_level", "by_service",
        "first_timestamp", "last_timestamp", "unique_fields",
    }
