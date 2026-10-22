# Graph Algorithms Explorer — Dijkstra & Min Heap

This branch, `shreyas-dijkstra-minheap`, implements **Dijkstra's shortest-path algorithm using a custom binary Min Heap**. The implementation is designed as a reusable module and is connected to the team's shared graph model through the integration layer.

## Contribution

- Implemented a reusable binary `MinHeap`.
- Implemented Dijkstra's single-source shortest-path algorithm.
- Added shortest-path reconstruction.
- Added input validation, including rejection of negative edge weights.
- Added unit tests for the heap and Dijkstra.
- Added reference-based shortest-path verification against Floyd–Warshall for small test graphs.
- Ran formatting, linting, and the complete test suite.

## Files

```text
src/algorithms/
├── min_heap.py
└── dijkstra.py

tests/
├── test_min_heap.py
├── test_dijkstra.py
└── test_reference_verification.py
```

The integrated project also contains `graph_integration/`, which adapts the shared `Graph` class to the algorithms without changing the standalone algorithm APIs.

## Min Heap

`MinHeap` stores `(priority, item)` entries. The smallest priority is removed first.

```python
from src.algorithms.min_heap import MinHeap

heap = MinHeap()
heap.insert(5, "task-low")
heap.insert(1, "task-high")
heap.insert(3, "task-mid")

print(heap.peek_min())    # (1, 'task-high')
print(heap.extract_min()) # (1, 'task-high')
```

A monotonically increasing insertion counter breaks ties between equal priorities, so heap items do not need to be mutually comparable.

| Operation | Time complexity |
|---|---:|
| `insert` | O(log n) |
| `extract_min` | O(log n) |
| `peek_min` | O(1) |
| `is_empty`, `size`, `len` | O(1) |

## Dijkstra's Algorithm

Dijkstra computes shortest distances from one source in a weighted graph with **non-negative edge weights**. It uses the Min Heap to repeatedly select the currently closest candidate vertex. Negative edge weights are rejected.

### Standalone usage

The standalone function accepts an adjacency list: a dictionary mapping each vertex to a list of `(neighbor, weight)` pairs.

```python
from src.algorithms.dijkstra import dijkstra, reconstruct_path

graph = {
    "A": [("B", 4), ("C", 1)],
    "B": [("D", 1)],
    "C": [("B", 2), ("D", 5)],
    "D": [],
}

result = dijkstra(graph, "A")
print(result.distances)
print(reconstruct_path(result, "D"))
```

`result.distances` contains shortest distances; unreachable vertices have distance `math.inf`. `result.predecessors` records predecessor vertices for path reconstruction. `reconstruct_path` returns a list from source to target, or `None` when the target is unreachable.

### Complexity

For an adjacency-list graph using a binary Min Heap:

- **Time:** O((V + E) log V)
- **Space:** O(V + E)

Here, `V` is the number of vertices and `E` is the number of edges.

## Run through the integrated project API

From the repository root:

```python
from graph_integration.graph import Graph
from graph_integration.integration import run_dijkstra

graph = Graph(directed=False)
graph.add_edge("A", "B", 4)
graph.add_edge("A", "C", 1)
graph.add_edge("C", "B", 2)
graph.add_edge("B", "D", 1)

result = run_dijkstra(graph, "A")
print(result.distances)
print(result.path_to("D"))
```

The integration API returns a standardized `ShortestPathResult` while preserving the graph's original vertex labels.

## Validation

Run the tests from the repository root:

```powershell
py -m pytest tests/ -v
```

Formatting and lint checks:

```powershell
py -m ruff format --check .
py -m ruff check .
```

At the latest recorded validation, the complete test suite passed: **88 tests passed, with 11 subtests**, and Ruff formatting and lint checks passed. Reference verification compares Dijkstra and Bellman–Ford distances with an independent Floyd–Warshall implementation on selected small graphs; this is additional test evidence, not an exhaustive proof for every possible graph.

## Branch scope

This README describes the contribution on `shreyas-dijkstra-minheap`. The full Worklet 2 integration—including Bellman–Ford, Kruskal, the shared graph model, adapters, and benchmarking—is documented in the integrated `main` branch README.
