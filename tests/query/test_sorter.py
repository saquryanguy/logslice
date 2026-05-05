"""Tests for logslice.query.sorter."""

import pytest

from logslice.query.sorter import SortError, sort_records


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _records():
    return [
        {"timestamp": "2024-01-03", "level": "error", "service": "api"},
        {"timestamp": "2024-01-01", "level": "info", "service": "worker"},
        {"timestamp": "2024-01-02", "level": "warn", "service": "api"},
    ]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_sort_asc_by_timestamp():
    result = sort_records(_records(), field="timestamp", direction="asc")
    timestamps = [r["timestamp"] for r in result]
    assert timestamps == ["2024-01-01", "2024-01-02", "2024-01-03"]


def test_sort_desc_by_timestamp():
    result = sort_records(_records(), field="timestamp", direction="desc")
    timestamps = [r["timestamp"] for r in result]
    assert timestamps == ["2024-01-03", "2024-01-02", "2024-01-01"]


def test_sort_asc_default_direction():
    result = sort_records(_records(), field="level")
    levels = [r["level"] for r in result]
    assert levels == sorted(["error", "info", "warn"])


def test_sort_does_not_mutate_input():
    original = _records()
    original_copy = [dict(r) for r in original]
    sort_records(original, field="timestamp")
    assert original == original_copy


def test_sort_missing_field_sorts_last():
    records = [
        {"timestamp": "2024-01-02"},
        {"timestamp": "2024-01-01"},
        {"service": "api"},  # no timestamp
    ]
    result = sort_records(records, field="timestamp", direction="asc")
    assert result[-1] == {"service": "api"}


def test_sort_all_missing_field_preserves_order():
    records = [{"level": "info"}, {"level": "error"}, {"level": "warn"}]
    result = sort_records(records, field="timestamp", direction="asc")
    # All missing — original relative order preserved (stable sort).
    assert [r["level"] for r in result] == ["info", "error", "warn"]


def test_sort_empty_records_returns_empty():
    assert sort_records([], field="timestamp") == []


def test_sort_invalid_direction_raises():
    with pytest.raises(SortError, match="Invalid sort direction"):
        sort_records(_records(), field="timestamp", direction="random")


def test_sort_accepts_generator_input():
    gen = (r for r in _records())
    result = sort_records(gen, field="timestamp", direction="asc")
    assert result[0]["timestamp"] == "2024-01-01"
