"""Tests for logslice.query.deduplicator."""

import pytest

from logslice.query.deduplicator import (
    DeduplicatorConfig,
    DeduplicatorError,
    DeduplicationResult,
    deduplicate,
)


def _records():
    return [
        {"level": "info", "service": "api", "message": "started"},
        {"level": "info", "service": "api", "message": "started"},  # duplicate
        {"level": "error", "service": "api", "message": "failed"},
        {"level": "info", "service": "worker", "message": "started"},
        {"level": "error", "service": "api", "message": "failed"},  # duplicate
    ]


def test_empty_records_returns_empty_result():
    result = deduplicate([])
    assert result.total_input == 0
    assert result.duplicates_removed == 0
    assert result.records == []


def test_no_duplicates_returns_all_records():
    records = [
        {"level": "info", "service": "a", "message": "x"},
        {"level": "warn", "service": "b", "message": "y"},
    ]
    result = deduplicate(records)
    assert result.total_input == 2
    assert result.duplicates_removed == 0
    assert len(result.records) == 2


def test_removes_exact_duplicates():
    result = deduplicate(_records())
    assert result.total_input == 5
    assert result.duplicates_removed == 2
    assert len(result.records) == 3


def test_preserves_first_occurrence():
    records = [
        {"level": "info", "service": "api", "message": "hello", "extra": 1},
        {"level": "info", "service": "api", "message": "hello", "extra": 2},
    ]
    result = deduplicate(records)
    assert len(result.records) == 1
    assert result.records[0]["extra"] == 1


def test_custom_key_fields():
    records = [
        {"level": "info", "service": "api", "message": "a"},
        {"level": "info", "service": "worker", "message": "a"},  # same level+message
    ]
    config = DeduplicatorConfig(key_fields=["level", "message"])
    result = deduplicate(records, config)
    assert result.duplicates_removed == 1
    assert len(result.records) == 1


def test_as_dict_contains_expected_keys():
    result = deduplicate(_records())
    d = result.as_dict()
    assert d["total_input"] == 5
    assert d["duplicates_removed"] == 2
    assert d["unique_count"] == 3


def test_empty_key_fields_raises():
    config = DeduplicatorConfig(key_fields=[])
    with pytest.raises(DeduplicatorError, match="key_fields"):
        deduplicate(_records(), config)


def test_invalid_max_seen_raises():
    config = DeduplicatorConfig(max_seen=0)
    with pytest.raises(DeduplicatorError, match="max_seen"):
        deduplicate(_records(), config)


def test_max_seen_limits_memory():
    # With max_seen=2, older keys are evicted; deduplication still works
    # but may not catch all duplicates across a large window.
    records = [
        {"level": "info", "service": "a", "message": "x"},
        {"level": "info", "service": "b", "message": "y"},
        {"level": "info", "service": "c", "message": "z"},
        {"level": "info", "service": "a", "message": "x"},  # 'a/x' was evicted
    ]
    config = DeduplicatorConfig(max_seen=2)
    result = deduplicate(records, config)
    # After eviction the last record is treated as new
    assert result.total_input == 4
    assert result.duplicates_removed == 0
    assert len(result.records) == 4


def test_single_record_no_duplicates():
    records = [{"level": "debug", "service": "x", "message": "only one"}]
    result = deduplicate(records)
    assert result.total_input == 1
    assert result.duplicates_removed == 0
