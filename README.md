# KnowledgeBench

[![CI](https://github.com/kapildhinwa2010-dev/KnowledgeBench/actions/workflows/ci.yml/badge.svg)](https://github.com/kapildhinwa2010-dev/KnowledgeBench/actions/workflows/ci.yml)
[![CodeQL](https://github.com/kapildhinwa2010-dev/KnowledgeBench/actions/workflows/codeql.yml/badge.svg)](https://github.com/kapildhinwa2010-dev/KnowledgeBench/actions/workflows/codeql.yml)

Benchmark fact-store query patterns: direct lookup, aliases, transitive chains, reverse lookup.

## What it does

Builds a synthetic in-memory fact store of (subject, predicate, object)
triples plus aliases, then times and scores four query patterns: direct
lookup, alias-resolved lookup, transitive chaining over one predicate,
and reverse lookup. Each pattern reports wall-clock seconds and the
fraction of queries that returned at least one result.

    from knowledgebench import benchmark_queries

    for row in benchmark_queries(n_facts=200, n_queries=50):
        print(row["pattern"], row["seconds"], row["hit_rate"])

## API

- FactStore.add / add_alias / resolve / lookup / reverse_lookup / chain
- benchmark_queries(n_facts, n_queries, seed) - one row per pattern

## Honest results and limitations

- Timings are wall-clock on whatever machine runs the benchmark; only
  relative comparisons between patterns on the same run are meaningful.
- The store is a list scanned linearly; hit rates and timings reflect that
  design, not any indexed store.
- Hit rates depend on the synthetic vocabulary sizes; with dense random
  facts almost every query hits.
- The chain is limited to one predicate per query and max_hops hops.

## Status

Part of the kapildhinwa2010-dev toolkit experiments. CI and CodeQL run on
every push to main. License: MIT.
