"""Unit tests for scenario graph metrics."""

from blindspot.scenarios.graph import ScenarioGraph, ScenarioGraphNode, ScenarioGraphEdge


def _linear_graph():
    return ScenarioGraph(
        nodes=[
            ScenarioGraphNode(node_id="n1", node_type="action"),
            ScenarioGraphNode(node_id="n2", node_type="action"),
            ScenarioGraphNode(node_id="n3", node_type="goal"),
        ],
        edges=[
            ScenarioGraphEdge(source="n1", target="n2", relation="requires"),
            ScenarioGraphEdge(source="n2", target="n3", relation="enables"),
        ],
    )


def test_dependency_span_linear():
    g = _linear_graph()
    assert g.dependency_span() == 3


def test_dependency_breadth():
    g = _linear_graph()
    # Only n1 has no incoming edges
    assert g.dependency_breadth() == 1


def test_empty_graph():
    g = ScenarioGraph()
    assert g.dependency_span() == 0
    assert g.metrics()["node_count"] == 0
