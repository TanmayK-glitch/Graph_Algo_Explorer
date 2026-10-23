"""Benchmark unit tests; small graphs keep tests fast.

From repository root:
    python -m unittest discover -s tests -p 'test_*.py' -v
"""

import csv
import tempfile
import unittest
from pathlib import Path

from graph_integration.benchmark import (
    ALGORITHM_COLUMNS,
    REPRESENTATION_COLUMNS,
    _write_csv,
    generate_graph,
    run_benchmarks,
)
from graph_integration.integration import run_bellman_ford, run_dijkstra, run_kruskal


class TestBenchmark(unittest.TestCase):
    def test_connected_sparse_graph(self):
        graph = generate_graph(vertices=10, density=0, seed=5)
        self.assertEqual(graph.num_vertices, 10)
        self.assertEqual(graph.num_edges, 9)
        self.assertTrue(all(weight > 0 for _, _, weight in graph.to_edge_list()))
        self.assertEqual(len(run_kruskal(graph).edges), 9)

    def test_density_and_no_duplicates(self):
        graph = generate_graph(vertices=8, density=1.0, seed=5)
        self.assertEqual(graph.num_edges, 28)
        self.assertEqual(graph.density, 1.0)

    def test_deterministic(self):
        a = generate_graph(20, 0.3, seed=100)
        b = generate_graph(20, 0.3, seed=100)
        self.assertEqual(a.to_edge_list(), b.to_edge_list())

    def test_reject_invalid_graph_settings(self):
        for n, density in ((0, 0.2), (10, -1), (10, 1.1)):
            with self.subTest(n=n, density=density), self.assertRaises(ValueError):
                generate_graph(n, density)

    def test_algorithms_agree(self):
        graph = generate_graph(20, 0.3, seed=99)
        self.assertEqual(
            run_dijkstra(graph, 0).distances, run_bellman_ford(graph, 0).distances
        )

    def test_summary_has_every_configuration(self):
        algorithms, representations = run_benchmarks(
            sizes=[5, 10], densities=[0.2], repetitions=2, seed=123
        )
        self.assertEqual(len(algorithms), 2 * 3)
        self.assertEqual(len(representations), 2 * 3)
        self.assertEqual(
            {row["algorithm"] for row in algorithms},
            {"dijkstra", "bellman_ford", "kruskal"},
        )
        self.assertEqual(
            {row["graph_representation"] for row in representations},
            {"adjacency_list", "adjacency_matrix", "edge_list"},
        )
        self.assertTrue(
            all(row["execution_status"] == "OK" for row in algorithms + representations)
        )
        self.assertTrue(
            all(row["repetitions"] == 2 for row in algorithms + representations)
        )
        self.assertTrue(
            all(row["execution_time_ms"] >= 0 for row in algorithms + representations)
        )

    def test_csv_export(self):
        algorithms, representations = run_benchmarks(
            sizes=[5], densities=[0.4], repetitions=1, seed=55
        )
        with tempfile.TemporaryDirectory() as folder:
            a = Path(folder) / "algorithms.csv"
            r = Path(folder) / "representations.csv"
            _write_csv(a, ALGORITHM_COLUMNS, algorithms)
            _write_csv(r, REPRESENTATION_COLUMNS, representations)
            with a.open(newline="", encoding="utf-8") as f:
                self.assertEqual(len(list(csv.DictReader(f))), 3)
            with r.open(newline="", encoding="utf-8") as f:
                self.assertEqual(len(list(csv.DictReader(f))), 3)

    def test_generate_graph_minimum_boundaries(self):
        """Boundary value testing for n=2 at densities 0.0 and 1.0."""
        g0 = generate_graph(vertices=2, density=0.0, seed=1)
        self.assertEqual(g0.num_vertices, 2)
        self.assertEqual(g0.num_edges, 1)

        g1 = generate_graph(vertices=2, density=1.0, seed=1)
        self.assertEqual(g1.num_vertices, 2)
        self.assertEqual(g1.num_edges, 1)
        self.assertEqual(g1.density, 1.0)

    def test_run_benchmarks_minimal_size(self):
        """run_benchmarks executes cleanly with minimal n=2 and 1 repetition."""
        algorithms, representations = run_benchmarks(
            sizes=[2], densities=[0.0], repetitions=1, seed=42
        )
        self.assertEqual(len(algorithms), 3)
        self.assertEqual(len(representations), 3)
        self.assertTrue(all(row["execution_status"] == "OK" for row in algorithms))


if __name__ == "__main__":
    unittest.main()
