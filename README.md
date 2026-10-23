# Graph Algorithms Explorer

Graph Algorithms Explorer is a Python-based mini-project that implements graph data structures and algorithms for graph traversal, shortest paths, connectivity, cycle detection, and minimum spanning trees.

The project brings together two worklets: **Worklet 1**, which focuses on graph representations and fundamental graph algorithms, and **Worklet 2**, which focuses on weighted graph algorithms, data structures, integration, and benchmarking.

The project is currently focused on backend algorithms and integration. An interactive visualization interface is a planned next step.

## 1. Project Structure

```text
Graph_Algo_Explorer/
├── worklet1/
│   ├── algorithms/
│   ├── graph/
│   ├── io/
│   ├── tests/
│   ├── sample_graphs/
│   ├── docs/
│   └── README.md
├── src/
│   └── algorithms/
│       ├── min_heap.py
│       ├── dijkstra.py
│       ├── bellman_ford.py
│       ├── dijkstra_radix.py
│       ├── radix_heap.py
│       ├── kruskal.py
│       └── dsu.py
├── graph_integration/
│   ├── graph.py
│   ├── integration.py
│   ├── benchmark.py
│   └── worklet1_adapter.py
├── tests/
├── pyproject.toml
└── README.md
```

The structure above summarizes the main components; individual files and directories may vary as the project evolves.

## 2. Worklet 1: Graph Representations and Fundamental Algorithms

Worklet 1 provides graph data structures and algorithms for common graph operations.

### Graph representations

* Adjacency List
* Adjacency Matrix

### Algorithms

* Breadth-First Search (BFS)
* Depth-First Search (DFS)
* Connected Components
* Cycle Detection
* Topological Sort
* Strongly Connected Components (SCC)
* Bipartite Graph Checking

Worklet 1 also includes graph input utilities, sample graphs, tests, and documentation.

## 3. Worklet 2: Weighted Graph Algorithms

Worklet 2 provides algorithms and data structures for shortest-path and minimum-spanning-tree problems.

### Algorithms and data structures

* Dijkstra's shortest-path algorithm
* Custom binary Min Heap
* Bellman–Ford shortest-path algorithm
* Kruskal's Minimum Spanning Tree algorithm
* Disjoint Set Union (DSU)
* Radix Heap and Radix-based Dijkstra implementations

### Additional components

* Shared weighted graph model
* Algorithm integration wrappers
* Graph representation conversions
* Benchmarking utilities
* Unit and reference-verification tests

Dijkstra requires non-negative edge weights. Bellman–Ford supports negative edge weights and can detect negative-weight cycles. Kruskal operates on weighted, undirected graphs to compute a minimum spanning tree or forest.

## 4. Integration Between the Worklets

Worklet 1 and Worklet 2 use different graph representations. The integration layer allows supported graph inputs to be passed to the existing weighted graph algorithms without rewriting their implementations.

### Worklet 2 shared graph model

`graph_integration/graph.py` defines the shared graph representation used by Worklet 2.

### Integration wrappers

`graph_integration/integration.py` provides wrappers for:

* `run_dijkstra(graph, source)`
* `run_bellman_ford(graph, source)`
* `run_kruskal(graph)`

These wrappers execute the corresponding algorithms and provide standardized result objects.

### Worklet 1 adapter

`graph_integration/worklet1_adapter.py` provides:

```python
to_worklet2_graph(graph)
```

The adapter converts a supported Worklet 1 graph into Worklet 2's graph representation.

It preserves vertex labels, edge weights, directedness, and isolated vertices. Since Worklet 2's graph model requires weighted edges and does not support self-loops, the adapter explicitly rejects unweighted graphs and graphs containing self-loops.

The adapter has been tested with both Worklet 1 adjacency-list and adjacency-matrix graph implementations.

### Example: Convert and execute Dijkstra

```python
from worklet1.graph import AdjacencyListGraph
from graph_integration.worklet1_adapter import to_worklet2_graph
from graph_integration.integration import run_dijkstra

graph = AdjacencyListGraph(directed=False, weighted=True)

graph.add_edge("A", "B", 4)
graph.add_edge("A", "C", 1)
graph.add_edge("C", "B", 2)
graph.add_edge("B", "D", 1)

converted_graph = to_worklet2_graph(graph)
result = run_dijkstra(converted_graph, "A")

print(result.distances)
print(result.path_to("D"))
```

This example demonstrates the graph conversion and execution workflow. The adapter currently bridges Worklet 1 graph inputs to Worklet 2's Dijkstra, Bellman–Ford, and Kruskal implementations; it does not automatically make every algorithm interchangeable between the worklets.

## 5. Min Heap

The custom `MinHeap` stores `(priority, item)` entries and removes the entry with the smallest priority first.

| Operation          | Time complexity |
| ------------------ | --------------: |
| Insert             |        O(log n) |
| Extract minimum    |        O(log n) |
| Peek minimum       |            O(1) |
| Check empty / size |            O(1) |

A monotonically increasing insertion counter breaks ties between equal priorities, so heap items do not need to be mutually comparable.

## 6. Dijkstra's Algorithm

Dijkstra computes shortest distances from a source vertex in a weighted graph with non-negative edge weights.

It uses the Min Heap to process the currently closest candidate vertex efficiently.

For an adjacency-list graph using a binary Min Heap:

* **Time complexity:** O((V + E) log V)
* **Space complexity:** O(V + E)

Here, V is the number of vertices and E is the number of edges.

The algorithm returns shortest distances and predecessor information for reconstructing paths. Unreachable vertices have infinite distance.

## 7. Testing and Validation

Run commands from the repository root.

### Complete test suite

```powershell
py -m pytest -q
```

### Worklet 1 tests

```powershell
py -m pytest .\worklet1\tests -v
```

### Adapter tests

```powershell
py -m pytest .\tests\test_worklet1_adapter.py -v
```

### Ruff lint check

```powershell
py -m ruff check .
```

### Ruff formatting check

```powershell
py -m ruff format --check .
```

### Latest reported validation

The following results were reported during development:

* Complete project test suite: **1,170 passed, 11 subtests passed**
* Worklet 1 tests run independently: **984 passed**
* Worklet 1 adapter tests: **7 passed**
* Ruff lint check: **All checks passed**

These results come from separate test runs and should not be added together as a count of unique tests. Run the commands above again after any further changes.

## 8. Current Status and Future Work

### Completed

* Graph representations and fundamental graph algorithms
* Weighted graph algorithms and supporting data structures
* Shared graph model and integration wrappers
* Adapter between supported Worklet 1 and Worklet 2 graph representations
* Automated tests for algorithms and adapter behavior
* Benchmarking utilities

### Planned

* Interactive graph visualization
* Graph creation and editing through a user interface
* Algorithm selection and execution through the interface
* Visualizing traversal order, shortest paths, and minimum spanning trees
* Step-by-step algorithm execution
* A consistent frontend/backend interface, if required by the final application design

The goal is to evolve the current algorithm-focused project into an interactive environment where users can create graphs, run algorithms, and understand their behavior visually.
