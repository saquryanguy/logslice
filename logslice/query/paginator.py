"""Pagination support for log record result sets."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


class PaginationError(Exception):
    """Raised when pagination parameters are invalid."""


@dataclass
class PageResult:
    """Holds a single page of records along with pagination metadata."""

    records: List[Dict[str, Any]]
    page: int
    page_size: int
    total: int
    has_next: bool
    has_prev: bool

    def as_dict(self) -> Dict[str, Any]:
        return {
            "records": self.records,
            "page": self.page,
            "page_size": self.page_size,
            "total": self.total,
            "has_next": self.has_next,
            "has_prev": self.has_prev,
        }


@dataclass
class PaginatorConfig:
    """Configuration for paginating a list of records."""

    page: int = 1
    page_size: int = 50


def paginate(
    records: List[Dict[str, Any]],
    config: Optional[PaginatorConfig] = None,
) -> PageResult:
    """Slice *records* into a single page described by *config*.

    Raises:
        PaginationError: if *page* or *page_size* are not positive integers.
    """
    if config is None:
        config = PaginatorConfig()

    if config.page < 1:
        raise PaginationError(f"page must be >= 1, got {config.page}")
    if config.page_size < 1:
        raise PaginationError(f"page_size must be >= 1, got {config.page_size}")

    total = len(records)
    start = (config.page - 1) * config.page_size
    end = start + config.page_size
    page_records = records[start:end]

    return PageResult(
        records=page_records,
        page=config.page,
        page_size=config.page_size,
        total=total,
        has_next=end < total,
        has_prev=config.page > 1,
    )
