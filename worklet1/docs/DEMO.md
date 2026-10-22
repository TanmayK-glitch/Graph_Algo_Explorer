# Demonstration procedure

The whole demonstration is **one file**: `worklet1/demo.py`. Run from the project root (see README for setup).

    python -m worklet1.demo            # everything at once
    python -m worklet1.demo --pause    # presenting: waits for ENTER between sections

It is a narrated walkthrough in 12 sections. Each prints what it shows, a small ASCII picture, the real output, and why it is correct.

| # | Section | What to say |
|---|---|---|
| 1 | Two representations, one interface | Same calls and answers from list and matrix; matrix view printed |
| 2 | Editing and error handling | Auto-created vertices, self-loop, duplicate / missing edge / unknown vertex / bad id errors, `remove_vertex` |
| 3 | Edge-list loader | Format v1 (PROPOSED), a loaded weighted graph, malformed files reported with line numbers |
| 4 | BFS and DFS | Order, BFS parent tree, recursive vs iterative DFS, single component vs `mode="all"`, unknown start |
| 5 | Connected components | Repeated BFS, isolated vertices, directed graph rejected |
| 6 | Strongly connected components | Kosaraju's two passes on two graphs |
| 7 | Cycle detection | Diamond (cross edges, no cycle) vs real cycles; triangle; self-loop |
| 8 | Topological sort | Valid order proven edge by edge; cycle gives `success=False`; undirected rejected |
| 9 | Bipartite test | 4-cycle colouring checked; triangle and self-loop fail; directed rejected |
| 10 | Representation independence | Five algorithms give identical output on list and matrix |
| 11 | Complexity evidence | Executed-line counts: list doubles, matrix quadruples when V doubles |
| 12 | Summary | What is done, pending, proposed, not built, limitations |

## Suggested 10-minute order

1. `python -m pytest` - show the whole suite passing (984 tests at the time of writing).
2. `python -m worklet1.demo --pause` - go through sections 1-12 (about 1 minute each).
3. Live edit in a Python shell to show it is real:

       >>> from worklet1.graph import AdjacencyMatrixGraph
       >>> from worklet1.algorithms import TopologicalSortAlgorithm
       >>> g = AdjacencyMatrixGraph(directed=True)
       >>> for e in [("A","B"),("B","C"),("C","A")]: g.add_edge(*e)
       >>> TopologicalSortAlgorithm().execute(g).success                    # False - cycle
       >>> g.remove_edge("C","A"); TopologicalSortAlgorithm().execute(g).primary_output   # ['A','B','C']

4. Open `worklet1/tests/test_architecture.py` to show that algorithms never touch `_adj` / `_matrix` and run unchanged on a made-up third graph class.
5. Close with `docs/WORKLET1_FINAL_REPORT.md`: verified, pending and blocked items.
