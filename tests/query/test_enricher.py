"""Tests for logslice.query.enricher."""
import pytest

from logslice.query.enricher import (
    EnrichConfig,
    EnrichError,
    EnrichRule,
    apply_rule,
    enrich_records,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _record(**kwargs):
    base = {"level": "info", "message": "hello", "service": "api"}
    base.update(kwargs)
    return base


# ---------------------------------------------------------------------------
# EnrichRule construction
# ---------------------------------------------------------------------------


def test_rule_requires_value_or_fn():
    with pytest.raises(EnrichError, match="must specify either"):
        EnrichRule(target_field="env")


def test_rule_rejects_both_value_and_fn():
    with pytest.raises(EnrichError, match="not both"):
        EnrichRule(target_field="env", value="prod", fn=lambda r: "prod")


# ---------------------------------------------------------------------------
# apply_rule
# ---------------------------------------------------------------------------


def test_apply_rule_static_value():
    rule = EnrichRule(target_field="env", value="production")
    result = apply_rule(_record(), rule)
    assert result["env"] == "production"


def test_apply_rule_callable():
    rule = EnrichRule(
        target_field="upper_level",
        fn=lambda r: r["level"].upper(),
    )
    result = apply_rule(_record(), rule)
    assert result["upper_level"] == "INFO"


def test_apply_rule_does_not_mutate_original():
    original = _record()
    rule = EnrichRule(target_field="env", value="staging")
    apply_rule(original, rule)
    assert "env" not in original


def test_apply_rule_overwrite_false_skips_existing():
    record = _record(env="prod")
    rule = EnrichRule(target_field="env", value="staging", overwrite=False)
    result = apply_rule(record, rule)
    assert result["env"] == "prod"


def test_apply_rule_overwrite_true_replaces_existing():
    record = _record(env="prod")
    rule = EnrichRule(target_field="env", value="staging", overwrite=True)
    result = apply_rule(record, rule)
    assert result["env"] == "staging"


def test_apply_rule_nested_target_field():
    rule = EnrichRule(target_field="meta.region", value="us-east-1")
    result = apply_rule(_record(), rule)
    assert result["meta"]["region"] == "us-east-1"


# ---------------------------------------------------------------------------
# enrich_records
# ---------------------------------------------------------------------------


def test_enrich_records_empty_rules():
    records = [_record(), _record(level="error")]
    config = EnrichConfig(rules=[])
    result = enrich_records(records, config)
    assert result == records


def test_enrich_records_applies_multiple_rules():
    rules = [
        EnrichRule(target_field="env", value="test"),
        EnrichRule(target_field="tagged", fn=lambda r: True),
    ]
    config = EnrichConfig(rules=rules)
    result = enrich_records([_record()], config)
    assert result[0]["env"] == "test"
    assert result[0]["tagged"] is True


def test_enrich_records_empty_input():
    config = EnrichConfig(rules=[EnrichRule(target_field="env", value="x")])
    assert enrich_records([], config) == []


def test_enrich_records_all_records_enriched():
    records = [_record(level="info"), _record(level="error")]
    config = EnrichConfig(
        rules=[EnrichRule(target_field="source", value="logslice")]
    )
    result = enrich_records(records, config)
    assert all(r["source"] == "logslice" for r in result)
