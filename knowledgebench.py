# KnowledgeBench - Benchmark fact-store query patterns: direct, alias, chain, reverse
# Part of the Kapildhinwa2010-dev Toolkit.

"""KnowledgeBench - fact-store query benchmark.

Lineage: knowledge-layer repos. Builds a small in-memory fact store of
(subject, predicate, object) triples with aliases, then times and scores
four query patterns: direct lookup, alias resolution, transitive chaining
and reverse lookup.

Timings are wall-clock on the machine running the benchmark; treat them
as relative comparisons, not absolute numbers.
"""

from __future__ import annotations

import random
import time

__all__ = ["FactStore", "benchmark_queries"]


class FactStore:
    """Minimal fact store: triples, aliases, transitive chains, reverse lookup."""

    def __init__(self) -> None:
        self._facts = []
        self._aliases = {}

    def add(self, subject: str, predicate: str, obj: str) -> None:
        if not subject or not predicate or not obj:
            raise ValueError("subject, predicate and object must be non-empty")
        self._facts.append((subject, predicate, obj))

    def add_alias(self, alias: str, canonical: str) -> None:
        if not alias or not canonical:
            raise ValueError("alias and canonical must be non-empty")
        self._aliases[alias] = canonical

    def resolve(self, name: str) -> str:
        return self._aliases.get(name, name)

    def lookup(self, subject: str, predicate: str) -> list:
        """Direct lookup: objects for (subject, predicate)."""
        s = self.resolve(subject)
        return [o for (sub, pred, o) in self._facts if sub == s and pred == predicate]

    def reverse_lookup(self, obj: str, predicate: str) -> list:
        """Reverse lookup: subjects with predicate pointing at obj."""
        return sorted({s for (s, pred, o) in self._facts if o == obj and pred == predicate})

    def chain(self, subject: str, predicate: str, max_hops: int = 3) -> set:
        """Transitive closure over one predicate, up to max_hops."""
        if max_hops < 1:
            raise ValueError("max_hops must be >= 1")
        frontier = {self.resolve(subject)}
        seen = set(frontier)
        reached = set()
        for _ in range(max_hops):
            nxt = set()
            for (s, pred, o) in self._facts:
                if s in frontier and pred == predicate and o not in seen:
                    nxt.add(o)
            reached |= nxt
            seen |= nxt
            frontier = nxt
            if not frontier:
                break
        return reached

    def __len__(self) -> int:
        return len(self._facts)


def benchmark_queries(n_facts: int = 200, n_queries: int = 50, seed: int = 0) -> list:
    """Build a synthetic store and time the four query patterns.

    Returns one row per pattern: queries run, wall-clock seconds and the
    fraction of queries that returned at least one result.
    """
    if n_facts < 1 or n_queries < 1:
        raise ValueError("n_facts and n_queries must be >= 1")
    rng = random.Random(seed)
    store = FactStore()
    subjects = ["s{}".format(i) for i in range(20)]
    predicates = ["p0", "p1", "p2"]
    objects = ["o{}".format(i) for i in range(50)]
    for _ in range(n_facts):
        store.add(rng.choice(subjects), rng.choice(predicates), rng.choice(objects))
    for i in range(0, 20, 2):
        store.add_alias("alias{}".format(i), "s{}".format(i))

    rows = []

    t0 = time.perf_counter()
    hits = 0
    for _ in range(n_queries):
        if store.lookup(rng.choice(subjects), rng.choice(predicates)):
            hits += 1
    rows.append({"pattern": "direct_lookup", "queries": n_queries,
                 "seconds": time.perf_counter() - t0, "hit_rate": hits / n_queries})

    alias_names = ["alias{}".format(i) for i in range(0, 20, 2)]
    t0 = time.perf_counter()
    hits = 0
    for _ in range(n_queries):
        if store.lookup(rng.choice(alias_names), rng.choice(predicates)):
            hits += 1
    rows.append({"pattern": "alias_lookup", "queries": n_queries,
                 "seconds": time.perf_counter() - t0, "hit_rate": hits / n_queries})

    t0 = time.perf_counter()
    hits = 0
    for _ in range(n_queries):
        if store.chain(rng.choice(subjects), rng.choice(predicates), max_hops=3):
            hits += 1
    rows.append({"pattern": "transitive_chain", "queries": n_queries,
                 "seconds": time.perf_counter() - t0, "hit_rate": hits / n_queries})

    t0 = time.perf_counter()
    hits = 0
    for _ in range(n_queries):
        if store.reverse_lookup(rng.choice(objects), rng.choice(predicates)):
            hits += 1
    rows.append({"pattern": "reverse_lookup", "queries": n_queries,
                 "seconds": time.perf_counter() - t0, "hit_rate": hits / n_queries})

    return rows
