"""Tests for logslice.query.partitioner."""

from __future__ import annotations

import pytest

from logslice.query.partitioner import (
    PartitionError,
    PartitionResult,
    PartitionerConfig,
    partition,
)


def _records(n: int) -> list[dict]:
    return [
        {"level": "info" if i % 2 == 0 else "error", "seq": i, "svc": f"svc{i % 3}"}
        for i in range(n)
    ]


# --- config validation ---

def test_config_default_num_partitions() -> None:
    cfg = PartitionerConfig()
    assert cfg.num_partitions == 2


def test_config_zero_partitions_raises() -> None:
    with pytest.raises(PartitionError):
        PartitionerConfig(num_partitions=0)


def test_config_negative_partitions_raises() -> None:
    with pytest.raises(PartitionError):
        PartitionerConfig(num_partitions=-3)


# --- basic partitioning ---

def test_empty_records_returns_empty_partitions() -> None:
    result = partition([])
    assert result.total == 0
    assert all(len(v) == 0 for v in result.partitions.values())


def test_total_equals_input_length() -> None:
    records = _records(10)
    result = partition(records, PartitionerConfig(num_partitions=3))
    assert result.total == 10


def test_all_records_distributed() -> None:
    records = _records(9)
    result = partition(records, PartitionerConfig(num_partitions=3))
    combined = [r for bucket in result.partitions.values() for r in bucket]
    assert len(combined) == 9


def test_round_robin_distribution() -> None:
    records = _records(6)
    result = partition(records, PartitionerConfig(num_partitions=3))
    # each partition should have exactly 2 records
    for bucket in result.partitions.values():
        assert len(bucket) == 2


def test_single_partition_contains_all() -> None:
    records = _records(5)
    result = partition(records, PartitionerConfig(num_partitions=1))
    assert len(result.partitions[0]) == 5


# --- key-field partitioning ---

def test_key_field_same_value_same_bucket() -> None:
    records = [
        {"level": "info", "svc": "alpha"},
        {"level": "error", "svc": "alpha"},
        {"level": "warn", "svc": "beta"},
    ]
    cfg = PartitionerConfig(num_partitions=4, key_field="svc")
    result = partition(records, cfg)
    alpha_bucket = hash("alpha") % 4
    beta_bucket = hash("beta") % 4
    assert all(r["svc"] == "alpha" for r in result.partitions[alpha_bucket])
    assert all(r["svc"] == "beta" for r in result.partitions[beta_bucket])


def test_key_field_missing_value_hashes_none() -> None:
    records = [{"level": "info"}, {"level": "error"}]
    cfg = PartitionerConfig(num_partitions=2, key_field="svc")
    result = partition(records, cfg)
    # should not raise; both records land in the same bucket
    combined = [r for bucket in result.partitions.values() for r in bucket]
    assert len(combined) == 2


# --- as_dict ---

def test_as_dict_keys() -> None:
    result = partition(_records(4), PartitionerConfig(num_partitions=2))
    d = result.as_dict()
    assert set(d.keys()) == {"total", "num_partitions", "partitions"}
    assert d["total"] == 4
    assert d["num_partitions"] == 2
    assert isinstance(d["partitions"], dict)
