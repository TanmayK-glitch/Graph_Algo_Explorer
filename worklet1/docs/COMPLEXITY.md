# Complexity analysis - Worklet 1

V = vertices, E = edges, d(v) = degree.

## Graph operations

| Operation | Adjacency list | Adjacency matrix |
|---|---|---|
| `add_vertex` | O(1) | O(V) (add a row and a column) |
| `add_edge` | O(d(u)) (duplicate check + ordered insert) | O(1) once vertices exist |
| `remove_edge` | O(d(u)) | O(1) |
| `remove_vertex` | O(V + E) | O(V^2) (delete row/column, re-index) |
| `has_edge` | O(d(u)) | O(1) |
| `edge_weight` | O(d(u)) | O(1) |
| `neighbours(v)` | O(d(v)) | O(V) |
| `all_edges`, `edge_count` | O(V + E) | O(V^2) |
| Space | O(V + E) | O(V^2) |

The list's `edge_weight` is not O(1) as Worklet 2 would like (proposal X-01); the matrix's is.

## Algorithms (cost = calls to `neighbours` dominates)

| Algorithm | List | Matrix | Notes |
|---|---|---|---|
| BFS / DFS (one component) | O(V + E) | O(V^2) | each vertex's `neighbours` is called once |
| BFS_ALL / DFS_ALL | O(V + E) | O(V^2) | restarts share one visited set |
| Connected components | O(V + E) | O(V^2) | repeated BFS |
| SCC (Kosaraju) | O(V + E) | O(V^2) | two DFS passes + a locally built transpose |
| Cycle detection | O(V + E) | O(V^2) | one DFS |
| Topological sort (Kahn) | O(V + E) | O(V^2) | in-degrees from `all_edges()`, then a queue |
| Bipartite test | O(V + E) | O(V^2) | BFS 2-colouring |

Extra space: O(V) for visited sets, queues, recursion stack, colour/in-degree maps (SCC also stores the transpose, O(V + E)).
Canonical component ordering adds O(V log V).

## Measured evidence (NFR-12)

`tests/test_complexity.py` counts executed lines inside the representation modules (via `sys.settrace`, so it is
deterministic and not wall-clock) while running `bfs_all` on a path graph (E = V - 1):

| V | list lines | matrix lines |
|---|---|---|
| 50 | 299 | 5,399 |
| 100 | 599 | 20,799 |
| 200 | 1,199 | 81,599 |
| 400 | 2,399 | 323,199 |

Doubling V doubles the list count (linear) and quadruples the matrix count (quadratic). The test asserts ratios in
1.7-2.3 for the list and 3.4-4.6 for the matrix. This measures the representation work only, on sparse graphs.

## When is a matrix better? (viva)

When the graph is dense (the V^2 cells are mostly used) or when an algorithm needs many O(1) `has_edge` lookups
(Floyd-Warshall, triangle counting). For sparse graphs and traversals the list wins: the table above shows 100x
more work for the matrix at V = 400.

## Recursion limit

DFS, cycle detection and Kosaraju recurse once per vertex on the current path. Measured: a directed path of 990
vertices works, 1000 raises `RecursionError` (default limit). The design targets "a few hundred vertices". `DFSAlgorithm.execute(..., iterative=True)` avoids the limit (tested at 5000 vertices); cycle detection and SCC have no iterative variant.
