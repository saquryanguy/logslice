"""Tests for logslice.ingestion.reader."""

from __future__ import annotations

import io
import json
import pytest

from logslice.ingestion.reader import LogReadError, read_stream, read_file


def _stream(*lines: str) -> io.StringIO:
    """Helper: build a StringIO from individual log lines."""
    return io.StringIO("\n".join(lines) + "\n")


def test_read_single_valid_record():
    record = {"level": "info", "msg": "hello"}
    stream = _stream(json.dumps(record))
    results = list(read_stream(stream))
    assert results == [record]


def test_read_multiple_records():
    records = [
        {"level": "info", "service": "api"},
        {"level": "error", "service": "db"},
    ]
    stream = _stream(*[json.dumps(r) for r in records])
    assert list(read_stream(stream)) == records


def test_empty_line_raises_by_default():
    stream = io.StringIO("\n")
    with pytest.raises(LogReadError, match="empty line"):
        list(read_stream(stream))


def test_empty_line_skipped_when_skip_invalid():
    valid = {"level": "warn"}
    stream = _stream("", json.dumps(valid))
    results = list(read_stream(stream, skip_invalid=True))
    assert results == [valid]


def test_invalid_json_raises_by_default():
    stream = _stream("not json at all")
    with pytest.raises(LogReadError, match="invalid JSON"):
        list(read_stream(stream))


def test_invalid_json_skipped_when_skip_invalid():
    valid = {"level": "debug"}
    stream = _stream("bad", json.dumps(valid))
    results = list(read_stream(stream, skip_invalid=True))
    assert results == [valid]


def test_non_object_json_raises():
    stream = _stream(json.dumps(["a", "b"]))
    with pytest.raises(LogReadError, match="expected a JSON object"):
        list(read_stream(stream))


def test_read_file(tmp_path):
    records = [{"level": "info", "n": i} for i in range(5)]
    log_file = tmp_path / "app.log"
    log_file.write_text("\n".join(json.dumps(r) for r in records) + "\n")
    assert list(read_file(str(log_file))) == records


def test_read_file_skip_invalid(tmp_path):
    valid = {"level": "info"}
    log_file = tmp_path / "mixed.log"
    log_file.write_text(f"corrupted\n{json.dumps(valid)}\n")
    results = list(read_file(str(log_file), skip_invalid=True))
    assert results == [valid]
