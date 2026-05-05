"""Export filtered log records to various output targets."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Iterable, Literal, TextIO

from logslice.output.formatter import format_record

OutputFormat = Literal["json", "compact", "pretty"]


class ExportError(Exception):
    """Raised when an export operation fails."""


def export_to_stream(
    records: Iterable[dict],
    stream: TextIO,
    fmt: OutputFormat = "compact",
    color: bool = False,
) -> int:
    """Write records to *stream* and return the number of records written."""
    count = 0
    for record in records:
        line = format_record(record, fmt=fmt, color=color)
        stream.write(line + "\n")
        count += 1
    return count


def export_to_file(
    records: Iterable[dict],
    path: str | Path,
    fmt: OutputFormat = "json",
    color: bool = False,
) -> int:
    """Write records to a file at *path* and return the number of records written."""
    path = Path(path)
    try:
        with path.open("w", encoding="utf-8") as fh:
            return export_to_stream(records, fh, fmt=fmt, color=color)
    except OSError as exc:
        raise ExportError(f"Cannot write to {path}: {exc}") from exc


def export_to_stdout(
    records: Iterable[dict],
    fmt: OutputFormat = "compact",
    color: bool = True,
) -> int:
    """Convenience wrapper that writes records to stdout."""
    return export_to_stream(records, sys.stdout, fmt=fmt, color=color)
