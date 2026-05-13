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


def test_deduplication_preserves_order():
    """Deduplication should keep the first occurrence of each filter."""
    f1 = _f("level", value="error")
    f2 = _f("service", value="api")
    f3 = _f("level", value="error")  # duplicate of f1
    q = _q(f1, f2, f3)
    result = rewrite_query(q)
    assert len(result.filters) == 2
    assert result.filters[0].field == "level"
    assert result.filters[1].field == "service"


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
