# Graph Algorithms Explorer — Worklet 2

A modular Python mini-project implementing and integrating graph algorithms for shortest paths and minimum spanning trees. Worklet 2 brings the individual algorithm modules together through a shared weighted-graph model and an integration API, with tests and reproducible benchmark scripts.

## Worklet 2 scope

- **Dijkstra's algorithm** with a custom binary Min Heap for shortest paths with non-negative edge weights.
- **Bellman–Ford** for shortest paths with negative edge weights and detection of reachable negative-weight cycles.
- **Kruskal's algorithm** for a minimum spanning tree (MST), supported by **Disjoint Set Union (Union-Find)**.
- A common `Graph` model, adapters, standardized results, input validation, tests, and benchmark tooling.
- Conversion of the shared graph model to adjacency-list, adjacency-matrix, and edge-list representations.

## Architecture

```text
Graph_Algo_Explorer/
├── src/
│   └── algorithms/
│       ├── min_heap.py       # Binary min-heap
│       ├── dijkstra.py       # Dijkstra + path reconstruction
│       ├── bellman_ford.py   # Bellman–Ford + negative-cycle detection
│       ├── dsu.py            # Disjoint Set Union / Union-Find
│       └── kruskal.py        # Kruskal MST
├── graph_integration/
│   ├── graph.py              # Shared weighted Graph model and conversions
│   ├── integration.py        # Adapters and standardized result objects
│   └── benchmark.py          # Algorithm and representation benchmarks
├── tests/
│   ├── test_min_heap.py
│   ├── test_dijkstra.py
│   ├── test_bellman_ford.py
│   ├── test_dsu.py
│   ├── test_kruskal.py
│   ├── test_graph.py
│   ├── test_integration.py
│   ├── test_benchmark.py
│   └── test_reference_verification.py
└── pyproject.toml
```

## Algorithms and complexity

| Component | Purpose | Time complexity |
|---|---|---|
| Min Heap | Priority queue used by Dijkstra | Insert/extract: O(log n); peek: O(1) |
| Dijkstra | Single-source shortest paths with non-negative weights | O((V + E) log V) |
| Bellman–Ford | Single-source shortest paths; supports negative edges | O(VE) |
| Disjoint Set Union | Tracks connected components during MST construction | Find/union: O(α(V)) amortized |
| Kruskal | Minimum spanning tree for a connected, undirected graph | O(E log E) |

`V` denotes vertices, `E` edges, and `α` the inverse Ackermann function. Actual performance depends on graph structure and implementation details.

## Shared graph model and integration

`graph_integration.graph.Graph` provides a common weighted graph representation. It supports directed or undirected graphs, hashable vertex labels, finite numeric weights, isolated vertices, and conversions to:

- **Adjacency list** — stores each vertex's neighbors and weights.
- **Adjacency matrix** — a `V × V` matrix; infinity represents a missing edge, while zero-weight edges remain valid.
- **Edge list** — a list of `(source, target, weight)` edges.

The current graph model rejects self-loops and duplicate edges. Dijkstra rejects negative weights. Bellman–Ford permits negative weights but raises an error when a negative-weight cycle is reachable from the selected source. Kruskal requires a connected, undirected graph to produce an MST.

`graph_integration.integration` exposes:

- `run_dijkstra(graph, source)`
- `run_bellman_ford(graph, source)`
- `run_kruskal(graph)`

The shortest-path wrappers return a `ShortestPathResult` containing the algorithm name, source, distances, predecessors, and `path_to(target)` helper. Unreachable vertices have distance `math.inf`, and `path_to` returns `None` for an unreachable target. Kruskal returns an `MSTResult` with selected edges and total weight, retaining the graph's original vertex labels.

## Quick start

Run commands from the repository root.

```python
from graph_integration.graph import Graph
from graph_integration.integration import (
    run_dijkstra,
    run_bellman_ford,
    run_kruskal,
)

# Non-negative weighted graph for shortest paths and MST
graph = Graph(directed=False)
graph.add_edge("A", "B", 4)
graph.add_edge("A", "C", 1)
graph.add_edge("C", "B", 2)
graph.add_edge("B", "D", 1)
graph.add_edge("C", "D", 5)

shortest_paths = run_dijkstra(graph, "A")
print(shortest_paths.distances)
print(shortest_paths.path_to("D"))

mst = run_kruskal(graph)
print(mst.edges)
print(mst.total_weight)
```

For Bellman–Ford with negative edges, create a directed graph that has no reachable negative-weight cycle:

```python
from graph_integration.graph import Graph
from graph_integration.integration import run_bellman_ford

graph = Graph(directed=True)
graph.add_edge("A", "B", 4)
graph.add_edge("A", "C", 5)
graph.add_edge("B", "C", -2)
graph.add_edge("C", "D", 3)

result = run_bellman_ford(graph, "A")
print(result.distances)
print(result.path_to("D"))
```

## Testing and code quality

Run the complete test suite:

```powershell
py -m pytest tests/ -v
```

Run Ruff formatting and lint checks:

```powershell
py -m ruff format --check .
py -m ruff check .
```

The latest recorded validation completed successfully: **88 tests passed, with 11 subtests**; Ruff formatting and lint checks also passed. The reference-verification tests compare Dijkstra and Bellman–Ford distances with an independent Floyd–Warshall implementation on selected small graphs. The test suite provides correctness evidence for its covered cases; it should not be interpreted as exhaustive proof for all possible inputs.

## Benchmarking

The benchmark script measures the algorithm wrappers and the cost of converting the shared graph into different representations.

Example command:

```powershell
py -m graph_integration.benchmark --sizes 10 50 100 500 1000 --densities 0.05 0.2 --repeats 10 --output benchmark_final
```

The output directory contains:

- `algorithms.csv` — timing summaries for Dijkstra, Bellman–Ford, and Kruskal.
- `representations.csv` — timing summaries for graph-to-representation conversions.

The algorithm timings include the integration/input-adaptation cost but exclude graph generation. The representation timings measure **conversion only**; they do not represent running the shortest-path algorithms natively on an adjacency matrix.

### Recorded benchmark snapshot

On the recorded run with 1,000 vertices and 10 repetitions:

| Algorithm | Edges | Mean execution time |
|---|---:|---:|
| Dijkstra | 24,975 | 19.92 ms |
| Bellman–Ford | 24,975 | 27.78 ms |
| Kruskal | 24,975 | 10.80 ms |
| Dijkstra | 99,900 | 132.97 ms |
| Bellman–Ford | 99,900 | 271.16 ms |
| Kruskal | 99,900 | 81.27 ms |

For the same run, graph-to-representation conversion at 1,000 vertices produced these mean timings:

| Representation | Edges: 24,975 | Edges: 99,900 |
|---|---:|---:|
| Adjacency list | 2.74 ms | 28.59 ms |
| Adjacency matrix | 9.88 ms | 32.75 ms |
| Edge list | 4.20 ms | 32.94 ms |

These figures describe one benchmark run and machine/environment, not universal performance guarantees. The generated benchmark graphs are connected, undirected, and have positive weights; a spanning tree is added, so actual density can be higher than a requested density when needed to ensure connectivity.

## Representation trade-offs

| Representation | Typical space | Strength | Trade-off |
|---|---|---|---|
| Adjacency list | O(V + E) | Efficient storage and neighbor traversal for sparse graphs | Checking a particular edge can require searching a neighbor list |
| Adjacency matrix | O(V²) | Edge lookup in O(1) | Higher memory use; scanning neighbors takes O(V) |
| Edge list | O(V + E) | Convenient for processing or sorting edges, as in Kruskal | Finding all neighbors of one vertex is less direct |

The benchmark currently compares the cost of producing these representations from the shared graph object. It does not implement or benchmark a separate matrix-native Dijkstra or Bellman–Ford algorithm.

## Limitations and assumptions

- The shared graph model represents a simple graph: self-loops and parallel edges are not supported.
- Dijkstra requires non-negative edge weights.
- Bellman–Ford reports a reachable negative-weight cycle as a `ValueError`; shortest-path distances are not returned for that case.
- Kruskal produces an MST only for a connected, undirected graph.
- Benchmark results depend on the environment, graph size, and density.
- Reference verification covers selected small shortest-path cases; MST correctness is covered by the Kruskal and integration unit tests rather than the Floyd–Warshall reference test.

## Worklet 2 completion summary

The integrated project combines the three requested graph-algorithm workflows with a shared graph abstraction, representation adapters, standardized outputs, automated tests, and benchmark CSV generation. The repository's latest recorded checks passed: 88 tests plus 11 subtests, Ruff formatting check, and Ruff lint check.
