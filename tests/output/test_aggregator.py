"""Tests for logslice.output.aggregator."""
from collections import Counter

import pytest

from logslice.output.aggregator import aggregate, AggregationResult


def _records(data):
    return iter(data)


def test_empty_records_returns_zero_total():
    result = aggregate(_records([]))
    assert result.total == 0
    assert result.by_level == {}
    assert result.by_service == {}
    assert result.first_ts is None
    assert result.last_ts is None


def test_total_count():
    records = [{"level": "info"}, {"level": "error"}, {"level": "info"}]
    result = aggregate(_records(records))
    assert result.total == 3


def test_by_level_counts():
    records = [
        {"level": "INFO"},
        {"level": "error"},
        {"level": "info"},
        {"level": "WARN"},
    ]
    result = aggregate(_records(records))
    assert result.by_level["info"] == 2
    assert result.by_level["error"] == 1
    assert result.by_level["warn"] == 1


def test_by_service_counts():
    records = [
        {"service": "auth"},
        {"service": "auth"},
        {"service": "gateway"},
    ]
    result = aggregate(_records(records))
    assert result.by_service["auth"] == 2
    assert result.by_service["gateway"] == 1


def test_missing_level_falls_back_to_unknown():
    records = [{"message": "no level here"}]
    result = aggregate(_records(records))
    assert result.by_level.get("unknown") == 1


def test_timestamp_tracking():
    records = [
        {"timestamp": "2024-01-01T00:00:00Z", "level": "info"},
        {"timestamp": "2024-01-02T00:00:00Z", "level": "info"},
        {"timestamp": "2024-01-03T00:00:00Z", "level": "info"},
    ]
    result = aggregate(_records(records))
    assert result.first_ts == "2024-01-01T00:00:00Z"
    assert result.last_ts == "2024-01-03T00:00:00Z"


def test_group_by_extra_field():
    records = [
        {"level": "info", "region": "us-east"},
        {"level": "error", "region": "eu-west"},
        {"level": "info", "region": "us-east"},
    ]
    result = aggregate(_records(records), group_by_fields=["region"])
    assert result.field_counts["region"]["us-east"] == 2
    assert result.field_counts["region"]["eu-west"] == 1


def test_as_dict_keys():
    records = [{"level": "debug", "service": "worker"}]
    result = aggregate(_records(records))
    d = result.as_dict()
    assert set(d.keys()) == {"total", "by_level", "by_service", "first_ts", "last_ts"}
    assert d["total"] == 1
