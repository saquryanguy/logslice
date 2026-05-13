"""Read and parse structured log lines from streams or files."""

from __future__ import annotations

import json
import sys
from typing import IO, Generator, Optional


class LogReadError(Exception):
    """Raised when a log line cannot be parsed."""


def _parse_line(line: str, line_number: int = 0) -> dict:
    """Parse a single JSON log line into a dict.

    Args:
        line: Raw log line string.
        line_number: Optional line number for error context.

    Returns:
        Parsed log record as a dict.

    Raises:
        LogReadError: If the line is not valid JSON or not a JSON object.
    """
    stripped = line.strip()
    if not stripped:
        raise LogReadError(f"Line {line_number}: empty line")
    try:
        record = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise LogReadError(
            f"Line {line_number}: invalid JSON — {exc.msg}"
        ) from exc
    if not isinstance(record, dict):
        raise LogReadError(
            f"Line {line_number}: expected a JSON object, got {type(record).__name__}"
        )
    return record


def read_stream(
    stream: IO[str],
    skip_invalid: bool = False,
) -> Generator[dict, None, None]:
    """Yield parsed log records from a text stream line by line.

    Args:
        stream: Any readable text stream (file, stdin, StringIO …).
        skip_invalid: When True, malformed lines are silently skipped.
                      When False (default), a LogReadError is raised.

    Yields:
        Parsed log record dicts.
    """
    for line_number, line in enumerate(stream, start=1):
        try:
            yield _parse_line(line, line_number)
        except LogReadError:
            if not skip_invalid:
                raise


def read_file(
    path: str,
    skip_invalid: bool = False,
) -> Generator[dict, None, None]:
    """Open a log file and yield parsed records.

    Args:
        path: Path to a newline-delimited JSON log file.
        skip_invalid: Passed through to :func:`read_stream`.

    Yields:
        Parsed log record dicts.
    """
    with open(path, "r", encoding="utf-8") as fh:
        yield from read_stream(fh, skip_invalid=skip_invalid)


def read_stdin(skip_invalid: bool = False) -> Generator[dict, None, None]:
    """Yield parsed log records from standard input.

    Convenience wrapper around :func:`read_stream` that reads from
    ``sys.stdin``.  Useful for pipeline usage::

        cat app.log | python -m logslice ...

    Args:
        skip_invalid: When True, malformed lines are silently skipped.
                      When False (default), a LogReadError is raised.

    Yields:
        Parsed log record dicts.
    """
    yield from read_stream(sys.stdin, skip_invalid=skip_invalid)
