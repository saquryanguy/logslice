"""Tests for logslice.pipeline.alert_runner."""
from __future__ import annotations

from logslice.pipeline.alert_runner import AlertRunnerConfig, run_alerts
from logslice.query.alerter import AlertEvent, AlertRule
from logslice.query.parser import ParsedQuery, QueryFilter


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _q(*filters: QueryFilter) -> ParsedQuery:
    return ParsedQuery(filters=list(filters))


def _f(field: str, op: str, value) -> QueryFilter:
    return QueryFilter(field=field, operator=op, value=value)


_RECORDS = [
    {"level": "error", "service": "api", "message": "fail"},
    {"level": "info", "service": "api", "message": "ok"},
    {"level": "error", "service": "db", "message": "timeout"},
]


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------

def test_run_alerts_no_rules_empty_events():
    config = AlertRunnerConfig(rules=[])
    result = run_alerts(iter(_RECORDS), config)
    assert result.total_evaluated == 3
    assert result.events == []


def test_run_alerts_fires_for_matching_records():
    rule = AlertRule(name="err", query=_q(_f("level", "eq", "error")))
    config = AlertRunnerConfig(rules=[rule])
    result = run_alerts(iter(_RECORDS), config)
    assert len(result.events) == 2


def test_run_alerts_runner_on_alert_called():
    fired: list[AlertEvent] = []
    rule = AlertRule(name="err", query=_q(_f("level", "eq", "error")))
    config = AlertRunnerConfig(rules=[rule], on_alert=fired.append)
    run_alerts(iter(_RECORDS), config)
    assert len(fired) == 2


def test_run_alerts_runner_and_rule_callbacks_both_called():
    rule_fired: list[AlertEvent] = []
    runner_fired: list[AlertEvent] = []
    rule = AlertRule(
        name="err",
        query=_q(_f("level", "eq", "error")),
        on_fire=rule_fired.append,
    )
    config = AlertRunnerConfig(rules=[rule], on_alert=runner_fired.append)
    run_alerts(iter(_RECORDS), config)
    assert len(rule_fired) == 2
    assert len(runner_fired) == 2


def test_run_alerts_accepts_generator():
    rule = AlertRule(name="err", query=_q(_f("level", "eq", "error")))
    config = AlertRunnerConfig(rules=[rule])
    gen = (r for r in _RECORDS)
    result = run_alerts(gen, config)
    assert result.total_evaluated == 3


def test_run_alerts_result_as_dict():
    rule = AlertRule(name="err", query=_q(_f("level", "eq", "error")))
    config = AlertRunnerConfig(rules=[rule])
    result = run_alerts(iter(_RECORDS), config)
    d = result.as_dict()
    assert d["total_evaluated"] == 3
    assert len(d["events"]) == 2
