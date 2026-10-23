"""Worklet 1 of the Graph Algorithms Explorer: graph model, traversal and connectivity.

Sub-packages: ``graph`` (model and representations), ``algorithms`` (strategy-pattern
algorithms returning :class:`AlgorithmResult`) and ``io`` (edge-list loader).
Always import as ``worklet1.io``; never put the ``worklet1`` directory itself on
``sys.path`` because its ``io`` package would shadow the standard-library ``io``.
"""

__version__ = "1.0.0"
