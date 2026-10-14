# Bellman–Ford Algorithm

## Overview

Bellman–Ford is a single-source shortest-path algorithm that computes the shortest distances from a given source vertex to all reachable vertices in a weighted, directed graph.

Unlike Dijkstra's algorithm, Bellman–Ford supports negative edge weights and can detect negative-weight cycles reachable from the source.

## Features

- Computes shortest distances from a source vertex.
- Supports positive, zero, and negative edge weights.
- Detects reachable negative-weight cycles.
- Reconstructs shortest paths using predecessor information.
- Represents unreachable vertices with infinity.
- Validates graph structure and edge weights.

## Input Format

The graph uses an adjacency-list representation:

```python
graph = {
    "A": [("B", 4), ("C", 5)],
    "B": [("C", -3)],
    "C": [],
}
```

Each vertex maps to a list of `(neighbor, weight)` pairs.

## Usage

Import the algorithm and path reconstruction function:

```python
from src.algorithms.bellman_ford import (
    bellman_ford,
    reconstruct_path,
)

graph = {
    "A": [("B", 4), ("C", 5)],
    "B": [("C", -3)],
    "C": [],
}

result = bellman_ford(graph, "A")

print(result.distances)
print(reconstruct_path(result, "C"))
```

Expected shortest distances:

- A: 0
- B: 4
- C: 1

Expected path to C:

```text
['A', 'B', 'C']
```

## How the Algorithm Works

1. Initialize the source vertex distance to zero and all other distances to infinity.
2. Relax every edge repeatedly for at most V − 1 passes.
3. Stop early if a complete pass makes no changes.
4. Check the edges again to detect reachable negative-weight cycles.
5. Return the shortest distances and predecessor information.

Here, V represents the number of vertices and E represents the number of edges.

### What Is Edge Relaxation?

For an edge from vertex `u` to vertex `v` with weight `w`, check whether:

`distance[u] + w < distance[v]`

If the condition is true, update the distance to `v` and record `u` as its predecessor.

## Negative-Weight Cycle Detection

A negative-weight cycle is a cycle whose edge weights add up to a negative value.

If an edge can still be relaxed after V − 1 passes, a negative-weight cycle is reachable from the source. The algorithm raises an exception when such a cycle is detected.

Negative-weight cycles that are unreachable from the source do not affect the result.

## Complexity Analysis

Let V be the number of vertices and E be the number of edges.

- **Time complexity:** O(VE)
- **Auxiliary space complexity:** O(V + E), if the implementation stores an additional edge list; otherwise, this depends on the data structures used.

## Limitations

- Shortest paths are not well-defined for vertices affected by a reachable negative-weight cycle.
- Negative cycles unreachable from the source are not reported.
- The algorithm computes shortest paths from one source vertex at a time.
- For graphs with only nonnegative edge weights, Dijkstra's algorithm is generally more efficient.

## Testing

Run the Bellman–Ford tests from the project root:

```bash
python3 -m tests.test_bellman_ford
```

Run the existing Dijkstra and MinHeap regression tests:

```bash
python3 -m unittest discover -s tests -v
```