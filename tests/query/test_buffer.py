"""Tests for logslice.query.buffer."""
import pytest

from logslice.query.buffer import (
    BufferConfig,
    BufferError,
    BufferResult,
    buffer_records,
)


def _records(n: int, level: str = "info") -> list:
    return [{"level": level, "message": f"msg {i}", "i": i} for i in range(n)]


# ---------------------------------------------------------------------------
# Config validation
# ---------------------------------------------------------------------------

def test_config_default_max_size():
    cfg = BufferConfig()
    assert cfg.max_size == 100


def test_config_zero_max_size_raises():
    with pytest.raises(BufferError):
        BufferConfig(max_size=0)


def test_config_negative_max_size_raises():
    with pytest.raises(BufferError):
        BufferConfig(max_size=-5)


# ---------------------------------------------------------------------------
# Buffering behaviour
# ---------------------------------------------------------------------------

def test_empty_records_returns_empty_result():
    result = buffer_records([])
    assert result.flushed_batches == 0
    assert result.total_flushed == 0
    assert result.remaining == []


def test_records_under_limit_stay_in_remaining():
    result = buffer_records(_records(5), BufferConfig(max_size=10))
    assert result.flushed_batches == 0
    assert result.total_flushed == 0
    assert len(result.remaining) == 5


def test_exact_batch_size_flushes_once():
    result = buffer_records(_records(10), BufferConfig(max_size=10))
    assert result.flushed_batches == 1
    assert result.total_flushed == 10
    assert result.remaining == []


def test_multiple_full_batches():
    result = buffer_records(_records(25), BufferConfig(max_size=10))
    assert result.flushed_batches == 2
    assert result.total_flushed == 20
    assert len(result.remaining) == 5


def test_on_flush_callback_called_per_batch():
    batches = []
    cfg = BufferConfig(max_size=3, on_flush=batches.append)
    buffer_records(_records(9), cfg)
    assert len(batches) == 3
    assert all(len(b) == 3 for b in batches)


def test_on_flush_receives_correct_records():
    seen = []
    cfg = BufferConfig(max_size=2, on_flush=lambda b: seen.extend(b))
    buffer_records(_records(4), cfg)
    assert [r["i"] for r in seen] == [0, 1, 2, 3]


def test_flush_on_full_false_never_flushes():
    cfg = BufferConfig(max_size=2, flush_on_full=False)
    result = buffer_records(_records(10), cfg)
    assert result.flushed_batches == 0
    assert len(result.remaining) == 10


def test_as_dict_keys():
    result = BufferResult(flushed_batches=2, total_flushed=20, remaining=[])
    d = result.as_dict()
    assert set(d.keys()) == {"flushed_batches", "total_flushed", "remaining_count"}
    assert d["remaining_count"] == 0


def test_default_config_used_when_none_passed():
    # Should not raise; uses BufferConfig() defaults
    result = buffer_records(_records(3))
    assert len(result.remaining) == 3
