"""Tests for logslice.query.transformer."""

from __future__ import annotations

import pytest

from logslice.query.transformer import (
    TransformConfig,
    TransformError,
    TransformRule,
    apply_rule,
    transform_record,
    transform_records,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _rule(src: str, tgt: str, fn, skip_missing: bool = True) -> TransformRule:
    return TransformRule(source_field=src, target_field=tgt, fn=fn, skip_missing=skip_missing)


# ---------------------------------------------------------------------------
# apply_rule
# ---------------------------------------------------------------------------

def test_apply_rule_transforms_value():
    record = {"level": "info"}
    rule = _rule("level", "level", str.upper)
    result = apply_rule(record, rule)
    assert result["level"] == "INFO"


def test_apply_rule_writes_to_different_target_field():
    record = {"level": "warn"}
    rule = _rule("level", "level_upper", str.upper)
    result = apply_rule(record, rule)
    assert result["level_upper"] == "WARN"
    assert result["level"] == "warn"  # original preserved


def test_apply_rule_does_not_mutate_original():
    record = {"level": "debug"}
    rule = _rule("level", "level", str.upper)
    apply_rule(record, rule)
    assert record["level"] == "debug"


def test_apply_rule_skip_missing_returns_unchanged():
    record = {"message": "hello"}
    rule = _rule("level", "level", str.upper, skip_missing=True)
    result = apply_rule(record, rule)
    assert result == record


def test_apply_rule_skip_missing_false_raises():
    record = {"message": "hello"}
    rule = _rule("level", "level", str.upper, skip_missing=False)
    with pytest.raises(TransformError, match="level"):
        apply_rule(record, rule)


def test_apply_rule_fn_exception_raises_transform_error():
    record = {"count": "not-a-number"}
    rule = _rule("count", "count", int)
    with pytest.raises(TransformError):
        apply_rule(record, rule)


# ---------------------------------------------------------------------------
# transform_record
# ---------------------------------------------------------------------------

def test_transform_record_applies_rules_sequentially():
    record = {"level": "info", "count": "42"}
    config = TransformConfig(rules=[
        _rule("level", "level", str.upper),
        _rule("count", "count", int),
    ])
    result = transform_record(record, config)
    assert result["level"] == "INFO"
    assert result["count"] == 42


def test_transform_record_empty_rules_returns_copy():
    record = {"level": "info"}
    config = TransformConfig()
    result = transform_record(record, config)
    assert result == record
    assert result is not record


def test_transform_record_chained_field_rename():
    record = {"ts": "2024-01-01"}
    config = TransformConfig(rules=[
        _rule("ts", "timestamp", lambda v: v),
    ])
    result = transform_record(record, config)
    assert "timestamp" in result
    assert result["timestamp"] == "2024-01-01"


# ---------------------------------------------------------------------------
# transform_records
# ---------------------------------------------------------------------------

def test_transform_records_applies_to_all():
    records = [{"level": "info"}, {"level": "error"}]
    config = TransformConfig(rules=[_rule("level", "level", str.upper)])
    results = transform_records(records, config)
    assert [r["level"] for r in results] == ["INFO", "ERROR"]


def test_transform_records_empty_list():
    config = TransformConfig(rules=[_rule("level", "level", str.upper)])
    assert transform_records([], config) == []
