"""From repo root: python -m unittest discover -s tests -p 'test_*.py' -v"""

import math
import unittest

from graph_integration.graph import Graph
from graph_integration.integration import (
    MSTResult,
    ShortestPathResult,
    run_bellman_ford,
    run_dijkstra,
    run_kruskal,
)


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.graph = Graph.from_edge_list([
            ("A", "B", 4), ("A", "C", 2),
            ("B", "C", 1), ("C", "D", 3),
        ])

    def test_dijkstra(self):
        result = run_dijkstra(self.graph, "A")
        self.assertIsInstance(result, ShortestPathResult)
        self.assertEqual(result.algorithm, "dijkstra")
        self.assertEqual(result.distances, {"A": 0, "B": 3, "C": 2, "D": 5})
        self.assertEqual(result.path_to("D"), ["A", "C", "D"])

    def test_bellman_ford(self):
        result = run_bellman_ford(self.graph, "A")
        self.assertIsInstance(result, ShortestPathResult)
        self.assertEqual(result.distances, {"A": 0, "B": 3, "C": 2, "D": 5})
        self.assertEqual(result.path_to("B"), ["A", "C", "B"])

    def test_kruskal_original_labels(self):
        result = run_kruskal(self.graph)
        self.assertIsInstance(result, MSTResult)
        self.assertEqual(result.algorithm, "kruskal")
        self.assertEqual(result.total_weight, 6)
        self.assertEqual(len(result.edges), 3)
        self.assertEqual({frozenset((u,v)) for u,v,_ in result.edges}, {
            frozenset(("A","C")), frozenset(("B","C")), frozenset(("C","D")),
        })

    def test_algorithm_execution(self):
        dijkstra_result = run_dijkstra(self.graph, "A")
        bellman_result = run_bellman_ford(self.graph, "A")
        kruskal_result = run_kruskal(self.graph)

        self.assertEqual(dijkstra_result.distances["D"], 5)
        self.assertEqual(bellman_result.distances["D"], 5)
        self.assertEqual(kruskal_result.total_weight, 6)

    def test_missing_source(self):
        with self.assertRaises(ValueError):
            run_dijkstra(self.graph, "Z")

        with self.assertRaises(ValueError):
            run_bellman_ford(self.graph, "Z")

    def test_isolated_vertex_path(self):
        graph = Graph.from_edge_list([(1,2,7)], vertices=[1,2,3])
        result = run_dijkstra(graph, 1)
        self.assertTrue(math.isinf(result.distances[3]))
        self.assertIsNone(result.path_to(3))
        self.assertIsNone(result.path_to(99))
        self.assertEqual(result.path_to(1), [1])

    def test_bellman_allows_negative_directed_edges(self):
        graph = Graph.from_edge_list([("A", "B", -2), ("B", "C", 3)], directed=True)
        self.assertEqual(run_bellman_ford(graph, "A").distances["C"], 1)
        with self.assertRaises(ValueError):
            run_dijkstra(graph, "A")

    def test_bellman_negative_cycle_detected(self):
        graph = Graph.from_edge_list([("A", "B", -2), ("B", "A", -1)], directed=True)
        with self.assertRaisesRegex(ValueError, "negative-weight cycle"):
            run_bellman_ford(graph, "A")

    def test_kruskal_rejects_directed(self):
        graph = Graph.from_edge_list([(0,1,1)], directed=True)
        with self.assertRaises(ValueError):
            run_kruskal(graph)

    def test_kruskal_rejects_disconnected(self):
        graph = Graph.from_edge_list([(0,1,1)], vertices=[0,1,2])
        with self.assertRaises(ValueError):
            run_kruskal(graph)

    def test_bad_graph_type(self):
        with self.assertRaises(TypeError):
            run_dijkstra({}, "A")
        with self.assertRaises(TypeError):
            run_kruskal({})

    def test_does_not_mutate_graph(self):
        before = self.graph.to_adjacency_list()
        run_dijkstra(self.graph, "A")
        run_bellman_ford(self.graph, "A")
        run_kruskal(self.graph)
        self.assertEqual(self.graph.to_adjacency_list(), before)


if __name__ == "__main__":
    unittest.main()
