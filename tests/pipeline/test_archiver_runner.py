"""Tests for logslice.pipeline.archiver_runner."""
from logslice.pipeline.archiver_runner import ArchiverRunnerConfig, run_archiver
from logslice.query.archiver import ArchiveConfig


def _records():
    return [
        {"timestamp": "2024-01-01", "level": "info", "message": "hello"},
        {"timestamp": "2024-01-01", "level": "error", "message": "oops"},
        {"timestamp": "2024-01-02", "level": "info", "message": "world"},
    ]


def test_run_archiver_returns_result():
    result = run_archiver(_records())
    assert result.total == 3
    assert result.bucket_count == 2


def test_run_archiver_no_config_does_not_raise():
    result = run_archiver([])
    assert result.total == 0


def test_on_result_callback_called():
    received = []

    def cb(r):
        received.append(r)

    cfg = ArchiverRunnerConfig(on_result=cb)
    run_archiver(_records(), config=cfg)
    assert len(received) == 1
    assert received[0].total == 3


def test_on_result_callback_not_called_when_none():
    # Should complete without error when on_result is None
    cfg = ArchiverRunnerConfig(on_result=None)
    result = run_archiver(_records(), config=cfg)
    assert result is not None


def test_custom_archive_config_propagated():
    archive_cfg = ArchiveConfig(tag_field="level")
    cfg = ArchiverRunnerConfig(archive_config=archive_cfg)
    result = run_archiver(_records(), config=cfg)
    assert "2024-01-01::info" in result.buckets
    assert "2024-01-01::error" in result.buckets


def test_run_archiver_dropped_count():
    records = [
        {"level": "info"},  # missing timestamp
        {"timestamp": "2024-03-01", "level": "warn"},
    ]
    result = run_archiver(records)
    assert result.dropped == 1
    assert result.total == 2
