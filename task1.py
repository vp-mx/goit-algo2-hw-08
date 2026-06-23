"""Task 1. Optimizing data access with an LRU cache.

The program demonstrates how an LRU cache speeds up repeated "hot"
Range queries against a large array of numbers.
"""

import random
import time
from collections import OrderedDict


class LRUCache:
    """A simple LRU cache backed by OrderedDict.

    get(key)  -> returns the value, or -1 on a cache-miss (key absent);
    put(key)  -> stores the value, evicting the least-recently-used entry
                 when capacity is exceeded.
    """

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: "OrderedDict[tuple, int]" = OrderedDict()

    def get(self, key):
        if key not in self.cache:
            return -1
        # mark the key as most-recently used
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            # evict the least-recently-used entry
            self.cache.popitem(last=False)

    def invalidate_index(self, index: int) -> None:
        """Remove every cached range (L, R) that contains index."""
        keys_to_remove = [
            (left, right)
            for (left, right) in self.cache
            if left <= index <= right
        ]
        for key in keys_to_remove:
            del self.cache[key]


# Global cache with capacity K = 1000 (function signatures are fixed by the task).
cache = LRUCache(1000)


# ---------------------------------------------------------------------------
# Functions without caching
# ---------------------------------------------------------------------------
def range_sum_no_cache(array, left, right):
    """Return the sum of array[left : right + 1] without caching."""
    return sum(array[left:right + 1])


def update_no_cache(array, index, value):
    """Update an array element without caching."""
    array[index] = value


# ---------------------------------------------------------------------------
# Functions with LRU caching
# ---------------------------------------------------------------------------
def range_sum_with_cache(array, left, right):
    """Return the sum of array[left : right + 1] using the LRU cache."""
    key = (left, right)
    result = cache.get(key)
    if result != -1:                      # cache-hit
        return result
    result = sum(array[left:right + 1])   # cache-miss — compute and store
    cache.put(key, result)
    return result


def update_with_cache(array, index, value):
    """Update an array element and invalidate every range containing it."""
    array[index] = value
    cache.invalidate_index(index)


# ---------------------------------------------------------------------------
# Query generation (provided in the task)
# ---------------------------------------------------------------------------
def make_queries(n, q, hot_pool=30, p_hot=0.95, p_update=0.03):
    hot = [(random.randint(0, n // 2), random.randint(n // 2, n - 1))
           for _ in range(hot_pool)]
    queries = []
    for _ in range(q):
        if random.random() < p_update:        # ~3% of queries are Update
            idx = random.randint(0, n - 1)
            val = random.randint(1, 100)
            queries.append(("Update", idx, val))
        else:                                 # ~97% are Range
            if random.random() < p_hot:        # 95% — "hot" ranges
                left, right = random.choice(hot)
            else:                              # 5% — random ranges
                left = random.randint(0, n - 1)
                right = random.randint(left, n - 1)
            queries.append(("Range", left, right))
    return queries


# ---------------------------------------------------------------------------
# Execution and timing
# ---------------------------------------------------------------------------
def run_no_cache(array, queries):
    for query in queries:
        if query[0] == "Range":
            range_sum_no_cache(array, query[1], query[2])
        else:
            update_no_cache(array, query[1], query[2])


def run_with_cache(array, queries):
    for query in queries:
        if query[0] == "Range":
            range_sum_with_cache(array, query[1], query[2])
        else:
            update_with_cache(array, query[1], query[2])


def main():
    n = 100_000
    q = 50_000

    array = [random.randint(1, 100) for _ in range(n)]
    queries = make_queries(n, q)

    # --- Without cache (run on a copy so both runs are identical) ---
    array_no_cache = array.copy()
    start = time.time()
    run_no_cache(array_no_cache, queries)
    time_no_cache = time.time() - start

    # --- With the LRU cache ---
    array_with_cache = array.copy()
    cache.cache.clear()
    start = time.time()
    run_with_cache(array_with_cache, queries)
    time_with_cache = time.time() - start

    speedup = time_no_cache / time_with_cache if time_with_cache else float("inf")

    print(f"Без кешу :  {time_no_cache:.2f} c")
    print(f"LRU-кеш  :  {time_with_cache:.2f} c  (прискорення ×{speedup:.1f})")


if __name__ == "__main__":
    main()
