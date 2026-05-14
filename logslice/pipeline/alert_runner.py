"""Pipeline integration: run alert evaluation as part of a log pipeline pass."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional

from logslice.query.alerter import AlertEvent, AlertResult, AlertRule, evaluate_alerts
from logslice.query.evaluator import matches


@dataclass
class AlertRunnerConfig:
    rules: List[AlertRule]
    passthrough: bool = True  # whether to also yield the original records
    on_alert: Optional[Callable[[AlertEvent], None]] = field(default=None, repr=False)


def run_alerts(
    records: Iterable[Dict[str, Any]],
    config: AlertRunnerConfig,
) -> AlertResult:
    """Consume *records*, evaluate all alert rules, and return an AlertResult.

    If *config.on_alert* is set it is called for every fired event in addition
    to any per-rule callbacks already attached to the rules.
    """
    collected: List[Dict[str, Any]] = list(records)

    # Wrap each rule's on_fire so the runner-level callback also fires.
    if config.on_alert is not None:
        wrapped_rules: List[AlertRule] = []
        for rule in config.rules:
            original_cb = rule.on_fire

            def _make_cb(
                ocb: Optional[Callable[[AlertEvent], None]],
                runner_cb: Callable[[AlertEvent], None],
            ) -> Callable[[AlertEvent], None]:
                def _cb(event: AlertEvent) -> None:
                    if ocb is not None:
                        ocb(event)
                    runner_cb(event)

                return _cb

            import dataclasses
            wrapped_rules.append(
                dataclasses.replace(rule, on_fire=_make_cb(original_cb, config.on_alert))
            )
    else:
        wrapped_rules = config.rules

    return evaluate_alerts(collected, wrapped_rules)
