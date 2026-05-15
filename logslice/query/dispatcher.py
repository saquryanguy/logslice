"""Dispatch log records to multiple named handlers based on routing rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from logslice.query.evaluator import matches
from logslice.query.parser import ParsedQuery


class DispatchError(Exception):
    """Raised when dispatcher configuration or dispatch fails."""


@dataclass
class DispatchRule:
    name: str
    query: Optional[ParsedQuery] = None
    predicate: Optional[Callable[[dict], bool]] = None
    stop_on_match: bool = False

    def __post_init__(self) -> None:
        if self.query is None and self.predicate is None:
            raise DispatchError(f"Rule '{self.name}' requires a query or predicate.")
        if self.query is not None and self.predicate is not None:
            raise DispatchError(f"Rule '{self.name}' cannot have both query and predicate.")
        if not self.name.strip():
            raise DispatchError("Rule name must not be empty.")

    def _matches(self, record: dict) -> bool:
        if self.predicate is not None:
            return self.predicate(record)
        return matches(record, self.query)  # type: ignore[arg-type]


@dataclass
class DispatchConfig:
    rules: List[DispatchRule] = field(default_factory=list)
    default_handler: Optional[str] = None


@dataclass
class DispatchResult:
    total: int
    dispatched: Dict[str, List[dict]] = field(default_factory=dict)
    unmatched: List[dict] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "total": self.total,
            "dispatched": {k: len(v) for k, v in self.dispatched.items()},
            "unmatched": len(self.unmatched),
        }


def dispatch(
    records: List[dict],
    config: DispatchConfig,
) -> DispatchResult:
    """Dispatch each record to one or more named buckets based on rules."""
    if not config.rules and config.default_handler is None:
        raise DispatchError("DispatchConfig must have at least one rule or a default_handler.")

    dispatched: Dict[str, List[dict]] = {}
    unmatched: List[dict] = []

    for record in records:
        matched_any = False
        for rule in config.rules:
            if rule._matches(record):
                dispatched.setdefault(rule.name, []).append(record)
                matched_any = True
                if rule.stop_on_match:
                    break

        if not matched_any:
            if config.default_handler is not None:
                dispatched.setdefault(config.default_handler, []).append(record)
            else:
                unmatched.append(record)

    return DispatchResult(
        total=len(records),
        dispatched=dispatched,
        unmatched=unmatched,
    )
