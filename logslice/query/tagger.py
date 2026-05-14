"""Tag log records with user-defined labels based on matching rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from logslice.query.evaluator import matches
from logslice.query.parser import ParsedQuery


class TaggerError(Exception):
    """Raised when tagging configuration or execution fails."""


@dataclass
class TagRule:
    """A single rule that applies a tag when a query matches a record."""

    tag: str
    query: Optional[ParsedQuery] = None
    predicate: Optional[Callable[[Dict[str, Any]], bool]] = None

    def __post_init__(self) -> None:
        if self.query is None and self.predicate is None:
            raise TaggerError("TagRule requires either 'query' or 'predicate'")
        if self.query is not None and self.predicate is not None:
            raise TaggerError("TagRule accepts 'query' or 'predicate', not both")
        if not self.tag or not self.tag.strip():
            raise TaggerError("TagRule 'tag' must be a non-empty string")


@dataclass
class TaggerConfig:
    """Configuration for the tagger."""

    rules: List[TagRule] = field(default_factory=list)
    tag_field: str = "_tags"
    overwrite: bool = False


@dataclass
class TagResult:
    """Result of a tagging operation."""

    records: List[Dict[str, Any]]
    total: int
    tagged: int

    def as_dict(self) -> Dict[str, Any]:
        return {"total": self.total, "tagged": self.tagged}


def _record_matches_rule(record: Dict[str, Any], rule: TagRule) -> bool:
    if rule.predicate is not None:
        return bool(rule.predicate(record))
    return matches(record, rule.query)  # type: ignore[arg-type]


def tag_records(
    records: List[Dict[str, Any]],
    config: TaggerConfig,
) -> TagResult:
    """Apply tag rules to each record, annotating matches with tags."""
    if not config.rules:
        return TagResult(records=[dict(r) for r in records], total=len(records), tagged=0)

    output: List[Dict[str, Any]] = []
    tagged_count = 0

    for record in records:
        copy = dict(record)
        applied: List[str] = []

        for rule in config.rules:
            if _record_matches_rule(record, rule):
                applied.append(rule.tag)

        if applied:
            existing = copy.get(config.tag_field, []) if not config.overwrite else []
            if not isinstance(existing, list):
                existing = [existing]
            merged = list(dict.fromkeys(existing + applied))
            copy[config.tag_field] = merged
            tagged_count += 1

        output.append(copy)

    return TagResult(records=output, total=len(records), tagged=tagged_count)
