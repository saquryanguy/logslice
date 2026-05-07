"""Tests for logslice.query.router."""
from __future__ import annotations

from typing import Any, Dict, List

import pytest

from logslice.query.parser import ParsedQuery, QueryFilter
from logslice.query.router import (
    Route,
    RouterConfig,
    RouterError,
    RoutingResult,
    route_records,
)


def _q(*filters: QueryFilter) -> ParsedQuery:
    return ParsedQuery(filters=list(filters))


def _f(field: str, op: str, value: Any) -> QueryFilter:
    return QueryFilter(field=field, operator=op, value=value)


_RECORDS: List[Dict[str, Any]] = [
    {"level": "error", "service": "api", "message": "oops"},
    {"level": "info", "service": "worker", "message": "ok"},
    {"level": "error", "service": "worker", "message": "fail"},
]


def test_route_by_level():
    config = RouterConfig(
        routes=[
            Route(name="errors", query=_q(_f("level", "eq", "error"))),
            Route(name="info", query=_q(_f("level", "eq", "info"))),
        ]
    )
    results = route_records(_RECORDS, config)
    assert results[0].matched_routes == ["errors"]
    assert results[1].matched_routes == ["info"]
    assert results[2].matched_routes == ["errors"]


def test_route_no_filter_matches_all():
    config = RouterConfig(routes=[Route(name="all")])
    results = route_records(_RECORDS, config)
    assert all(r.matched_routes == ["all"] for r in results)


def test_default_route_used_when_no_match():
    config = RouterConfig(
        routes=[Route(name="errors", query=_q(_f("level", "eq", "error")))],
        default_route="fallback",
    )
    results = route_records(_RECORDS, config)
    assert results[1].matched_routes == ["fallback"]


def test_drop_unmatched_leaves_empty_routes():
    config = RouterConfig(
        routes=[Route(name="errors", query=_q(_f("level", "eq", "error")))],
        drop_unmatched=True,
    )
    results = route_records(_RECORDS, config)
    assert results[1].matched_routes == []


def test_sink_is_called():
    collected: List[Dict[str, Any]] = []
    config = RouterConfig(
        routes=[Route(name="errors", query=_q(_f("level", "eq", "error")), sink=collected.append)]
    )
    route_records(_RECORDS, config)
    assert len(collected) == 2
    assert all(r["level"] == "error" for r in collected)


def test_multiple_routes_can_match_same_record():
    config = RouterConfig(
        routes=[
            Route(name="errors", query=_q(_f("level", "eq", "error"))),
            Route(name="worker", query=_q(_f("service", "eq", "worker"))),
        ]
    )
    results = route_records(_RECORDS, config)
    # third record: error + worker
    assert set(results[2].matched_routes) == {"errors", "worker"}


def test_empty_config_raises():
    with pytest.raises(RouterError):
        route_records(_RECORDS, RouterConfig())


def test_routing_result_as_dict():
    config = RouterConfig(routes=[Route(name="all")])
    result = route_records([_RECORDS[0]], config)[0]
    d = result.as_dict()
    assert d["matched_routes"] == ["all"]
    assert d["record"] == _RECORDS[0]
