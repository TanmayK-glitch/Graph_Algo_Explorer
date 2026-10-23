# Design decision log - Worklet 1

DD-01..DD-07 come from section 10 of the design document. DD-08 and later were added during
implementation and are labelled **(added)**. Pending cross-worklet items are in `docs/DECISIONS_PENDING.md`.

| ID | Decision | Alternatives | Choice | Rationale | Where |
|---|---|---|---|---|---|
| DD-01 | Graph interface mechanism | ABC / Protocol / duck typing | ABC | Incomplete implementations cannot be instantiated | `graph/base.py`, `test_graph_base.py` |
| DD-02 | Default representation | list / matrix | list | Sparse-friendly O(V+E); loader default | `io/edge_list_loader.py` |
| DD-03 | Topological sort | Kahn / DFS post-order | Kahn | Cycle detection falls out of output length | `algorithms/topological_sort.py` |
| DD-04 | Edge-list format | custom text / adjacency file | custom plain text | Hand-writable, extensible | `io/edge_list_loader.py`, `sample_graphs/` |
| DD-05 | Result structure | dict / tuple / dataclass | dataclass | Typed and readable across worklets | `algorithms/base.py` |
| DD-06 | Directed cycle detection | one visited set / visited + rec_stack | visited + rec_stack | One set cannot tell back edge from cross edge | `algorithms/cycle_detection.py` |
| DD-07 | DFS style | recursive / iterative | recursive | Clearer; recursion-limit risk documented | `algorithms/dfs.py` |
| DD-08 (added) | SCC algorithm | Kosaraju / Tarjan | Kosaraju | Reuses DFS, easiest to defend in viva; costs a transpose | `algorithms/scc.py` |
| DD-09 (added, D-23) | Neighbour / edge ordering | edge-insertion order / vertex-creation order | vertex-creation order | A matrix has no edge-insertion order; one rule makes both representations return identical results (NFR-02) | `adj_list.py` (`bisect.insort` by rank), `adj_matrix.py` |
| DD-10 (added, D-02) | Undirected `all_edges`/`edge_count` | both directions / once | once, lower creation rank first | Consumers (MST, drawing) need each edge once | both representations |
| DD-11 (added, D-07/08) | Weight policy | default weight / strict | strict: weighted needs a finite weight, unweighted rejects one; negatives/zero allowed | Avoids silent loss (matrix `None` = no edge); keeps sign rules for Worklet 2 | `Graph._normalise_weight` |
| DD-12 (added, D-01) | Connected components on directed graph | reject / weak components | `ValueError` | Out-neighbour BFS would give order-dependent, wrong partitions | `connected_components.py` |
| DD-13 (added, D-03) | BFS_ALL / DFS_ALL API | implicit / explicit | `mode="single"\|"all"` plus module functions `bfs_all`, `dfs_all` | Forgetting `start` must not silently traverse everything | `bfs.py`, `dfs.py` |
| DD-14 (added, D-11) | Component ordering | traversal order / canonical | members in vertex order; components by earliest member | Reproduces the design's SCC example; deterministic | `algorithms/base.py` |
| DD-15 (added, D-05) | Exceptions | plain KeyError/ValueError / custom | custom classes that also subclass KeyError / ValueError | Satisfies both readings of section 11 | `graph/exceptions.py` |
| DD-16 (added, D-06) | Vertex ids | any hashable / int and str | `int` (not bool) and `str` | `True == 1` would collide | `Graph.validate_vertex_id` |
| DD-18 (added, D-12) | Recursion limit | document only / opt-in iterative | recursive default (DD-07 unchanged) plus opt-in `iterative=True` for DFS | Removes the 1000-deep failure for DFS without changing defaults; order proven equal by tests | `algorithms/dfs.py`, `test_dfs.py` |
| DD-17 (added) | Mutation safety | mutate then validate / validate first | validate first | A failed `add_edge` leaves the graph unchanged | `add_edge` in both classes |

## Noted in the design document, not changed (D-17)

The table of contents lists Kosaraju as "Decision 3" while the body's Decision 3 is Kahn's; Appendix A expects DD-01..DD-08
while the table has DD-01..DD-07 (DD-08 is supplied above); section 13 gives two members the same MIS number; the section 8.4
step list is numbered 7-10.
