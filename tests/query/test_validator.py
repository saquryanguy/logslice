"""Tests for logslice.query.validator."""

import pytest

from logslice.query.parser import ParsedQuery, QueryFilter
from logslice.query.validator import (
    MAX_FIELD_LENGTH,
    MAX_FILTERS,
    MAX_VALUE_LENGTH,
    ValidationError,
    validate_query,
)


def _make_query(*filters, limit=None):
    return ParsedQuery(filters=list(filters), limit=limit)


def _f(field="level", operator="eq", value="info"):
    return QueryFilter(field=field, operator=operator, value=value)


def test_valid_empty_query_passes():
    validate_query(_make_query())


def test_valid_single_filter_passes():
    validate_query(_make_query(_f()))


def test_valid_limit_passes():
    validate_query(_make_query(_f(), limit=100))


def test_invalid_limit_zero_raises():
    with pytest.raises(ValidationError, match="limit must be a positive integer"):
        validate_query(_make_query(limit=0))


def test_invalid_limit_negative_raises():
    with pytest.raises(ValidationError, match="limit must be a positive integer"):
        validate_query(_make_query(limit=-5))


def test_too_many_filters_raises():
    filters = [_f(field=f"field_{i}") for i in range(MAX_FILTERS + 1)]
    with pytest.raises(ValidationError, match="maximum allowed"):
        validate_query(_make_query(*filters))


def test_unknown_operator_raises():
    with pytest.raises(ValidationError, match="Unknown operator"):
        validate_query(_make_query(_f(operator="between")))


def test_field_too_long_raises():
    long_field = "x" * (MAX_FIELD_LENGTH + 1)
    with pytest.raises(ValidationError, match="exceeds max length"):
        validate_query(_make_query(_f(field=long_field)))


def test_value_too_long_raises():
    long_value = "v" * (MAX_VALUE_LENGTH + 1)
    with pytest.raises(ValidationError, match="exceeds max length"):
        validate_query(_make_query(_f(value=long_value)))


def test_invalid_regex_raises():
    with pytest.raises(ValidationError, match="Invalid regex pattern"):
        validate_query(_make_query(_f(operator="regex", value="[unclosed")))


def test_valid_regex_passes():
    validate_query(_make_query(_f(operator="regex", value="^error.*$")))


def test_multiple_errors_reported_together():
    bad_filters = [
        _f(operator="unknown_op"),
        _f(operator="regex", value="[bad"),
    ]
    with pytest.raises(ValidationError) as exc_info:
        validate_query(_make_query(*bad_filters))
    msg = str(exc_info.value)
    assert "Unknown operator" in msg
    assert "Invalid regex" in msg
