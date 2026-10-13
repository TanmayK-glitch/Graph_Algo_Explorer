"""Reusable min-heap data structure.

This module provides a :class:`MinHeap` built from scratch on a plain
Python list.  Entries are stored as ``(priority, _counter, item)``
triples so that items with equal priorities are extracted in insertion
order and **arbitrary (potentially non-comparable) item objects never
need to be compared**.

Complexities (where *n* is the number of entries in the heap):

+--------------+----------+
| Operation    | Time     |
+==============+==========+
| insert       | O(log n) |
+--------------+----------+
| extract_min  | O(log n) |
+--------------+----------+
| peek_min     | O(1)     |
+--------------+----------+
| is_empty     | O(1)     |
+--------------+----------+
| size / len   | O(1)     |
+--------------+----------+
"""

from __future__ import annotations

from typing import Any


class MinHeap:
    """A binary min-heap that stores ``(priority, item)`` pairs.

    Internally each entry is augmented with a monotonically increasing
    counter so that entries with **equal priorities** are ordered by
    insertion time, avoiding any comparison of the *item* objects.

    Parameters
    ----------
    None

    Examples
    --------
    >>> heap = MinHeap()
    >>> heap.insert(3, "C")
    >>> heap.insert(1, "A")
    >>> heap.insert(2, "B")
    >>> heap.extract_min()
    (1, 'A')
    >>> len(heap)
    2
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def __init__(self) -> None:
        self._data: list[tuple[float | int, int, Any]] = []
        self._counter: int = 0  # monotonic tie-breaker

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def insert(self, priority: float | int, item: Any) -> None:
        """Add an entry to the heap.

        Parameters
        ----------
        priority:
            Numeric priority (lower == higher priority).
            Negative values are allowed.
        item:
            Arbitrary payload associated with this priority.

        Time complexity: O(log n).
        """
        entry = (priority, self._counter, item)
        self._counter += 1
        self._data.append(entry)
        self._heapify_up(len(self._data) - 1)

    def peek_min(self) -> tuple[float | int, Any]:
        """Return the ``(priority, item)`` pair with the lowest priority.

        Raises
        ------
        IndexError
            If the heap is empty.

        Time complexity: O(1).
        """
        if not self._data:
            raise IndexError("peek_min() called on an empty MinHeap")
        priority, _counter, item = self._data[0]
        return (priority, item)

    def extract_min(self) -> tuple[float | int, Any]:
        """Remove and return the ``(priority, item)`` pair with the lowest priority.

        Raises
        ------
        IndexError
            If the heap is empty.

        Time complexity: O(log n).
        """
        if not self._data:
            raise IndexError("extract_min() called on an empty MinHeap")
        # Swap root with last element, pop, then restore heap property.
        self._swap(0, len(self._data) - 1)
        priority, _counter, item = self._data.pop()
        if self._data:
            self._heapify_down(0)
        return (priority, item)

    def is_empty(self) -> bool:
        """Return ``True`` if the heap contains no entries.

        Time complexity: O(1).
        """
        return len(self._data) == 0

    def size(self) -> int:
        """Return the number of entries in the heap.

        Time complexity: O(1).
        """
        return len(self._data)

    def __len__(self) -> int:
        """Return the number of entries in the heap.

        Supports the built-in ``len()`` protocol.

        Time complexity: O(1).
        """
        return len(self._data)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _heapify_up(self, index: int) -> None:
        """Restore the heap property by bubbling *index* upward."""
        while index > 0:
            parent = (index - 1) // 2
            if self._data[index] < self._data[parent]:
                self._swap(index, parent)
                index = parent
            else:
                break

    def _heapify_down(self, index: int) -> None:
        """Restore the heap property by sinking *index* downward."""
        size = len(self._data)
        while True:
            smallest = index
            left = 2 * index + 1
            right = 2 * index + 2

            if left < size and self._data[left] < self._data[smallest]:
                smallest = left
            if right < size and self._data[right] < self._data[smallest]:
                smallest = right

            if smallest != index:
                self._swap(index, smallest)
                index = smallest
            else:
                break

    def _swap(self, i: int, j: int) -> None:
        """Swap two entries in the internal list."""
        self._data[i], self._data[j] = self._data[j], self._data[i]

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        entries = [(p, item) for p, _c, item in self._data]
        return f"MinHeap({entries})"
