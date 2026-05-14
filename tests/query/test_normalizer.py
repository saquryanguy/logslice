"""Tests for logslice.query.normalizer."""

import pytest

from logslice.query.normalizer import (
    NormalizeConfig,
    NormalizeError,
    NormalizeRule,
    NormalizeResult,
    normalize,
)


def _records():
    return [
        {"lvl": "error", "svc": "auth", "msg": "login failed"},
        {"lvl": "info", "svc": "api", "msg": "request ok"},
        {"level": "warn", "service": "db", "message": "slow query"},
    ]


def test_rule_empty_source_raises():
    with pytest.raises(NormalizeError, match="source"):
        NormalizeRule(source="", target="level")


def test_rule_empty_target_raises():
    with pytest.raises(NormalizeError, match="target"):
        NormalizeRule(source="lvl", target="")


def test_empty_config_returns_copies():
    records = _records()
    result = normalize(records, NormalizeConfig())
    assert result.total == 3
    assert result.rules_applied == 0
    assert result.records == records


def test_rename_field():
    records = [{"lvl": "error", "msg": "oops"}]
    config = NormalizeConfig(rules=[NormalizeRule(source="lvl", target="level")])
    result = normalize(records, config)
    assert result.records[0]["level"] == "error"
    assert "lvl" not in result.records[0]


def test_drop_source_false_keeps_original():
    records = [{"lvl": "info"}]
    config = NormalizeConfig(
        rules=[NormalizeRule(source="lvl", target="level")],
        drop_source=False,
    )
    result = normalize(records, config)
    assert result.records[0]["level"] == "info"
    assert result.records[0]["lvl"] == "info"


def test_transform_applied():
    records = [{"level": "ERROR"}]
    config = NormalizeConfig(
        rules=[NormalizeRule(source="level", target="level", transform=str.lower)]
    )
    result = normalize(records, config)
    assert result.records[0]["level"] == "error"


def test_missing_source_field_skipped():
    records = [{"message": "hello"}]
    config = NormalizeConfig(rules=[NormalizeRule(source="lvl", target="level")])
    result = normalize(records, config)
    assert "level" not in result.records[0]
    assert result.rules_applied == 0


def test_rules_applied_count():
    records = _records()[:2]  # both have lvl and svc
    config = NormalizeConfig(
        rules=[
            NormalizeRule(source="lvl", target="level"),
            NormalizeRule(source="svc", target="service"),
        ]
    )
    result = normalize(records, config)
    assert result.rules_applied == 4  # 2 rules x 2 records


def test_does_not_mutate_original():
    records = [{"lvl": "info", "msg": "hi"}]
    original_keys = set(records[0].keys())
    config = NormalizeConfig(rules=[NormalizeRule(source="lvl", target="level")])
    normalize(records, config)
    assert set(records[0].keys()) == original_keys


def test_multiple_rules_chained():
    records = [{"lvl": "WARN", "svc": "cache", "msg": "miss"}]
    config = NormalizeConfig(
        rules=[
            NormalizeRule(source="lvl", target="level", transform=str.lower),
            NormalizeRule(source="svc", target="service"),
            NormalizeRule(source="msg", target="message"),
        ]
    )
    result = normalize(records, config)
    rec = result.records[0]
    assert rec == {"level": "warn", "service": "cache", "message": "miss"}


def test_as_dict_keys():
    result = NormalizeResult(records=[], total=0, rules_applied=0)
    d = result.as_dict()
    assert set(d.keys()) == {"total", "rules_applied", "records"}
