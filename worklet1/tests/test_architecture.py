"""Architecture checks: FR-19, NFR-01/02/03/04/05/07, stub-graph independence, io shadowing."""

import ast
import importlib
import pkgutil
import sys
from pathlib import Path

import pytest

import worklet1
from worklet1.algorithms import (
    Algorithm,
    BFSAlgorithm,
    BipartiteTestAlgorithm,
    ConnectedComponentsAlgorithm,
    CycleDetectionAlgorithm,
    DFSAlgorithm,
    SCCAlgorithm,
    TopologicalSortAlgorithm,
)
from worklet1.graph import Edge, Graph, VertexNotFoundError

PKG = Path(worklet1.__file__).parent
ALGO_FILES = sorted((PKG / "algorithms").glob("*.py"))
FORBIDDEN_ATTRS = {"_adj", "_matrix", "_index", "_vertices", "_rank", "_directed", "_weighted"}
FORBIDDEN_IMPORTS = {"adj_list", "adj_matrix", "AdjacencyListGraph", "AdjacencyMatrixGraph"}


def parse(path):
    return ast.parse(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("path", ALGO_FILES, ids=lambda p: p.name)
def test_algorithms_never_touch_representation_internals(path):
    for node in ast.walk(parse(path)):
        if isinstance(node, ast.Attribute):
            assert node.attr not in FORBIDDEN_ATTRS, f"{path.name}: .{node.attr}"
        if isinstance(node, ast.ImportFrom):
            assert not ({a.name for a in node.names} & FORBIDDEN_IMPORTS), path.name
            assert "adj_" not in (node.module or ""), path.name
        if isinstance(node, ast.Import):
            assert all("adj_" not in a.name for a in node.names)


def test_only_stdlib_and_package_imports():
    stdlib = set(sys.stdlib_module_names)
    for path in PKG.rglob("*.py"):
        if "tests" in path.parts:
            continue
        for node in ast.walk(parse(path)):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                names = [node.module.split(".")[0]]
            for name in names:
                assert name in stdlib or name == "worklet1", f"{path.name} imports {name}"


def test_required_module_layout():
    for rel in ["graph/base.py", "graph/adj_list.py", "graph/adj_matrix.py", "algorithms/base.py",
                "algorithms/bfs.py", "algorithms/dfs.py", "algorithms/connected_components.py",
                "algorithms/scc.py", "algorithms/cycle_detection.py",
                "algorithms/topological_sort.py", "algorithms/bipartite.py",
                "io/edge_list_loader.py"]:
        assert (PKG / rel).is_file(), rel


def test_public_api_has_docstrings():
    missing = []
    for path in PKG.rglob("*.py"):
        if "tests" in path.parts:
            continue
        tree = parse(path)
        if not ast.get_docstring(tree):
            missing.append(f"{path.name}: module")
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
                if not ast.get_docstring(node):
                    missing.append(f"{path.name}: class {node.name}")
                for item in node.body:
                    if (isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                            and (not item.name.startswith("_") or item.name == "__init__")
                            and not ast.get_docstring(item)):
                        missing.append(f"{path.name}: {node.name}.{item.name}")
        for item in tree.body:
            if (isinstance(item, ast.FunctionDef) and not item.name.startswith("_")
                    and not ast.get_docstring(item)):
                missing.append(f"{path.name}: {item.name}")
    assert not missing, missing


def test_bfs_is_iterative_and_uses_deque():
    src = (PKG / "algorithms" / "bfs.py").read_text()
    assert "deque" in src and "popleft" in src
    for node in ast.walk(parse(PKG / "algorithms" / "bfs.py")):
        if isinstance(node, ast.FunctionDef):
            calls = [n.func.id for n in ast.walk(node) if isinstance(n, ast.Call)
                     and isinstance(n.func, ast.Name)]
            assert node.name not in calls, f"{node.name} is recursive"


def test_dfs_uses_a_stack_via_recursion():
    tree = parse(PKG / "algorithms" / "dfs.py")
    inner = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "_visit"]
    assert inner and any(isinstance(c, ast.Call) and getattr(c.func, "id", "") == "_visit"
                         for c in ast.walk(inner[0]))


def test_stdlib_io_not_shadowed():
    import io

    assert io.__name__ == "io" and hasattr(io, "StringIO")
    assert importlib.import_module("worklet1.io").__name__ == "worklet1.io"


def test_all_modules_import():
    for info in pkgutil.walk_packages(worklet1.__path__, "worklet1."):
        importlib.import_module(info.name)


class StubGraph(Graph):
    """Minimal third representation: proves algorithms need only the Graph interface."""

    def __init__(self, directed, edges, verts):
        super().__init__(directed=directed)
        self._v = list(verts)
        self._e = list(edges)

    @property
    def vertices(self):
        return list(self._v)

    def add_vertex(self, v): raise NotImplementedError
    def remove_vertex(self, v): raise NotImplementedError
    def add_edge(self, u, v, weight=None): raise NotImplementedError
    def remove_edge(self, u, v): raise NotImplementedError

    def has_edge(self, u, v):
        return v in self.neighbours(u)

    def neighbours(self, v):
        if v not in self._v:
            raise VertexNotFoundError(v)
        out = [b for a, b in self._e if a == v]
        if not self._directed:
            out += [a for a, b in self._e if b == v and a != v]
        return sorted(out, key=self._v.index)

    def all_edges(self):
        return [Edge(a, b) for a, b in self._e]

    def vertex_count(self): return len(self._v)
    def edge_count(self): return len(self._e)
    def edge_weight(self, u, v): return None


def test_every_algorithm_runs_on_a_stub_graph():
    d = StubGraph(True, [("A", "B"), ("B", "C")], "ABC")
    u = StubGraph(False, [("A", "B"), ("C", "D")], "ABCD")
    assert BFSAlgorithm().execute(d, start="A").primary_output == ["A", "B", "C"]
    assert DFSAlgorithm().execute(d, start="A").primary_output == ["A", "B", "C"]
    assert SCCAlgorithm().execute(d).primary_output == [["A"], ["B"], ["C"]]
    assert TopologicalSortAlgorithm().execute(d).primary_output == ["A", "B", "C"]
    assert CycleDetectionAlgorithm().execute(d).primary_output is False
    assert ConnectedComponentsAlgorithm().execute(u).primary_output == [["A", "B"], ["C", "D"]]
    assert BipartiteTestAlgorithm().execute(u).primary_output is True


def test_algorithms_are_interchangeable_strategies():
    algos = [BFSAlgorithm(), DFSAlgorithm(), ConnectedComponentsAlgorithm(), SCCAlgorithm(),
             CycleDetectionAlgorithm(), TopologicalSortAlgorithm(), BipartiteTestAlgorithm()]
    assert all(isinstance(a, Algorithm) for a in algos)
    assert [a.name for a in algos] == ["BFS", "DFS", "ConnectedComponents", "SCC",
                                       "CycleDetection", "TopologicalSort", "BipartiteTest"]
