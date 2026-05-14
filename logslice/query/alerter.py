"""Alert rule evaluation: fire alerts when log records match defined conditions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from logslice.query.evaluator import matches
from logslice.query.parser import ParsedQuery


class AlertError(Exception):
    """Raised when alert configuration or evaluation fails."""


@dataclass
class AlertRule:
    name: str
    query: ParsedQuery
    message: str = "Alert triggered"
    severity: str = "warning"
    on_fire: Optional[Callable[["AlertEvent"], None]] = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise AlertError("AlertRule.name must be a non-empty string")
        if self.severity not in ("info", "warning", "error", "critical"):
            raise AlertError(
                f"Invalid severity {self.severity!r}; "
                "expected one of: info, warning, error, critical"
            )


@dataclass
class AlertEvent:
    rule_name: str
    severity: str
    message: str
    record: Dict[str, Any]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "rule_name": self.rule_name,
            "severity": self.severity,
            "message": self.message,
            "record": self.record,
        }


@dataclass
class AlertResult:
    total_evaluated: int
    events: List[AlertEvent]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "total_evaluated": self.total_evaluated,
            "events": [e.as_dict() for e in self.events],
        }


def evaluate_alerts(
    records: List[Dict[str, Any]],
    rules: List[AlertRule],
) -> AlertResult:
    """Evaluate *rules* against every record and collect fired AlertEvents."""
    if not rules:
        return AlertResult(total_evaluated=len(records), events=[])

    events: List[AlertEvent] = []
    for record in records:
        for rule in rules:
            if matches(record, rule.query):
                event = AlertEvent(
                    rule_name=rule.name,
                    severity=rule.severity,
                    message=rule.message,
                    record=record,
                )
                events.append(event)
                if rule.on_fire is not None:
                    rule.on_fire(event)

    return AlertResult(total_evaluated=len(records), events=events)
