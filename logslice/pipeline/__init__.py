"""Pipeline package: runner, scheduler, and file watcher."""

from logslice.pipeline.runner import PipelineConfig, run_pipeline
from logslice.pipeline.scheduler import SchedulerConfig, SchedulerError, run_scheduler
from logslice.pipeline.watcher import WatcherConfig, WatcherError, iter_lines

__all__ = [
    "PipelineConfig",
    "run_pipeline",
    "SchedulerConfig",
    "SchedulerError",
    "run_scheduler",
    "WatcherConfig",
    "WatcherError",
    "iter_lines",
]
