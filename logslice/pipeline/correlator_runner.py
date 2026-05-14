"""Pipeline integration for log record correlation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from logslice.query.correlator import CorrelationResult, CorrelatorConfig, correlate


@dataclass
class CorrelatorRunnerConfig:
    """Configuration for the pipeline correlator runner."""

    correlator: CorrelatorConfig
    on_group: Optional[Callable[[str, List[Dict[str, Any]]], None]] = None


def run_correlator(
    records: List[Dict[str, Any]],
    config: CorrelatorRunnerConfig,
) -> CorrelationResult:
    """Run correlation over *records* and optionally invoke a callback per group.

    Parameters
    ----------
    records:
        Flat list of log record dicts.
    config:
        Runner configuration including the :class:`CorrelatorConfig` and an
        optional *on_group* callback that receives ``(key, records)`` for every
        correlated group found.

    Returns
    -------
    CorrelationResult
        The full correlation result.
    """
    result = correlate(records, config.correlator)

    if config.on_group is not None:
        for group in result.groups:
            config.on_group(group.key, group.records)

    return result
