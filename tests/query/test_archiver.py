"""Tests for logslice.query.archiver."""
import pytest

from logslice.query.archiver import ArchiveConfig, ArchiveError, ArchiveResult, archive


def _records():
    return [
        {"timestamp": "2024-01-01", "level": "info", "message": "a"},
        {"timestamp": "2024-01-01", "level": "error", "message": "b"},
        {"timestamp": "2024-01-02", "level": "info", "message": "c"},
        {"timestamp": "2024-01-03", "level": "warn", "message": "d"},
    ]


def test_config_empty_bucket_field_raises():
    with pytest.raises(ArchiveError, match="bucket_field"):
        ArchiveConfig(bucket_field="")


def test_config_negative_max_buckets_raises():
    with pytest.raises(ArchiveError, match="max_buckets"):
        ArchiveConfig(max_buckets=-1)


def test_archive_groups_by_timestamp():
    result = archive(_records())
    assert "2024-01-01" in result.buckets
    assert len(result.buckets["2024-01-01"]) == 2
    assert len(result.buckets["2024-01-02"]) == 1


def test_archive_total_equals_input_length():
    result = archive(_records())
    assert result.total == 4


def test_archive_bucket_count():
    result = archive(_records())
    assert result.bucket_count == 3


def test_archive_dropped_when_field_missing():
    records = [
        {"level": "info", "message": "no ts"},
        {"timestamp": "2024-01-01", "message": "has ts"},
    ]
    result = archive(records)
    assert result.dropped == 1
    assert result.total == 2


def test_archive_with_tag_field_creates_compound_key():
    cfg = ArchiveConfig(tag_field="level")
    result = archive(_records(), config=cfg)
    assert "2024-01-01::info" in result.buckets
    assert "2024-01-01::error" in result.buckets


def test_archive_bucket_fn_applied():
    cfg = ArchiveConfig(bucket_fn=lambda ts: ts[:7])  # YYYY-MM
    result = archive(_records(), config=cfg)
    assert list(result.buckets.keys()) == ["2024-01"]
    assert len(result.buckets["2024-01"]) == 4


def test_archive_max_buckets_limits_new_buckets():
    cfg = ArchiveConfig(max_buckets=2)
    result = archive(_records(), config=cfg)
    assert result.bucket_count <= 2
    assert result.dropped >= 1


def test_archive_does_not_mutate_input():
    records = [{"timestamp": "2024-01-01", "x": 1}]
    archive(records)
    assert records[0]["x"] == 1


def test_archive_empty_records():
    result = archive([])
    assert result.total == 0
    assert result.bucket_count == 0
    assert result.dropped == 0


def test_as_dict_keys():
    result = archive(_records())
    d = result.as_dict()
    assert set(d.keys()) == {"total", "bucket_count", "dropped", "buckets"}


def test_archive_nested_bucket_field():
    records = [
        {"meta": {"date": "2024-06-01"}, "level": "info"},
        {"meta": {"date": "2024-06-01"}, "level": "error"},
    ]
    cfg = ArchiveConfig(bucket_field="meta.date")
    result = archive(records, config=cfg)
    assert "2024-06-01" in result.buckets
    assert len(result.buckets["2024-06-01"]) == 2
