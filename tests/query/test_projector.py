"""Tests for logslice.query.projector."""

import pytest

from logslice.query.projector import (
    ProjectionError,
    ProjectorConfig,
    project,
)


def _records():
    return [
        {"level": "info", "service": "api", "message": "started", "meta": {"host": "h1", "pid": 1}},
        {"level": "error", "service": "db", "message": "failed", "meta": {"host": "h2", "pid": 2}},
        {"level": "warn", "service": "api", "message": "slow", "meta": {"host": "h3", "pid": 3}},
    ]


def test_no_config_returns_copies_of_all_records():
    records = _records()
    result = project(records)
    assert result.total == 3
    assert result.records == records
    assert result.records is not records


def test_include_top_level_fields():
    result = project(_records(), ProjectorConfig(include=["level", "message"]))
    for rec in result.records:
        assert set(rec.keys()) == {"level", "message"}


def test_include_nested_field():
    result = project(_records(), ProjectorConfig(include=["meta.host"]))
    assert result.records[0] == {"meta": {"host": "h1"}}
    assert "pid" not in result.records[0].get("meta", {})


def test_include_missing_field_omits_key():
    result = project(_records(), ProjectorConfig(include=["nonexistent"]))
    for rec in result.records:
        assert rec == {}


def test_exclude_top_level_field():
    result = project(_records(), ProjectorConfig(exclude=["service"]))
    for rec in result.records:
        assert "service" not in rec
        assert "level" in rec


def test_exclude_nested_field():
    result = project(_records(), ProjectorConfig(exclude=["meta.pid"]))
    for rec in result.records:
        assert "pid" not in rec.get("meta", {})
        assert "host" in rec.get("meta", {})


def test_exclude_missing_field_does_not_raise():
    result = project(_records(), ProjectorConfig(exclude=["does_not_exist"]))
    assert result.total == 3


def test_fields_applied_reflects_include():
    config = ProjectorConfig(include=["level", "service"])
    result = project(_records(), config)
    assert set(result.fields_applied) == {"level", "service"}


def test_fields_applied_reflects_exclude():
    config = ProjectorConfig(exclude=["meta"])
    result = project(_records(), config)
    assert result.fields_applied == ["meta"]


def test_fields_applied_empty_when_no_config():
    result = project(_records())
    assert result.fields_applied == []


def test_include_and_exclude_raises():
    with pytest.raises(ProjectionError, match="mutually exclusive"):
        ProjectorConfig(include=["level"], exclude=["service"])


def test_empty_records_returns_empty_result():
    result = project([], ProjectorConfig(include=["level"]))
    assert result.total == 0
    assert result.records == []


def test_as_dict_structure():
    result = project(_records(), ProjectorConfig(include=["level"]))
    d = result.as_dict()
    assert "total" in d
    assert "fields_applied" in d
    assert "records" in d
    assert d["total"] == 3


def test_original_records_not_mutated():
    records = _records()
    original_keys = [set(r.keys()) for r in records]
    project(records, ProjectorConfig(exclude=["level", "meta.pid"]))
    for i, rec in enumerate(records):
        assert set(rec.keys()) == original_keys[i]
