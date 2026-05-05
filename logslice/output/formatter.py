"""Output formatters for log records."""

from __future__ import annotations

import json
from typing import Any, Dict, Literal

OutputFormat = Literal["json", "pretty", "compact"]

_LEVEL_COLORS = {
    "debug": "\033[36m",    # cyan
    "info": "\033[32m",     # green
    "warning": "\033[33m",  # yellow
    "warn": "\033[33m",
    "error": "\033[31m",    # red
    "critical": "\033[35m", # magenta
}
_RESET = "\033[0m"
_BOLD = "\033[1m"


def _colorize_level(level: str) -> str:
    color = _LEVEL_COLORS.get(level.lower(), "")
    return f"{color}{_BOLD}{level.upper()}{_RESET}" if color else level.upper()


def format_record(
    record: Dict[str, Any],
    fmt: OutputFormat = "pretty",
    color: bool = True,
) -> str:
    """Format a log record as a string.

    Args:
        record: Parsed log record dictionary.
        fmt: Output format — 'json', 'pretty', or 'compact'.
        color: Whether to apply ANSI color codes (pretty format only).

    Returns:
        Formatted string representation of the record.
    """
    if fmt == "json":
        return json.dumps(record, default=str)

    if fmt == "compact":
        timestamp = record.get("timestamp", record.get("ts", ""))
        level = record.get("level", record.get("severity", "?")).upper()
        service = record.get("service", record.get("app", ""))
        message = record.get("message", record.get("msg", ""))
        parts = [str(timestamp), level]
        if service:
            parts.append(f"[{service}]")
        parts.append(message)
        return " ".join(parts)

    # pretty format
    timestamp = record.get("timestamp", record.get("ts", ""))
    level_raw = record.get("level", record.get("severity", "?"))
    service = record.get("service", record.get("app", ""))
    message = record.get("message", record.get("msg", ""))

    level_str = _colorize_level(level_raw) if color else level_raw.upper()
    service_str = f" {_BOLD}[{service}]{_RESET}" if service else ""

    extras = {
        k: v for k, v in record.items()
        if k not in {"timestamp", "ts", "level", "severity", "service", "app", "message", "msg"}
    }
    extra_str = ""
    if extras:
        extra_parts = [f"{k}={json.dumps(v, default=str)}" for k, v in extras.items()]
        extra_str = "  " + "  ".join(extra_parts)

    return f"{timestamp} {level_str}{service_str}  {message}{extra_str}"
