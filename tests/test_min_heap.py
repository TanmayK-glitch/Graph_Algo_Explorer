"""Comprehensive tests for :class:`src.algorithms.min_heap.MinHeap`."""

from __future__ import annotations

import math
import unittest

from src.algorithms.min_heap import MinHeap


class TestMinHeapBasic(unittest.TestCase):
    """Basic insertion, extraction, and property tests."""

    def test_insert_and_extract_in_priority_order(self) -> None:
        heap = MinHeap()
        for priority, item in [(5, "e"), (3, "c"), (1, "a"), (4, "d"), (2, "b")]:
            heap.insert(priority, item)

        extracted = [heap.extract_min() for _ in range(5)]
        self.assertEqual(
            extracted,
            [(1, "a"), (2, "b"), (3, "c"), (4, "d"), (5, "e")],
        )

    def test_extract_single_element(self) -> None:
        heap = MinHeap()
        heap.insert(42, "only")
        self.assertEqual(heap.extract_min(), (42, "only"))
        self.assertTrue(heap.is_empty())

    def test_peek_returns_min_without_removing(self) -> None:
        heap = MinHeap()
        heap.insert(10, "ten")
        heap.insert(5, "five")
        self.assertEqual(heap.peek_min(), (5, "five"))
        self.assertEqual(heap.size(), 2)

    def test_size_and_len(self) -> None:
        heap = MinHeap()
        self.assertEqual(heap.size(), 0)
        self.assertEqual(len(heap), 0)
        heap.insert(1, "a")
        heap.insert(2, "b")
        self.assertEqual(heap.size(), 2)
        self.assertEqual(len(heap), 2)
        heap.extract_min()
        self.assertEqual(heap.size(), 1)

    def test_is_empty(self) -> None:
        heap = MinHeap()
        self.assertTrue(heap.is_empty())
        heap.insert(1, "x")
        self.assertFalse(heap.is_empty())
        heap.extract_min()
        self.assertTrue(heap.is_empty())


class TestMinHeapEdgeCases(unittest.TestCase):
    """Edge cases: empty heap, duplicates, negatives, tie-breaking."""

    def test_peek_on_empty_heap_raises(self) -> None:
        heap = MinHeap()
        with self.assertRaises(IndexError):
            heap.peek_min()

    def test_extract_on_empty_heap_raises(self) -> None:
        heap = MinHeap()
        with self.assertRaises(IndexError):
            heap.extract_min()

    def test_duplicate_priorities(self) -> None:
        heap = MinHeap()
        heap.insert(1, "first")
        heap.insert(1, "second")
        heap.insert(1, "third")
        # Insertion-order tie-breaking.
        results = [heap.extract_min() for _ in range(3)]
        self.assertEqual(results[0], (1, "first"))
        self.assertEqual(results[1], (1, "second"))
        self.assertEqual(results[2], (1, "third"))

    def test_negative_priorities(self) -> None:
        heap = MinHeap()
        heap.insert(-5, "neg5")
        heap.insert(0, "zero")
        heap.insert(-3, "neg3")
        heap.insert(2, "two")
        self.assertEqual(heap.extract_min(), (-5, "neg5"))
        self.assertEqual(heap.extract_min(), (-3, "neg3"))
        self.assertEqual(heap.extract_min(), (0, "zero"))
        self.assertEqual(heap.extract_min(), (2, "two"))

    def test_non_comparable_items_with_equal_priorities(self) -> None:
        """Items that cannot be compared (no __lt__) must not cause errors."""

        class Opaque:
            """Intentionally has no comparison operators."""

        a, b, c = Opaque(), Opaque(), Opaque()
        heap = MinHeap()
        heap.insert(0, a)
        heap.insert(0, b)
        heap.insert(0, c)
        # Must not raise TypeError; extracted in insertion order.
        results = [heap.extract_min()[1] for _ in range(3)]
        self.assertIs(results[0], a)
        self.assertIs(results[1], b)
        self.assertIs(results[2], c)

    def test_interleaved_insert_and_extract(self) -> None:
        heap = MinHeap()
        heap.insert(10, "ten")
        heap.insert(4, "four")
        self.assertEqual(heap.extract_min(), (4, "four"))
        heap.insert(7, "seven")
        heap.insert(1, "one")
        self.assertEqual(heap.extract_min(), (1, "one"))
        self.assertEqual(heap.extract_min(), (7, "seven"))
        self.assertEqual(heap.extract_min(), (10, "ten"))
        self.assertTrue(heap.is_empty())


class TestMinHeapInvariant(unittest.TestCase):
    """Verify the heap invariant is maintained after operations."""

    @staticmethod
    def _is_valid_min_heap(data: list) -> bool:
        """Check that every parent ≤ both children."""
        n = len(data)
        for i in range(n):
            left = 2 * i + 1
            right = 2 * i + 2
            if left < n and data[i] > data[left]:
                return False
            if right < n and data[i] > data[right]:
                return False
        return True

    def test_heap_property_after_many_inserts(self) -> None:
        import random

        heap = MinHeap()
        random.seed(42)
        for _ in range(200):
            heap.insert(random.randint(-100, 100), None)
        # Access internal data for invariant check.
        self.assertTrue(self._is_valid_min_heap(heap._data))

    def test_heap_property_after_mixed_operations(self) -> None:
        import random

        heap = MinHeap()
        random.seed(99)
        for _ in range(300):
            if random.random() < 0.7 or heap.is_empty():
                heap.insert(random.randint(-50, 50), "v")
            else:
                heap.extract_min()
        self.assertTrue(self._is_valid_min_heap(heap._data))


class TestMinHeapAdditional(unittest.TestCase):
    """Float priorities, infinity, and heap drain-and-reuse."""

    def test_float_and_infinity_priorities(self) -> None:
        heap = MinHeap()
        heap.insert(math.inf, "inf")
        heap.insert(1.5, "one_half")
        heap.insert(-math.inf, "neg_inf")
        heap.insert(0.0, "zero")

        extracted = [heap.extract_min() for _ in range(4)]
        self.assertEqual(
            extracted,
            [
                (-math.inf, "neg_inf"),
                (0.0, "zero"),
                (1.5, "one_half"),
                (math.inf, "inf"),
            ],
        )

    def test_drain_and_reuse(self) -> None:
        heap = MinHeap()
        for i in [5, 1, 3]:
            heap.insert(i, str(i))
        while not heap.is_empty():
            heap.extract_min()
        self.assertTrue(heap.is_empty())
        self.assertEqual(len(heap), 0)

        # Re-insert and verify normal operation
        heap.insert(10, "ten")
        heap.insert(2, "two")
        self.assertEqual(len(heap), 2)
        self.assertEqual(heap.extract_min(), (2, "two"))
        self.assertEqual(heap.extract_min(), (10, "ten"))

    def test_peek_preserves_insertion_order_tie_breaking(self) -> None:
        heap = MinHeap()
        heap.insert(5, "first")
        heap.insert(5, "second")
        self.assertEqual(heap.peek_min(), (5, "first"))
        self.assertEqual(heap.extract_min(), (5, "first"))
        self.assertEqual(heap.peek_min(), (5, "second"))


if __name__ == "__main__":
    unittest.main()
