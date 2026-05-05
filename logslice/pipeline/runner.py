"""Pipeline runner: wires ingestion, filtering, and output together."""

from __future__ import annotations

import sys
from typing import IO, Iterator, Optional

from logslice.ingestion.reader import LogReadError, read_stream
from logslice.output.formatter import format_record
from logslice.query.evaluator import matches
from logslice.query.parser import ParsedQuery, parse_query


class PipelineConfig:
    """Configuration for a single pipeline run."""

    def __init__(
        self,
        query: str = "",
        output_format: str = "pretty",
        skip_invalid: bool = True,
        color: bool = True,
        max_records: Optional[int] = None,
    ) -> None:
        self.query = query
        self.output_format = output_format
        self.skip_invalid = skip_invalid
        self.color = color
        self.max_records = max_records


def _filtered_records(
    stream: IO[str],
    parsed: ParsedQuery,
    skip_invalid: bool,
) -> Iterator[dict]:
    """Yield log records from *stream* that satisfy *parsed* query."""
    for record in read_stream(stream, skip_invalid=skip_invalid):
        if matches(record, parsed):
            yield record


def run_pipeline(
    stream: IO[str],
    config: PipelineConfig,
    output: IO[str] = sys.stdout,
) -> int:
    """Run the full log-slice pipeline.

    Returns the number of records written to *output*.
    """
    parsed: ParsedQuery = parse_query(config.query)
    count = 0

    try:
        for record in _filtered_records(stream, parsed, config.skip_invalid):
            line = format_record(
                record,
                fmt=config.output_format,
                color=config.color,
            )
            output.write(line + "\n")
            count += 1
            if config.max_records is not None and count >= config.max_records:
                break
    except LogReadError as exc:
        print(f"[logslice] read error: {exc}", file=sys.stderr)
        raise

    return count
