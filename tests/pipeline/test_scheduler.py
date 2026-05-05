"""Tests for logslice.pipeline.scheduler."""

from __future__ import annotations

import io
import json
from unittest.mock import patch

import pytest

from logslice.pipeline.runner import PipelineConfig
from logslice.pipeline.scheduler import (
    SchedulerConfig,
    SchedulerError,
    iter_scheduler,
    run_scheduler,
)


def _make_stream(*records: dict) -> io.TextIOWrapper:
    lines = [json.dumps(r) for r in records]
    return io.StringIO("\n".join(lines))


_RECORDS = [
    {"level": "INFO", "service": "api", "message": "started"},
    {"level": "ERROR", "service": "db", "message": "timeout"},
    {"level": "DEBUG", "service": "api", "message": "query"},
]


def _pipeline(query: str = "") -> PipelineConfig:
    return PipelineConfig(stream=_make_stream(*_RECORDS), query=query)


# ---------------------------------------------------------------------------
# iter_scheduler
# ---------------------------------------------------------------------------

def test_iter_scheduler_single_iteration():
    cfg = SchedulerConfig(pipeline=_pipeline(), max_iterations=1, interval_seconds=0)
    batches = list(iter_scheduler(cfg))
    assert len(batches) == 1
    assert len(batches[0]) == 3


def test_iter_scheduler_zero_iterations():
    cfg = SchedulerConfig(pipeline=_pipeline(), max_iterations=0, interval_seconds=0)
    batches = list(iter_scheduler(cfg))
    assert batches == []


def test_iter_scheduler_calls_on_records():
    collected: list[dict] = []
    cfg = SchedulerConfig(
        pipeline=_pipeline(),
        max_iterations=1,
        interval_seconds=0,
        on_records=lambda recs: collected.extend(recs),
    )
    list(iter_scheduler(cfg))
    assert len(collected) == 3


def test_iter_scheduler_negative_interval_raises():
    cfg = SchedulerConfig(pipeline=_pipeline(), max_iterations=1, interval_seconds=-1)
    with pytest.raises(SchedulerError):
        list(iter_scheduler(cfg))


def test_iter_scheduler_sleeps_between_ticks():
    cfg = SchedulerConfig(pipeline=_pipeline(), max_iterations=2, interval_seconds=0.5)
    with patch("logslice.pipeline.scheduler.time.sleep") as mock_sleep:
        # Provide fresh stream for second tick
        call_count = 0

        def fresh_pipeline():
            nonlocal call_count
            call_count += 1
            return PipelineConfig(stream=_make_stream(*_RECORDS), query="")

        cfg.pipeline = fresh_pipeline()
        list(iter_scheduler(cfg))
        mock_sleep.assert_called_once_with(0.5)


# ---------------------------------------------------------------------------
# run_scheduler
# ---------------------------------------------------------------------------

def test_run_scheduler_returns_total_count():
    cfg = SchedulerConfig(pipeline=_pipeline(), max_iterations=1, interval_seconds=0)
    total = run_scheduler(cfg)
    assert total == 3


def test_run_scheduler_with_filter():
    cfg = SchedulerConfig(
        pipeline=_pipeline(query="level=ERROR"),
        max_iterations=1,
        interval_seconds=0,
    )
    total = run_scheduler(cfg)
    assert total == 1
