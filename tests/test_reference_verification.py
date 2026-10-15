"""Verify shortest-path algorithms against an independent reference."""

import math
import unittest

from graph_integration.graph import Graph
from graph_integration.integration import run_bellman_ford, run_dijkstra


def floyd_warshall(vertices, edges):
    """Calculate all-pairs shortest distances independently."""
    infinity = math.inf
    distances = {
        u: {v: (0 if u == v else infinity) for v in vertices} for u in vertices
    }

    for u, v, weight in edges:
        distances[u][v] = min(distances[u][v], weight)
        distances[v][u] = min(distances[v][u], weight)

    for k in vertices:
        for i in vertices:
            for j in vertices:
                if distances[i][k] != infinity and distances[k][j] != infinity:
                    distances[i][j] = min(
                        distances[i][j],
                        distances[i][k] + distances[k][j],
                    )

    return distances


class TestReferenceVerification(unittest.TestCase):
    def test_dijkstra_against_floyd_warshall(self):
        """Compare Dijkstra with reference distances on small graphs."""
        graph_cases = [
            (
                [0, 1, 2],
                [(0, 1, 4), (0, 2, 2), (2, 1, 1)],
            ),
            (
                [0, 1, 2, 3],
                [(0, 1, 5), (0, 2, 1), (2, 1, 1), (1, 3, 2)],
            ),
            (
                [0, 1, 2, 3],
                [(0, 1, 0), (1, 2, 3), (0, 2, 5)],
            ),
        ]

        for vertices, edges in graph_cases:
            with self.subTest(vertices=vertices, edges=edges):
                graph = Graph.from_edge_list(edges, vertices=vertices)
                reference = floyd_warshall(vertices, edges)

                for source in vertices:
                    result = run_dijkstra(graph, source)

                    for target in vertices:
                        self.assertEqual(
                            result.distances[target],
                            reference[source][target],
                            msg=f"Incorrect distance from {source} to {target}",
                        )

    def test_bellman_ford_with_negative_edges(self):
        """Check Bellman-Ford against reference distances on a DAG."""
        vertices = [0, 1, 2, 3]
        edges = [
            (0, 1, 4),
            (0, 2, 5),
            (1, 2, -2),
            (2, 3, 3),
            (1, 3, 6),
        ]

        graph = Graph.from_edge_list(edges, vertices=vertices, directed=True)
        reference = floyd_warshall_directed(vertices, edges)

        for source in vertices:
            result = run_bellman_ford(graph, source)

            for target in vertices:
                self.assertEqual(
                    result.distances[target],
                    reference[source][target],
                    msg=f"Incorrect distance from {source} to {target}",
                )


def floyd_warshall_directed(vertices, edges):
    """Calculate directed all-pairs shortest distances independently."""
    distances = {
        u: {v: (0 if u == v else math.inf) for v in vertices} for u in vertices
    }

    for u, v, weight in edges:
        distances[u][v] = min(distances[u][v], weight)

    for k in vertices:
        for i in vertices:
            for j in vertices:
                if distances[i][k] != math.inf and distances[k][j] != math.inf:
                    distances[i][j] = min(
                        distances[i][j],
                        distances[i][k] + distances[k][j],
                    )

    return distances


if __name__ == "__main__":
    unittest.main()
