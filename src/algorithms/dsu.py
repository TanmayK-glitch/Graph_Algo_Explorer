"""Disjoint Set Union (Union-Find) data structure.

This module provides a DisjointSetUnion class that efficiently
manages disjoint sets using path compression and union by rank.

Complexities:
    find       : O(alpha(n)) amortized
    union      : O(alpha(n)) amortized
    connected  : O(alpha(n)) amortized

Here alpha(n) is the inverse Ackermann function, which grows
extremely slowly.
"""

from __future__ import annotations


class DisjointSetUnion:
    """Manage disjoint sets using path compression and union by rank.

    Initially, each element belongs to its own set.

    Parameters
    ----------
    n:
        Number of elements, indexed from 0 to n-1.
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def __init__(self, n: int) -> None:
        if n < 0:
            raise ValueError("Number of elements cannot be negative")

        self.parent: list[int] = list(range(n))
        self.rank: list[int] = [0] * n

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def find(self, x: int) -> int:
        """Return the representative of the set containing x.

        Uses path compression to shorten future searches.

        Time complexity: O(alpha(n)) amortized.
        """
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])

        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        """Merge the sets containing x and y.

        Returns True if the sets were merged.
        Returns False if both elements already belong
        to the same set.

        Time complexity: O(alpha(n)) amortized.
        """
        root_x = self.find(x)
        root_y = self.find(y)

        if root_x == root_y:
            return False

        # Attach the shorter tree under the taller tree.
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y

        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x

        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1

        return True

    def connected(self, x: int, y: int) -> bool:
        """Check whether x and y belong to the same set."""
        return self.find(x) == self.find(y)

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"DisjointSetUnion(parent={self.parent}, rank={self.rank})"
