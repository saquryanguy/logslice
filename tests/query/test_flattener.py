"""Tests for logslice.query.flattener."""
import pytest

from logslice.query.flattener import (
    FlattenerConfig,
    FlattenerError,
    flatten_record,
    flatten_records,
)


def test_flat_record_unchanged():
    record = {"level": "info", "message": "hello", "ts": 1}
    result = flatten_record(record)
    assert result.flattened == record


def test_nested_dict_flattened():
    record = {"level": "info", "context": {"user": "alice", "id": 42}}
    result = flatten_record(record)
    assert result.flattened["context.user"] == "alice"
    assert result.flattened["context.id"] == 42
    assert "context" not in result.flattened


def test_deeply_nested_flattened():
    record = {"a": {"b": {"c": "deep"}}}
    result = flatten_record(record)
    assert result.flattened["a.b.c"] == "deep"


def test_list_items_indexed():
    record = {"tags": ["x", "y", "z"]}
    result = flatten_record(record)
    assert result.flattened["tags.0"] == "x"
    assert result.flattened["tags.1"] == "y"
    assert result.flattened["tags.2"] == "z"


def test_skip_arrays_keeps_list_intact():
    record = {"tags": ["x", "y"]}
    config = FlattenerConfig(skip_arrays=True)
    result = flatten_record(record, config)
    assert result.flattened["tags"] == ["x", "y"]


def test_custom_separator():
    record = {"context": {"user": "bob"}}
    config = FlattenerConfig(separator="/")
    result = flatten_record(record, config)
    assert "context/user" in result.flattened


def test_prefix_prepended():
    record = {"level": "warn"}
    config = FlattenerConfig(prefix="log")
    result = flatten_record(record, config)
    assert "log.level" in result.flattened


def test_original_preserved():
    record = {"a": {"b": 1}}
    result = flatten_record(record)
    assert result.original is record


def test_original_not_mutated():
    record = {"a": {"b": 1}}
    flatten_record(record)
    assert record == {"a": {"b": 1}}


def test_non_dict_raises():
    with pytest.raises(FlattenerError, match="Expected dict"):
        flatten_record(["not", "a", "dict"])  # type: ignore[arg-type]


def test_max_depth_exceeded_raises():
    record = {"a": {"b": {"c": {"d": "deep"}}}}
    config = FlattenerConfig(max_depth=2)
    with pytest.raises(FlattenerError, match="Max nesting depth"):
        flatten_record(record, config)


def test_flatten_records_returns_all():
    records = [
        {"level": "info", "ctx": {"svc": "api"}},
        {"level": "error", "ctx": {"svc": "db"}},
    ]
    results = flatten_records(records)
    assert len(results) == 2
    assert results[0].flattened["ctx.svc"] == "api"
    assert results[1].flattened["ctx.svc"] == "db"


def test_as_dict_contains_keys():
    record = {"level": "debug"}
    result = flatten_record(record)
    d = result.as_dict()
    assert "original" in d
    assert "flattened" in d


def test_empty_record_returns_empty_flattened():
    result = flatten_record({})
    assert result.flattened == {}
