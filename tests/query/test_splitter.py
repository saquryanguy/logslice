"""Tests for logslice.query.splitter."""

from __future__ import annotations

import pytest

from logslice.query.splitter import (
    SplitterConfig,
    SplitterError,
    SplitResult,
    split_records,
)


def _records():
    return [
        {"level": "info", "service": "api", "msg": "started"},
        {"level": "error", "service": "api", "msg": "boom"},
        {"level": "info", "service": "worker", "msg": "processing"},
        {"level": "warn", "service": "db", "msg": "slow query"},
        {"level": "error", "service": "worker", "msg": "failed"},
    ]


# ---------------------------------------------------------------------------
# Basic splitting
# ---------------------------------------------------------------------------

def test_split_by_level_creates_correct_buckets():
    cfg = SplitterConfig(split_field="level")
    result = split_records(_records(), cfg)
    assert set(result.buckets.keys()) == {"info", "error", "warn"}
    assert len(result.buckets["info"]) == 2
    assert len(result.buckets["error"]) == 2
    assert len(result.buckets["warn"]) == 1


def test_split_total_equals_input_length():
    cfg = SplitterConfig(split_field="service")
    result = split_records(_records(), cfg)
    assert result.total == 5
    assert result.dropped == 0


def test_split_by_service():
    cfg = SplitterConfig(split_field="service")
    result = split_records(_records(), cfg)
    assert set(result.buckets.keys()) == {"api", "worker", "db"}


# ---------------------------------------------------------------------------
# Missing field falls back to default_bucket
# ---------------------------------------------------------------------------

def test_missing_field_goes_to_default_bucket():
    records = [{"msg": "no level here"}, {"level": "info", "msg": "ok"}]
    cfg = SplitterConfig(split_field="level")
    result = split_records(records, cfg)
    assert "__other__" in result.buckets
    assert len(result.buckets["__other__"]) == 1


def test_custom_default_bucket_name():
    records = [{"msg": "orphan"}]
    cfg = SplitterConfig(split_field="level", default_bucket="unclassified")
    result = split_records(records, cfg)
    assert "unclassified" in result.buckets


# ---------------------------------------------------------------------------
# allowed_buckets filtering
# ---------------------------------------------------------------------------

def test_allowed_buckets_filters_others_to_default():
    cfg = SplitterConfig(split_field="level", allowed_buckets=["error"])
    result = split_records(_records(), cfg)
    assert "error" in result.buckets
    assert "__other__" in result.buckets
    assert "info" not in result.buckets
    assert "warn" not in result.buckets


# ---------------------------------------------------------------------------
# max_buckets cap
# ---------------------------------------------------------------------------

def test_max_buckets_caps_distinct_buckets():
    records = [{"svc": str(i)} for i in range(20)]
    cfg = SplitterConfig(split_field="svc", max_buckets=5)
    result = split_records(records, cfg)
    assert len(result.buckets) <= 5
    assert result.dropped == 15


# ---------------------------------------------------------------------------
# as_dict
# ---------------------------------------------------------------------------

def test_as_dict_contains_expected_keys():
    cfg = SplitterConfig(split_field="level")
    result = split_records(_records(), cfg)
    d = result.as_dict()
    assert "buckets" in d
    assert "total" in d
    assert "dropped" in d
    assert "bucket_count" in d
    assert d["bucket_count"] == len(result.buckets)


# ---------------------------------------------------------------------------
# Validation errors
# ---------------------------------------------------------------------------

def test_max_buckets_zero_raises():
    cfg = SplitterConfig(split_field="level", max_buckets=0)
    with pytest.raises(SplitterError, match="max_buckets"):
        split_records([], cfg)


def test_empty_split_field_raises():
    cfg = SplitterConfig(split_field="")
    with pytest.raises(SplitterError, match="split_field"):
        split_records([], cfg)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_records_returns_empty_result():
    cfg = SplitterConfig(split_field="level")
    result = split_records([], cfg)
    assert result.total == 0
    assert result.buckets == {}
    assert result.dropped == 0


def test_nested_field_splitting():
    records = [
        {"meta": {"env": "prod"}, "msg": "a"},
        {"meta": {"env": "staging"}, "msg": "b"},
        {"meta": {"env": "prod"}, "msg": "c"},
    ]
    cfg = SplitterConfig(split_field="meta.env")
    result = split_records(records, cfg)
    assert len(result.buckets["prod"]) == 2
    assert len(result.buckets["staging"]) == 1
