"""Tests for logslice.query.merger."""

import pytest

from logslice.query.merger import (
    MergeResult,
    MergerConfig,
    MergerError,
    iter_merged,
    merge,
)


def _records(*timestamps):
    return [{"timestamp": ts, "message": f"msg-{ts}"} for ts in timestamps]


# ---------------------------------------------------------------------------
# merge() basic behaviour
# ---------------------------------------------------------------------------

def test_merge_raises_on_empty_stream_list():
    with pytest.raises(MergerError):
        merge([])


def test_merge_single_stream_returns_all_records():
    result = merge([_records("2024-01-01", "2024-01-02", "2024-01-03")])
    assert result.total == 3
    assert result.stream_count == 1


def test_merge_result_as_dict_keys():
    result = merge([_records("2024-01-01")])
    d = result.as_dict()
    assert set(d.keys()) == {"total", "stream_count", "records"}


# ---------------------------------------------------------------------------
# Ordering across streams
# ---------------------------------------------------------------------------

def test_merge_two_streams_sorted_ascending():
    s1 = _records("2024-01-01", "2024-01-03")
    s2 = _records("2024-01-02", "2024-01-04")
    result = merge([s1, s2])
    timestamps = [r["timestamp"] for r in result.records]
    assert timestamps == sorted(timestamps)


def test_merge_three_streams_all_records_present():
    s1 = _records("A", "D")
    s2 = _records("B", "E")
    s3 = _records("C", "F")
    result = merge([s1, s2, s3])
    assert result.total == 6
    assert result.stream_count == 3


def test_merge_empty_stream_among_non_empty():
    s1 = _records("2024-01-01")
    s2: list = []
    s3 = _records("2024-01-02")
    result = merge([s1, s2, s3])
    assert result.total == 2


# ---------------------------------------------------------------------------
# MergerConfig options
# ---------------------------------------------------------------------------

def test_merge_custom_sort_key():
    s1 = [{"level": "error", "msg": "a"}, {"level": "warn", "msg": "c"}]
    s2 = [{"level": "info", "msg": "b"}]
    config = MergerConfig(sort_key="level")
    result = merge([s1, s2], config=config)
    levels = [r["level"] for r in result.records]
    assert levels == sorted(levels)


def test_merge_skip_missing_key_true_includes_record():
    s1 = [{"message": "no-ts"}]
    s2 = _records("2024-01-01")
    config = MergerConfig(skip_missing_key=True)
    result = merge([s1, s2], config=config)
    assert result.total == 2


def test_merge_skip_missing_key_false_omits_record():
    s1 = [{"message": "no-ts"}]
    s2 = _records("2024-01-01")
    config = MergerConfig(skip_missing_key=False)
    result = merge([s1, s2], config=config)
    # record without timestamp should be omitted
    assert all("timestamp" in r for r in result.records)


# ---------------------------------------------------------------------------
# iter_merged lazy interface
# ---------------------------------------------------------------------------

def test_iter_merged_is_lazy_iterator():
    s1 = _records("2024-01-01", "2024-01-03")
    s2 = _records("2024-01-02")
    it = iter_merged([s1, s2])
    first = next(it)
    assert first["timestamp"] == "2024-01-01"


def test_iter_merged_all_records_consumed():
    s1 = _records("X", "Z")
    s2 = _records("Y")
    records = list(iter_merged([s1, s2]))
    assert len(records) == 3
