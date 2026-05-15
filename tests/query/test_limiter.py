"""Tests for logslice.query.limiter."""
import pytest

from logslice.query.limiter import LimiterConfig, LimiterError, LimitResult, limit


def _records(n: int, level: str = "info", service: str = "svc") -> list:
    return [{"level": level, "service": service, "msg": f"msg-{i}"} for i in range(n)]


# ---------------------------------------------------------------------------
# Config validation
# ---------------------------------------------------------------------------

def test_config_default_max_records():
    cfg = LimiterConfig()
    assert cfg.max_records == 100


def test_config_zero_max_records_raises():
    with pytest.raises(LimiterError, match="max_records"):
        LimiterConfig(max_records=0)


def test_config_negative_max_records_raises():
    with pytest.raises(LimiterError, match="max_records"):
        LimiterConfig(max_records=-5)


def test_config_zero_max_per_bucket_raises():
    with pytest.raises(LimiterError, match="max_per_bucket"):
        LimiterConfig(max_per_bucket=0)


def test_config_negative_max_per_bucket_raises():
    with pytest.raises(LimiterError, match="max_per_bucket"):
        LimiterConfig(max_per_bucket=-1)


# ---------------------------------------------------------------------------
# Basic limiting
# ---------------------------------------------------------------------------

def test_empty_records_returns_empty_result():
    result = limit([])
    assert result.kept == []
    assert result.dropped == 0
    assert result.total == 0


def test_all_kept_when_under_global_limit():
    records = _records(5)
    result = limit(records, LimiterConfig(max_records=10))
    assert len(result.kept) == 5
    assert result.dropped == 0


def test_excess_records_are_dropped_globally():
    records = _records(10)
    result = limit(records, LimiterConfig(max_records=4))
    assert len(result.kept) == 4
    assert result.dropped == 6
    assert result.total == 10


# ---------------------------------------------------------------------------
# Per-bucket limiting
# ---------------------------------------------------------------------------

def test_per_bucket_cap_applied():
    records = _records(6, level="error") + _records(6, level="info")
    cfg = LimiterConfig(max_records=100, bucket_field="level", max_per_bucket=3)
    result = limit(records, cfg)
    assert result.by_bucket["error"] == 3
    assert result.by_bucket["info"] == 3
    assert result.dropped == 6


def test_by_bucket_counts_reflect_kept_records():
    records = _records(3, level="warn") + _records(2, level="debug")
    cfg = LimiterConfig(max_records=10, bucket_field="level")
    result = limit(records, cfg)
    assert result.by_bucket["warn"] == 3
    assert result.by_bucket["debug"] == 2


def test_missing_bucket_field_goes_to_unknown():
    records = [{"msg": "no-level"}, {"msg": "also-no-level"}]
    cfg = LimiterConfig(max_records=10, bucket_field="level")
    result = limit(records, cfg)
    assert "__unknown__" in result.by_bucket
    assert result.by_bucket["__unknown__"] == 2


# ---------------------------------------------------------------------------
# as_dict
# ---------------------------------------------------------------------------

def test_as_dict_keys():
    result = limit(_records(3), LimiterConfig(max_records=2))
    d = result.as_dict()
    assert set(d.keys()) == {"kept", "dropped", "total", "by_bucket"}
    assert d["kept"] == 2
    assert d["dropped"] == 1
    assert d["total"] == 3
