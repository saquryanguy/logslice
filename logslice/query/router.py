"""Route log records to named destinations based on query filters."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from logslice.query.evaluator import matches
from logslice.query.parser import ParsedQuery


class RouterError(Exception):
    """Raised when the router is misconfigured or routing fails."""


@dataclass
class Route:
    """A named destination with an optional filter query."""

    name: str
    query: Optional[ParsedQuery] = None
    # Optional sink: called with every record routed here
    sink: Optional[Callable[[Dict[str, Any]], None]] = None


@dataclass
class RouterConfig:
    routes: List[Route] = field(default_factory=list)
    default_route: Optional[str] = None
    drop_unmatched: bool = False


@dataclass
class RoutingResult:
    record: Dict[str, Any]
    matched_routes: List[str]

    def as_dict(self) -> Dict[str, Any]:
        return {"record": self.record, "matched_routes": self.matched_routes}


def _validate_config(config: RouterConfig) -> None:
    """Raise RouterError if the config references duplicate route names."""
    seen: set[str] = set()
    for route in config.routes:
        if route.name in seen:
            raise RouterError(f"Duplicate route name: {route.name!r}")
        seen.add(route.name)
    if config.default_route and config.default_route in seen:
        raise RouterError(
            f"default_route {config.default_route!r} conflicts with an explicit route name."
        )


def _route_record(
    record: Dict[str, Any], config: RouterConfig
) -> RoutingResult:
    matched: List[str] = []

    for route in config.routes:
        if route.query is None or matches(record, route.query):
            matched.append(route.name)
            if route.sink is not None:
                route.sink(record)

    if not matched and not config.drop_unmatched and config.default_route:
        matched.append(config.default_route)

    return RoutingResult(record=record, matched_routes=matched)


def route_records(
    records: List[Dict[str, Any]], config: RouterConfig
) -> List[RoutingResult]:
    """Route each record and return a list of RoutingResult objects."""
    if not config.routes and not config.default_route:
        raise RouterError("RouterConfig must define at least one route or a default_route.")
    _validate_config(config)
    return [_route_record(r, config) for r in records]
