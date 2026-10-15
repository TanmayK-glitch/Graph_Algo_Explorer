<div align="center">

# 🌐 Graph Algorithms Explorer

### Kruskal's Minimum Spanning Tree & Disjoint Set Union

**A clean, tested Python implementation of minimum spanning trees using Union-Find.**

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Algorithm](https://img.shields.io/badge/Algorithm-Kruskal's%20MST-16A085?style=for-the-badge)
![Data Structure](https://img.shields.io/badge/Data%20Structure-DSU-8E44AD?style=for-the-badge)
![Tests](https://img.shields.io/badge/Project%20Tests-50%20Passed-2EA44F?style=for-the-badge)

**[Overview](#-overview) · [Features](#-features) · [Quick-start](#-quick-start) · [How-it-works](#-how-it-works) · [Testing](#-testing)**

</div>

---

## ✨ Overview

This contribution to **Graph Algorithms Explorer** implements two closely related components:

- **Disjoint Set Union (DSU / Union-Find):** efficiently maintains groups of connected vertices.
- **Kruskal's algorithm:** constructs a minimum spanning tree (MST) of a connected, undirected, weighted graph by choosing low-weight edges without creating cycles.

The modules are written in Python, include type hints and docstrings, and follow the existing repository's `src/algorithms/` structure.

> **Scope:** This README documents the Kruskal + DSU contribution. It does not claim that the full graph explorer GUI or every planned algorithm is complete.

## 🚀 Features

| Component | Capabilities |
|:--|:--|
| **DSU** | `find`, `union`, `connected` |
| **Optimizations** | Path compression and union by rank |
| **Kruskal MST** | Sorts weighted edges and avoids cycles with DSU |
| **Weights** | Supports positive, zero, and negative edge weights |
| **Validation** | Rejects invalid vertex indices and disconnected graphs |
| **Edge cases** | Supports empty and single-vertex graphs |
| **Testing** | Unit tests for DSU and Kruskal; 50 project tests reported passing during development |

## 🗂️ Project structure

```text
Graph_Algo_Explorer/
├── src/
│   ├── __init__.py
│   └── algorithms/
│       ├── __init__.py
│       ├── dijkstra.py           # Existing teammate contribution
│       ├── min_heap.py           # Existing teammate contribution
│       ├── dsu.py                # ✨ This contribution
│       └── kruskal.py            # ✨ This contribution
├── tests/
│   ├── test_dijkstra.py
│   ├── test_min_heap.py
│   ├── test_dsu.py               # ✨ This contribution
│   └── test_kruskal.py           # ✨ This contribution
├── examples/
├── pyproject.toml
└── README.md
```

## ⚡ Quick start

### 1. Clone the repository

```bash
git clone https://github.com/TanmayK-glitch/Graph_Algo_Explorer.git
cd Graph_Algo_Explorer
```

### 2. Check out the contribution branch

```bash
git fetch origin
git switch samruddhi-kruskal-dsu
```

If the branch is not yet available locally, use:

```bash
git switch --track origin/samruddhi-kruskal-dsu
```

### 3. Run a Kruskal example

From the **repository root**, create a temporary Python script or run this in a Python interpreter:

```python
from src.algorithms.kruskal import kruskal_mst

edges = [
    (0, 1, 1),
    (0, 2, 4),
    (1, 3, 3),
    (2, 3, 2),
    (0, 3, 5),
]

mst_edges, total_weight = kruskal_mst(4, edges)

print("MST edges:", mst_edges)
print("Total weight:", total_weight)
```

**Expected output:**

```text
MST edges: [(0, 1, 1), (2, 3, 2), (1, 3, 3)]
Total weight: 6
```

### 4. Try DSU directly

```python
from src.algorithms.dsu import DisjointSetUnion

dsu = DisjointSetUnion(5)
dsu.union(0, 1)
dsu.union(1, 2)

print(dsu.connected(0, 2))  # True
print(dsu.connected(0, 3))  # False
print(dsu.union(0, 2))      # False: already connected
```

## 🧠 How it works

### Disjoint Set Union (Union-Find)

Initially, every vertex belongs to its own set:

```text
Vertices: 0   1   2   3
Parents:  0   1   2   3
```

After `union(0, 1)` and `union(1, 2)`, vertices `0`, `1`, and `2` are connected. DSU uses:

1. **Path compression:** `find(x)` shortens paths to the root, speeding up future lookups.
2. **Union by rank:** `union(x, y)` attaches a shallower tree below a deeper one, keeping the structure efficient.

`union` returns `False` when two vertices already belong to the same set. Kruskal uses that result to avoid cycles.

### Kruskal's algorithm

1. Sort all edges in ascending order of weight.
2. Visit edges from lightest to heaviest.
3. Use DSU to check whether the edge joins two different components.
4. Accept the edge only when it does **not** create a cycle.
5. Stop after selecting `V - 1` edges.

For the example above:

| Order | Edge | Weight | Decision |
|:--:|:--:|--:|:--|
| 1 | 0–1 | 1 | ✅ Accept |
| 2 | 2–3 | 2 | ✅ Accept |
| 3 | 1–3 | 3 | ✅ Accept — MST complete |

**MST total weight = 1 + 2 + 3 = 6.**

For a disconnected graph, this implementation raises `ValueError` rather than returning a minimum spanning forest.

## 📈 Complexity

Let `V` be the number of vertices and `E` the number of edges.

| Operation | Time complexity |
|:--|:--|
| DSU `find` | `O(α(V))` amortized |
| DSU `union` | `O(α(V))` amortized |
| DSU `connected` | `O(α(V))` amortized |
| Kruskal sorting | `O(E log E)` |
| Kruskal overall | `O(E log E + E α(V))` |

Here `α` is the inverse Ackermann function, which grows extremely slowly. The DSU uses `O(V)` auxiliary space; sorting and storing edges require additional space proportional to `E` in this implementation.

## 🧪 Testing

Install pytest if needed:

```bash
python -m pip install pytest
```

Run only this contribution's tests:

```bash
python -m pytest tests/test_dsu.py tests/test_kruskal.py -v
```

Run the complete project test suite:

```bash
python -m pytest tests/ -v
```

**Development checkpoint:** 50 tests passed across the project when this contribution was tested locally. This is a recorded local result, not a live CI badge.

Test coverage includes initialization, unions, connectivity, path compression, union by rank, MST edge selection, cycle prevention, negative weights, invalid vertices, and disconnected graphs.

## 🔌 API reference

| API | Description | Result |
|:--|:--|:--|
| `DisjointSetUnion(n)` | Create `n` disjoint sets indexed `0..n-1` | DSU object |
| `find(x)` | Get representative of the set containing `x` | `int` |
| `union(x, y)` | Merge two components if distinct | `bool` |
| `connected(x, y)` | Check whether vertices share a component | `bool` |
| `kruskal_mst(num_vertices, edges)` | Compute MST from `(u, v, weight)` tuples | `(mst_edges, total_weight)` |

**Input convention:** Vertices are integer IDs from `0` to `num_vertices - 1`. Edges represent an **undirected** weighted graph.

## 🤝 Team collaboration

This work is part of the **Graph Algorithms Explorer** mini-project.

| Area | Contributor |
|:--|:--|
| Kruskal's MST and DSU | Samruddhi Ombase |
| Dijkstra and MinHeap | Shreyas Joshi |
| Bellman-Ford | Mrudula Dagale (separate branch) |
| Additional algorithms / integration | Tanmay Kangule (in progress at this checkpoint) |

**Contribution branch:** [`samruddhi-kruskal-dsu`](https://github.com/TanmayK-glitch/Graph_Algo_Explorer/tree/samruddhi-kruskal-dsu)  
**Commit:** `e1de69a`  
**Repository:** [TanmayK-glitch/Graph_Algo_Explorer](https://github.com/TanmayK-glitch/Graph_Algo_Explorer)

> Integration note: Agree on a shared base branch before merging teammates' changes. Run the full test suite again after integration.

---

<div align="center">

### 🌟 Built to make graph algorithms easier to understand, test, and extend.

**Graph Algorithms Explorer · Kruskal MST + DSU**

</div>
