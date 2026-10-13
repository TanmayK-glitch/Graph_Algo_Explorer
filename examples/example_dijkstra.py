"""Example: Dijkstra's shortest path on a small weighted graph.

Run from the repository root::

    python -m examples.example_dijkstra
"""

from __future__ import annotations

from src.algorithms.dijkstra import dijkstra, reconstruct_path


def main() -> None:
    # Define a weighted directed graph as an adjacency list.
    graph = {
        "A": [("B", 4), ("C", 1)],
        "B": [("D", 1)],
        "C": [("B", 2), ("D", 5)],
        "D": [],
    }

    source = "A"
    result = dijkstra(graph, source)

    # ---- Shortest distances ----
    print(f"Shortest distances from {source!r}:")
    for vertex in sorted(result.distances):
        print(f"  {vertex}: {result.distances[vertex]}")

    # ---- Shortest path from A to D ----
    target = "D"
    path = reconstruct_path(result, target)
    if path is not None:
        print(f"\nShortest path from {source!r} to {target!r}:")
        print(f"  {' -> '.join(path)}")
        print(f"  Total distance: {result.distances[target]}")
    else:
        print(f"\n{target!r} is unreachable from {source!r}.")


if __name__ == "__main__":
    main()
