"""Breadth-first search (iterative, FIFO queue built on ``collections.deque``)."""

from __future__ import annotations

from collections import deque
from typing import Any

from ..graph.base import Graph
from .base import Algorithm, AlgorithmResult, require_vertex


def bfs_component(graph: Graph, start: Any, visited: set) -> tuple[list, dict]:
    """Traverse the part of the graph reachable from *start* that is not in *visited*.

    *visited* is updated in place.  Returns ``(visit_order, parent_map)``.
    Shared by BFS, BFS_ALL and connected components.
    """
    # Mark a vertex as visited when it is ENQUEUED (not when dequeued) so that it can
    # never be put in the queue twice.
    visited.add(start)
    queue: deque = deque([start])  # FIFO queue: deque gives O(1) append and popleft
    order: list = []  # the answer: vertices in the order they are dequeued
    parent: dict = {start: None}  # parent[v] = vertex we came from (forms the BFS tree)
    while queue:
        v = queue.popleft()  # oldest waiting vertex => closest to start first
        order.append(v)
        # neighbours() is the ONLY way we look at the graph, so this works unchanged
        # for the list and the matrix representation.
        for nbr in graph.neighbours(v):
            if nbr not in visited:
                visited.add(nbr)
                parent[nbr] = v  # following parents back to start gives a shortest path
                queue.append(nbr)
    return order, parent


def bfs(graph: Graph, start: Any) -> AlgorithmResult:
    """BFS over the component containing *start* (FR-11, FR-18)."""
    require_vertex(graph, start)  # clear VertexNotFoundError instead of a confusing failure later
    order, parent = bfs_component(graph, start, set())
    return AlgorithmResult("BFS", order, {"start": start, "parent": parent})


def bfs_all(graph: Graph) -> AlgorithmResult:
    """BFS restarted from every unvisited vertex, covering the whole graph (FR-18)."""
    visited: set = set()  # shared across restarts so no vertex is visited twice
    order: list = []
    for v in graph.vertices:  # vertices come in creation order => deterministic result
        if v not in visited:  # a new, not-yet-reached component starts here
            comp, _ = bfs_component(graph, v, visited)
            order.extend(comp)
    return AlgorithmResult("BFS_ALL", order, {})


class BFSAlgorithm(Algorithm):
    """Strategy wrapper: ``execute(graph, start=..., mode='single'|'all')`` (decision D-03)."""

    @property
    def name(self) -> str:
        """Algorithm name."""
        return "BFS"

    def execute(self, graph: Graph, start: Any | None = None, mode: str = "single",
                **kwargs: Any) -> AlgorithmResult:
        """Run BFS.

        ``mode='single'`` needs *start* and visits only its component;
        ``mode='all'`` ignores *start* and visits every vertex.
        """
        if mode == "all":
            return bfs_all(graph)
        if mode != "single":
            raise ValueError(f"mode must be 'single' or 'all', got {mode!r}")
        # An explicit mode means forgetting `start` is an error, not a silent full traversal.
        if start is None:
            raise ValueError("BFS in 'single' mode requires a start vertex")
        return bfs(graph, start)
