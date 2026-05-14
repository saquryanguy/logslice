"""Tests for logslice.query.windower."""

import pytest

from logslice.query.windower import (
    WindowError,
    WindowerConfig,
    window_records,
)


def _records(*timestamps, field="timestamp"):
    return [{field: ts, "message": f"msg@{ts}"} for ts in timestamps]


# ---------------------------------------------------------------------------
# WindowerConfig validation
# ---------------------------------------------------------------------------

def test_config_default_window_is_60():
    cfg = WindowerConfig()
    assert cfg.window_seconds == 60


def test_config_zero_window_raises():
    with pytest.raises(WindowError, match="positive"):
        WindowerConfig(window_seconds=0)


def test_config_negative_window_raises():
    with pytest.raises(WindowError):
        WindowerConfig(window_seconds=-10)


# ---------------------------------------------------------------------------
# Basic bucketing
# ---------------------------------------------------------------------------

def test_empty_records_returns_empty_result():
    result = window_records([])
    assert result.total == 0
    assert result.dropped == 0
    assert result.windows == {}


def test_single_record_creates_one_window():
    result = window_records(_records(1_000), WindowerConfig(window_seconds=60))
    assert len(result.windows) == 1
    assert result.total == 1


def test_records_in_same_window_grouped_together():
    cfg = WindowerConfig(window_seconds=60)
    recs = _records(0, 30, 59)
    result = window_records(recs, cfg)
    assert len(result.windows) == 1
    assert len(list(result.windows.values())[0]) == 3


def test_records_in_different_windows_split_correctly():
    cfg = WindowerConfig(window_seconds=60)
    recs = _records(0, 60, 120)
    result = window_records(recs, cfg)
    assert len(result.windows) == 3


def test_bucket_key_aligns_to_window_boundary():
    cfg = WindowerConfig(window_seconds=300)
    recs = _records(299, 300, 599, 600)
    result = window_records(recs, cfg)
    keys = sorted(result.windows.keys())
    assert keys == [0, 300, 600]
    assert len(result.windows[0]) == 1
    assert len(result.windows[300]) == 2


# ---------------------------------------------------------------------------
# Missing / invalid timestamps
# ---------------------------------------------------------------------------

def test_missing_timestamp_raises_by_default():
    recs = [{"message": "no ts"}]
    with pytest.raises(WindowError, match="missing timestamp"):
        window_records(recs)


def test_missing_timestamp_skipped_when_skip_missing():
    recs = [{"message": "no ts"}, {"timestamp": 100, "message": "ok"}]
    cfg = WindowerConfig(skip_missing=True)
    result = window_records(recs, cfg)
    assert result.dropped == 1
    assert result.total == 2
    assert sum(len(v) for v in result.windows.values()) == 1


def test_non_numeric_timestamp_raises_by_default():
    recs = [{"timestamp": "not-a-number"}]
    with pytest.raises(WindowError, match="Cannot parse"):
        window_records(recs)


def test_non_numeric_timestamp_skipped_when_skip_missing():
    recs = [{"timestamp": "bad"}, {"timestamp": 200}]
    cfg = WindowerConfig(skip_missing=True)
    result = window_records(recs, cfg)
    assert result.dropped == 1


# ---------------------------------------------------------------------------
# as_dict
# ---------------------------------------------------------------------------

def test_as_dict_contains_expected_keys():
    result = window_records(_records(0, 60), WindowerConfig(window_seconds=60))
    d = result.as_dict()
    assert "windows" in d
    assert "total" in d
    assert "dropped" in d
    assert "window_count" in d
    assert d["window_count"] == 2
