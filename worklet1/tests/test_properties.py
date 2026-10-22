"""Mathematical-property tests on seeded random graphs, checked against independent oracles."""

import itertools
import random
from collections import deque

import pytest

from worklet1.algorithms import (
    BFSAlgorithm,
    BipartiteTestAlgorithm,
    ConnectedComponentsAlgorithm,
    CycleDetectionAlgorithm,
    DFSAlgorithm,
    SCCAlgorithm,
    TopologicalSortAlgorithm,
)
from worklet1.graph import AdjacencyListGraph, AdjacencyMatrixGraph

SEEDS = range(40)


def random_edges(rng, n, p, directed, loops):
    edges = []
    for u in range(n):
        for v in range(n):
            if u == v and not loops:
                continue
            if not directed and v < u:
                continue
            if rng.random() < p:
                edges.append((u, v))
    return edges


def build(cls, n, edges, directed):
    g = cls(directed=directed)
    for v in range(n):
        g.add_vertex(v)
    for u, v in edges:
        g.add_edge(u, v)
    return g


def case(seed, directed):
    rng = random.Random(seed)
    n = rng.randint(0, 9)
    return n, random_edges(rng, n, rng.choice([0.1, 0.25, 0.5]), directed, loops=seed % 4 == 0)


def reach(n, adj):
    """Independent oracle: reachability closure via Floyd-Warshall on booleans."""
    r = [[False] * n for _ in range(n)]
    for u in range(n):
        r[u][u] = True
        for v in adj[u]:
            r[u][v] = True
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if r[i][k] and r[k][j]:
                    r[i][j] = True
    return r


def adjacency(n, edges, directed):
    adj = {u: set() for u in range(n)}
    for u, v in edges:
        adj[u].add(v)
        if not directed:
            adj[v].add(u)
    return adj


@pytest.mark.parametrize("directed", [False, True])
@pytest.mark.parametrize("seed", SEEDS)
def test_representations_are_equivalent(seed, directed):
    n, edges = case(seed, directed)
    a = build(AdjacencyListGraph, n, edges, directed)
    b = build(AdjacencyMatrixGraph, n, edges, directed)
    assert a.vertices == b.vertices and a.all_edges() == b.all_edges()
    assert a.edge_count() == b.edge_count() == len(edges)
    for v in a.vertices:
        assert a.neighbours(v) == b.neighbours(v)
    # same random removals keep them equivalent
    rng = random.Random(seed)
    for v in rng.sample(a.vertices, k=min(2, len(a.vertices))):
        a.remove_vertex(v)
        b.remove_vertex(v)
    assert a.vertices == b.vertices and a.all_edges() == b.all_edges()
    assert a.edge_count() == b.edge_count() == len(a.all_edges())


@pytest.mark.parametrize("cls", [AdjacencyListGraph, AdjacencyMatrixGraph])
@pytest.mark.parametrize("seed", SEEDS)
def test_undirected_symmetry_and_handshake(cls, seed):
    n, edges = case(seed, False)
    g = build(cls, n, edges, False)
    loops = sum(1 for u, v in edges if u == v)
    for u in g.vertices:
        for v in g.neighbours(u):
            assert g.has_edge(v, u) and u in g.neighbours(v)
    assert sum(len(g.neighbours(v)) for v in g.vertices) == 2 * len(edges) - loops


@pytest.mark.parametrize("cls", [AdjacencyListGraph, AdjacencyMatrixGraph])
@pytest.mark.parametrize("seed", SEEDS)
def test_bfs_distances_and_dfs_reachability(cls, seed):
    n, edges = case(seed, seed % 2 == 0)
    directed = seed % 2 == 0
    g = build(cls, n, edges, directed)
    adj = adjacency(n, edges, directed)
    r = reach(n, adj)
    for s in range(n):
        reachable = {v for v in range(n) if r[s][v]}
        res = BFSAlgorithm().execute(g, start=s)
        assert set(res.primary_output) == reachable == set(DFSAlgorithm().execute(g, start=s).primary_output)
        dist = {s: 0}
        queue = deque([s])
        while queue:  # independent reference BFS
            u = queue.popleft()
            for v in sorted(adj[u]):
                if v not in dist:
                    dist[v] = dist[u] + 1
                    queue.append(v)
        parent = res.metadata["parent"]
        for v in res.primary_output:
            hops, x = 0, v
            while parent[x] is not None:
                x, hops = parent[x], hops + 1
            assert hops == dist[v]  # BFS tree paths are shortest paths
        order_dist = [dist[v] for v in res.primary_output]
        assert order_dist == sorted(order_dist)  # non-decreasing distance


@pytest.mark.parametrize("cls", [AdjacencyListGraph, AdjacencyMatrixGraph])
@pytest.mark.parametrize("seed", SEEDS)
def test_connected_components_partition_oracle(cls, seed):
    n, edges = case(seed, False)
    g = build(cls, n, edges, False)
    r = reach(n, adjacency(n, edges, False))
    comps = ConnectedComponentsAlgorithm().execute(g).primary_output
    flat = [v for c in comps for v in c]
    assert sorted(flat) == list(range(n))
    for c in comps:
        for u, v in itertools.product(c, c):
            assert r[u][v]
    for c1, c2 in itertools.combinations(comps, 2):
        assert not r[c1[0]][c2[0]]


@pytest.mark.parametrize("cls", [AdjacencyListGraph, AdjacencyMatrixGraph])
@pytest.mark.parametrize("seed", SEEDS)
def test_scc_matches_mutual_reachability(cls, seed):
    n, edges = case(seed, True)
    g = build(cls, n, edges, True)
    r = reach(n, adjacency(n, edges, True))
    comps = SCCAlgorithm().execute(g).primary_output
    expected = {frozenset(v for v in range(n) if r[u][v] and r[v][u]) for u in range(n)}
    assert {frozenset(c) for c in comps} == expected
    assert sorted(v for c in comps for v in c) == list(range(n))


@pytest.mark.parametrize("cls", [AdjacencyListGraph, AdjacencyMatrixGraph])
@pytest.mark.parametrize("seed", SEEDS)
def test_directed_cycle_iff_topological_sort_fails(cls, seed):
    n, edges = case(seed, True)
    g = build(cls, n, edges, True)
    r = reach(n, adjacency(n, edges, True))
    oracle = any(r[v][u] for u, v in edges)  # an edge u->v lying on a closed walk
    assert CycleDetectionAlgorithm().execute(g).primary_output is oracle
    topo = TopologicalSortAlgorithm().execute(g)
    assert topo.success is (not oracle)
    if topo.success:
        pos = {v: i for i, v in enumerate(topo.primary_output)}
        assert sorted(pos) == list(range(n))
        assert all(pos[u] < pos[v] for u, v in edges)


@pytest.mark.parametrize("cls", [AdjacencyListGraph, AdjacencyMatrixGraph])
@pytest.mark.parametrize("seed", SEEDS)
def test_undirected_cycle_oracle(cls, seed):
    n, edges = case(seed, False)
    g = build(cls, n, edges, False)
    comps = ConnectedComponentsAlgorithm().execute(g).metadata["count"]
    forest = len(edges) == n - comps  # acyclic iff |E| = |V| - #components (no loops)
    assert CycleDetectionAlgorithm().execute(g).primary_output is (not forest)


@pytest.mark.parametrize("cls", [AdjacencyListGraph, AdjacencyMatrixGraph])
@pytest.mark.parametrize("seed", SEEDS)
def test_bipartite_matches_brute_force(cls, seed):
    n, edges = case(seed, False)
    g = build(cls, n, edges, False)
    brute = any(all(col[u] != col[v] for u, v in edges)
                for col in itertools.product((0, 1), repeat=n))
    res = BipartiteTestAlgorithm().execute(g)
    assert res.primary_output is brute
    if brute:
        colouring = res.metadata["colouring"]
        assert all(colouring[u] != colouring[v] for u, v in edges)


@pytest.mark.parametrize("seed", SEEDS)
def test_algorithms_identical_on_both_representations(seed):
    for directed in (False, True):
        n, edges = case(seed, directed)
        a = build(AdjacencyListGraph, n, edges, directed)
        b = build(AdjacencyMatrixGraph, n, edges, directed)
        algos = [CycleDetectionAlgorithm()]
        algos += [SCCAlgorithm(), TopologicalSortAlgorithm()] if directed else [
            ConnectedComponentsAlgorithm(), BipartiteTestAlgorithm()]
        for algo in algos:
            ra, rb = algo.execute(a), algo.execute(b)
            assert (ra.primary_output, ra.metadata, ra.success) == (rb.primary_output, rb.metadata, rb.success)
        for mode in ("all",):
            for cls in (BFSAlgorithm, DFSAlgorithm):
                assert cls().execute(a, mode=mode).primary_output == cls().execute(b, mode=mode).primary_output
