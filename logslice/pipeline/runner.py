"""Pipeline runner: read, filter, optionally highlight, and emit log records."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import IO, Any, Generator, Iterable

from logslice.ingestion.reader import read_stream
from logslice.query.evaluator import matches
from logslice.query.parser import ParsedQuery
from logslice.query.highlighter import highlight_record


@dataclass
class PipelineConfig:
    query: ParsedQuery | None = None
    max_records: int | None = None
    skip_invalid: bool = True
    highlight: bool = False
    extra_fields: dict[str, Any] = field(default_factory=dict)


class Pipeline:
    def __init__(self, stream: IO[str], config: PipelineConfig | None = None) -> None:
        self._stream = stream
        self._config = config or PipelineConfig()

    def _filtered_records(
        self,
    ) -> Generator[dict[str, Any], None, None]:
        cfg = self._config
        emitted = 0

        for record in read_stream(
            self._stream, skip_invalid=cfg.skip_invalid
        ):
            if cfg.query and not matches(record, cfg.query):
                continue

            if cfg.extra_fields:
                record = {**record, **cfg.extra_fields}

            if cfg.highlight and cfg.query:
                record = highlight_record(record, cfg.query, enabled=True)

            yield record
            emitted += 1

            if cfg.max_records is not None and emitted >= cfg.max_records:
                break

    def run_pipeline(self) -> list[dict[str, Any]]:
        return list(self._filtered_records())


def run_pipeline(
    stream: IO[str],
    config: PipelineConfig | None = None,
) -> list[dict[str, Any]]:
    """Convenience function: run the pipeline and return all matched records."""
    return Pipeline(stream, config).run_pipeline()
