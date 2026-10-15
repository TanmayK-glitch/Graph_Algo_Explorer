
"""Common weighted graph representation for Dijkstra, Bellman-Ford and Kruskal.

This module models a *simple* graph: no self-loops or parallel edges.
Vertex labels may be any hashable Python object. Edge weights may be finite
ints or floats, including zero and negative values. Individual algorithms
have their own additional restrictions (e.g., Dijkstra rejects negatives).
"""

from __future__ import annotations

import math
from collections.abc import Hashable, Iterable, Mapping

Vertex = Hashable
Weight = int | float
Edge = tuple[Vertex, Vertex, Weight]


class Graph:
    def __init__(self, directed: bool = False) -> None:
        if not isinstance(directed, bool):
            raise ValueError("directed must be True or False")
        self.directed = directed
        # Internal representation: vertex -> {neighbor: weight}.
        self._adj: dict[Vertex, dict[Vertex, Weight]] = {}

    @staticmethod
    def _check_vertex(vertex: Vertex) -> None:
        try:
            hash(vertex)
        except TypeError as exc:
            raise ValueError("Vertex labels must be hashable") from exc

    @staticmethod
    def _check_weight(weight: Weight) -> None:
        if isinstance(weight, bool) or not isinstance(weight, (int, float)):
            raise ValueError("Edge weight must be a number (not bool)")
        if isinstance(weight, float) and not math.isfinite(weight):
            raise ValueError("Edge weight must be finite")

    def add_vertex(self, vertex: Vertex) -> None:
        """Add an isolated vertex if it does not exist yet."""
        self._check_vertex(vertex)
        self._adj.setdefault(vertex, {})

    def add_edge(self, source: Vertex, target: Vertex, weight: Weight) -> None:
        """Add one edge; an undirected graph also stores the reverse edge."""
        self._check_vertex(source)
        self._check_vertex(target)
        self._check_weight(weight)
        if source == target:
            raise ValueError("Self-loops are not supported")
        if target in self._adj.get(source, {}):
            raise ValueError(f"Duplicate edge: {source!r} -> {target!r}")

        self.add_vertex(source)
        self.add_vertex(target)
        self._adj[source][target] = weight
        if not self.directed:
            self._adj[target][source] = weight

    @property
    def vertices(self) -> list[Vertex]:
        """Vertex labels in insertion order (used for matrix/ID mapping)."""
        return list(self._adj)

    @property
    def num_vertices(self) -> int:
        return len(self._adj)

    @property
    def num_edges(self) -> int:
        """Count undirected edges once, not twice."""
        total = sum(len(neighbors) for neighbors in self._adj.values())
        return total if self.directed else total // 2

    @property
    def density(self) -> float:
        """Graph density for a simple directed or undirected graph."""
        n = self.num_vertices
        if n < 2:
            return 0.0
        max_edges = n * (n - 1) if self.directed else n * (n - 1) // 2
        return self.num_edges / max_edges

    def to_adjacency_list(self) -> dict[Vertex, list[tuple[Vertex, Weight]]]:
        """Format expected by the existing Dijkstra and Bellman-Ford code."""
        return {u: list(neighbors.items()) for u, neighbors in self._adj.items()}

    def to_adjacency_matrix(self) -> tuple[list[Vertex], list[list[Weight | float]]]:
        """Return (vertex_order, matrix); infinity means 'no edge'.

        Diagonal entries are zero. Off-diagonal zero-weight edges remain 0.
        """
        order = self.vertices
        index = {vertex: i for i, vertex in enumerate(order)}
        n = len(order)
        matrix: list[list[Weight | float]] = [
            [math.inf] * n for _ in range(n)
        ]
        for i in range(n):
            matrix[i][i] = 0
        for source, neighbors in self._adj.items():
            for target, weight in neighbors.items():
                matrix[index[source]][index[target]] = weight
        return order, matrix

    def to_edge_list(self) -> list[Edge]:
        """Return (source, target, weight) edges, without double-counting."""
        index = {vertex: i for i, vertex in enumerate(self._adj)}
        edges: list[Edge] = []
        for source, neighbors in self._adj.items():
            for target, weight in neighbors.items():
                if self.directed or index[source] < index[target]:
                    edges.append((source, target, weight))
        return edges

    def to_kruskal_input(self) -> tuple[int, list[tuple[int, int, Weight]], list[Vertex]]:
        """Return (vertex_count, indexed_edges, labels) for kruskal_mst().

        After Kruskal returns (u, v, weight) with integer IDs, decode the
        original labels using labels[u] and labels[v].
        """
        if self.directed:
            raise ValueError("Kruskal requires an undirected graph")
        labels = self.vertices
        index = {vertex: i for i, vertex in enumerate(labels)}
        indexed_edges = [
            (index[u], index[v], weight) for u, v, weight in self.to_edge_list()
        ]
        return len(labels), indexed_edges, labels

    @classmethod
    def from_edge_list(
        cls,
        edges: Iterable[tuple[Vertex, Vertex, Weight]],
        directed: bool = False,
        vertices: Iterable[Vertex] = (),
    ) -> Graph:
        """Build a graph from edges; 'vertices' preserves isolated vertices."""
        graph = cls(directed=directed)
        for vertex in vertices:
            graph.add_vertex(vertex)
        for edge in edges:
            if not isinstance(edge, (tuple, list)) or len(edge) != 3:
                raise ValueError("Each edge must be (source, target, weight)")
            graph.add_edge(*edge)
        return graph

    @classmethod
    def from_adjacency_list(
        cls,
        adjacency: Mapping[Vertex, list[tuple[Vertex, Weight]]],
        directed: bool = False,
    ) -> Graph:
        """Build from an adjacency list; merge matching reverse edges."""
        if not isinstance(adjacency, Mapping):
            raise ValueError("Adjacency list must map vertices to neighbors")
        graph = cls(directed=directed)
        for vertex in adjacency:
            graph.add_vertex(vertex)
        seen_arcs: set[tuple[Vertex, Vertex]] = set()
        for source, neighbors in adjacency.items():
            if not isinstance(neighbors, list):
                raise ValueError("Each vertex's neighbors must be a list")
            for entry in neighbors:
                if not isinstance(entry, (tuple, list)) or len(entry) != 2:
                    raise ValueError("Each neighbor must be (target, weight)")
                target, weight = entry
                graph._check_vertex(target)
                graph._check_weight(weight)
                arc = (source, target)
                if arc in seen_arcs:
                    raise ValueError(f"Duplicate adjacency entry: {arc!r}")
                seen_arcs.add(arc)
                if not directed and target in graph._adj.get(source, {}):
                    if graph._adj[source][target] != weight:
                        raise ValueError("Reverse undirected edges have different weights")
                    continue
                graph.add_edge(source, target, weight)
        return graph

    @classmethod
    def from_adjacency_matrix(
        cls,
        vertices: Iterable[Vertex],
        matrix: list[list[Weight | float]],
        directed: bool = False,
    ) -> Graph:
        """Build from a matrix using infinity for absent edges.

        The vertex labels determine the row/column order. Zero off-diagonal
        entries are treated as real zero-weight edges, not missing edges.
        """
        labels = list(vertices)
        graph = cls(directed=directed)
        for vertex in labels:
            graph.add_vertex(vertex)
        if graph.num_vertices != len(labels):
            raise ValueError("Vertex labels must be unique")

        n = len(labels)
        if len(matrix) != n or any(len(row) != n for row in matrix):
            raise ValueError("Adjacency matrix must be square and match vertices")

        for i in range(n):
            for j in range(n):
                value = matrix[i][j]
                if value != math.inf:
                    graph._check_weight(value)
                if i == j and value != 0:
                    raise ValueError("Matrix diagonal must contain zeros")
                if not directed and value != matrix[j][i]:
                    raise ValueError("Undirected adjacency matrix must be symmetric")

        for i in range(n):
            for j in range(n):
                if i != j and matrix[i][j] != math.inf:
                    if directed or i < j:
                        graph.add_edge(labels[i], labels[j], matrix[i][j])
        return graph
