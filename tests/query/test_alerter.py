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
    r1 = AlertRule(name="err", query=_q(_f("level", "eq", "error")))
    r2 = AlertRule(name="api", query=_q(_f("service", "eq", "api")))
    result = evaluate_alerts(_ERROR_RECORDS, rules=[r1, r2])
    names = [e.rule_name for e in result.events]
    assert names.count("err") == 2
    assert names.count("api") == 2


def test_alert_event_as_dict_keys():
    rule = AlertRule(name="r", query=_q(_f("level", "eq", "error")), message="uh oh")
    result = evaluate_alerts([_ERROR_RECORDS[0]], rules=[rule])
    d = result.events[0].as_dict()
    assert set(d.keys()) == {"rule_name", "severity", "message", "record"}
    assert d["message"] == "uh oh"


def test_result_as_dict_structure():
    rule = AlertRule(name="r", query=_q(_f("level", "eq", "error")))
    result = evaluate_alerts(_ERROR_RECORDS, rules=[rule])
    d = result.as_dict()
    assert "total_evaluated" in d
    assert "events" in d
    assert isinstance(d["events"], list)
