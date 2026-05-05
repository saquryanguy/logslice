"""Tests for logslice.query.paginator."""

import pytest
from logslice.query.paginator import (
    PaginationError,
    PageResult,
    PaginatorConfig,
    paginate,
)


def _records(n: int):
    return [{"id": i, "message": f"msg {i}"} for i in range(n)]


def test_paginate_first_page_default_config():
    records = _records(10)
    result = paginate(records)
    assert result.page == 1
    assert result.page_size == 50
    assert result.total == 10
    assert len(result.records) == 10
    assert result.has_next is False
    assert result.has_prev is False


def test_paginate_first_page_partial():
    records = _records(120)
    cfg = PaginatorConfig(page=1, page_size=50)
    result = paginate(records, cfg)
    assert len(result.records) == 50
    assert result.records[0]["id"] == 0
    assert result.has_next is True
    assert result.has_prev is False


def test_paginate_second_page():
    records = _records(120)
    cfg = PaginatorConfig(page=2, page_size=50)
    result = paginate(records, cfg)
    assert len(result.records) == 50
    assert result.records[0]["id"] == 50
    assert result.has_next is True
    assert result.has_prev is True


def test_paginate_last_page_partial():
    records = _records(120)
    cfg = PaginatorConfig(page=3, page_size=50)
    result = paginate(records, cfg)
    assert len(result.records) == 20
    assert result.has_next is False
    assert result.has_prev is True


def test_paginate_beyond_total_returns_empty():
    records = _records(10)
    cfg = PaginatorConfig(page=5, page_size=50)
    result = paginate(records, cfg)
    assert result.records == []
    assert result.total == 10
    assert result.has_next is False
    assert result.has_prev is True


def test_paginate_empty_records():
    result = paginate([], PaginatorConfig(page=1, page_size=10))
    assert result.records == []
    assert result.total == 0
    assert result.has_next is False
    assert result.has_prev is False


def test_invalid_page_raises():
    with pytest.raises(PaginationError, match="page must be"):
        paginate(_records(5), PaginatorConfig(page=0))


def test_invalid_page_size_raises():
    with pytest.raises(PaginationError, match="page_size must be"):
        paginate(_records(5), PaginatorConfig(page=1, page_size=0))


def test_as_dict_keys():
    result = paginate(_records(3), PaginatorConfig(page=1, page_size=10))
    d = result.as_dict()
    assert set(d.keys()) == {"records", "page", "page_size", "total", "has_next", "has_prev"}
    assert d["total"] == 3
