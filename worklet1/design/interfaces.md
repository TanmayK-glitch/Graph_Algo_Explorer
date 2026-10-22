# Interface specification - Worklet 1

Status labels: **AGREED** = listed as agreed in sections 9.3 / 9.4 of the design document;
**PROPOSED** = offered by Worklet 1, no approval from other worklets is claimed.

## Graph (`worklet1.graph.Graph`)

| Member | Signature | Status |
|---|---|---|
| `is_directed`, `is_weighted` | properties -> bool | AGREED |
| `vertices` | property -> `list` (new list, creation order) | AGREED |
| `add_vertex(v)` | idempotent; `TypeError` if `v` is not int/str | AGREED |
| `remove_vertex(v)` | removes incident edges; `VertexNotFoundError` | AGREED |
| `add_edge(u, v, weight=None)` | creates missing vertices; `EdgeAlreadyExistsError`; weighted graphs require a finite weight, unweighted reject one (`ValueError`) | AGREED (policy details are Worklet 1 choices) |
| `remove_edge(u, v)` | `VertexNotFoundError` / `EdgeNotFoundError` | AGREED |
| `has_edge(u, v)` | bool; `VertexNotFoundError` for unknown vertices | AGREED |
| `neighbours(v)` | list of ids in vertex-creation order; for directed graphs out-neighbours | AGREED |
| `all_edges()` | list of `Edge` copies; **undirected edges once** (lower creation rank first) | AGREED interface; once-per-edge rule is a Worklet 1 choice to confirm with W2/W3 |
| `vertex_count()`, `edge_count()` | undirected edge and self-loop count once | AGREED |
| `edge_weight(u, v)` | float or `None` (absent edge or unweighted) | **PROPOSED** (X-01) |

`Edge(src, dst, weight=None)`; `Vertex(id, data=None)` (not used by the API).
Self-loops allowed (stored once); parallel edges rejected; negative weights allowed.

## Algorithms

`Algorithm.name` and `Algorithm.execute(graph, **kwargs) -> AlgorithmResult`.
`AlgorithmResult(algorithm, primary_output, metadata, success, error_message)`.

| Algorithm (`algorithm` string) | kwargs | `primary_output` | `metadata` |
|---|---|---|---|
| `BFSAlgorithm` ('BFS' / 'BFS_ALL') | `start`, or `mode="all"` | visit order | BFS: `start`, `parent`; BFS_ALL: `{}` |
| `DFSAlgorithm` ('DFS' / 'DFS_ALL') | `start`, or `mode="all"`; optional `iterative=True` (explicit stack, same order) | visit order | DFS: `start`; DFS_ALL: `{}` |
| `ConnectedComponentsAlgorithm` ('ConnectedComponents') | - | `[[...]]` | `count`; `component_map` (**PROPOSED**, X-03) |
| `SCCAlgorithm` ('SCC') | - | `[[...]]` | `count`; `component_map` (**PROPOSED**, X-03) |
| `CycleDetectionAlgorithm` ('CycleDetection') | - | bool | `{}` |
| `TopologicalSortAlgorithm` ('TopologicalSort') | - | order, or `None` with `success=False` | `has_cycle` |
| `BipartiteTestAlgorithm` ('BipartiteTest') | - | bool | `colouring` (vertex -> 0/1) when True (AGREED with W3) |

Errors: wrong graph direction -> `ValueError`; unknown `start` -> `VertexNotFoundError`; missing `start` in single
mode or bad `mode` -> `ValueError`. Module-level helpers: `bfs`, `bfs_all`, `dfs`, `dfs_all`.
Not provided: animation step data (X-04, pending with Worklet 3).

## EdgeListLoader (`worklet1.io`)

`EdgeListLoader.load(filepath, graph_class=AdjacencyListGraph) -> Graph`. Format v1 (**PROPOSED**, X-02, pending W2/W3):

    # comments (whole-line or trailing)
    DIRECTED | UNDIRECTED
    WEIGHTED | UNWEIGHTED
    u v [weight]          one edge per line; weight present iff WEIGHTED
    v                     isolated vertex

Keywords are upper-case. Ids are whitespace-free strings. Errors: `FileNotFoundError`; `EdgeListFormatError`
(a `ValueError` with `.line_number`) for missing/invalid headers, wrong field count, missing/invalid/NaN/inf weight,
duplicate edge, empty file. UTF-8 (BOM tolerated).
