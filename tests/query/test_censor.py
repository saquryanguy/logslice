"""Tests for logslice.query.censor."""
import pytest

from logslice.query.censor import CensorConfig, CensorError, CensorResult, censor


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _records():
    return [
        {"level": "INFO", "message": "hello", "password": "s3cr3t", "token": "abc"},
        {"level": "ERROR", "message": "oops", "password": "hunter2", "user": "alice"},
        {"level": "DEBUG", "message": "trace", "user": "bob"},
    ]


# ---------------------------------------------------------------------------
# CensorConfig validation
# ---------------------------------------------------------------------------


def test_config_requires_keys_or_patterns():
    with pytest.raises(CensorError):
        CensorConfig(keys=[], patterns=[])


def test_config_keys_only_is_valid():
    cfg = CensorConfig(keys=["password"])
    assert cfg.keys == ["password"]


def test_config_patterns_only_is_valid():
    cfg = CensorConfig(patterns=[r"pass.*"])
    assert cfg.patterns == [r"pass.*"]


# ---------------------------------------------------------------------------
# Basic censoring
# ---------------------------------------------------------------------------


def test_censor_replaces_exact_key():
    cfg = CensorConfig(keys=["password"])
    result = censor(_records(), cfg)
    for rec in result.records:
        if "password" in rec:
            assert rec["password"] == "***"


def test_censor_custom_replacement():
    cfg = CensorConfig(keys=["password"], replacement="[REDACTED]")
    result = censor(_records(), cfg)
    for rec in result.records:
        if "password" in rec:
            assert rec["password"] == "[REDACTED]"


def test_censor_drop_removes_field():
    cfg = CensorConfig(keys=["password"], drop=True)
    result = censor(_records(), cfg)
    for rec in result.records:
        assert "password" not in rec


def test_censor_pattern_matches_key():
    cfg = CensorConfig(patterns=[r"pass.*"])
    result = censor(_records(), cfg)
    for rec in result.records:
        if "password" in rec:
            assert rec["password"] == "***"


def test_censor_unrelated_fields_untouched():
    cfg = CensorConfig(keys=["password"])
    result = censor(_records(), cfg)
    assert result.records[0]["level"] == "INFO"
    assert result.records[0]["message"] == "hello"


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------


def test_censor_total_equals_input_length():
    cfg = CensorConfig(keys=["password"])
    result = censor(_records(), cfg)
    assert result.total == len(_records())


def test_censor_censored_fields_count():
    cfg = CensorConfig(keys=["password"])
    result = censor(_records(), cfg)
    # Two records have 'password'
    assert result.censored_fields == 2


def test_censor_multiple_keys_counted():
    cfg = CensorConfig(keys=["password", "token"])
    result = censor(_records(), cfg)
    # record 0: password + token = 2; record 1: password = 1
    assert result.censored_fields == 3


def test_censor_no_config_raises():
    with pytest.raises(CensorError):
        censor(_records(), config=None)


def test_censor_empty_records():
    cfg = CensorConfig(keys=["password"])
    result = censor([], cfg)
    assert result.total == 0
    assert result.censored_fields == 0
    assert result.records == []


def test_as_dict_keys():
    cfg = CensorConfig(keys=["password"])
    result = censor(_records(), cfg)
    d = result.as_dict()
    assert set(d.keys()) == {"total", "censored_fields", "records"}


def test_censor_does_not_mutate_original():
    records = _records()
    original_pw = records[0]["password"]
    cfg = CensorConfig(keys=["password"])
    censor(records, cfg)
    assert records[0]["password"] == original_pw
