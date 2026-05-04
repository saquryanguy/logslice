"""Tests for the query evaluator."""

import pytest
from logslice.query.parser import parse_query
from logslice.query.evaluator import matches


SAMPLE_RECORD = {
    "level": "ERROR",
    "service": "auth",
    "message": "connection timeout occurred",
    "status_code": 503,
    "http": {"method": "POST", "status": 503},
    "retries": 3,
}


def test_matches_by_level():
    q = parse_query("level == ERROR")
    assert matches(SAMPLE_RECORD, q) is True


def test_no_match_wrong_level():
    q = parse_query("level == INFO")
    assert matches(SAMPLE_RECORD, q) is False


def test_matches_by_service():
    q = parse_query("service == auth")
    assert matches(SAMPLE_RECORD, q) is True


def test_no_match_wrong_service():
    q = parse_query("service == payments")
    assert matches(SAMPLE_RECORD, q) is False


def test_matches_numeric_gte():
    q = parse_query("status_code >= 500")
    assert matches(SAMPLE_RECORD, q) is True


def test_no_match_numeric_lt():
    q = parse_query("status_code < 500")
    assert matches(SAMPLE_RECORD, q) is False


def test_matches_regex():
    q = parse_query('message ~= "timeout"')
    assert matches(SAMPLE_RECORD, q) is True


def test_no_match_regex():
    q = parse_query('message ~= "^auth"')
    assert matches(SAMPLE_RECORD, q) is False


def test_matches_nested_field():
    q = parse_query("http.status == 503")
    assert matches(SAMPLE_RECORD, q) is True


def test_combined_query_match():
    q = parse_query("level == ERROR service == auth status_code >= 500")
    assert matches(SAMPLE_RECORD, q) is True


def test_combined_query_no_match():
    q = parse_query("level == ERROR service == payments")
    assert matches(SAMPLE_RECORD, q) is False


def test_missing_field_returns_false():
    q = parse_query("nonexistent == value")
    assert matches(SAMPLE_RECORD, q) is False
