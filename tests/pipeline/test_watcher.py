"""Tests for logslice.pipeline.watcher."""

from __future__ import annotations

import os
import tempfile
import threading
import time

import pytest

from logslice.pipeline.watcher import WatcherConfig, WatcherError, iter_lines


def _write_lines(path: str, lines: list[str], delay: float = 0.0) -> None:
    """Helper: write lines to a file, optionally with a delay."""
    if delay:
        time.sleep(delay)
    with open(path, "a") as fh:
        for line in lines:
            fh.write(line + "\n")


def test_iter_lines_reads_existing_content(tmp_path):
    log = tmp_path / "app.log"
    log.write_text("line1\nline2\nline3\n")
    config = WatcherConfig(path=str(log), poll_interval=0.05, max_iterations=1)
    result = list(iter_lines(config))
    assert result == ["line1", "line2", "line3"]


def test_iter_lines_skips_empty_lines(tmp_path):
    log = tmp_path / "app.log"
    log.write_text("line1\n\nline2\n")
    config = WatcherConfig(path=str(log), poll_interval=0.05, max_iterations=1)
    result = list(iter_lines(config))
    assert result == ["line1", "line2"]


def test_iter_lines_skip_to_end_misses_existing(tmp_path):
    log = tmp_path / "app.log"
    log.write_text("old_line\n")
    config = WatcherConfig(
        path=str(log), poll_interval=0.05, max_iterations=1, skip_to_end=True
    )
    result = list(iter_lines(config))
    assert result == []


def test_iter_lines_picks_up_new_content(tmp_path):
    log = tmp_path / "app.log"
    log.write_text("")
    config = WatcherConfig(path=str(log), poll_interval=0.05, max_iterations=4)

    t = threading.Thread(
        target=_write_lines, args=([str(log), ["new_line"]], ), kwargs={"delay": 0.08}
    )
    # Rewrite to pass args correctly
    t = threading.Thread(
        target=lambda: _write_lines(str(log), ["new_line"], delay=0.08)
    )
    t.start()
    result = list(iter_lines(config))
    t.join()
    assert "new_line" in result


def test_iter_lines_missing_file_raises():
    config = WatcherConfig(path="/nonexistent/path/app.log", max_iterations=1)
    with pytest.raises(WatcherError, match="does not exist"):
        list(iter_lines(config))


def test_iter_lines_max_iterations_zero(tmp_path):
    log = tmp_path / "app.log"
    log.write_text("line1\n")
    config = WatcherConfig(path=str(log), poll_interval=0.01, max_iterations=0)
    # max_iterations=0 means stop immediately after first empty read
    result = list(iter_lines(config))
    # Content is read before the first empty poll triggers the counter
    assert "line1" in result
