"""Tests for KnowledgeBench: fact-store query benchmark."""

import pytest

from knowledgebench import FactStore, benchmark_queries


def test_lookup_direct_and_via_alias():
    store = FactStore()
    store.add("alice", "knows", "bob")
    store.add_alias("ali", "alice")
    assert store.lookup("alice", "knows") == ["bob"]
    assert store.lookup("ali", "knows") == ["bob"]


def test_reverse_lookup():
    store = FactStore()
    store.add("alice", "knows", "bob")
    store.add("carol", "knows", "bob")
    assert store.reverse_lookup("bob", "knows") == ["alice", "carol"]


def test_chain_transitive():
    store = FactStore()
    store.add("a", "feeds", "b")
    store.add("b", "feeds", "c")
    store.add("c", "feeds", "d")
    assert store.chain("a", "feeds", max_hops=3) == {"b", "c", "d"}
    assert store.chain("a", "feeds", max_hops=1) == {"b"}
    with pytest.raises(ValueError):
        store.chain("a", "feeds", max_hops=0)


def test_add_validation():
    store = FactStore()
    with pytest.raises(ValueError):
        store.add("", "p", "o")
    with pytest.raises(ValueError):
        store.add_alias("", "x")


def test_benchmark_queries_returns_four_patterns():
    rows = benchmark_queries(n_facts=100, n_queries=10, seed=1)
    patterns = [r["pattern"] for r in rows]
    assert patterns == ["direct_lookup", "alias_lookup", "transitive_chain", "reverse_lookup"]
    for r in rows:
        assert r["queries"] == 10
        assert r["seconds"] >= 0.0
        assert 0.0 <= r["hit_rate"] <= 1.0


def test_benchmark_deterministic_hit_rates():
    a = benchmark_queries(n_facts=80, n_queries=20, seed=7)
    b = benchmark_queries(n_facts=80, n_queries=20, seed=7)
    assert [r["hit_rate"] for r in a] == [r["hit_rate"] for r in b]
