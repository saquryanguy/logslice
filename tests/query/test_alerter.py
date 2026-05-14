"""Tests for logslice.query.alerter."""
from __future__ import annotations

import pytest

from logslice.query.alerter import (
    AlertError,
    AlertEvent,
    AlertRule,
    AlertResult,
    evaluate_alerts,
)
from logslice.query.parser import ParsedQuery, QueryFilter


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _q(*filters: QueryFilter) -> ParsedQuery:
    return ParsedQuery(filters=list(filters))


def _f(field: str, op: str, value) -> QueryFilter:
    return QueryFilter(field=field, operator=op, value=value)


_ERROR_RECORDS = [
    {"level": "error", "service": "api", "message": "boom"},
    {"level": "error", "service": "worker", "message": "crash"},
    {"level": "info", "service": "api", "message": "ok"},
]


# ---------------------------------------------------------------------------
# AlertRule validation
# ---------------------------------------------------------------------------

def test_rule_empty_name_raises():
    with pytest.raises(AlertError, match="non-empty"):
        AlertRule(name="", query=_q())


def test_rule_invalid_severity_raises():
    with pytest.raises(AlertError, match="severity"):
        AlertRule(name="r", query=_q(), severity="fatal")


def test_rule_valid_severities():
    for sev in ("info", "warning", "error", "critical"):
        rule = AlertRule(name="r", query=_q(), severity=sev)
        assert rule.severity == sev


# ---------------------------------------------------------------------------
# evaluate_alerts
# ---------------------------------------------------------------------------

def test_no_rules_returns_empty_events():
    result = evaluate_alerts(_ERROR_RECORDS, rules=[])
    assert result.total_evaluated == 3
    assert result.events == []


def test_no_matching_records_returns_empty_events():
    rule = AlertRule(name="high", query=_q(_f("level", "eq", "critical")))
    result = evaluate_alerts(_ERROR_RECORDS, rules=[rule])
    assert result.events == []


def test_matching_records_fire_events():
    rule = AlertRule(name="errors", query=_q(_f("level", "eq", "error")), severity="error")
    result = evaluate_alerts(_ERROR_RECORDS, rules=[rule])
    assert len(result.events) == 2
    assert all(e.rule_name == "errors" for e in result.events)
    assert all(e.severity == "error" for e in result.events)


def test_total_evaluated_reflects_all_records():
    rule = AlertRule(name="r", query=_q(_f("level", "eq", "error")))
    result = evaluate_alerts(_ERROR_RECORDS, rules=[rule])
    assert result.total_evaluated == 3


def test_on_fire_callback_called():
    fired = []
    rule = AlertRule(
        name="cb",
        query=_q(_f("level", "eq", "error")),
        on_fire=fired.append,
    )
    evaluate_alerts(_ERROR_RECORDS, rules=[rule])
    assert len(fired) == 2
    assert all(isinstance(e, AlertEvent) for e in fired)


def test_multiple_rules_each_evaluated():
    """Each rule is evaluated independently against all records."""
    rule_errors = AlertRule(name="errors", query=_q(_f("level", "eq", "error")))
    rule_info = AlertRule(name="info", query=_q(_f("level", "eq", "info")))
    result = evaluate_alerts(_ERROR_RECORDS, rules=[rule_errors, rule_info])
    error_events = [e for e in result.events if e.rule_name == "errors"]
    info_events = [e for e in result.events if e.rule_name == "info"]
    assert len(error_events) == 2
    assert len(info_events) == 1
    assert result.total_evaluated == 3
