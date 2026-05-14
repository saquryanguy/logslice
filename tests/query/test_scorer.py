"""Tests for logslice.query.scorer."""

from __future__ import annotations

import pytest

from logslice.query.parser import ParsedQuery, QueryFilter
from logslice.query.scorer import (
    ScorerConfig,
    ScorerError,
    ScoreResult,
    score_record,
    score_records,
)


def _q(*filters: QueryFilter) -> ParsedQuery:
    return ParsedQuery(filters=list(filters))


def _f(field: str, op: str, value: object) -> QueryFilter:
    return QueryFilter(field=field, operator=op, value=value)


_RECORD = {"level": "error", "service": "api", "status": 500}


def test_score_no_filters_returns_base_score() -> None:
    result = score_record(_RECORD, _q())
    assert result.score == 0.0
    assert result.matched_fields == []


def test_score_single_matching_filter() -> None:
    result = score_record(_RECORD, _q(_f("level", "eq", "error")))
    assert result.score == 1.0
    assert result.matched_fields == ["level"]


def test_score_non_matching_filter_contributes_zero() -> None:
    result = score_record(_RECORD, _q(_f("level", "eq", "info")))
    assert result.score == 0.0
    assert result.matched_fields == []


def test_score_multiple_matching_filters_accumulate() -> None:
    q = _q(_f("level", "eq", "error"), _f("service", "eq", "api"))
    result = score_record(_RECORD, q)
    assert result.score == 2.0
    assert set(result.matched_fields) == {"level", "service"}


def test_score_base_score_added() -> None:
    cfg = ScorerConfig(base_score=5.0)
    result = score_record(_RECORD, _q(_f("level", "eq", "error")), cfg)
    assert result.score == 6.0


def test_score_custom_match_weight() -> None:
    cfg = ScorerConfig(match_weight=3.0)
    result = score_record(_RECORD, _q(_f("level", "eq", "error")), cfg)
    assert result.score == 3.0


def test_score_field_weight_overrides_match_weight() -> None:
    cfg = ScorerConfig(match_weight=1.0, field_weights={"level": 10.0})
    result = score_record(_RECORD, _q(_f("level", "eq", "error")), cfg)
    assert result.score == 10.0


def test_score_result_as_dict_keys() -> None:
    result = score_record(_RECORD, _q())
    d = result.as_dict()
    assert set(d.keys()) == {"record", "score", "matched_fields"}


def test_score_records_sorted_descending() -> None:
    records = [
        {"level": "info", "service": "web"},
        {"level": "error", "service": "api"},
    ]
    q = _q(_f("level", "eq", "error"), _f("service", "eq", "api"))
    results = score_records(records, q)
    assert results[0].score >= results[1].score


def test_score_records_unsorted() -> None:
    records = [
        {"level": "error"},
        {"level": "info"},
        {"level": "error"},
    ]
    q = _q(_f("level", "eq", "error"))
    results = score_records(records, q, sort_descending=False)
    scores = [r.score for r in results]
    assert scores == [1.0, 0.0, 1.0]


def test_scorer_config_negative_match_weight_raises() -> None:
    with pytest.raises(ScorerError, match="match_weight"):
        ScorerConfig(match_weight=-1.0)


def test_scorer_config_negative_field_weight_raises() -> None:
    with pytest.raises(ScorerError, match="level"):
        ScorerConfig(field_weights={"level": -2.0})
