"""Tests for logslice.query.throttler."""
import pytest

from logslice.query.throttler import (
    ThrottlerConfig,
    ThrottlerError,
    ThrottleResult,
    as_dict,
    throttle,
)


def _records(n: int, hour: str = "2024-01-01T10") -> list:
    return [{"timestamp": f"{hour}:00:{i:02d}Z", "level": "info", "msg": f"msg {i}"} for i in range(n)]


def test_empty_records_returns_empty_result():
    result = throttle([])
    assert result.records == []
    assert result.total_input == 0
    assert result.total_dropped == 0


def test_all_kept_when_under_limit():
    cfg = ThrottlerConfig(max_per_window=10)
    records = _records(5)
    result = throttle(records, cfg)
    assert result.total_input == 5
    assert result.total_dropped == 0
    assert len(result.records) == 5


def test_excess_records_are_dropped():
    cfg = ThrottlerConfig(max_per_window=3)
    records = _records(7)
    result = throttle(records, cfg)
    assert result.total_input == 7
    assert result.total_dropped == 4
    assert len(result.records) == 3


def test_limit_applied_per_bucket():
    cfg = ThrottlerConfig(max_per_window=2, window_granularity=13)
    hour_a = _records(4, hour="2024-01-01T10")
    hour_b = _records(4, hour="2024-01-01T11")
    result = throttle(hour_a + hour_b, cfg)
    # 2 kept per bucket × 2 buckets = 4
    assert len(result.records) == 4
    assert result.total_dropped == 4


def test_order_of_records_preserved():
    cfg = ThrottlerConfig(max_per_window=5)
    records = _records(5)
    result = throttle(records, cfg)
    assert result.records == records


def test_default_config_used_when_none():
    records = _records(10)
    result = throttle(records, None)
    assert len(result.records) == 10


def test_max_per_window_zero_raises():
    with pytest.raises(ThrottlerError, match="max_per_window"):
        throttle(_records(3), ThrottlerConfig(max_per_window=0))


def test_window_granularity_zero_raises():
    with pytest.raises(ThrottlerError, match="window_granularity"):
        throttle(_records(3), ThrottlerConfig(max_per_window=5, window_granularity=0))


def test_missing_window_field_uses_empty_bucket():
    cfg = ThrottlerConfig(max_per_window=2)
    records = [{"level": "info", "msg": f"m{i}"} for i in range(5)]
    result = throttle(records, cfg)
    assert len(result.records) == 2
    assert result.total_dropped == 3


def test_as_dict_structure():
    result = ThrottleResult(records=[{"a": 1}], total_input=3, total_dropped=2)
    d = as_dict(result)
    assert d["total_input"] == 3
    assert d["total_dropped"] == 2
    assert d["records"] == [{"a": 1}]
