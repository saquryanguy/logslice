"""Tests for logslice.query.tagger."""
from __future__ import annotations

from typing import Any, Dict, List

import pytest

from logslice.query.parser import ParsedQuery, QueryFilter
from logslice.query.tagger import (
    TaggerConfig,
    TaggerError,
    TagResult,
    TagRule,
    tag_records,
)


def _q(*filters: QueryFilter) -> ParsedQuery:
    return ParsedQuery(filters=list(filters))


def _f(field: str, op: str, value: Any) -> QueryFilter:
    return QueryFilter(field=field, operator=op, value=value)


def _records() -> List[Dict[str, Any]]:
    return [
        {"level": "error", "service": "api", "message": "boom"},
        {"level": "info", "service": "worker", "message": "ok"},
        {"level": "error", "service": "db", "message": "timeout"},
    ]


# --- TagRule validation ---

def test_rule_requires_query_or_predicate():
    with pytest.raises(TaggerError, match="requires either"):
        TagRule(tag="x")


def test_rule_rejects_both_query_and_predicate():
    with pytest.raises(TaggerError, match="not both"):
        TagRule(tag="x", query=_q(), predicate=lambda r: True)


def test_rule_rejects_empty_tag():
    with pytest.raises(TaggerError, match="non-empty"):
        TagRule(tag="  ", query=_q())


# --- tag_records ---

def test_empty_rules_returns_copies_unchanged():
    recs = _records()
    result = tag_records(recs, TaggerConfig(rules=[]))
    assert result.total == 3
    assert result.tagged == 0
    assert result.records == recs
    assert result.records is not recs


def test_tag_by_level_query():
    rule = TagRule(tag="critical", query=_q(_f("level", "eq", "error")))
    result = tag_records(_records(), TaggerConfig(rules=[rule]))
    assert result.tagged == 2
    tagged = [r for r in result.records if "critical" in r.get("_tags", [])]
    assert len(tagged) == 2


def test_tag_by_predicate():
    rule = TagRule(tag="api", predicate=lambda r: r.get("service") == "api")
    result = tag_records(_records(), TaggerConfig(rules=[rule]))
    assert result.tagged == 1
    assert result.records[0]["_tags"] == ["api"]


def test_multiple_tags_applied_to_same_record():
    rules = [
        TagRule(tag="error", query=_q(_f("level", "eq", "error"))),
        TagRule(tag="api", predicate=lambda r: r.get("service") == "api"),
    ]
    result = tag_records(_records(), TaggerConfig(rules=rules))
    first = result.records[0]
    assert "error" in first["_tags"]
    assert "api" in first["_tags"]


def test_custom_tag_field():
    rule = TagRule(tag="flagged", query=_q(_f("level", "eq", "error")))
    result = tag_records(_records(), TaggerConfig(rules=[rule], tag_field="labels"))
    assert all("labels" in r for r in result.records if r["level"] == "error")


def test_overwrite_replaces_existing_tags():
    recs = [{"level": "error", "_tags": ["old"]}]
    rule = TagRule(tag="new", query=_q(_f("level", "eq", "error")))
    result = tag_records(recs, TaggerConfig(rules=[rule], overwrite=True))
    assert result.records[0]["_tags"] == ["new"]


def test_no_duplicate_tags():
    rules = [
        TagRule(tag="dup", predicate=lambda r: True),
        TagRule(tag="dup", predicate=lambda r: True),
    ]
    result = tag_records([{"level": "info"}], TaggerConfig(rules=rules))
    assert result.records[0]["_tags"].count("dup") == 1


def test_as_dict_keys():
    result = TagResult(records=[], total=5, tagged=3)
    d = result.as_dict()
    assert d == {"total": 5, "tagged": 3}


def test_does_not_mutate_input():
    recs = [{"level": "error"}]
    rule = TagRule(tag="x", query=_q(_f("level", "eq", "error")))
    tag_records(recs, TaggerConfig(rules=[rule]))
    assert "_tags" not in recs[0]
