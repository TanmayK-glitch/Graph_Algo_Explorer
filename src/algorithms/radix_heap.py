"""One-level Radix Heap — a monotone priority queue for non-negative integer keys.

Background & Literature
-----------------------
A **monotone priority queue** is a priority queue where every inserted key
must be greater than or equal to the most recently extracted key (``d_last``).
Dijkstra's shortest-path algorithm with non-negative edge weights naturally
satisfies this monotonicity condition.

The one-level Radix Heap was introduced by Ahuja, Mehlhorn, Orlin, and Tarjan
(1990) and extensively analysed by Cherkassky, Goldberg, and Radzik (1996),
as well as Costa, Castro, and Freitas (2025).

How the Standard One-Level Radix Heap Works
--------------------------------------------
A standard one-level Radix Heap maintains a dynamic sequence of buckets
``_buckets[0], _buckets[1], ..., _buckets[K]`` and an array of bucket
bounds ``_u[0], _u[1], ..., _u[K+1]``.

Bucket Invariant
~~~~~~~~~~~~~~~~
1. **Monotonic bounds:**
   ``_u[0] <= _u[1] <= _u[2] <= ... <= _u[K+1]``
2. **Disjoint intervals:**
   Bucket ``i`` stores entries whose keys lie in the half-open interval
   ``[_u[i], _u[i+1])``.
3. **Bucket 0 property:**
   ``_u[1] - _u[0] == 1`` always. Since all keys are integers, Bucket 0
   contains **only** entries with key equal to ``_u[0]`` (which is ``d_last``).
4. **Bucket capacities:**
   ``_u[i+1] - _u[i] <= 2^(max(0, i-1))`` for all ``i >= 1``.
   Specifically, Bucket 0 has capacity 1, Bucket 1 has capacity 1,
   Bucket 2 has capacity 2, Bucket 3 has capacity 4, Bucket 4 has capacity 8,
   and in general Bucket ``i`` has capacity at most ``2^(i-1)``.

Why the First Non-Empty Bucket Always Contains the Global Minimum
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Because the bucket intervals partition the keyspace from ``_u[0]`` upwards:
- Bucket 0 holds keys in ``[_u[0], _u[1])``.
- Bucket 1 holds keys in ``[_u[1], _u[2])`` where ``_u[1] >= _u[0]``.
- Higher buckets ``k > j`` hold keys in ``[_u[k], _u[k+1])`` where ``_u[k] >= _u[j+1]``.

When Bucket 0 is empty, let ``j`` be the **smallest index such that bucket ``j``
is non-empty**.
Because buckets ``0, 1, ..., j-1`` are empty, all entries in the heap have
keys ``>= _u[j]``. All entries in buckets ``k > j`` have keys ``>= _u[j+1]``.
Therefore, the **global minimum of the entire heap is strictly inside bucket ``j``**.
No other bucket ever needs to be inspected.

How Extraction and Redistribution Work
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. If Bucket 0 is non-empty, pop any element directly in O(1). Its key is
   guaranteed to be ``_u[0] == d_last``.
2. If Bucket 0 is empty:
   a. Find the first non-empty bucket ``j`` by scanning bucket pointers
      (at most ``K = O(log C)`` checks).
   b. Find ``new_min = min(key for key, _ in _buckets[j])`` by scanning
      **only** bucket ``j``.
   c. Set ``d_last = new_min``.
   d. Update the bounds for buckets ``0`` through ``j``:
      - ``_u[0] = new_min``
      - ``_u[1] = new_min + 1``
      - For ``k = 2`` to ``j``:
        ``_u[k] = min(_u[j+1], new_min + 2^(k-1))``
      - Bounds for buckets ``> j`` are **not changed**.
   e. Redistribute all entries from bucket ``j`` into the newly reconfigured
      buckets ``0, 1, ..., j-1``.
      Since every key in bucket ``j`` satisfies ``key - new_min < 2^(j-1)``,
      every redistributed item strictly lands in a bucket index ``< j``.
   f. The entries with key equal to ``new_min`` now land in Bucket 0.
      Pop one of them and return it.

Complexity Analysis
~~~~~~~~~~~~~~~~~~~
- **Space:** ``O(B + N)`` where ``B = O(log C)`` is the number of buckets
  and ``N`` is the number of elements in the heap.
- **insert():**
  Finding the bucket via binary search on ``_u`` takes ``O(log B) = O(log log C)``
  comparisons. Appending to the bucket takes ``O(1)``. Extending buckets takes
  ``O(log C)`` total across the lifetime of the heap.
- **extract_min():**
  - If Bucket 0 is non-empty: ``O(1)``.
  - If Bucket 0 is empty:
    Finding the first non-empty bucket takes ``O(B) = O(log C)`` time.
    Updating the bounds ``_u[0...j]`` takes ``O(j) <= O(log C)`` time.
    Redistributing items from bucket ``j``:
    Define potential function ``Phi = sum(bucket_index(item) for item in heap)``.
    Each insertion increases ``Phi`` by at most ``B = O(log C)``.
    Every time an item is redistributed, its bucket index decreases by at least 1,
    releasing at least 1 unit of potential to pay for the move.
    An item can be redistributed at most ``B = O(log C)`` times before reaching
    Bucket 0.
    Therefore, the amortised cost of ``extract_min()`` is **O(log C)**.
- **Total Dijkstra complexity with RadixHeap:**
  ``O(E + V log C)`` where ``C`` is the maximum edge weight or distance difference.

Support for Arbitrary Large Integer Keys
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The bucket array dynamically expands whenever a key ``>= _u[-1]`` is inserted.
Python's arbitrary-precision integers mean there is no 32-bit or 64-bit limitation.
"""

from __future__ import annotations

import bisect
from typing import Any


class RadixHeap:
    """One-level Radix Heap for non-negative integer keys.

    This is a monotone priority queue: every key inserted must be greater than
    or equal to the last key extracted (``d_last``).

    Parameters
    ----------
    None — the heap starts empty with ``d_last = 0``.

    Examples
    --------
    >>> rh = RadixHeap()
    >>> rh.insert(0, "source")
    >>> rh.insert(3, "A")
    >>> rh.insert(1, "B")
    >>> rh.extract_min()
    (0, 'source')
    >>> rh.extract_min()
    (1, 'B')
    >>> rh.extract_min()
    (3, 'A')
    """

    def __init__(self) -> None:
        # d_last is the key of the last extracted item (starts at 0).
        # Every newly inserted key must be >= d_last.
        self._d_last: int = 0

        # _buckets is a list of lists holding (key, item) tuples.
        # _buckets[i] contains entries whose keys lie in [_u[i], _u[i+1]).
        self._buckets: list[list[tuple[int, Any]]] = [[]]

        # _u maintains the lower bounds of each bucket.
        # _u[i] is the inclusive lower bound for _buckets[i].
        # _u[i+1] is the exclusive upper bound for _buckets[i].
        # Invariant: _u[0] <= _u[1] <= ... <= _u[-1].
        # Initially, bucket 0 covers [0, 1).
        self._u: list[int] = [0, 1]

        # Track total number of entries so is_empty() and __len__() are O(1).
        self._size: int = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def insert(self, key: int, item: Any) -> None:
        """Insert an item with the given non-negative integer key.

        Parameters
        ----------
        key:
            A non-negative integer. Must be >= the last extracted key.
        item:
            Any Python object to associate with this key.

        Raises
        ------
        TypeError
            If ``key`` is not an integer (e.g. a float or bool).
        ValueError
            If ``key`` is negative, or less than ``d_last``
            (which violates the monotonicity requirement).

        Time complexity: O(log log C) worst-case (binary search over bounds).
        """
        _validate_key(key, self._d_last)

        # Dynamically extend buckets if key exceeds the current upper bound.
        self._ensure_capacity_for(key)

        # Find the bucket index i such that _u[i] <= key < _u[i+1].
        # bisect_right finds the insertion point after all bounds <= key.
        # Subtracting 1 gives the highest index i where _u[i] <= key.
        bucket_index = bisect.bisect_right(self._u, key) - 1
        self._buckets[bucket_index].append((key, item))
        self._size += 1

    def extract_min(self) -> tuple[int, Any]:
        """Remove and return the ``(key, item)`` pair with the smallest key.

        Raises
        ------
        IndexError
            If the heap is empty.

        Time complexity: O(log C) amortised, where C is the maximum key difference.
        """
        if self._size == 0:
            raise IndexError("extract_min() called on an empty RadixHeap")

        # Step 1: If bucket 0 contains items, pop directly.
        # Bucket 0 has range [_u[0], _u[1]) of width 1, so all its items
        # have key == _u[0] == d_last. Popping from bucket 0 is O(1).
        if self._buckets[0]:
            self._size -= 1
            return self._buckets[0].pop()

        # Step 2: Find the smallest index j such that _buckets[j] is non-empty.
        # By the bucket invariant, all items in buckets k > j have keys >= _u[j+1]
        # >= min(keys in bucket j). Thus the global minimum is GUARANTEED to be
        # in bucket j. We do NOT scan any other bucket.
        j = 1
        while j < len(self._buckets) and not self._buckets[j]:
            j += 1

        if j >= len(self._buckets):  # pragma: no cover
            raise RuntimeError("RadixHeap: internal size is inconsistent with bucket contents")

        # Step 3: Scan ONLY bucket j to find the minimum key.
        new_min = min(k for k, _ in self._buckets[j])
        self._d_last = new_min

        # Step 4: Update bounds _u[0...j] to partition [new_min, _u[j+1]).
        # Bounds for buckets > j remain completely untouched.
        self._u[0] = new_min
        self._u[1] = new_min + 1
        for k in range(2, j + 1):
            self._u[k] = min(self._u[j + 1], new_min + (1 << (k - 1)))

        # Step 5: Redistribute all items from bucket j into buckets 0...j-1.
        items_to_redistribute = self._buckets[j]
        self._buckets[j] = []
        for key, item in items_to_redistribute:
            # All items in bucket j satisfy key < _u[j+1], so they will
            # land strictly in buckets 0...j-1.
            new_idx = bisect.bisect_right(self._u, key, 0, j + 1) - 1
            self._buckets[new_idx].append((key, item))

        # Step 6: Bucket 0 now contains all items with key == new_min.
        self._size -= 1
        return self._buckets[0].pop()

    def is_empty(self) -> bool:
        """Return ``True`` if the heap contains no entries.

        Time complexity: O(1).
        """
        return self._size == 0

    def __len__(self) -> int:
        """Return the number of entries currently in the heap.

        Time complexity: O(1).
        """
        return self._size

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_capacity_for(self, key: int) -> None:
        """Extend ``_buckets`` and ``_u`` dynamically so that ``_u[-1] > key``.

        Each new bucket k (for k >= 1) is given capacity 2^(k-1), maintaining
        the standard Radix Heap capacity invariant:
        _u[k+1] - _u[k] <= 2^(k-1).
        """
        while key >= self._u[-1]:
            k = len(self._buckets)
            self._buckets.append([])
            self._u.append(self._u[-1] + (1 << (k - 1)))

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"RadixHeap(d_last={self._d_last}, size={self._size})"


# ------------------------------------------------------------------
# Module-level helpers (not part of the public API)
# ------------------------------------------------------------------


def _validate_key(key: int, d_last: int) -> None:
    """Raise an informative error if ``key`` is invalid."""
    if isinstance(key, bool) or not isinstance(key, int):
        raise TypeError(
            f"RadixHeap keys must be non-negative integers, got {type(key).__name__!r}"
        )
    if key < 0:
        raise ValueError(f"RadixHeap keys must be non-negative, got {key}")
    if key < d_last:
        raise ValueError(
            f"RadixHeap is monotone: key {key} is less than last extracted key {d_last}"
        )
