# Graph Algorithms Explorer — AI Agent Skill Library

> **Location:** Put this file at the **repository root** as `skills.md`.
> **Purpose:** A shared, version-controlled development contract for humans and AI coding agents.
> **Scope:** Repository-wide working rules; concrete interfaces below are verified for **Worklet 2**. Other worklets must define their own interfaces before an agent implements or changes them.

## 1. Mandatory agent workflow

Before generating, editing, refactoring, or testing project code, the AI agent must:

1. Read this entire `skills.md` file, the root `README.md`, the relevant module(s), and the corresponding tests.
2. Inspect the **actual repository** before assuming files, functions, dependencies, or APIs exist.
3. Explain the requested change briefly, identify affected files and public contracts, and make the smallest safe change.
4. Keep the **canonical names** in Sections 3–5 unchanged unless the team explicitly approves an interface migration.
5. If code, tests, README, and this file disagree, **flag the mismatch**. Do not silently invent an API, rename variables across the repository, or weaken a test simply to make it pass.
6. Run relevant tests; report the exact command, pass/fail result, and any tests not run. Do not fabricate benchmark timings, test counts, coverage, or implementation status.
7. Update tests and documentation alongside any **approved** interface change.

**Do not treat this file as permission to rewrite teammates' code.** Prefer adapters over unnecessary changes to tested algorithm implementations.

## 2. Project purpose and architecture

**Project:** Graph Algorithms Explorer — an educational toolkit for weighted graph algorithms.

**Implemented Worklet 2 flow:**

```text
Graph input
   -> graph_integration/graph.py        # shared Graph and conversions
   -> graph_integration/integration.py  # adapters / wrapper functions
   -> src/algorithms/                  # team's algorithms
   -> standardized result objects
   -> downstream worklets / visualization (integration still to be agreed)

benchmark.py independently generates graphs, measures execution and
conversion times, and writes CSV reports.
```

### Expected repository layout

```text
Graph_Algo_Explorer/
├── skills.md                       # THIS FILE: shared agent contract
├── AGENTS.md                       # optional agent entry point (see below)
├── README.md                       # main project documentation
├── pyproject.toml                  # project configuration, if present
├── graph_integration/
│   ├── __init__.py
│   ├── graph.py
│   ├── integration.py
│   ├── benchmark.py
│   └── README.md
├── src/
│   └── algorithms/
│       ├── dijkstra.py
│       ├── bellman_ford.py
│       ├── kruskal.py
│       ├── min_heap.py
│       └── dsu.py
└── tests/
    ├── test_graph.py
    ├── test_integration.py
    ├── test_benchmark.py
    └── ...
```

Inspect the real tree before editing: not every environment will have exactly this layout.

## 3. Canonical naming conventions — DO NOT DRIFT

**Python conventions**

- Files, functions, variables, and modules: `snake_case`.
- Classes and result types: `PascalCase`.
- Constants, fixed CSV column sets: `UPPER_SNAKE_CASE`.
- Keep module/package names consistent with the existing imports: `graph_integration` and `src.algorithms`.
- Use `source`, `target`, `weight` for the `Graph.add_edge(...)` contract. In a local Kruskal edge tuple, `u`, `v`, `weight` is acceptable.
- Use `vertices` for a vertex-label sequence, `edges` for edge tuples, `directed` for orientation, `density` for **actual** density, and `requested_density` for the requested benchmark setting.
- Use `repetitions` for recorded run count. The command-line option is `--repeats`; do not rename either casually.
- Internal or temporary variable names may differ, but **public API names, result fields, test imports, and CSV column names must match exactly**.

| Canonical item | Exact spelling / meaning | Do not substitute |
| --- | --- | --- |
| Shared graph class | `Graph` | `WeightedGraph`, `GraphModel` without migration |
| Graph orientation | `directed` (`bool`) | `isDirected` |
| Internal adjacency | `_adj` | Do not access/modify it outside `graph.py` |
| Graph counts | `num_vertices`, `num_edges` | `vertex_count`, `edge_count` as public replacements |
| Graph density | `density` | Requested and actual density are not interchangeable |
| Edge shape | `(source, target, weight)` | Unlabelled reordering such as `(weight, source, target)` |
| Algorithm identifier | `"dijkstra"` | `"Dijkstra"` in machine-readable fields |
| Algorithm identifier | `"bellman_ford"` | `"bellman-ford"`, `"bellmanFord"` |
| Algorithm identifier | `"kruskal"` | `"krushkal"` |
| Shortest path result | `ShortestPathResult` | Unapproved result dict format |
| MST result | `MSTResult` | Unapproved result dict format |
| Benchmark status | `"OK"` / `"ERROR"` | Mixed capitalization/status strings |

**Important compatibility note:** Some copies/branches of `integration.py` have an optional `run_algorithm(...)` dispatcher; a tested user checkout did not. **Do not assume or require it** without checking the actual branch. The three `run_*` functions below are the agreed required interfaces.

## 4. Worklet 2 graph model contract — `graph.py`

### Types and storage

```python
Vertex = Hashable
Weight = int | float
Edge = tuple[Vertex, Vertex, Weight]
```

- `Graph(directed: bool = False)` creates a weighted graph.
- Internally, `_adj` is a dictionary of dictionaries: `vertex -> {neighbor: weight}`.
- Vertex labels must be **hashable**; preserve their original labels in outputs.
- Valid weights are finite `int` or `float`, including `0` and negative values; reject `bool`, `NaN`, and infinities as edge weights.
- This is a **simple graph**: reject self-loops and duplicate/parallel edges.
- `add_vertex(vertex)` must preserve isolated vertices.
- `add_edge(source, target, weight)` creates missing vertices; for undirected graphs, store the reverse adjacency internally.
- For undirected graphs, `num_edges` and `to_edge_list()` count each undirected edge **once**.

### Stable public API

```python
Graph(directed=False)
graph.add_vertex(vertex)
graph.add_edge(source, target, weight)
graph.vertices                # list of labels, insertion order
graph.num_vertices            # int
graph.num_edges               # int
graph.density                 # float, ACTUAL density

graph.to_adjacency_list()     # dict[Vertex, list[tuple[Vertex, Weight]]]
graph.to_adjacency_matrix()   # (vertex_order, matrix)
graph.to_edge_list()          # list[(source, target, weight)]
graph.to_kruskal_input()      # (num_vertices, indexed_edges, labels)

Graph.from_edge_list(edges, directed=False, vertices=())
Graph.from_adjacency_list(adjacency, directed=False)
Graph.from_adjacency_matrix(vertices, matrix, directed=False)
```

### Conversion rules

- **Adjacency list:** For existing shortest-path implementations, use `dict[Vertex, list[(neighbor, weight)]]`, including isolated vertices as keys with empty lists.
- **Adjacency matrix:** Return `(vertex_order, matrix)` together. Rows/columns follow `vertex_order`. Diagonal is `0`; missing edges use `math.inf` (not `0`). Off-diagonal zero means a valid zero-weight edge. Undirected matrices are symmetric.
- **Edge list:** Return tuples `(source, target, weight)`. For undirected graphs, return just one copy of each edge.
- **Kruskal mapping:** `to_kruskal_input()` rejects directed graphs and returns `(count, indexed_edges, labels)`, where indices are `0..count-1`. After Kruskal, map each index back to `labels[index]`.
- Round-trips between representations should preserve vertices, weights, directionality and isolated vertices where the format allows it.

**Algorithm-specific constraints must not be imposed on the shared `Graph`:** a negative-weight graph is valid in `graph.py` even though Dijkstra must reject it.

## 5. Worklet 2 algorithm and integration contracts

### Algorithm modules owned by other contributors

| Existing function | Expected input | Return / constraints |
| --- | --- | --- |
| `src.algorithms.dijkstra.dijkstra(graph, source)` | Weighted adjacency list | Dijkstra result with `source`, `distances`, `predecessors`; rejects negative weights |
| `src.algorithms.bellman_ford.bellman_ford(graph, source)` | Weighted adjacency list | Bellman–Ford result with same fields; supports negative weights; rejects a reachable negative cycle |
| `src.algorithms.kruskal.kruskal_mst(num_vertices, edges)` | Integer vertex IDs `0..n-1`, weighted edge list | `(mst_edges, total_weight)`; expects an undirected, connected graph for a spanning tree |
| `src.algorithms.min_heap.MinHeap` | Heap entries | Dijkstra support; do not change casually |
| `src.algorithms.dsu.DisjointSetUnion` | Integer elements | Kruskal support; do not change casually |

### Required wrapper API — `graph_integration/integration.py`

```python
run_dijkstra(graph: Graph, source: Vertex) -> ShortestPathResult
run_bellman_ford(graph: Graph, source: Vertex) -> ShortestPathResult
run_kruskal(graph: Graph) -> MSTResult
```

- Accept the shared **`Graph` object**, not a raw adjacency dict at these wrapper entry points.
- Convert inputs inside the wrapper; keep algorithm internals in `src/algorithms` unchanged.
- Standardize shortest-path results as:

```python
ShortestPathResult(
    algorithm: str,                     # "dijkstra" or "bellman_ford"
    source: Vertex,
    distances: dict[Vertex, float],
    predecessors: dict[Vertex, Vertex | None],
)
result.path_to(target) -> list[Vertex] | None
```

- `math.inf` signifies an unreachable vertex; `path_to` returns `None` for unreachable/unknown targets.
- Standardize Kruskal results as:

```python
MSTResult(
    algorithm: str,                     # "kruskal"
    edges: list[Edge],                  # ORIGINAL vertex labels
    total_weight: Weight,
)
```

- Reject incorrect graph argument types explicitly; propagate documented algorithm validation errors.
- Wrappers must not mutate the original Graph object.
- Do not make a test import or call `run_algorithm` unless the actual checked-out `integration.py` supports it. If the team elects to add a dispatcher, coordinate its exact signature and tests first.

## 6. Benchmarking and reporting contract — `benchmark.py`

### Repeatable methodology

- `generate_graph(vertices, density, seed=42)` generates connected, simple, **undirected** weighted graphs with positive edge weights and a fixed seed.
- Worklet 2 benchmark sizes: `10, 50, 100, 500, 1000` vertices.
- Requested densities: `0.05` and `0.20`. Record **actual** density separately.
- The minimum actual density for a connected, simple undirected graph with 10 vertices is `9 / 45 = 0.20`, even if `0.05` was requested.
- Final reported experiment: `10` repetitions for every size/density/operation, unless an explicitly labelled experiment says otherwise.
- Use `time.perf_counter_ns()` for elapsed timing; convert nanoseconds to milliseconds; record **mean**, **minimum**, and **maximum**.
- Time algorithm **wrappers (including input conversion)**; exclude graph generation from timed regions.
- Benchmark representation **conversion/export separately**. Do not claim this is a native adjacency-matrix Dijkstra or Bellman–Ford speed test.
- Report errors as `execution_status="ERROR"` with an error message; do not replace missing measurements with zeros or fabricated values.
- Kruskal computes an MST, not shortest paths. Do not declare it the "best shortest-path algorithm" based on timing.

### Stable benchmark interfaces

```python
generate_graph(vertices, density, seed=42)
benchmark_algorithms(graph, requested_density, repetitions)
benchmark_representations(graph, requested_density, repetitions)
run_benchmarks(sizes, densities, repetitions, seed=42)
```

Stable CLI option names: `--sizes`, `--densities`, `--repeats`, `--seed`, `--output`.

### Stable CSV files and exact headers

`algorithms.csv`:

```text
algorithm,vertices,edges,density,requested_density,graph_representation,repetitions,execution_time_ms,min_time_ms,max_time_ms,execution_status,error
```

`representations.csv`:

```text
operation,graph_representation,vertices,edges,density,requested_density,repetitions,execution_time_ms,min_time_ms,max_time_ms,execution_status,error
```

Representation labels must be `"adjacency_list"`, `"adjacency_matrix"`, or `"edge_list"`. Conversion operation label is `"graph_to_representation"`.

### Reproduce the final benchmark

Run from the repository root on Windows PowerShell:

```powershell
py -m graph_integration.benchmark --sizes 10 50 100 500 1000 --densities 0.05 0.2 --repeats 10 --output benchmark_final
```

Expected outputs: `benchmark_final/algorithms.csv` and `benchmark_final/representations.csv`. Treat the **actual CSVs**, not old presentation figures or previous chat messages, as the source of timing evidence.

## 7. Testing and quality gate

Use the existing testing framework already present in the project; do not migrate frameworks without approval.

- Place integration tests in the root `tests/` folder, not inside `graph_integration/`.
- Maintain tests for `Graph` input validation, isolated vertices, directed/undirected behavior, conversion round-trips, and zero/negative weights.
- Maintain tests for wrapper output contracts, original label preservation, nonmutation, invalid source, negative cycles, disconnected MST, and directed Kruskal rejection.
- Maintain tests for seeded graph generation, connectivity, edge count/density, repeat counts, error status, and CSV schemas.
- For a change to a public name, update **all imports, tests, examples, docs, and dependent modules** in one coordinated change. Prefer no public rename at all.
- A previous local `unittest` run passed **68 discovered tests**; counts may change as the team adds tests. Report only a freshly observed result for the current commit. Do not assume separately reported `pytest` or lint counts are verified for this checkout.

Run from repo root:

```powershell
py -m unittest discover -s tests -p "test_*.py" -v
```

For focused tests:

```powershell
py -m unittest discover -s tests -p "test_graph.py" -v
py -m unittest discover -s tests -p "test_integration.py" -v
py -m unittest discover -s tests -p "test_benchmark.py" -v
```

Use `python` instead of `py` where `py` is unavailable. If the root `pyproject.toml` prescribes a lint/formatter tool, follow it; do not claim it passed unless run.

## 8. Change management and cross-worklet contracts

- Worklet 2 owns the graph representation, adapters, and weighted algorithms described above. Worklet 3 or other worklets may consume them through the agreed wrapper API, but their implementation is **not assumed complete**.
- Never add a new dependency, relocate a package, change an algorithm signature, or change result/CSV schemas without checking downstream callers and asking for team approval when compatibility is affected.
- Prefer explicit typed function arguments and return values. No magic positional tuples outside the agreed edge/result contracts.
- Do not hardcode benchmark outcomes, expected runtime measurements, or unverified test counts into the application.
- Keep generated benchmark outputs out of source modules; save under named output folders.
- Preserve reproducibility: record graph size, actual/requested density, repetitions, timing units, seed/settings where applicable, and software/environment context in the final report.
- Keep documentation honest: implemented features vs planned features, verified behavior vs assumptions, and conversion timings vs native algorithm timings must be separated.

### Agent completion checklist

Before saying a task is complete, the agent should be able to answer **yes** to these checks:

- [ ] I read `skills.md` and inspected the relevant actual files.
- [ ] I preserved canonical names and existing public signatures.
- [ ] My change does not break teammate modules or original vertex labels.
- [ ] I added/updated appropriate tests and ran them (or disclosed why not).
- [ ] I checked benchmark and CSV terminology if performance data is involved.
- [ ] I updated the relevant README/docs and reported exactly what changed.

## 9. Minimal reference example

```python
from graph_integration.graph import Graph
from graph_integration.integration import (
    run_dijkstra,
    run_bellman_ford,
    run_kruskal,
)

graph = Graph.from_edge_list([
    ("A", "B", 4),
    ("A", "C", 2),
    ("B", "C", 1),
    ("C", "D", 3),
])

assert run_dijkstra(graph, "A").distances["D"] == 5
assert run_bellman_ford(graph, "A").path_to("D") == ["A", "C", "D"]
assert run_kruskal(graph).total_weight == 6
```

**Core rule:** One shared `Graph`, consistent public names, adapters for algorithm-specific inputs, tested outputs, and no undocumented breaking changes.
