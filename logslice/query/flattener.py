"""Flatten nested log records into dot-notation key-value pairs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class FlattenerError(Exception):
    """Raised when flattening fails."""


@dataclass
class FlattenerConfig:
    separator: str = "."
    max_depth: int = 10
    skip_arrays: bool = False
    prefix: str = ""


@dataclass
class FlattenResult:
    original: dict[str, Any]
    flattened: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "original": self.original,
            "flattened": self.flattened,
        }


def _flatten(
    obj: Any,
    parent_key: str,
    sep: str,
    depth: int,
    max_depth: int,
    skip_arrays: bool,
    acc: dict[str, Any],
) -> None:
    if depth > max_depth:
        raise FlattenerError(
            f"Max nesting depth {max_depth} exceeded at key '{parent_key}'"
        )
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            _flatten(v, new_key, sep, depth + 1, max_depth, skip_arrays, acc)
    elif isinstance(obj, list):
        if skip_arrays:
            acc[parent_key] = obj
        else:
            for i, item in enumerate(obj):
                new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
                _flatten(item, new_key, sep, depth + 1, max_depth, skip_arrays, acc)
    else:
        acc[parent_key] = obj


def flatten_record(
    record: dict[str, Any],
    config: FlattenerConfig | None = None,
) -> FlattenResult:
    """Flatten a nested log record into dot-notation keys."""
    if config is None:
        config = FlattenerConfig()
    if not isinstance(record, dict):
        raise FlattenerError(f"Expected dict, got {type(record).__name__}")
    acc: dict[str, Any] = {}
    _flatten(
        record,
        config.prefix,
        config.separator,
        depth=0,
        max_depth=config.max_depth,
        skip_arrays=config.skip_arrays,
        acc=acc,
    )
    return FlattenResult(original=record, flattened=acc)


def flatten_records(
    records: list[dict[str, Any]],
    config: FlattenerConfig | None = None,
) -> list[FlattenResult]:
    """Flatten a list of log records."""
    return [flatten_record(r, config) for r in records]
