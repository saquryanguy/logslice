"""Tests for logslice.pipeline.correlator_runner."""
from typing import Any, Dict, List

from logslice.query.correlator import CorrelatorConfig
from logslice.pipeline.correlator_runner import CorrelatorRunnerConfig, run_correlator


def _records() -> List[Dict[str, Any]]:
    return [
        {"timestamp": 100, "trace_id": "t1", "level": "info", "message": "req start"},
        {"timestamp": 110, "trace_id": "t1", "level": "error", "message": "req fail"},
        {"timestamp": 120, "trace_id": "t2", "level": "info", "message": "req start"},
        {"timestamp": 130, "trace_id": "t2", "level": "info", "message": "req end"},
        {"timestamp": 140, "trace_id": "t3", "level": "debug", "message": "ping"},
    ]


def test_run_correlator_returns_result():
    cfg = CorrelatorRunnerConfig(
        correlator=CorrelatorConfig(key_field="trace_id", min_group_size=2)
    )
    result = run_correlator(_records(), cfg)
    assert result.total_groups >= 1


def test_run_correlator_no_callback_does_not_raise():
    cfg = CorrelatorRunnerConfig(
        correlator=CorrelatorConfig(key_field="trace_id", min_group_size=2),
        on_group=None,
    )
    result = run_correlator(_records(), cfg)
    assert result is not None


def test_on_group_callback_called_for_each_group():
    seen_keys: List[str] = []

    def _cb(key: str, recs: List[Dict[str, Any]]) -> None:
        seen_keys.append(key)

    cfg = CorrelatorRunnerConfig(
        correlator=CorrelatorConfig(key_field="trace_id", min_group_size=2),
        on_group=_cb,
    )
    result = run_correlator(_records(), cfg)
    assert len(seen_keys) == result.total_groups


def test_on_group_callback_receives_correct_records():
    groups: Dict[str, List[Dict[str, Any]]] = {}

    def _cb(key: str, recs: List[Dict[str, Any]]) -> None:
        groups[key] = recs

    cfg = CorrelatorRunnerConfig(
        correlator=CorrelatorConfig(key_field="trace_id", min_group_size=2),
        on_group=_cb,
    )
    run_correlator(_records(), cfg)
    for key, recs in groups.items():
        assert all(r["trace_id"] == key for r in recs)


def test_empty_records_returns_empty_result():
    cfg = CorrelatorRunnerConfig(
        correlator=CorrelatorConfig(key_field="trace_id", min_group_size=2)
    )
    result = run_correlator([], cfg)
    assert result.total_groups == 0
    assert result.total_records == 0


def test_result_as_dict_has_expected_keys():
    cfg = CorrelatorRunnerConfig(
        correlator=CorrelatorConfig(key_field="trace_id", min_group_size=2)
    )
    result = run_correlator(_records(), cfg)
    d = result.as_dict()
    assert "total_records" in d
    assert "total_groups" in d
    assert "groups" in d
