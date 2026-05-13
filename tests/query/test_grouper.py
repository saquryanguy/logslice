"""Tests for logslice.query.grouper."""

from __future__ import annotations

from typing import Any, Dict, List

import pytest

from logslice.query.grouper import (
    GrouperConfig,
    GrouperError,
    GroupResult,
    group_records,
)


def _records() -> List[Dict[str, Any]]:
    return [
        {"level": "info", "service": "api", "message": "started"},
        {"level": "info", "service": "worker", "message": "task done"},
        {"level": "error", "service": "api", "message": "boom"},
        {"level": "error", "service": "api", "message": "crash"},
        {"level": "warn", "service": "worker", "message": "slow"},
    ]


def test_group_by_level_creates_correct_buckets():
    result = group_records(_records(), GrouperConfig(keys=["level"]))
    assert set(result.groups.keys()) == {("info",), ("error",), ("warn",)}


def test_group_total_equals_input_length():
    result = group_records(_records(), GrouperConfig(keys=["level"]))
    assert result.total == len(_records())


def test_group_count_matches_unique_values():
    result = group_records(_records(), GrouperConfig(keys=["level"]))
    assert result.group_count == 3


def test_group_by_service():
    result = group_records(_records(), GrouperConfig(keys=["service"]))
    assert len(result.groups[("api",)]) == 3
    assert len(result.groups[("worker",)]) == 2


def test_group_by_multiple_keys():
    result = group_records(_records(), GrouperConfig(keys=["level", "service"]))
    assert ("error", "api") in result.groups
    assert len(result.groups[("error", "api")]) == 2


def test_missing_field_uses_missing_value():
    records = [{"level": "info"}, {"level": "info", "service": "api"}]
    result = group_records(records, GrouperConfig(keys=["service"], missing_value="n/a"))
    assert ("n/a",) in result.groups
    assert ("api",) in result.groups


def test_max_groups_truncates():
    result = group_records(_records(), GrouperConfig(keys=["level"], max_groups=2))
    assert result.group_count == 2
    assert result.truncated is True
    assert result.total < len(_records())


def test_no_truncation_when_under_max_groups():
    result = group_records(_records(), GrouperConfig(keys=["level"], max_groups=10))
    assert result.truncated is False


def test_empty_keys_raises():
    with pytest.raises(GrouperError, match="at least one field"):
        group_records(_records(), GrouperConfig(keys=[]))


def test_empty_records_returns_empty_result():
    result = group_records([], GrouperConfig(keys=["level"]))
    assert result.total == 0
    assert result.group_count == 0
    assert result.groups == {}


def test_as_dict_serializes_tuple_keys():
    result = group_records(_records(), GrouperConfig(keys=["level", "service"]))
    d = result.as_dict()
    assert isinstance(d, dict)
    assert "error|api" in d["groups"]
    assert d["group_count"] == result.group_count
    assert d["truncated"] is False


def test_nested_field_grouping():
    records = [
        {"meta": {"env": "prod"}, "message": "ok"},
        {"meta": {"env": "staging"}, "message": "ok"},
        {"meta": {"env": "prod"}, "message": "fail"},
    ]
    result = group_records(records, GrouperConfig(keys=["meta.env"]))
    assert len(result.groups[("prod",)]) == 2
    assert len(result.groups[("staging",)]) == 1
