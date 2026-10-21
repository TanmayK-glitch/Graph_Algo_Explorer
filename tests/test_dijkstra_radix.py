"""Tests for :func:`src.algorithms.dijkstra_radix.dijkstra_radix`.

Run from the repository root::

    py -m pytest tests/test_dijkstra_radix.py -v

Design note
-----------
When multiple shortest paths of equal cost exist, different heap
implementations may settle on different predecessor chains.  These tests
therefore always compare *distances* rather than requiring a specific
path, unless only one path exists.
"""

from __future__ import annotations

import math
import random
import unittest

from src.algorithms.dijkstra import dijkstra
from src.algorithms.dijkstra_radix import dijkstra_radix, reconstruct_path


class TestDijkstraRadixSimple(unittest.TestCase):
    """Basic shortest-path computations — mirrors test_dijkstra.py."""

    def setUp(self) -> None:
        # Classic README example (integer weights).
        self.graph = {
            "A": [("B", 4), ("C", 1)],
            "B": [("D", 1)],
            "C": [("B", 2), ("D", 5)],
            "D": [],
        }

    def test_distances(self) -> None:
        result = dijkstra_radix(self.graph, "A")
        self.assertEqual(result.distances["A"], 0)
        self.assertEqual(result.distances["B"], 3)
        self.assertEqual(result.distances["C"], 1)
        self.assertEqual(result.distances["D"], 4)

    def test_path_reconstruction(self) -> None:
        result = dijkstra_radix(self.graph, "A")
        path = reconstruct_path(result, "D")
        # Exactly one shortest path exists: A -> C -> B -> D.
        self.assertEqual(path, ["A", "C", "B", "D"])

    def test_source_to_source(self) -> None:
        result = dijkstra_radix(self.graph, "A")
        self.assertEqual(result.distances["A"], 0)
        self.assertEqual(reconstruct_path(result, "A"), ["A"])


class TestDijkstraRadixAgreement(unittest.TestCase):
    """dijkstra_radix() must produce identical distances to dijkstra()."""

    def _assert_same_distances(self, graph: dict, source: object) -> None:
        ref = dijkstra(graph, source)
        got = dijkstra_radix(graph, source)
        self.assertEqual(ref.distances, got.distances)

    def test_readme_example(self) -> None:
        graph = {
            "A": [("B", 4), ("C", 1)],
            "B": [("D", 1)],
            "C": [("B", 2), ("D", 5)],
            "D": [],
        }
        self._assert_same_distances(graph, "A")

    def test_competing_paths(self) -> None:
        graph = {
            "S": [("A", 2), ("B", 5)],
            "A": [("B", 1), ("C", 7)],
            "B": [("C", 3)],
            "C": [],
        }
        self._assert_same_distances(graph, "S")

    def test_single_vertex(self) -> None:
        graph = {"X": []}
        self._assert_same_distances(graph, "X")

    def test_neighbor_only_vertex(self) -> None:
        # "Z" appears only as a neighbor, has no key in the dict.
        graph = {"A": [("B", 2), ("Z", 10)], "B": [("Z", 3)]}
        self._assert_same_distances(graph, "A")

    def test_randomized(self) -> None:
        """Random integer-weight graphs must produce identical distances."""
        rng = random.Random(2025)
        for _ in range(20):
            n = rng.randint(3, 10)
            vertices = list(range(n))
            graph: dict = {v: [] for v in vertices}
            # Randomly add edges (no duplicates, integer weights 1-50).
            for u in vertices:
                for v in vertices:
                    if u != v and rng.random() < 0.4 and not any(nb == v for nb, _ in graph[u]):
                        graph[u].append((v, rng.randint(1, 50)))
            for source in vertices:
                self._assert_same_distances(graph, source)


class TestDijkstraRadixZeroWeights(unittest.TestCase):
    """Graphs with zero-weight edges."""

    def test_zero_weight_edges(self) -> None:
        graph = {
            "A": [("B", 0), ("C", 3)],
            "B": [("C", 0)],
            "C": [],
        }
        result = dijkstra_radix(graph, "A")
        self.assertEqual(result.distances["B"], 0)
        self.assertEqual(result.distances["C"], 0)

    def test_all_zero_weights(self) -> None:
        graph = {0: [(1, 0), (2, 0)], 1: [(3, 0)], 2: [(3, 0)], 3: []}
        result = dijkstra_radix(graph, 0)
        self.assertEqual(result.distances[3], 0)


class TestDijkstraRadixDisconnected(unittest.TestCase):
    """Unreachable vertices must receive distance infinity."""

    def test_unreachable_vertex(self) -> None:
        graph = {"A": [("B", 1)], "B": [], "C": []}  # C is isolated
        result = dijkstra_radix(graph, "A")
        self.assertTrue(math.isinf(result.distances["C"]))

    def test_unreachable_path_is_none(self) -> None:
        graph = {"A": [("B", 1)], "B": [], "C": []}
        result = dijkstra_radix(graph, "A")
        self.assertIsNone(reconstruct_path(result, "C"))

    def test_unknown_target_path_is_none(self) -> None:
        graph = {"A": []}
        result = dijkstra_radix(graph, "A")
        self.assertIsNone(reconstruct_path(result, "Z"))


class TestDijkstraRadixEqualCost(unittest.TestCase):
    """Multiple shortest paths — compare distances, not specific paths."""

    def test_equal_cost_paths_distance(self) -> None:
        graph = {
            "A": [("B", 1), ("C", 1)],
            "B": [("D", 1)],
            "C": [("D", 1)],
            "D": [],
        }
        result = dijkstra_radix(graph, "A")
        self.assertEqual(result.distances["D"], 2)
        # Either A->B->D or A->C->D is valid.
        path = reconstruct_path(result, "D")
        self.assertIn(path, [["A", "B", "D"], ["A", "C", "D"]])


class TestDijkstraRadixLargeWeights(unittest.TestCase):
    """Python integers can be arbitrarily large."""

    def test_large_integer_weights(self) -> None:
        big = 10**15
        graph = {0: [(1, big), (2, 1)], 1: [(3, 1)], 2: [(3, big)], 3: []}
        result = dijkstra_radix(graph, 0)
        # 0->2->3 costs 1 + big, 0->1->3 costs big + 1 — same.
        # 0->2 costs 1 which is clearly the shortest to vertex 2.
        self.assertEqual(result.distances[2], 1)
        self.assertEqual(result.distances[1], big)


class TestDijkstraRadixStaleEntries(unittest.TestCase):
    """Stale (superseded) queue entries must be silently ignored."""

    def test_many_relaxations_same_vertex(self) -> None:
        # Each edge relaxation to "C" inserts a new entry.
        # Only the shortest should matter.
        graph = {
            "A": [("B", 1), ("C", 100)],
            "B": [("C", 1)],
            "C": [],
        }
        result = dijkstra_radix(graph, "A")
        self.assertEqual(result.distances["C"], 2)  # A->B->C, not A->C


class TestDijkstraRadixValidation(unittest.TestCase):
    """Invalid inputs must be rejected with informative errors."""

    def test_unknown_source_raises(self) -> None:
        graph = {"A": [("B", 1)], "B": []}
        with self.assertRaises(ValueError):
            dijkstra_radix(graph, "Z")

    def test_negative_weight_raises(self) -> None:
        graph = {"A": [("B", -1)], "B": []}
        with self.assertRaises(ValueError):
            dijkstra_radix(graph, "A")

    def test_float_weight_raises(self) -> None:
        graph = {"A": [("B", 1.5)], "B": []}
        with self.assertRaises(TypeError):
            dijkstra_radix(graph, "A")

    def test_float_whole_number_raises(self) -> None:
        """Even 2.0 (a whole-number float) must be rejected."""
        graph = {"A": [("B", 2.0)], "B": []}
        with self.assertRaises(TypeError):
            dijkstra_radix(graph, "A")

    def test_malformed_edge_raises(self) -> None:
        graph: dict = {"A": [("B",)]}  # type: ignore[list-item]
        with self.assertRaises(ValueError):
            dijkstra_radix(graph, "A")

    def test_string_weight_raises(self) -> None:
        graph: dict = {"A": [("B", "fast")]}  # type: ignore[list-item]
        with self.assertRaises(ValueError):
            dijkstra_radix(graph, "A")

    def test_graph_must_be_dict(self) -> None:
        with self.assertRaises(ValueError):
            dijkstra_radix([], "A")  # type: ignore[arg-type]


class TestDijkstraRadixResult(unittest.TestCase):
    """DijkstraResult dataclass must be identical to that from dijkstra()."""

    def test_result_type_is_dijkstra_result(self) -> None:
        from src.algorithms.dijkstra import DijkstraResult

        graph = {"A": [("B", 1)], "B": []}
        result = dijkstra_radix(graph, "A")
        self.assertIsInstance(result, DijkstraResult)

    def test_result_is_frozen(self) -> None:
        graph = {"A": []}
        result = dijkstra_radix(graph, "A")
        with self.assertRaises(AttributeError):
            result.source = "X"  # type: ignore[misc]

    def test_predecessor_of_source_is_none(self) -> None:
        graph = {"A": [("B", 3)], "B": []}
        result = dijkstra_radix(graph, "A")
        self.assertIsNone(result.predecessors["A"])


if __name__ == "__main__":
    unittest.main()
