"""Log ingestion utilities for logslice."""

from .reader import LogReadError, read_file, read_stream

__all__ = ["read_stream", "read_file", "LogReadError"]
