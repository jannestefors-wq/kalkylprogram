"""
LUF Editorial Engine V1A -- first vertical chain.

Raw Idea -> Interpretation -> Canonical Classification -> Existing Content
Comparison -> Candidate Angles -> Recommended Angle -> Human Decision.

Pure domain logic. No generator, no UI, no API, no RAG/embeddings, no
network calls required to run the test suite. See docs/V1A_PURPOSE.md,
docs/V1A_DOES_NOT_DO.md, docs/V1A_PIPELINE.md,
docs/V1A_CANONICAL_BOUNDARY.md, docs/V1A_HUMAN_AUTHORITY.md,
docs/V1A_MEMORY_LIMITATION.md, docs/V1A_FUTURE_EXTENSION_POINTS.md.

This package depends on `schema/` and `canonical_data/` only. It never
depends on `fixtures/` (fixtures are test illustration, not something
domain logic should rely on) and nothing here is imported back into
`schema/` or `canonical_data/`.
"""
