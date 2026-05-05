"""Tests for query composer utilities."""

from logslice.query.builder import QueryBuilder
from logslice.query.composer import merge_queries, negate_query
from logslice.query.parser import QueryFilter


def _q(*pairs, limit=None):
    """Helper: build a ParsedQuery from (field, op, value) triples."""
    b = QueryBuilder()
    for field, op, value in pairs:
        b.where(field, op, value)
    if limit:
        b.limit(limit)
    return b.build()


def test_merge_empty_queries():
    result = merge_queries(_q(), _q())
    assert result.filters == []
    assert result.limit is None


def test_merge_combines_filters():
    q1 = _q(("level", "eq", "error"))
    q2 = _q(("service", "eq", "api"))
    result = merge_queries(q1, q2)
    assert len(result.filters) == 2


def test_merge_explicit_limit_wins():
    q1 = _q(limit=100)
    q2 = _q(limit=50)
    result = merge_queries(q1, q2, limit=200)
    assert result.limit == 200


def test_merge_smallest_limit_wins_when_no_override():
    q1 = _q(limit=100)
    q2 = _q(limit=25)
    result = merge_queries(q1, q2)
    assert result.limit == 25


def test_merge_preserves_single_limit():
    q1 = _q(limit=10)
    q2 = _q()
    result = merge_queries(q1, q2)
    assert result.limit == 10


def test_negate_eq_becomes_neq():
    q = _q(("level", "eq", "debug"))
    neg = negate_query(q)
    assert neg.filters[0].operator == "neq"


def test_negate_gte_becomes_lt():
    q = _q(("latency", "gte", 100))
    neg = negate_query(q)
    assert neg.filters[0].operator == "lt"


def test_negate_regex_becomes_not_regex():
    q = _q(("message", "regex", "error"))
    neg = negate_query(q)
    assert neg.filters[0].operator == "not_regex"


def test_negate_unknown_operator_unchanged():
    q = _q(("field", "custom_op", "val"))
    neg = negate_query(q)
    assert neg.filters[0].operator == "custom_op"


def test_negate_preserves_limit():
    q = _q(("level", "eq", "info"), limit=5)
    neg = negate_query(q)
    assert neg.limit == 5
