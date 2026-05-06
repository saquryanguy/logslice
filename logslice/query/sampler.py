"""Record sampling utilities for logslice queries."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


class SamplerError(Exception):
    """Raised when sampling configuration is invalid."""


@dataclass
class SamplerConfig:
    """Configuration for record sampling."""

    rate: float = 1.0  # fraction of records to keep (0.0 < rate <= 1.0)
    seed: Optional[int] = None  # optional RNG seed for reproducibility
    max_records: Optional[int] = None  # hard cap on returned records


@dataclass
class SampleResult:
    """Result of a sampling operation."""

    records: List[Dict[str, Any]]
    total_seen: int
    total_kept: int

    def as_dict(self) -> Dict[str, Any]:
        return {
            "total_seen": self.total_seen,
            "total_kept": self.total_kept,
            "records": self.records,
        }


def _validate_config(config: SamplerConfig) -> None:
    if not (0.0 < config.rate <= 1.0):
        raise SamplerError(
            f"Sampling rate must be in (0.0, 1.0], got {config.rate}"
        )
    if config.max_records is not None and config.max_records < 0:
        raise SamplerError(
            f"max_records must be non-negative, got {config.max_records}"
        )


def sample(
    records: List[Dict[str, Any]],
    config: Optional[SamplerConfig] = None,
) -> SampleResult:
    """Sample records according to the given config.

    Args:
        records: Input log records.
        config: Sampling configuration. Defaults to rate=1.0 (keep all).

    Returns:
        SampleResult with sampled records and counters.

    Raises:
        SamplerError: If configuration is invalid.
    """
    if config is None:
        config = SamplerConfig()

    _validate_config(config)

    rng = random.Random(config.seed)
    kept: List[Dict[str, Any]] = []

    for record in records:
        if rng.random() < config.rate:
            kept.append(record)
            if config.max_records is not None and len(kept) >= config.max_records:
                # consume remaining to get accurate total_seen
                break

    total_seen = len(records)
    return SampleResult(
        records=kept,
        total_seen=total_seen,
        total_kept=len(kept),
    )
