"""Tests for the query parser."""

import pytest
from logslice.query.parser import parse_query


def test_parse_empty_query():
    q = parse_query("")
    assert q.filters == []
    assert q.level is None
    assert q.service is None
    assert q.limit == 100


def test_parse_level_filter():
    q = parse_query('level == ERROR')
    assert q.level == "ERROR"
    assert q.filters == []


def test_parse_service_filter():
    q = parse_query('service == auth')
    assert q.service == "auth"


def test_parse_custom_field_equality():
    q = parse_query('status_code == 404')
    assert len(q.filters) == 1
    assert q.filters[0].field == "status_code"
    assert q.filters[0].operator == "=="
    assert q.filters[0].value == 404


def test_parse_regex_operator():
    q = parse_query('message ~= "timeout"')
    assert q.filters[0].operator == "~="
    assert q.filters[0].value == "timeout"


def test_parse_limit():
    q = parse_query('level == INFO limit 50')
    assert q.limit == 50
    assert q.level == "INFO"


def test_parse_combined_query():
    q = parse_query('service == payments level == ERROR status_code >= 500 limit 25')
    assert q.service == "payments"
    assert q.level == "ERROR"
    assert q.limit == 25
    assert any(f.field == "status_code" and f.operator == ">=" and f.value == 500 for f in q.filters)


def test_parse_nested_field():
    q = parse_query('http.status == 200')
    assert q.filters[0].field == "http.status"
    assert q.filters[0].value == 200
