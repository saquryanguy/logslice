"""Tests for logslice.query.rewriter."""

import pytest

from logslice.query.parser import ParsedQuery, QueryFilter
from logslice.query.rewriter import (
    RewriteConfig,
    RewriteError,
    rewrite_query,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _q(*filters, limit=None):
    return ParsedQuery(filters=list(filters), limit=limit)


def _f(field, operator="eq", value="x"):
    return QueryFilter(field=field, operator=operator, value=value)


# ---------------------------------------------------------------------------
# Alias resolution
# ---------------------------------------------------------------------------


def test_resolve_alias_lvl_to_level():
    q = _q(_f("lvl", value="error"))
    result = rewrite_query(q)
    assert result.filters[0].field == "level"


def test_resolve_alias_svc_to_service():
    q = _q(_f("svc", value="api"))
    result = rewrite_query(q)
    assert result.filters[0].field == "service"


def test_resolve_alias_msg_to_message():
    q = _q(_f("msg", value="hello"))
    result = rewrite_query(q)
    assert result.filters[0].field == "message"


def test_unknown_field_unchanged():
    q = _q(_f("custom_field", value="v"))
    result = rewrite_query(q)
    assert result.filters[0].field == "custom_field"


def test_alias_resolution_disabled():
    cfg = RewriteConfig(resolve_aliases=False)
    q = _q(_f("lvl", value="warn"))
    result = rewrite_query(q, cfg)
    assert result.filters[0].field == "lvl"


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------


def test_duplicate_filters_removed():
    f = _f("level", value="error")
    q = _q(f, f)
    result = rewrite_query(q)
    assert len(result.filters) == 1


def test_non_duplicate_filters_kept():
    q = _q(_f("level", value="error"), _f("level", value="warn"))
    result = rewrite_query(q)
    assert len(result.filters) == 2


def test_deduplication_disabled():
    f = _f("level", value="error")
    cfg = RewriteConfig(deduplicate_filters=False)
    q = _q(f, f)
    result = rewrite_query(q, cfg)
    assert len(result.filters) == 2


# ---------------------------------------------------------------------------
# Default injection
# ---------------------------------------------------------------------------


def test_inject_default_adds_missing_field():
    cfg = RewriteConfig(inject_defaults={"env": "production"})
    q = _q(_f("level", value="error"))
    result = rewrite_query(q, cfg)
    fields = {f.field for f in result.filters}
    assert "env" in fields


def test_inject_default_skips_existing_field():
    cfg = RewriteConfig(inject_defaults={"level": "info"})
    q = _q(_f("level", value="error"))
    result = rewrite_query(q, cfg)
    level_filters = [f for f in result.filters if f.field == "level"]
    assert len(level_filters) == 1
    assert level_filters[0].value == "error"


# ---------------------------------------------------------------------------
# Limit capping
# ---------------------------------------------------------------------------


def test_max_limit_caps_existing_limit():
    cfg = RewriteConfig(max_limit=50)
    q = _q(limit=200)
    result = rewrite_query(q, cfg)
    assert result.limit == 50


def test_max_limit_does_not_raise_lower_limit():
    cfg = RewriteConfig(max_limit=100)
    q = _q(limit=30)
    result = rewrite_query(q, cfg)
    assert result.limit == 30


def test_max_limit_injected_when_no_limit_set():
    cfg = RewriteConfig(max_limit=500)
    q = _q()
    result = rewrite_query(q, cfg)
    assert result.limit == 500


# ---------------------------------------------------------------------------
# Immutability
# ---------------------------------------------------------------------------


def test_original_query_not_mutated():
    f = _f("lvl", value="warn")
    q = _q(f, limit=100)
    rewrite_query(q)
    assert q.filters[0].field == "lvl"
    assert q.limit == 100
