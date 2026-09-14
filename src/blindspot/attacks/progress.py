"""Attack progress graph models."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class AttackProgressNode(BaseModel):
    model_config = ConfigDict(frozen=True)
    node_id: str
    description: str
    predicate_id: str
    weight: float = 1.0
    terminal: bool = False


class AttackProgressEdge(BaseModel):
    model_config = ConfigDict(frozen=True)
    source: str
    target: str
    edge_type: Literal["requires", "enables", "activates", "blocks"]


class AttackProgressGraph(BaseModel):
    model_config = ConfigDict(frozen=True)
    nodes: list[AttackProgressNode]
    edges: list[AttackProgressEdge]

    def total_weight(self) -> float:
        return sum(n.weight for n in self.nodes)

    def terminal_nodes(self) -> list[str]:
        return [n.node_id for n in self.nodes if n.terminal]


class AttackProgressResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    progress: float
    achieved_nodes: list[str]
    newly_achieved_nodes: list[str]
    blocked_nodes: list[str]
    terminal_nodes_achieved: list[str]
    evidence: list[dict[str, Any]] = Field(default_factory=list)


def evaluate_graph_progress(
    graph: AttackProgressGraph,
    previously_achieved: list[str],
    predicate_results: dict[str, bool],
) -> AttackProgressResult:
    """Evaluate progress over a graph given predicate satisfaction results."""
    now_achieved: set[str] = set(previously_achieved)
    newly_achieved: list[str] = []
    blocked: list[str] = []

    # Nodes whose prerequisites are met
    required_by: dict[str, list[str]] = {n.node_id: [] for n in graph.nodes}
    for edge in graph.edges:
        if edge.edge_type == "requires":
            required_by[edge.target].append(edge.source)

    for node in graph.nodes:
        if node.node_id in now_achieved:
            continue
        prereqs = required_by[node.node_id]
        if all(p in now_achieved for p in prereqs):
            if predicate_results.get(node.predicate_id, False):
                now_achieved.add(node.node_id)
                newly_achieved.append(node.node_id)
        else:
            blocked.append(node.node_id)

    total_weight = graph.total_weight() or 1.0
    achieved_weight = sum(
        n.weight for n in graph.nodes if n.node_id in now_achieved
    )
    progress = achieved_weight / total_weight

    terminal_achieved = [nid for nid in now_achieved
                         if any(n.node_id == nid and n.terminal for n in graph.nodes)]

    return AttackProgressResult(
        progress=min(1.0, progress),
        achieved_nodes=sorted(now_achieved),
        newly_achieved_nodes=newly_achieved,
        blocked_nodes=blocked,
        terminal_nodes_achieved=terminal_achieved,
    )
