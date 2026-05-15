"""Tests for logslice.query.dispatcher."""
import pytest

from logslice.query.dispatcher import (
    DispatchConfig,
    DispatchError,
    DispatchRule,
    dispatch,
)
from logslice.query.parser import ParsedQuery, QueryFilter


def _q(*filters) -> ParsedQuery:
    return ParsedQuery(filters=list(filters))


def _f(field, op, value) -> QueryFilter:
    return QueryFilter(field=field, operator=op, value=value)


_records = [
    {"level": "error", "service": "auth", "message": "failed"},
    {"level": "info", "service": "auth", "message": "started"},
    {"level": "warn", "service": "api", "message": "slow"},
    {"level": "error", "service": "api", "message": "crash"},
]


def test_rule_requires_query_or_predicate():
    with pytest.raises(DispatchError, match="requires a query or predicate"):
        DispatchRule(name="r")


def test_rule_rejects_both_query_and_predicate():
    with pytest.raises(DispatchError, match="cannot have both"):
        DispatchRule(name="r", query=_q(), predicate=lambda r: True)


def test_rule_empty_name_raises():
    with pytest.raises(DispatchError, match="name must not be empty"):
        DispatchRule(name="  ", query=_q())


def test_dispatch_no_rules_no_default_raises():
    with pytest.raises(DispatchError, match="at least one rule"):
        dispatch(_records, DispatchConfig())


def test_dispatch_by_level_error():
    rule = DispatchRule(name="errors", query=_q(_f("level", "eq", "error")))
    result = dispatch(_records, DispatchConfig(rules=[rule]))
    assert result.total == 4
    assert len(result.dispatched["errors"]) == 2
    assert result.unmatched == [
        {"level": "info", "service": "auth", "message": "started"},
        {"level": "warn", "service": "api", "message": "slow"},
    ]


def test_dispatch_multiple_rules_no_stop():
    r_errors = DispatchRule(name="errors", query=_q(_f("level", "eq", "error")))
    r_auth = DispatchRule(name="auth", query=_q(_f("service", "eq", "auth")))
    result = dispatch(_records, DispatchConfig(rules=[r_errors, r_auth]))
    # auth error record matches BOTH rules
    assert len(result.dispatched["errors"]) == 2
    assert len(result.dispatched["auth"]) == 2
    assert result.unmatched == [{"level": "warn", "service": "api", "message": "slow"}]


def test_dispatch_stop_on_match():
    r_errors = DispatchRule(name="errors", query=_q(_f("level", "eq", "error")), stop_on_match=True)
    r_auth = DispatchRule(name="auth", query=_q(_f("service", "eq", "auth")))
    result = dispatch(_records, DispatchConfig(rules=[r_errors, r_auth]))
    # auth+error record stops at 'errors'; only plain info record reaches 'auth'
    assert len(result.dispatched["errors"]) == 2
    assert result.dispatched.get("auth", []) == [
        {"level": "info", "service": "auth", "message": "started"}
    ]


def test_dispatch_default_handler():
    rule = DispatchRule(name="errors", query=_q(_f("level", "eq", "error")))
    result = dispatch(_records, DispatchConfig(rules=[rule], default_handler="other"))
    assert "other" in result.dispatched
    assert len(result.dispatched["other"]) == 2
    assert result.unmatched == []


def test_dispatch_predicate_rule():
    rule = DispatchRule(name="api", predicate=lambda r: r.get("service") == "api")
    result = dispatch(_records, DispatchConfig(rules=[rule]))
    assert len(result.dispatched["api"]) == 2


def test_dispatch_as_dict_keys():
    rule = DispatchRule(name="errors", query=_q(_f("level", "eq", "error")))
    result = dispatch(_records, DispatchConfig(rules=[rule]))
    d = result.as_dict()
    assert set(d.keys()) == {"total", "dispatched", "unmatched"}
    assert d["total"] == 4
    assert d["dispatched"]["errors"] == 2


def test_dispatch_empty_records():
    rule = DispatchRule(name="errors", query=_q(_f("level", "eq", "error")))
    result = dispatch([], DispatchConfig(rules=[rule]))
    assert result.total == 0
    assert result.dispatched == {}
    assert result.unmatched == []
