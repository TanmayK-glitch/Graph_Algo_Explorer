"""Unit tests for :class:`src.algorithms.radix_heap.RadixHeap`.

Run from the repository root::

    py -m pytest tests/test_radix_heap.py -v
"""

from __future__ import annotations

import unittest

from src.algorithms.radix_heap import RadixHeap


class TestRadixHeapEmpty(unittest.TestCase):
    """Behaviour on an empty heap."""

    def test_is_empty_on_creation(self) -> None:
        rh = RadixHeap()
        self.assertTrue(rh.is_empty())

    def test_len_is_zero_on_creation(self) -> None:
        rh = RadixHeap()
        self.assertEqual(len(rh), 0)

    def test_extract_min_on_empty_raises(self) -> None:
        rh = RadixHeap()
        with self.assertRaises(IndexError):
            rh.extract_min()


class TestRadixHeapSingleElement(unittest.TestCase):
    """Inserting and extracting exactly one element."""

    def test_single_element(self) -> None:
        rh = RadixHeap()
        rh.insert(7, "only")
        self.assertEqual(len(rh), 1)
        self.assertFalse(rh.is_empty())
        key, item = rh.extract_min()
        self.assertEqual(key, 7)
        self.assertEqual(item, "only")
        self.assertTrue(rh.is_empty())

    def test_single_zero_key(self) -> None:
        rh = RadixHeap()
        rh.insert(0, "zero")
        self.assertEqual(rh.extract_min(), (0, "zero"))

    def test_single_large_key(self) -> None:
        large = 10**18  # bigger than any 64-bit int
        rh = RadixHeap()
        rh.insert(large, "big")
        key, item = rh.extract_min()
        self.assertEqual(key, large)
        self.assertEqual(item, "big")


class TestRadixHeapOrder(unittest.TestCase):
    """Extracted keys must always be non-decreasing."""

    def test_increasing_insertion_order(self) -> None:
        rh = RadixHeap()
        for k in [1, 3, 5, 10, 20]:
            rh.insert(k, k)
        extracted = [rh.extract_min()[0] for _ in range(5)]
        self.assertEqual(extracted, sorted(extracted))

    def test_decreasing_insertion_order(self) -> None:
        rh = RadixHeap()
        for k in [20, 10, 5, 3, 1]:
            rh.insert(k, k)
        extracted = [rh.extract_min()[0] for _ in range(5)]
        self.assertEqual(extracted, sorted(extracted))

    def test_random_insertion_order(self) -> None:
        import random

        rh = RadixHeap()
        rng = random.Random(42)
        keys = [rng.randint(0, 1000) for _ in range(50)]
        for k in keys:
            rh.insert(k, k)
        extracted = [rh.extract_min()[0] for _ in range(50)]
        self.assertEqual(extracted, sorted(extracted))
        self.assertTrue(rh.is_empty())


class TestRadixHeapDuplicates(unittest.TestCase):
    """Keys with the same value must all be extractable."""

    def test_duplicate_keys(self) -> None:
        rh = RadixHeap()
        rh.insert(5, "a")
        rh.insert(5, "b")
        rh.insert(5, "c")
        results = sorted(rh.extract_min()[1] for _ in range(3))
        self.assertEqual(results, ["a", "b", "c"])
        self.assertTrue(rh.is_empty())

    def test_duplicate_zero_keys(self) -> None:
        rh = RadixHeap()
        rh.insert(0, 1)
        rh.insert(0, 2)
        keys = [rh.extract_min()[0] for _ in range(2)]
        self.assertEqual(keys, [0, 0])


class TestRadixHeapZeroKeys(unittest.TestCase):
    """Zero-key items must be reachable and extracted first."""

    def test_zero_is_extracted_before_positive(self) -> None:
        rh = RadixHeap()
        rh.insert(5, "five")
        rh.insert(0, "zero")
        rh.insert(3, "three")
        key, _ = rh.extract_min()
        self.assertEqual(key, 0)


class TestRadixHeapLargeIntegers(unittest.TestCase):
    """Python integers can be arbitrarily large; the heap must handle them."""

    def test_very_large_keys(self) -> None:
        rh = RadixHeap()
        big = 2**100
        rh.insert(big, "huge")
        rh.insert(big + 1, "huge+1")
        k1, _ = rh.extract_min()
        k2, _ = rh.extract_min()
        self.assertEqual(k1, big)
        self.assertEqual(k2, big + 1)

    def test_large_then_larger(self) -> None:
        rh = RadixHeap()
        rh.insert(10**15, "a")
        rh.insert(10**15 + 500, "b")
        rh.insert(10**15 + 1, "c")
        keys = [rh.extract_min()[0] for _ in range(3)]
        self.assertEqual(keys, sorted(keys))


class TestRadixHeapMonotonicity(unittest.TestCase):
    """Inserting a key smaller than the last extracted key must raise."""

    def test_key_less_than_d_last_raises(self) -> None:
        rh = RadixHeap()
        rh.insert(10, "ten")
        rh.extract_min()  # d_last = 10
        with self.assertRaises(ValueError):
            rh.insert(5, "five")  # 5 < d_last=10 — illegal

    def test_key_equal_to_d_last_is_allowed(self) -> None:
        """Inserting a key == d_last (same distance) must be permitted."""
        rh = RadixHeap()
        rh.insert(7, "first")
        rh.insert(7, "second")
        rh.extract_min()  # d_last = 7
        # Inserting another item with the same key must not raise.
        rh.insert(7, "same")
        key, item = rh.extract_min()
        self.assertEqual(key, 7)
        self.assertEqual(item, "same")


class TestRadixHeapInvalidKeys(unittest.TestCase):
    """Incorrect key types and negative keys must be rejected immediately."""

    def test_float_key_raises(self) -> None:
        rh = RadixHeap()
        with self.assertRaises(TypeError):
            rh.insert(1.5, "x")

    def test_string_key_raises(self) -> None:
        rh = RadixHeap()
        with self.assertRaises(TypeError):
            rh.insert("five", "x")  # type: ignore[arg-type]

    def test_bool_key_raises(self) -> None:
        """Booleans are a subclass of int in Python but should be rejected."""
        rh = RadixHeap()
        with self.assertRaises(TypeError):
            rh.insert(True, "x")  # type: ignore[arg-type]

    def test_negative_key_raises(self) -> None:
        rh = RadixHeap()
        with self.assertRaises(ValueError):
            rh.insert(-1, "x")


class TestRadixHeapRepeatedInsertExtract(unittest.TestCase):
    """Interleaved insertions and extractions must stay correct."""

    def test_interleaved_operations(self) -> None:
        rh = RadixHeap()
        rh.insert(0, "a")
        rh.insert(3, "b")
        self.assertEqual(rh.extract_min()[0], 0)   # d_last = 0
        rh.insert(1, "c")
        rh.insert(5, "d")
        self.assertEqual(rh.extract_min()[0], 1)   # d_last = 1
        self.assertEqual(rh.extract_min()[0], 3)   # d_last = 3
        self.assertEqual(rh.extract_min()[0], 5)   # d_last = 5
        self.assertTrue(rh.is_empty())

    def test_len_decreases_on_extract(self) -> None:
        rh = RadixHeap()
        for k in [2, 4, 6]:
            rh.insert(k, None)
        self.assertEqual(len(rh), 3)
        rh.extract_min()
        self.assertEqual(len(rh), 2)
        rh.extract_min()
        self.assertEqual(len(rh), 1)
        rh.extract_min()
        self.assertEqual(len(rh), 0)

    def test_non_comparable_items(self) -> None:
        """Items with no comparison operators must never be compared."""

        class Opaque:
            """No __lt__, __eq__ etc."""

        a, b = Opaque(), Opaque()
        rh = RadixHeap()
        rh.insert(0, a)
        rh.insert(0, b)
        # Must not raise TypeError from comparing a and b.
        results = {rh.extract_min()[1], rh.extract_min()[1]}
        self.assertEqual(results, {a, b})


class TestRadixHeapInvariants(unittest.TestCase):
    """Test bucket invariants: monotonicity of bounds, interval containment, bucket 0."""

    def test_bounds_and_bucket_containment_invariants(self) -> None:
        import random

        rng = random.Random(12345)
        rh = RadixHeap()
        current_min = 0

        for step in range(150):
            if not rh.is_empty() and rng.random() < 0.4:
                key, _ = rh.extract_min()
                self.assertGreaterEqual(key, current_min)
                current_min = key
            else:
                k = current_min + rng.randint(0, 500)
                rh.insert(k, f"val_{step}")

            # Verify Invariant 1: _u is monotonically non-decreasing
            for i in range(len(rh._u) - 1):
                self.assertLessEqual(rh._u[i], rh._u[i + 1])

            # Verify Invariant 2: Bucket 0 property: _u[1] - _u[0] == 1
            self.assertEqual(rh._u[1] - rh._u[0], 1)

            # Verify Invariant 3: Bucket containment: all items in bucket i have _u[i] <= key < _u[i+1]
            for i, bucket in enumerate(rh._buckets):
                for key, _ in bucket:
                    self.assertGreaterEqual(key, rh._u[i])
                    self.assertLess(key, rh._u[i + 1])

            # Verify Invariant 4: Bucket 0 entries have key == d_last
            for key, _ in rh._buckets[0]:
                self.assertEqual(key, rh._d_last)


class TestRadixHeapRandomizedHeapq(unittest.TestCase):
    """Randomized sequence of operations matching heapq."""

    def test_randomized_trials_vs_heapq(self) -> None:
        import heapq
        import random

        rng = random.Random(999)
        for _ in range(50):
            rh = RadixHeap()
            hq: list[int] = []
            cur_min = 0

            for _step in range(80):
                if not hq or rng.random() < 0.6:
                    k = cur_min + rng.randint(0, 2000)
                    if rng.random() < 0.1:
                        k += 10**25  # Large arbitrary precision integer
                    rh.insert(k, k)
                    heapq.heappush(hq, k)
                else:
                    k_rh, _ = rh.extract_min()
                    k_hq = heapq.heappop(hq)
                    self.assertEqual(k_rh, k_hq)
                    cur_min = k_rh

            # Drain remainder
            while hq:
                k_rh, _ = rh.extract_min()
                k_hq = heapq.heappop(hq)
                self.assertEqual(k_rh, k_hq)
                cur_min = k_rh
            self.assertTrue(rh.is_empty())


if __name__ == "__main__":
    unittest.main()
