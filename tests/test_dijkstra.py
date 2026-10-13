"""Comprehensive tests for :func:`src.algorithms.dijkstra.dijkstra`."""

from __future__ import annotations

import math
import unittest

from src.algorithms.dijkstra import DijkstraResult, dijkstra, reconstruct_path


class TestDijkstraSimple(unittest.TestCase):
    """Basic shortest-path computations."""

    def setUp(self) -> None:
        # The example graph from the README / spec.
        self.graph = {
            "A": [("B", 4), ("C", 1)],
            "B": [("D", 1)],
            "C": [("B", 2), ("D", 5)],
            "D": [],
        }

    def test_simple_connected_graph_distances(self) -> None:
        result = dijkstra(self.graph, "A")
        self.assertEqual(result.distances["A"], 0)
        self.assertEqual(result.distances["B"], 3)
        self.assertEqual(result.distances["C"], 1)
        self.assertEqual(result.distances["D"], 4)

    def test_simple_connected_graph_path_a_to_d(self) -> None:
        result = dijkstra(self.graph, "A")
        path = reconstruct_path(result, "D")
        self.assertEqual(path, ["A", "C", "B", "D"])

    def test_source_to_source_path(self) -> None:
        result = dijkstra(self.graph, "A")
        path = reconstruct_path(result, "A")
        self.assertEqual(path, ["A"])

    def test_source_to_source_distance(self) -> None:
        result = dijkstra(self.graph, "A")
        self.assertEqual(result.distances["A"], 0)

    def test_readme_example(self) -> None:
        """Matches the exact example from the README spec."""
        result = dijkstra(self.graph, "A")
        self.assertEqual(result.distances, {"A": 0, "B": 3, "C": 1, "D": 4})
        self.assertEqual(reconstruct_path(result, "D"), ["A", "C", "B", "D"])


class TestDijkstraCompetingPaths(unittest.TestCase):
    """Graphs where multiple candidate paths compete."""

    def test_competing_paths(self) -> None:
        graph = {
            "S": [("A", 2), ("B", 5)],
            "A": [("B", 1), ("C", 7)],
            "B": [("C", 3)],
            "C": [],
        }
        result = dijkstra(graph, "S")
        self.assertEqual(result.distances["B"], 3)  # S->A->B
        self.assertEqual(result.distances["C"], 6)  # S->A->B->C
        self.assertEqual(reconstruct_path(result, "C"), ["S", "A", "B", "C"])


class TestDijkstraDisconnected(unittest.TestCase):
    """Graphs with unreachable vertices."""

    def test_disconnected_vertex_distance_is_inf(self) -> None:
        graph = {
            "A": [("B", 1)],
            "B": [],
            "C": [],  # isolated
        }
        result = dijkstra(graph, "A")
        self.assertTrue(math.isinf(result.distances["C"]))

    def test_unreachable_target_path_is_none(self) -> None:
        graph = {
            "A": [("B", 1)],
            "B": [],
            "C": [],
        }
        result = dijkstra(graph, "A")
        self.assertIsNone(reconstruct_path(result, "C"))

    def test_reconstruct_path_unknown_target(self) -> None:
        graph = {"A": []}
        result = dijkstra(graph, "A")
        self.assertIsNone(reconstruct_path(result, "Z"))


class TestDijkstraZeroWeight(unittest.TestCase):
    """Graphs with zero-weight edges."""

    def test_zero_weight_edges(self) -> None:
        graph = {
            "A": [("B", 0), ("C", 3)],
            "B": [("C", 0)],
            "C": [],
        }
        result = dijkstra(graph, "A")
        self.assertEqual(result.distances["B"], 0)
        self.assertEqual(result.distances["C"], 0)


class TestDijkstraEqualCost(unittest.TestCase):
    """Graphs with multiple shortest paths of equal cost."""

    def test_multiple_equal_cost_paths(self) -> None:
        graph = {
            "A": [("B", 1), ("C", 1)],
            "B": [("D", 1)],
            "C": [("D", 1)],
            "D": [],
        }
        result = dijkstra(graph, "A")
        self.assertEqual(result.distances["D"], 2)
        path = reconstruct_path(result, "D")
        # Either A->B->D or A->C->D is valid.
        self.assertIn(path, [["A", "B", "D"], ["A", "C", "D"]])


class TestDijkstraNeighborOnly(unittest.TestCase):
    """Vertices that appear only as neighbors (no adjacency-list key)."""

    def test_vertex_only_as_neighbor(self) -> None:
        # "Z" is reachable but has no key in the graph dict.
        graph = {
            "A": [("B", 2), ("Z", 10)],
            "B": [("Z", 3)],
        }
        result = dijkstra(graph, "A")
        self.assertEqual(result.distances["Z"], 5)  # A->B->Z
        self.assertEqual(reconstruct_path(result, "Z"), ["A", "B", "Z"])


class TestDijkstraValidation(unittest.TestCase):
    """Input validation: bad source, negative weights, malformed edges."""

    def test_invalid_source_vertex(self) -> None:
        graph = {"A": [("B", 1)], "B": []}
        with self.assertRaises(ValueError):
            dijkstra(graph, "X")

    def test_negative_weight_raises(self) -> None:
        graph = {
            "A": [("B", -1)],
            "B": [],
        }
        with self.assertRaises(ValueError):
            dijkstra(graph, "A")

    def test_invalid_edge_format_too_short(self) -> None:
        graph: dict = {"A": [("B",)]}  # type: ignore[list-item]
        with self.assertRaises(ValueError):
            dijkstra(graph, "A")

    def test_invalid_edge_format_too_long(self) -> None:
        graph: dict = {"A": [("B", 1, "extra")]}  # type: ignore[list-item]
        with self.assertRaises(ValueError):
            dijkstra(graph, "A")

    def test_invalid_weight_type(self) -> None:
        graph: dict = {"A": [("B", "fast")]}  # type: ignore[list-item]
        with self.assertRaises(ValueError):
            dijkstra(graph, "A")

    def test_adjacency_list_not_a_list(self) -> None:
        graph: dict = {"A": {("B", 1)}}  # type: ignore[dict-item]
        with self.assertRaises(ValueError):
            dijkstra(graph, "A")

    def test_nan_weight_raises(self) -> None:
        graph: dict = {"A": [("B", float("nan"))], "B": []}
        with self.assertRaises(ValueError):
            dijkstra(graph, "A")


class TestDijkstraSingleVertex(unittest.TestCase):
    """Graph with exactly one vertex."""

    def test_single_vertex(self) -> None:
        graph = {"A": []}
        result = dijkstra(graph, "A")
        self.assertEqual(result.distances, {"A": 0})
        self.assertEqual(reconstruct_path(result, "A"), ["A"])


class TestDijkstraPredecessors(unittest.TestCase):
    """Predecessor map correctness."""

    def test_predecessors_basic(self) -> None:
        graph = {
            "A": [("B", 4), ("C", 1)],
            "B": [("D", 1)],
            "C": [("B", 2), ("D", 5)],
            "D": [],
        }
        result = dijkstra(graph, "A")
        self.assertIsNone(result.predecessors["A"])
        self.assertEqual(result.predecessors["C"], "A")
        self.assertEqual(result.predecessors["B"], "C")
        self.assertEqual(result.predecessors["D"], "B")


class TestDijkstraResultType(unittest.TestCase):
    """DijkstraResult dataclass contract."""

    def test_result_is_frozen_dataclass(self) -> None:
        graph = {"A": []}
        result = dijkstra(graph, "A")
        self.assertIsInstance(result, DijkstraResult)
        with self.assertRaises(AttributeError):
            result.source = "X"  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
