"""Field-level censoring: mask or drop fields matching a pattern or key list."""
from __future__ import annotations

import copy
import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional


class CensorError(Exception):
    """Raised when censoring configuration is invalid."""


@dataclass
class CensorConfig:
    """Configuration for the censor operation.

    Attributes:
        keys: Exact field names to censor.
        patterns: Regex patterns; any key fully matching is censored.
        replacement: Value to substitute for censored fields.
        drop: When True, remove the field entirely instead of replacing.
    """

    keys: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    replacement: str = "***"
    drop: bool = False

    def __post_init__(self) -> None:
        if not self.keys and not self.patterns:
            raise CensorError("CensorConfig requires at least one key or pattern")
        invalid = [p for p in self.patterns if not p]
        if invalid:
            raise CensorError("CensorConfig patterns must not be empty strings")
        try:
            self._compiled: List[re.Pattern[str]] = [
                re.compile(p) for p in self.patterns
            ]
        except re.error as exc:
            raise CensorError(f"Invalid regex pattern in CensorConfig: {exc}") from exc

    def _should_censor(self, key: str) -> bool:
        if key in self.keys:
            return True
        return any(p.fullmatch(key) for p in self._compiled)


@dataclass
class CensorResult:
    records: List[Dict]
    total: int
    censored_fields: int

    def as_dict(self) -> Dict:
        return {
            "total": self.total,
            "censored_fields": self.censored_fields,
            "records": self.records,
        }


def _censor_record(record: Dict, config: CensorConfig) -> tuple[Dict, int]:
    """Return a shallow-copied record with censored fields and a count of changes."""
    out = copy.copy(record)
    count = 0
    for key in list(out.keys()):
        if config._should_censor(key):
            if config.drop:
                del out[key]
            else:
                out[key] = config.replacement
            count += 1
    return out, count


def censor(
    records: Iterable[Dict],
    config: Optional[CensorConfig] = None,
) -> CensorResult:
    """Apply censoring rules to each record.

    Args:
        records: Iterable of log record dicts.
        config: CensorConfig instance; if None a CensorError is raised.

    Returns:
        CensorResult with processed records and statistics.
    """
    if config is None:
        raise CensorError("A CensorConfig must be provided")

    out_records: List[Dict] = []
    total_censored = 0
    for record in records:
        processed, n = _censor_record(record, config)
        out_records.append(processed)
        total_censored += n

    return CensorResult(
        records=out_records,
        total=len(out_records),
        censored_fields=total_censored,
    )
