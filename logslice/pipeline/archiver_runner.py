"""Pipeline integration for the archiver: run archival over a live record stream."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable, Optional

from logslice.query.archiver import ArchiveConfig, ArchiveResult, archive


@dataclass
class ArchiverRunnerConfig:
    archive_config: ArchiveConfig = field(default_factory=ArchiveConfig)
    on_result: Optional[Callable[[ArchiveResult], None]] = None


def run_archiver(
    records: Iterable[dict],
    config: Optional[ArchiverRunnerConfig] = None,
) -> ArchiveResult:
    """Archive *records* and optionally invoke a callback with the result.

    Parameters
    ----------
    records:
        Iterable of parsed log record dicts.
    config:
        Runner configuration including the :class:`ArchiveConfig` and an
        optional ``on_result`` callback.

    Returns
    -------
    ArchiveResult
        The fully populated archive result.
    """
    if config is None:
        config = ArchiverRunnerConfig()

    result = archive(records, config=config.archive_config)

    if config.on_result is not None:
        config.on_result(result)

    return result
