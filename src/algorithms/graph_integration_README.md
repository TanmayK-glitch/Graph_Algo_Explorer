# Graph Integration and Benchmarking (Worklet 2)

This folder contains the **Member 4 contribution** to Graph Algorithm Explorer: a shared graph data model, adapters for the team's graph algorithms, and a reproducible benchmarking harness. The original algorithm implementations are kept in `src/algorithms/` and do not need to be modified.

## Files and responsibilities

| File | Purpose |
| --- | --- |
| `graph.py` | Build and validate weighted graphs; export adjacency lists, adjacency matrices, and edge lists; import graphs from these formats. |
| `integration.py` | Adapt the shared `Graph` to the team's Dijkstra, Bellman–Ford, and Kruskal functions and return consistent result objects. |
| `benchmark.py` | Generate connected weighted test graphs, time algorithms and representation exports, and write CSV summaries. |
| `../tests/test_graph.py` | Test representations, conversions, validation, and algorithm compatibility. |
| `../tests/test_integration.py` | Test adapter outputs and error handling. |
| `../tests/test_benchmark.py` | Test graph generation and benchmark export behavior. |

## How it works

```text
Weighted graph input
        |
    graph.py
 (shared Graph class)
        |
   integration.py
   /     |      \
Dijkstra Bellman-Ford Kruskal
   \     |      /
  Standardized results

benchmark.py -> generates graphs, runs adapters,
                times exports, writes CSVs
```

### Graph representation (`graph.py`)

- Supports directed and undirected weighted graphs, isolated vertices, and finite numeric edge weights (including zero or negative values).
- Rejects invalid labels/weights, self-loops, and duplicate edges. Undirected edges are stored in both directions internally but counted only once.
- Provides `to_adjacency_list()`, `to_adjacency_matrix()`, and `to_edge_list()`, plus `from_*` constructors.
- The matrix uses `math.inf` for absent edges and `0` on its diagonal, so zero-weight edges are unambiguous.
- `to_kruskal_input()` maps arbitrary vertex labels (e.g., `"A"`) to IDs `0..n-1` for the existing Kruskal implementation.

### Algorithm integration (`integration.py`)

- `run_dijkstra(graph, source)` and `run_bellman_ford(graph, source)` pass an adjacency list and return `ShortestPathResult` (`distances`, `predecessors`, `path_to()`).
- `run_kruskal(graph)` converts an undirected graph to an indexed edge list and returns `MSTResult` with original vertex labels and total weight.
- Dijkstra does **not** accept negative-weight edges. Bellman–Ford can accept negative edges but rejects reachable negative-weight cycles. Kruskal expects an undirected, connected graph.

## Example (run from repository root)

```python
from graph_integration.graph import Graph
from graph_integration.integration import run_dijkstra, run_bellman_ford, run_kruskal

graph = Graph.from_edge_list([
    ("A", "B", 4), ("A", "C", 2),
    ("B", "C", 1), ("C", "D", 3),
])

print(run_dijkstra(graph, "A").distances)
print(run_bellman_ford(graph, "A").path_to("D"))
print(run_kruskal(graph).total_weight)
```

Expected: shortest distances `A=0, B=3, C=2, D=5`; path from A to D is `['A', 'C', 'D']`; MST total weight is `6`.

## Tests

Run from **repository root** (Windows PowerShell):

```powershell
py -m unittest discover -s tests -p "test_*.py" -v
```

The team-run test suite reported **68 tests passing** on 15 October 2026. Run the command again after changes.

## Benchmarks

Run from **repository root**:

```powershell
py -m graph_integration.benchmark --sizes 10 50 100 500 1000 --densities 0.05 0.2 --repeats 10 --output benchmark_final
```

Outputs:

- `benchmark_final/algorithms.csv`: algorithm name, vertex/edge counts, actual and requested density, representation, repetitions, average/min/max execution time (ms), and status.
- `benchmark_final/representations.csv`: timing for exporting adjacency lists, matrices, and edge lists with the same metadata.

The benchmark uses deterministic connected **undirected** graphs with positive edge weights. It measures algorithm execution **including input adaptation**, but excludes graph generation. Each setting is repeated 10 times in the documented final run. The generated CSV files should be used as the source for reported timings.

**Limitations:**

- The algorithms are *not* implemented natively against adjacency matrices: matrix timings measure **conversion/export cost only**, not matrix-based Dijkstra or Bellman–Ford execution.
- A connected graph of 10 vertices requires at least 9 edges, so the requested density `0.05` produces actual density `0.20`; the CSV records both.
- Kruskal solves a different problem (minimum spanning tree) from the two shortest-path algorithms, so runtime differences should not be interpreted as algorithmic superiority.

## Member 4 deliverables

1. Common graph representation, graph input checks, and conversions.
2. Compatibility adapters and standardized output types for all three algorithms.
3. Benchmark generator, repeatable timing harness, and CSV reporting.
4. Unit/integration tests and results for the final Worklet 2 report.
