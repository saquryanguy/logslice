"""Tests for logslice.output.exporter."""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from logslice.output.exporter import (
    ExportError,
    export_to_file,
    export_to_stream,
    export_to_stdout,
)


RECORDS = [
    {"level": "INFO", "service": "api", "message": "started", "ts": "2024-01-01T00:00:00Z"},
    {"level": "ERROR", "service": "db", "message": "timeout", "ts": "2024-01-01T00:00:01Z"},
    {"level": "DEBUG", "service": "api", "message": "query ok", "ts": "2024-01-01T00:00:02Z"},
]


def test_export_to_stream_returns_count():
    buf = io.StringIO()
    count = export_to_stream(RECORDS, buf, fmt="compact")
    assert count == len(RECORDS)


def test_export_to_stream_json_parseable():
    buf = io.StringIO()
    export_to_stream(RECORDS, buf, fmt="json")
    buf.seek(0)
    lines = [l for l in buf.read().splitlines() if l.strip()]
    assert len(lines) == len(RECORDS)
    for line in lines:
        obj = json.loads(line)
        assert "level" in obj


def test_export_to_stream_empty_records():
    buf = io.StringIO()
    count = export_to_stream([], buf, fmt="compact")
    assert count == 0
    assert buf.getvalue() == ""


def test_export_to_file_creates_file(tmp_path: Path):
    out = tmp_path / "out.log"
    count = export_to_file(RECORDS, out, fmt="json")
    assert count == len(RECORDS)
    assert out.exists()
    lines = [l for l in out.read_text().splitlines() if l.strip()]
    assert len(lines) == len(RECORDS)


def test_export_to_file_invalid_path_raises():
    with pytest.raises(ExportError):
        export_to_file(RECORDS, "/no/such/directory/out.log", fmt="json")


def test_export_to_stdout_returns_count(capsys):
    count = export_to_stdout(RECORDS, fmt="compact", color=False)
    captured = capsys.readouterr()
    assert count == len(RECORDS)
    assert captured.out.count("\n") == len(RECORDS)


def test_export_to_stream_pretty_format():
    buf = io.StringIO()
    export_to_stream(RECORDS[:1], buf, fmt="pretty")
    buf.seek(0)
    text = buf.read()
    assert "INFO" in text or "started" in text
