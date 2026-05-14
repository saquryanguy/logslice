"""Relevance scoring for log records based on query filter matches."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from logslice.query.parser import ParsedQuery
from logslice.query.evaluator import _filter_matches


class ScorerError(Exception):
    """Raised when scoring configuration is invalid."""


@dataclass
class ScorerConfig:
    """Configuration for the relevance scorer."""

    base_score: float = 0.0
    match_weight: float = 1.0
    field_weights: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.match_weight < 0:
            raise ScorerError("match_weight must be non-negative")
        for fname, w in self.field_weights.items():
            if w < 0:
                raise ScorerError(
                    f"field weight for '{fname}' must be non-negative"
                )


@dataclass
class ScoreResult:
    """Result of scoring a single record."""

    record: dict[str, Any]
    score: float
    matched_fields: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "record": self.record,
            "score": self.score,
            "matched_fields": self.matched_fields,
        }


def score_record(
    record: dict[str, Any],
    query: ParsedQuery,
    config: ScorerConfig | None = None,
) -> ScoreResult:
    """Score a single record against all filters in *query*.

    Each matching filter contributes *match_weight* to the total score,
    optionally multiplied by a per-field weight from *config.field_weights*.
    """
    if config is None:
        config = ScorerConfig()

    total = config.base_score
    matched: list[str] = []

    for f in query.filters:
        if _filter_matches(record, f):
            weight = config.field_weights.get(f.field, config.match_weight)
            total += weight
            matched.append(f.field)

    return ScoreResult(record=record, score=total, matched_fields=matched)


def score_records(
    records: list[dict[str, Any]],
    query: ParsedQuery,
    config: ScorerConfig | None = None,
    *,
    sort_descending: bool = True,
) -> list[ScoreResult]:
    """Score and optionally sort *records* by relevance."""
    results = [score_record(r, query, config) for r in records]
    if sort_descending:
        results.sort(key=lambda r: r.score, reverse=True)
    return results
