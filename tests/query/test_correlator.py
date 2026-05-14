"""Tests for logslice.query.correlator."""
import pytest

from logslice.query.correlator import (
    CorrelationGroup,
    CorrelationResult,
    CorrelatorConfig,
    CorrelatorError,
    correlate,
)


def _records():
    return [
        {"timestamp": 1000, "request_id": "abc", "level": "info", "message": "start"},
        {"timestamp": 1010, "request_id": "abc", "level": "error", "message": "fail"},
        {"timestamp": 1020, "request_id": "xyz", "level": "info", "message": "ok"},
        {"timestamp": 1030, "request_id": "abc", "level": "info", "message": "retry"},
        {"timestamp": 2000, "request_id": "xyz", "level": "warn", "message": "slow"},
    ]


# --- Config validation ---

def test_config_empty_key_field_raises():
    with pytest.raises(CorrelatorError, match="key_field"):
        CorrelatorConfig(key_field="")


def test_config_zero_window_raises():
    with pytest.raises(CorrelatorError, match="window_seconds"):
        CorrelatorConfig(key_field="id", window_seconds=0)


def test_config_negative_window_raises():
    with pytest.raises(CorrelatorError, match="window_seconds"):
        CorrelatorConfig(key_field="id", window_seconds=-5.0)


def test_config_min_group_size_zero_raises():
    with pytest.raises(CorrelatorError, match="min_group_size"):
        CorrelatorConfig(key_field="id", min_group_size=0)


# --- Core behaviour ---

def test_empty_records_returns_empty_result():
    result = correlate([], CorrelatorConfig(key_field="request_id"))
    assert result.total_records == 0
    assert result.total_groups == 0
    assert result.groups == []


def test_groups_by_key_field():
    cfg = CorrelatorConfig(key_field="request_id", min_group_size=2)
    result = correlate(_records(), cfg)
    keys = {g.key for g in result.groups}
    assert "abc" in keys


def test_min_group_size_filters_single_records():
    cfg = CorrelatorConfig(key_field="request_id", min_group_size=3)
    result = correlate(_records(), cfg)
    # only "abc" appears 3 times within window
    assert all(len(g.records) >= 3 for g in result.groups)


def test_records_missing_key_are_ignored():
    records = [
        {"timestamp": 1, "message": "no key"},
        {"timestamp": 2, "request_id": "a", "message": "has key"},
        {"timestamp": 3, "request_id": "a", "message": "has key 2"},
    ]
    cfg = CorrelatorConfig(key_field="request_id", min_group_size=2)
    result = correlate(records, cfg)
    assert result.total_groups == 1
    assert result.groups[0].key == "a"


def test_window_resets_group_when_exceeded():
    records = [
        {"timestamp": 0, "request_id": "a", "message": "first"},
        {"timestamp": 200, "request_id": "a", "message": "second"},  # outside 60s window
    ]
    cfg = CorrelatorConfig(key_field="request_id", window_seconds=60, min_group_size=2)
    result = correlate(records, cfg)
    # second record resets the window so group never reaches min_group_size=2
    assert result.total_groups == 0


def test_total_records_matches_sum_of_group_sizes():
    cfg = CorrelatorConfig(key_field="request_id", min_group_size=2)
    result = correlate(_records(), cfg)
    assert result.total_records == sum(len(g.records) for g in result.groups)


def test_as_dict_shape():
    cfg = CorrelatorConfig(key_field="request_id", min_group_size=2)
    result = correlate(_records(), cfg)
    d = result.as_dict()
    assert "total_records" in d
    assert "total_groups" in d
    assert "groups" in d
    for g in d["groups"]:
        assert "key" in g
        assert "count" in g
        assert "records" in g


def test_default_config_uses_request_id():
    records = [
        {"timestamp": 1, "request_id": "r1", "message": "a"},
        {"timestamp": 2, "request_id": "r1", "message": "b"},
    ]
    result = correlate(records)
    assert result.total_groups == 1
