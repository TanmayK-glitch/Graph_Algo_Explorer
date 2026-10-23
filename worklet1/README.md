# Worklet 1 - Graph Model, Traversal and Connectivity

COEP Mini Project 9 (Graph Algorithms Explorer). Pure Python 3.10+, standard library only: hand-built
adjacency-list and adjacency-matrix graphs, BFS, DFS, connected components, SCC (Kosaraju), cycle
detection, topological sort (Kahn), bipartite test and an edge-list loader.
Specification: `Worklet1_Week3_Design_Document_last(5).docx`. Status of every requirement:
`docs/WORKLET1_FINAL_REPORT.md`.

## Setup (Windows PowerShell shown; Linux/macOS use `source .venv/bin/activate`)

Run everything from the **project root** (the folder that contains `worklet1/` and `pyproject.toml`).

    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -r requirements-dev.txt
    python -m pytest                 # full suite
    python -m worklet1.demo --pause  # complete narrated demonstration (see docs/DEMO.md)
    python -m ruff check worklet1    # optional lint
    python -m mypy worklet1/graph worklet1/algorithms worklet1/io   # optional type check

Only `pytest` is needed to run the tests; the library itself imports nothing outside the standard library.
Never put the `worklet1/` folder itself on `sys.path` - its `io` sub-package would shadow Python's `io`.

## Quick example

```python
from worklet1.graph import AdjacencyListGraph, AdjacencyMatrixGraph
from worklet1.algorithms import BFSAlgorithm, TopologicalSortAlgorithm
from worklet1.io import EdgeListLoader

g = AdjacencyListGraph(directed=True)            # or AdjacencyMatrixGraph - same API
g.add_edge("A", "B"); g.add_edge("A", "C"); g.add_edge("B", "D"); g.add_edge("C", "D")
BFSAlgorithm().execute(g, start="A").primary_output          # ['A', 'B', 'C', 'D']
BFSAlgorithm().execute(g, mode="all")                        # whole graph (BFS_ALL)
TopologicalSortAlgorithm().execute(g).primary_output         # ['A', 'B', 'C', 'D']

h = EdgeListLoader.load("worklet1/sample_graphs/weighted_directed.edgelist")
```

## Package map

| Path | Contents |
|---|---|
| `graph/` | `Graph` ABC, `Vertex`, `Edge`, exceptions, `AdjacencyListGraph`, `AdjacencyMatrixGraph` |
| `algorithms/` | `Algorithm`, `AlgorithmResult`, BFS, DFS, ConnectedComponents, SCC, CycleDetection, TopologicalSort, BipartiteTest |
| `io/` | `EdgeListLoader`, `EdgeListFormatError` |
| `tests/` | pytest suite (graph contract, each algorithm, loader, properties, architecture, complexity, integration) |
| `sample_graphs/` | `.edgelist` fixtures (+ `malformed/`) |
| `design/` | `design_decisions.md`, `interfaces.md` |
| `docs/` | requirements matrix, plan, pending decisions, complexity, demo guide, viva prep, final report |

## Algorithms at a glance

| Algorithm | Class | Needs | Output (`primary_output`) |
|---|---|---|---|
| BFS / BFS_ALL | `BFSAlgorithm` | `start` or `mode="all"` | visit order (+ `parent` map) |
| DFS / DFS_ALL | `DFSAlgorithm` | `start` or `mode="all"` (optional `iterative=True`) | visit order |
| Connected components | `ConnectedComponentsAlgorithm` | undirected | list of components |
| SCC | `SCCAlgorithm` | directed | list of components |
| Cycle detection | `CycleDetectionAlgorithm` | any | `True`/`False` |
| Topological sort | `TopologicalSortAlgorithm` | directed | order, or `success=False` on a cycle |
| Bipartite test | `BipartiteTestAlgorithm` | undirected | `True` + `colouring`, or `False` |

Wrong graph type -> `ValueError`; unknown start vertex -> `VertexNotFoundError`.

## Proposed / pending (not agreed with other worklets)

* `Graph.edge_weight(u, v)` - proposed to Worklet 2.
* Edge-list format v1 - proposed, pending Worklet 2 and 3 sign-off.
* `metadata["component_map"]` on component results - proposed to Worklet 3.
* Animation step data - not implemented (open question for Worklet 3).

## Known limitations

* DFS, cycle detection and SCC are recursive by default: graphs about 1000 vertices deep raise `RecursionError`.
  Plain DFS has an opt-in fix: `DFSAlgorithm().execute(g, start=..., iterative=True)` (same order, no depth limit).
  Cycle detection and SCC have no iterative variant.
* The list representation's `edge_weight` is O(degree), not O(1).
* The project folder is not a git repository, so NFR-10 (shared repo, small commits) is not demonstrated.
