"""Adjudicator registry."""

from __future__ import annotations

from blindspot.adjudicators.base import Adjudicator
from blindspot.adjudicators.rules import RuleBasedAdjudicator


class AdjudicatorRegistry:
    def __init__(self) -> None:
        self._adj: dict[str, Adjudicator] = {}

    def register(self, adj: Adjudicator) -> None:
        self._adj[adj.adjudicator_id] = adj

    def get(self, adjudicator_id: str) -> Adjudicator:
        a = self._adj.get(adjudicator_id)
        if a is None:
            raise KeyError(f"No adjudicator: {adjudicator_id!r}")
        return a


def get_default_adjudicator_registry() -> AdjudicatorRegistry:
    reg = AdjudicatorRegistry()
    reg.register(RuleBasedAdjudicator())
    return reg
