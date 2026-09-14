"""Unit tests for attack progress graph evaluation."""

from blindspot.attacks.progress import (
    AttackProgressGraph, AttackProgressEdge, AttackProgressNode,
    evaluate_graph_progress,
)


def _graph():
    return AttackProgressGraph(
        nodes=[
            AttackProgressNode(node_id="n1", description="First", predicate_id="p1", weight=0.5),
            AttackProgressNode(node_id="n2", description="Second", predicate_id="p2",
                               weight=0.5, terminal=True),
        ],
        edges=[AttackProgressEdge(source="n1", target="n2", edge_type="requires")],
    )


def test_no_nodes_achieved_initially():
    result = evaluate_graph_progress(_graph(), [], {"p1": False, "p2": False})
    assert result.progress == 0.0
    assert result.achieved_nodes == []


def test_first_node_achieved():
    result = evaluate_graph_progress(_graph(), [], {"p1": True, "p2": False})
    assert "n1" in result.achieved_nodes
    assert result.progress == 0.5


def test_terminal_node_requires_prerequisite():
    # n2 requires n1, so even if p2=True, n2 not achieved without n1
    result = evaluate_graph_progress(_graph(), [], {"p1": False, "p2": True})
    assert "n2" not in result.achieved_nodes


def test_full_completion():
    result = evaluate_graph_progress(_graph(), [], {"p1": True, "p2": True})
    assert result.progress == 1.0
    assert "n2" in result.terminal_nodes_achieved


def test_weighted_progress_correct():
    result = evaluate_graph_progress(_graph(), [], {"p1": True, "p2": False})
    assert result.progress == 0.5


def test_evidence_recorded():
    result = evaluate_graph_progress(_graph(), [], {"p1": True, "p2": True})
    assert isinstance(result.achieved_nodes, list)
