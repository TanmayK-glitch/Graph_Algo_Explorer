"""Algorithm layer: strategy-pattern algorithms that use only the public Graph interface."""

from .base import Algorithm, AlgorithmResult
from .bfs import BFSAlgorithm, bfs, bfs_all
from .bipartite import BipartiteTestAlgorithm
from .connected_components import ConnectedComponentsAlgorithm
from .cycle_detection import CycleDetectionAlgorithm
from .dfs import DFSAlgorithm, dfs, dfs_all
from .scc import SCCAlgorithm
from .topological_sort import TopologicalSortAlgorithm

__all__ = [
    "Algorithm",
    "AlgorithmResult",
    "BFSAlgorithm",
    "BipartiteTestAlgorithm",
    "ConnectedComponentsAlgorithm",
    "CycleDetectionAlgorithm",
    "DFSAlgorithm",
    "SCCAlgorithm",
    "TopologicalSortAlgorithm",
    "bfs",
    "bfs_all",
    "dfs",
    "dfs_all",
]
