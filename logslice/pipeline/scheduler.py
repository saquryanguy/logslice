"""Tail/watch mode scheduler: re-runs the pipeline at a fixed interval."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Iterator, Optional

from logslice.pipeline.runner import PipelineConfig, run_pipeline


@dataclass
class SchedulerConfig:
    """Configuration for the polling scheduler."""

    pipeline: PipelineConfig
    interval_seconds: float = 2.0
    max_iterations: Optional[int] = None  # None means run forever
    on_records: Callable[[list[dict]], None] = field(
        default_factory=lambda: lambda records: None
    )


class SchedulerError(RuntimeError):
    """Raised when the scheduler encounters an unrecoverable error."""


def _tick(
    config: SchedulerConfig,
    seen_ids: set[int],
) -> list[dict]:
    """Run one pipeline pass and return only records not yet seen."""
    records = run_pipeline(config.pipeline)
    new_records = [r for r in records if id(r) not in seen_ids]
    seen_ids.update(id(r) for r in new_records)
    return new_records


def iter_scheduler(config: SchedulerConfig) -> Iterator[list[dict]]:
    """Yield batches of new records on each tick.

    Stops automatically when *max_iterations* is reached.
    """
    if config.interval_seconds < 0:
        raise SchedulerError("interval_seconds must be non-negative")

    seen_ids: set[int] = set()
    iteration = 0

    while True:
        if config.max_iterations is not None and iteration >= config.max_iterations:
            break

        new_records = _tick(config, seen_ids)
        if new_records:
            config.on_records(new_records)
            yield new_records

        iteration += 1

        if config.max_iterations is None or iteration < config.max_iterations:
            time.sleep(config.interval_seconds)


def run_scheduler(config: SchedulerConfig) -> int:
    """Run the scheduler to completion and return the total records emitted."""
    total = 0
    for batch in iter_scheduler(config):
        total += len(batch)
    return total
