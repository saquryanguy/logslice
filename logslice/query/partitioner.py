"""Partition log records into N roughly equal buckets."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List


class PartitionError(Exception):
    """Raised when partitioning cannot be performed."""


@dataclass
class PartitionerConfig:
    num_partitions: int = 2
    key_field: str | None = None  # if set, partition by hash of field value

    def __post_init__(self) -> None:
        if self.num_partitions < 1:
            raise PartitionError("num_partitions must be >= 1")


@dataclass
class PartitionResult:
    partitions: Dict[int, List[dict]] = field(default_factory=dict)
    total: int = 0
    num_partitions: int = 0

    def as_dict(self) -> dict:
        return {
            "total": self.total,
            "num_partitions": self.num_partitions,
            "partitions": {str(k): v for k, v in self.partitions.items()},
        }


def _get_field(record: dict, field_path: str) -> object:
    """Return a nested field value using dot notation."""
    parts = field_path.split(".")
    node: object = record
    for part in parts:
        if not isinstance(node, dict):
            return None
        node = node.get(part)
    return node


def partition(
    records: List[dict],
    config: PartitionerConfig | None = None,
) -> PartitionResult:
    """Distribute *records* across ``config.num_partitions`` buckets.

    When *key_field* is set each record is assigned to a bucket by hashing
    the field value so that records sharing the same value always land in
    the same bucket.  Without a key field records are distributed in round-
    robin order.
    """
    if config is None:
        config = PartitionerConfig()

    n = config.num_partitions
    buckets: Dict[int, List[dict]] = {i: [] for i in range(n)}

    for idx, record in enumerate(records):
        if config.key_field is not None:
            value = _get_field(record, config.key_field)
            bucket_idx = hash(value) % n
        else:
            bucket_idx = idx % n
        buckets[bucket_idx].append(record)

    return PartitionResult(
        partitions=buckets,
        total=len(records),
        num_partitions=n,
    )
