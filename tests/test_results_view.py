"""Unit tests for human-readable algorithm result presentations."""

from __future__ import annotations

from typing import Any

from visualization.execution import execute_algorithm
from visualization.input_parser import parse_edge_list
from visualization.results_view import _format_weight, render_human_results


class DummyStreamlit:
    """Mock Streamlit recorder to test human-readable output without a browser."""

    def __init__(self):
        self.markdowns: list[str] = []
        self.writes: list[str] = []
        self.warnings: list[str] = []
        self.errors: list[str] = []
        self.successes: list[str] = []
        self.metrics: list[tuple[str, Any]] = []

    def markdown(self, text: str) -> None:
        self.markdowns.append(text)

    def write(self, *args: Any) -> None:
        for arg in args:
            self.writes.append(str(arg))

    def warning(self, text: str) -> None:
        self.warnings.append(text)

    def error(self, text: str) -> None:
        self.errors.append(text)

    def success(self, text: str) -> None:
        self.successes.append(text)

    def columns(self, count: int) -> list[DummyStreamlit]:
        return [self] * count

    def metric(self, label: str, value: Any) -> None:
        self.metrics.append((label, value))


def test_format_weight():
    assert _format_weight(10.0) == "10"
    assert _format_weight(2.5) == "2.5"
    assert _format_weight(0.0) == "0"
    assert _format_weight(-3.0) == "-3"
    assert _format_weight(None) == ""


def test_dijkstra_human_results(monkeypatch):
    mock = DummyStreamlit()
    monkeypatch.setattr("visualization.results_view.st", mock)

    edges = "s y 5\ns t 10\ny t 3\nt x 1"
    parsed = parse_edge_list(edges, directed=True, weighted=True)
    result = execute_algorithm(parsed.graph, "dijkstra", source="s")

    render_human_results("dijkstra", result, parsed.graph, source="s", target="x")

    assert any("Shortest Route Found" in md for md in mock.markdowns)
    assert any("s ➔ y ➔ t ➔ x" in md for md in mock.markdowns)
    metric_labels = [label for label, _ in mock.metrics]
    assert "Source" in metric_labels
    assert "Destination" in metric_labels
    assert "Total Cost" in metric_labels
    assert ("Total Cost", "9") in mock.metrics


def test_dijkstra_unreachable_target(monkeypatch):
    mock = DummyStreamlit()
    monkeypatch.setattr("visualization.results_view.st", mock)

    edges = "s t 5\nisolated"
    parsed = parse_edge_list(edges, directed=True, weighted=True)
    result = execute_algorithm(parsed.graph, "dijkstra", source="s")

    render_human_results(
        "dijkstra", result, parsed.graph, source="s", target="isolated"
    )

    assert any("No Route Available" in md for md in mock.markdowns)
    assert any("cannot be reached" in w for w in mock.warnings)
    assert ("Route Status", "Unreachable") in mock.metrics


def test_kruskal_human_results(monkeypatch):
    mock = DummyStreamlit()
    monkeypatch.setattr("visualization.results_view.st", mock)

    edges = "A B 4\nA C 2\nB C 1\nC D 3"
    parsed = parse_edge_list(edges, directed=False, weighted=True)
    result = execute_algorithm(parsed.graph, "kruskal")

    render_human_results("kruskal", result, parsed.graph)

    assert any("Minimum Spanning Tree Computed" in md for md in mock.markdowns)
    assert ("Total Weight", "6") in mock.metrics
    assert any("Edge Connection" in md for md in mock.markdowns)


def test_bfs_traversal_human_results(monkeypatch):
    mock = DummyStreamlit()
    monkeypatch.setattr("visualization.results_view.st", mock)

    edges = "A B\nA C\nB D"
    parsed = parse_edge_list(edges, directed=False, weighted=False)
    result = execute_algorithm(parsed.graph, "BFS", source="A")

    render_human_results(
        "BFS", result, parsed.graph, source="A", objective="Explore or traverse"
    )

    assert any("Breadth-First Traversal Completed" in md for md in mock.markdowns)
    assert any("A ➔ B ➔ C ➔ D" in md for md in mock.markdowns)
    assert ("Start Vertex", "A") in mock.metrics


def test_dfs_traversal_human_results(monkeypatch):
    mock = DummyStreamlit()
    monkeypatch.setattr("visualization.results_view.st", mock)

    edges = "A B\nA C\nB D"
    parsed = parse_edge_list(edges, directed=False, weighted=False)
    result = execute_algorithm(parsed.graph, "DFS", source="A")

    render_human_results("DFS", result, parsed.graph, source="A")

    assert any("Depth-First Traversal Completed" in md for md in mock.markdowns)
    assert ("Start Vertex", "A") in mock.metrics


def test_connected_components_human_results(monkeypatch):
    mock = DummyStreamlit()
    monkeypatch.setattr("visualization.results_view.st", mock)

    edges = "A B\nC D"
    parsed = parse_edge_list(edges, directed=False, weighted=False)
    result = execute_algorithm(parsed.graph, "ConnectedComponents")

    render_human_results("ConnectedComponents", result, parsed.graph)

    assert any("Connected Components Identified" in md for md in mock.markdowns)
    assert ("Component Count", "2") in mock.metrics


def test_scc_human_results(monkeypatch):
    mock = DummyStreamlit()
    monkeypatch.setattr("visualization.results_view.st", mock)

    edges = "A B\nB A\nC D"
    parsed = parse_edge_list(edges, directed=True, weighted=False)
    result = execute_algorithm(parsed.graph, "SCC")

    render_human_results("SCC", result, parsed.graph)

    assert any(
        "Strongly Connected Components Identified" in md for md in mock.markdowns
    )
    assert ("SCC Count", "3") in mock.metrics


def test_cycle_detection_human_results(monkeypatch):
    mock = DummyStreamlit()
    monkeypatch.setattr("visualization.results_view.st", mock)

    # Graph with cycle
    edges_cycle = "A B\nB C\nC A"
    parsed = parse_edge_list(edges_cycle, directed=True, weighted=False)
    result = execute_algorithm(parsed.graph, "CycleDetection")
    render_human_results("CycleDetection", result, parsed.graph)
    assert any("Cycle Detected" in md for md in mock.markdowns)
    assert ("Has Cycle", "Yes") in mock.metrics

    # Graph without cycle
    mock_acyclic = DummyStreamlit()
    monkeypatch.setattr("visualization.results_view.st", mock_acyclic)
    edges_no_cycle = "A B\nB C"
    parsed_no_cycle = parse_edge_list(edges_no_cycle, directed=True, weighted=False)
    result_no_cycle = execute_algorithm(parsed_no_cycle.graph, "CycleDetection")
    render_human_results("CycleDetection", result_no_cycle, parsed_no_cycle.graph)
    assert any("No Cycles Detected" in md for md in mock_acyclic.markdowns)
    assert ("Has Cycle", "No") in mock_acyclic.metrics


def test_topological_sort_human_results(monkeypatch):
    mock = DummyStreamlit()
    monkeypatch.setattr("visualization.results_view.st", mock)

    edges = "A B\nA C\nB D\nC D"
    parsed = parse_edge_list(edges, directed=True, weighted=False)
    result = execute_algorithm(parsed.graph, "TopologicalSort")

    render_human_results("TopologicalSort", result, parsed.graph)

    assert any("Topological Ordering Found" in md for md in mock.markdowns)
    assert any("Valid Execution Sequence:" in md for md in mock.markdowns)


def test_bipartite_test_human_results(monkeypatch):
    mock = DummyStreamlit()
    monkeypatch.setattr("visualization.results_view.st", mock)

    # Even cycle (bipartite)
    edges = "A B\nB C\nC D\nD A"
    parsed = parse_edge_list(edges, directed=False, weighted=False)
    result = execute_algorithm(parsed.graph, "BipartiteTest")

    render_human_results("BipartiteTest", result, parsed.graph)

    assert any("Graph Is Bipartite" in md for md in mock.markdowns)
    assert ("Is Bipartite", "Yes") in mock.metrics
