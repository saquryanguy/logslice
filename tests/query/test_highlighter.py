"""Tests for logslice.query.highlighter."""

from __future__ import annotations

import pytest

from logslice.query.parser import ParsedQuery, QueryFilter
from logslice.query.highlighter import highlight_record, ANSI_YELLOW, ANSI_RESET


def _q(*filters: QueryFilter) -> ParsedQuery:
    return ParsedQuery(filters=list(filters), limit=None)


def _f(field: str, op: str, value) -> QueryFilter:
    return QueryFilter(field=field, operator=op, value=value)


# ---------------------------------------------------------------------------
# highlight disabled
# ---------------------------------------------------------------------------

def test_highlight_disabled_returns_original():
    record = {"level": "error", "message": "boom"}
    query = _q(_f("level", "=", "error"))
    result = highlight_record(record, query, enabled=False)
    assert result["level"] == "error"


def test_no_filters_returns_copy():
    record = {"level": "info"}
    query = _q()
    result = highlight_record(record, query)
    assert result == record
    assert result is not record


# ---------------------------------------------------------------------------
# equality operator
# ---------------------------------------------------------------------------

def test_equality_match_highlights_field():
    record = {"level": "error"}
    query = _q(_f("level", "=", "error"))
    result = highlight_record(record, query)
    assert ANSI_RESET in result["level"]
    assert "error" in result["level"]


def test_equality_no_match_leaves_field_unchanged():
    record = {"level": "info"}
    query = _q(_f("level", "=", "error"))
    result = highlight_record(record, query)
    assert result["level"] == "info"


# ---------------------------------------------------------------------------
# contains operator
# ---------------------------------------------------------------------------

def test_contains_highlights_substring():
    record = {"message": "connection refused by host"}
    query = _q(_f("message", "contains", "refused"))
    result = highlight_record(record, query)
    assert ANSI_YELLOW in result["message"]
    assert "refused" in result["message"]


def test_contains_no_match_unchanged():
    record = {"message": "all good"}
    query = _q(_f("message", "contains", "refused"))
    result = highlight_record(record, query)
    assert result["message"] == "all good"


# ---------------------------------------------------------------------------
# regex operator
# ---------------------------------------------------------------------------

def test_regex_highlights_match():
    record = {"message": "error code 42"}
    query = _q(_f("message", "~=", r"\d+"))
    result = highlight_record(record, query)
    assert ANSI_RESET in result["message"]


def test_invalid_regex_leaves_field_unchanged():
    record = {"message": "hello world"}
    query = _q(_f("message", "~=", "[invalid"))
    result = highlight_record(record, query)
    assert result["message"] == "hello world"


# ---------------------------------------------------------------------------
# nested fields skipped
# ---------------------------------------------------------------------------

def test_nested_field_skipped():
    record = {"meta.region": "us-east-1"}
    query = _q(_f("meta.region", "=", "us-east-1"))
    result = highlight_record(record, query)
    assert result["meta.region"] == "us-east-1"


# ---------------------------------------------------------------------------
# non-string field values
# ---------------------------------------------------------------------------

def test_numeric_field_not_highlighted():
    record = {"status": 200}
    query = _q(_f("status", "=", 200))
    result = highlight_record(record, query)
    assert result["status"] == 200
