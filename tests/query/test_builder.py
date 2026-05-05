"""Tests for the fluent QueryBuilder."""

import pytest

from logslice.query.builder import QueryBuilder
from logslice.query.parser import ParsedQuery, QueryFilter


def test_build_empty_query():
    q = QueryBuilder().build()
    assert isinstance(q, ParsedQuery)
    assert q.filters == []
    assert q.limit is None


def test_build_level_filter():
    q = QueryBuilder().level("error").build()
    assert len(q.filters) == 1
    assert q.filters[0] == QueryFilter(field="level", operator="eq", value="error")


def test_build_service_filter():
    q = QueryBuilder().service("auth").build()
    assert q.filters[0].field == "service"
    assert q.filters[0].value == "auth"


def test_build_message_contains():
    q = QueryBuilder().message_contains("timeout").build()
    assert q.filters[0].operator == "regex"
    assert q.filters[0].value == "timeout"


def test_build_chained_filters():
    q = QueryBuilder().level("warn").service("payments").build()
    assert len(q.filters) == 2


def test_build_with_limit():
    q = QueryBuilder().level("info").limit(50).build()
    assert q.limit == 50


def test_limit_zero_raises():
    with pytest.raises(ValueError, match="limit must be"):
        QueryBuilder().limit(0)


def test_where_custom_operator():
    q = QueryBuilder().where("latency", "gte", 200).build()
    assert q.filters[0] == QueryFilter(field="latency", operator="gte", value=200)


def test_from_parsed_roundtrip():
    original = QueryBuilder().level("error").service("api").limit(10).build()
    rebuilt = QueryBuilder.from_parsed(original).build()
    assert rebuilt.filters == original.filters
    assert rebuilt.limit == original.limit


def test_from_parsed_does_not_mutate_original():
    original = QueryBuilder().level("info").build()
    builder = QueryBuilder.from_parsed(original)
    builder.service("db")
    rebuilt = builder.build()
    assert len(original.filters) == 1
    assert len(rebuilt.filters) == 2
