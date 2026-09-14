"""Scenario causal graph."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ScenarioGraphNode(BaseModel):
    model_config = ConfigDict(frozen=True)
    node_id: str
    node_type: Literal[
        "observation", "action", "tool_call", "state_transition",
        "event", "goal", "hazard", "attack", "recovery",
    ]
    predicate_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ScenarioGraphEdge(BaseModel):
    model_config = ConfigDict(frozen=True)
    source: str
    target: str
    relation: Literal[
        "requires", "enables", "causes", "reveals",
        "blocks", "recovers", "counterfactual_to",
    ]


class ScenarioGraph(BaseModel):
    model_config = ConfigDict(frozen=True)
    nodes: list[ScenarioGraphNode] = Field(default_factory=list)
    edges: list[ScenarioGraphEdge] = Field(default_factory=list)

    def dependency_span(self) -> int:
        """Longest path length in the graph."""
        if not self.nodes:
            return 0
        successors: dict[str, list[str]] = {n.node_id: [] for n in self.nodes}
        for e in self.edges:
            if e.relation in ("requires", "enables", "causes"):
                successors[e.source].append(e.target)

        def _depth(node_id: str, visited: set[str]) -> int:
            if node_id in visited:
                return 0
            visited.add(node_id)
            children = successors.get(node_id, [])
            if not children:
                return 1
            return 1 + max(_depth(c, visited) for c in children)

        return max(_depth(n.node_id, set()) for n in self.nodes)

    def dependency_breadth(self) -> int:
        """Number of nodes with in-degree 0 (sources)."""
        targets = {e.target for e in self.edges}
        return sum(1 for n in self.nodes if n.node_id not in targets)

    def metrics(self) -> dict[str, Any]:
        return {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "dependency_span": self.dependency_span(),
            "dependency_breadth": self.dependency_breadth(),
        }
