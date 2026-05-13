"""Tests for logslice.query.redactor."""

import pytest

from logslice.query.redactor import (
    RedactConfig,
    RedactError,
    RedactRule,
    redact,
)


def _records():
    return [
        {"level": "info", "service": "auth", "message": "login", "token": "abc123"},
        {"level": "warn", "service": "api", "message": "retry", "token": "xyz789"},
        {"level": "error", "service": "db", "message": "fail", "token": "nope"},
    ]


def test_empty_config_returns_copies():
    records = _records()
    result = redact(records, RedactConfig())
    assert result.redacted_count == 0
    assert result.records == records
    assert result.records is not records


def test_redact_keys_shorthand():
    records = _records()
    config = RedactConfig(redact_keys=["token"])
    result = redact(records, config)
    assert result.redacted_count == 3
    for r in result.records:
        assert r["token"] == "***REDACTED***"


def test_custom_replacement():
    records = [{"password": "s3cr3t", "user": "alice"}]
    rule = RedactRule(field="password", replacement="[HIDDEN]")
    result = redact(records, RedactConfig(rules=[rule]))
    assert result.records[0]["password"] == "[HIDDEN]"
    assert result.records[0]["user"] == "alice"


def test_pattern_partial_redaction():
    records = [{"message": "token=abc123 received"}]
    rule = RedactRule(field="message", pattern=r"token=\w+", replacement="token=***")
    result = redact(records, RedactConfig(rules=[rule]))
    assert result.records[0]["message"] == "token=*** received"
    assert result.redacted_count == 1


def test_pattern_no_match_not_counted():
    records = [{"message": "no sensitive data here"}]
    rule = RedactRule(field="message", pattern=r"secret=\w+", replacement="secret=***")
    result = redact(records, RedactConfig(rules=[rule]))
    assert result.redacted_count == 0


def test_mask_fn_applied():
    records = [{"email": "user@example.com"}]
    rule = RedactRule(field="email", mask_fn=lambda v: v.split("@")[0][:2] + "***@***")
    result = redact(records, RedactConfig(rules=[rule]))
    assert result.records[0]["email"] == "us***@***"


def test_nested_field_redacted():
    records = [{"user": {"name": "alice", "ssn": "123-45-6789"}}]
    rule = RedactRule(field="user.ssn")
    result = redact(records, RedactConfig(rules=[rule]))
    assert result.records[0]["user"]["ssn"] == "***REDACTED***"
    assert result.records[0]["user"]["name"] == "alice"


def test_missing_field_not_counted():
    records = [{"level": "info"}]
    rule = RedactRule(field="token")
    result = redact(records, RedactConfig(rules=[rule]))
    assert result.redacted_count == 0


def test_original_records_not_mutated():
    records = [{"token": "secret"}]
    original_token = records[0]["token"]
    redact(records, RedactConfig(redact_keys=["token"]))
    assert records[0]["token"] == original_token


def test_rule_rejects_pattern_and_mask_fn():
    with pytest.raises(RedactError):
        RedactRule(field="x", pattern=r"\w+", mask_fn=lambda v: v)


def test_as_dict_structure():
    records = [{"token": "abc"}]
    result = redact(records, RedactConfig(redact_keys=["token"]))
    d = result.as_dict()
    assert "records" in d
    assert "redacted_count" in d
    assert d["redacted_count"] == 1
