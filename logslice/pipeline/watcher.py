"""File watcher that tails a log file and emits new lines as they appear."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Generator, Optional


class WatcherError(Exception):
    """Raised when the watcher encounters an unrecoverable error."""


@dataclass
class WatcherConfig:
    path: str
    poll_interval: float = 0.5
    max_iterations: Optional[int] = None  # None = run forever
    encoding: str = "utf-8"
    skip_to_end: bool = False  # if True, start reading from current EOF


def _open_file(path: str, encoding: str):
    """Open file for reading, raising WatcherError on failure."""
    try:
        return open(path, "r", encoding=encoding)
    except OSError as exc:
        raise WatcherError(f"Cannot open file {path!r}: {exc}") from exc


def iter_lines(config: WatcherConfig) -> Generator[str, None, None]:
    """Yield new lines from a growing log file.

    Polls the file at *poll_interval* seconds.  Each yielded value is a
    raw (stripped) line string.  Stops after *max_iterations* poll cycles
    when that value is set.
    """
    if not os.path.exists(config.path):
        raise WatcherError(f"File does not exist: {config.path!r}")

    fh = _open_file(config.path, config.encoding)
    try:
        if config.skip_to_end:
            fh.seek(0, 2)  # seek to EOF

        iterations = 0
        while True:
            line = fh.readline()
            if line:
                stripped = line.rstrip("\n")
                if stripped:
                    yield stripped
            else:
                if config.max_iterations is not None:
                    iterations += 1
                    if iterations >= config.max_iterations:
                        break
                time.sleep(config.poll_interval)
    finally:
        fh.close()
