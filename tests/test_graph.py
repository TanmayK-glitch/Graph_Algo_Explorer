"""Run from repo root: python -m unittest discover -s tests -p test_graph.py -v"""

import math
import unittest

from graph_integration.graph import Graph
from src.algorithms.dijkstra import dijkstra
from src.algorithms.bellman_ford import bellman_ford  # type: ignore[reportMissingImports]
from src.algorithms.kruskal import kruskal_mst  # type: ignore[reportMissingImports]


class TestGraph(unittest.TestCase):
    def setUp(self):
        self.g = Graph.from_edge_list([
            ("A", "B", 4),
            ("A", "C", 2),
            ("B", "C", 1),
            ("C", "D", 3),
        ])

    def test_adjacency_list(self):
        self.assertEqual(self.g.to_adjacency_list(), {
            "A": [("B", 4), ("C", 2)],
            "B": [("A", 4), ("C", 1)],
            "C": [("A", 2), ("B", 1), ("D", 3)],
            "D": [("C", 3)],
        })

    def test_matrix(self):
        vertices, matrix = self.g.to_adjacency_matrix()
        self.assertEqual(vertices, ["A", "B", "C", "D"])
        self.assertEqual(matrix, [
            [0, 4, 2, math.inf],
            [4, 0, 1, math.inf],
            [2, 1, 0, 3],
            [math.inf, math.inf, 3, 0],
        ])

    def test_edges_not_doubled(self):
        self.assertEqual(self.g.to_edge_list(), [
            ("A", "B", 4), ("A", "C", 2),
            ("B", "C", 1), ("C", "D", 3),
        ])
        self.assertEqual((self.g.num_vertices, self.g.num_edges), (4, 4))
        self.assertAlmostEqual(self.g.density, 4 / 6)

    def test_directed_edges(self):
        g = Graph(directed=True)
        g.add_edge("A", "B", 5)
        self.assertEqual(g.to_adjacency_list(), {"A": [("B", 5)], "B": []})
        self.assertEqual(g.num_edges, 1)
        self.assertAlmostEqual(g.density, 0.5)
        with self.assertRaises(ValueError):
            g.to_kruskal_input()

    def test_zero_weight_not_confused_with_no_edge(self):
        g = Graph()
        g.add_edge("X", "Y", 0)
        g.add_vertex("Z")
        _, matrix = g.to_adjacency_matrix()
        self.assertEqual(matrix[0][1], 0)
        self.assertEqual(matrix[0][2], math.inf)

    def test_isolated_vertex(self):
        g = Graph.from_edge_list([(1, 2, 5)], vertices=[1, 2, 3])
        self.assertEqual(g.to_adjacency_list()[3], [])
        self.assertEqual(g.num_vertices, 3)

    def test_from_adjacency_list_roundtrip(self):
        restored = Graph.from_adjacency_list(self.g.to_adjacency_list())
        self.assertEqual(restored.to_edge_list(), self.g.to_edge_list())

    def test_from_matrix_roundtrip(self):
        vertices, matrix = self.g.to_adjacency_matrix()
        restored = Graph.from_adjacency_matrix(vertices, matrix)
        self.assertEqual(restored.to_adjacency_list(), self.g.to_adjacency_list())

    def test_from_matrix_rejects_nonsymmetric(self):
        with self.assertRaises(ValueError):
            Graph.from_adjacency_matrix(["A", "B"], [[0, 2], [3, 0]])

    def test_mismatched_reverse_weight_rejected(self):
        with self.assertRaises(ValueError):
            Graph.from_adjacency_list({"A": [("B", 2)], "B": [("A", 3)]})

    def test_invalid_input_rejected(self):
        for weight in (float("nan"), float("inf"), -float("inf"), "5", True):
            with self.subTest(weight=weight), self.assertRaises(ValueError):
                Graph().add_edge("A", "B", weight)
        with self.assertRaises(ValueError):
            Graph().add_vertex([])
        with self.assertRaises(ValueError):
            Graph().add_edge("A", "A", 1)
        with self.assertRaises(ValueError):
            self.g.add_edge("B", "A", 4)
        with self.assertRaises(ValueError):
            Graph.from_edge_list([("A", "B")])

    def test_algorithm_compatibility(self):
        adjacency = self.g.to_adjacency_list()
        d = dijkstra(adjacency, "A")
        b = bellman_ford(adjacency, "A")
        expected = {"A": 0, "B": 3, "C": 2, "D": 5}
        self.assertEqual(d.distances, expected)
        self.assertEqual(b.distances, expected)

    def test_kruskal_compatibility(self):
        n, indexed_edges, labels = self.g.to_kruskal_input()
        mst, total = kruskal_mst(n, indexed_edges)
        self.assertEqual(total, 6)
        self.assertEqual(len(mst), n - 1)
        self.assertEqual({frozenset((labels[u], labels[v])) for u, v, _ in mst}, {
            frozenset(("A", "C")),
            frozenset(("B", "C")),
            frozenset(("C", "D")),
        })

    def test_negative_weight_supported_by_graph_but_not_dijkstra(self):
        g = Graph.from_edge_list([("A", "B", -2)], directed=True)
        self.assertEqual(bellman_ford(g.to_adjacency_list(), "A").distances["B"], -2)
        with self.assertRaises(ValueError):
            dijkstra(g.to_adjacency_list(), "A")


if __name__ == "__main__":
    unittest.main()
