"""Adjacency-list representation: ``dict`` mapping each vertex to its outgoing edges."""

from __future__ import annotations

from bisect import insort
from typing import Any

from .base import Edge, Graph
from .exceptions import EdgeAlreadyExistsError, EdgeNotFoundError, VertexNotFoundError


class AdjacencyListGraph(Graph):
    """Dict-of-lists graph.  O(V+E) space, O(degree) neighbour access.

    Each adjacency list is kept ordered by the creation order of the neighbour
    (decision D-23) so that results equal those of the matrix representation.
    """

    def __init__(self, directed: bool = False, weighted: bool = False) -> None:
        """Create an empty graph (see :class:`Graph`)."""
        super().__init__(directed, weighted)
        # Core structure: vertex -> list of OUTGOING Edge objects.
        # Undirected edges are stored twice (u->v in u's list, v->u in v's list).
        self._adj: dict[Any, list[Edge]] = {}
        # rank = creation order of each vertex. Adjacency lists are kept sorted by the rank of
        # the neighbour, so neighbours() order is the same as in the matrix (decision D-23).
        self._rank: dict[Any, int] = {}
        self._next_rank = 0

    def _require(self, v: Any) -> None:
        if v not in self._adj:
            raise VertexNotFoundError(v)

    def _insert(self, u: Any, edge: Edge) -> None:
        # insort = binary-search insert; keeps u's list ordered by neighbour creation rank.
        insort(self._adj[u], edge, key=lambda e: self._rank[e.dst])

    @property
    def vertices(self) -> list:
        """All vertices in creation order."""
        return list(self._adj)

    def add_vertex(self, v: Any) -> None:
        """Add vertex *v* (no-op if present).  O(1)."""
        self.validate_vertex_id(v)
        if v not in self._adj:
            self._adj[v] = []
            self._rank[v] = self._next_rank
            self._next_rank += 1

    def remove_vertex(self, v: Any) -> None:
        """Remove *v* and all incident edges.  O(V+E)."""
        self._require(v)
        del self._adj[v]  # drops v's outgoing edges (and a self-loop on v)
        del self._rank[v]
        # Every other vertex may have an edge INTO v (always true for undirected graphs,
        # possible for directed ones), so filter those out as well: O(V + E) in total.
        for u, edges in self._adj.items():
            self._adj[u] = [e for e in edges if e.dst != v]

    def add_edge(self, u: Any, v: Any, weight: float | None = None) -> None:
        """Add edge ``u -> v``.  O(degree(u)) because of the duplicate check."""
        self.validate_vertex_id(u)
        self.validate_vertex_id(v)
        # 1) Validate EVERYTHING first, so a failed call leaves the graph unchanged.
        value = self._normalise_weight(weight)
        if u in self._adj and v in self._adj and self.has_edge(u, v):
            raise EdgeAlreadyExistsError(u, v)  # parallel edges are not allowed
        # 2) Only now change state: create missing endpoints, then insert the edge.
        self.add_vertex(u)
        self.add_vertex(v)
        self._insert(u, Edge(u, v, value))
        # Undirected: also store the reverse edge. A self-loop (u == v) is stored only once,
        # otherwise it would appear twice in neighbours().
        if not self._directed and u != v:
            self._insert(v, Edge(v, u, value))

    def remove_edge(self, u: Any, v: Any) -> None:
        """Remove edge ``u -> v`` (both directions if undirected)."""
        self._require(u)
        self._require(v)
        if not self.has_edge(u, v):
            raise EdgeNotFoundError(u, v)
        self._adj[u] = [e for e in self._adj[u] if e.dst != v]
        if not self._directed and u != v:
            self._adj[v] = [e for e in self._adj[v] if e.dst != u]

    def has_edge(self, u: Any, v: Any) -> bool:
        """Whether ``u -> v`` exists.  O(degree(u))."""
        self._require(u)
        self._require(v)
        return any(e.dst == v for e in self._adj[u])

    def neighbours(self, v: Any) -> list:
        """Adjacent vertex identifiers.  O(degree(v))."""
        self._require(v)
        return [e.dst for e in self._adj[v]]

    def all_edges(self) -> list:
        """Edge copies; each undirected edge once, lower-creation-order endpoint first."""
        out: list[Edge] = []
        for u, edges in self._adj.items():
            for e in edges:
                # Undirected edges are stored twice; report only the copy that starts at the
                # earlier-created vertex so each edge appears exactly once. Copies are returned
                # so callers cannot corrupt the graph by editing them.
                if self._directed or self._rank[u] <= self._rank[e.dst]:
                    out.append(Edge(e.src, e.dst, e.weight))
        return out

    def vertex_count(self) -> int:
        """Number of vertices."""
        return len(self._adj)

    def edge_count(self) -> int:
        """Number of edges (undirected edge and self-loop each count once)."""
        total = sum(len(edges) for edges in self._adj.values())
        if self._directed:
            return total
        # Undirected: every normal edge is stored twice, every self-loop once,
        # so edges = (total + loops) / 2.
        loops = sum(1 for u, edges in self._adj.items() for e in edges if e.dst == u)
        return (total + loops) // 2

    def edge_weight(self, u: Any, v: Any) -> float | None:
        """PROPOSED: weight of ``u -> v`` or ``None``.  O(degree(u)) in this representation."""
        self._require(u)
        self._require(v)
        for e in self._adj[u]:
            if e.dst == v:
                return e.weight
        return None
