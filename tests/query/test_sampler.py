"""Tests for logslice.query.sampler."""

from __future__ import annotations

import pytest
from typing import List, Dict, Any

from logslice.query.sampler import (
    SamplerConfig,
    SamplerError,
    SampleResult,
    sample,
)


def _records(n: int = 10) -> List[Dict[str, Any]]:
    return [
        {"level": "info", "service": "svc", "message": f"msg {i}", "idx": i}
        for i in range(n)
    ]


def test_sample_rate_one_keeps_all():
    recs = _records(10)
    result = sample(recs, SamplerConfig(rate=1.0))
    assert result.total_seen == 10
    assert result.total_kept == 10
    assert len(result.records) == 10


def test_sample_rate_zero_raises():
    with pytest.raises(SamplerError, match="rate"):
        sample(_records(), SamplerConfig(rate=0.0))


def test_sample_negative_rate_raises():
    with pytest.raises(SamplerError, match="rate"):
        sample(_records(), SamplerConfig(rate=-0.1))


def test_sample_rate_above_one_raises():
    with pytest.raises(SamplerError, match="rate"):
        sample(_records(), SamplerConfig(rate=1.5))


def test_sample_negative_max_records_raises():
    with pytest.raises(SamplerError, match="max_records"):
        sample(_records(), SamplerConfig(rate=1.0, max_records=-1))


def test_sample_with_seed_is_reproducible():
    recs = _records(100)
    r1 = sample(recs, SamplerConfig(rate=0.3, seed=42))
    r2 = sample(recs, SamplerConfig(rate=0.3, seed=42))
    assert r1.records == r2.records
    assert r1.total_kept == r2.total_kept


def test_sample_different_seeds_differ():
    recs = _records(100)
    r1 = sample(recs, SamplerConfig(rate=0.5, seed=1))
    r2 = sample(recs, SamplerConfig(rate=0.5, seed=2))
    # Very unlikely to be identical with 100 records at 50%
    assert r1.records != r2.records


def test_sample_max_records_caps_output():
    recs = _records(50)
    result = sample(recs, SamplerConfig(rate=1.0, max_records=5))
    assert result.total_kept == 5
    assert len(result.records) == 5


def test_sample_max_records_zero_returns_empty():
    recs = _records(10)
    result = sample(recs, SamplerConfig(rate=1.0, max_records=0))
    assert result.total_kept == 0
    assert result.records == []


def test_sample_empty_records():
    result = sample([], SamplerConfig(rate=0.5, seed=0))
    assert result.total_seen == 0
    assert result.total_kept == 0
    assert result.records == []


def test_sample_default_config_keeps_all():
    recs = _records(5)
    result = sample(recs)
    assert result.total_kept == 5


def test_as_dict_structure():
    recs = _records(3)
    result = sample(recs, SamplerConfig(rate=1.0))
    d = result.as_dict()
    assert "total_seen" in d
    assert "total_kept" in d
    assert "records" in d
    assert d["total_seen"] == 3
    assert d["total_kept"] == 3
