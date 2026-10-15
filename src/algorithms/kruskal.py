
"""Kruskal's Minimum Spanning Tree algorithm.

This module implements Kruskal's algorithm using the
Disjoint Set Union (DSU) data structure.

The algorithm sorts edges by weight and selects edges
that do not create a cycle.

Time complexity: O(E log E)
"""

from __future__ import annotations

from .dsu import DisjointSetUnion


def kruskal_mst(
    num_vertices: int,
    edges: list[tuple[int, int, float | int]]
) -> tuple[list[tuple[int, int, float | int]], float | int]:
    """Find the Minimum Spanning Tree of an undirected graph.

    Parameters
    ----------
    num_vertices:
        Number of vertices, numbered 0 to n-1.
    edges:
        List of edges represented as (u, v, weight).

    Returns
    -------
    mst_edges:
        List of edges selected for the MST.
    total_weight:
        Sum of the weights of selected edges.

    Raises
    ------
    ValueError
        If the graph is disconnected or has invalid vertices.
    """

    if num_vertices < 0:
        raise ValueError("Number of vertices cannot be negative")

    for u, v, weight in edges:
        if not (0 <= u < num_vertices and
                0 <= v < num_vertices):
            raise ValueError("Invalid vertex in edge")

    dsu = DisjointSetUnion(num_vertices)

    # Sort edges in increasing order of weight.
    sorted_edges = sorted(edges, key=lambda edge: edge[2])

    mst_edges = []
    total_weight = 0

    for u, v, weight in sorted_edges:

        # union() returns False if adding the edge
        # would create a cycle.
        if dsu.union(u, v):
            mst_edges.append((u, v, weight))
            total_weight += weight

        # A spanning tree has exactly V - 1 edges.
        if len(mst_edges) == num_vertices - 1:
            break

    if num_vertices > 0 and len(mst_edges) != num_vertices - 1:
        raise ValueError("Graph is disconnected. MST not possible.")

    return mst_edges, total_weight
