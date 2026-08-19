# V1B Retrieval

`memory/retrieval.py::retrieve_relevant_memory()`. Smallest transparent
mechanism that works (order section 13) -- no embeddings, no vector
database, no RAG, no external search service (hard boundary, order
section 13/28).

## Signals, all explainable

1. Shared canonical Thesis Family id with the classification result.
2. Shared canonical Territory id with the classification result.
3. Shared topic label (exact, case-insensitive match against the record's
   own `topic_labels`).
4. Shared literal word between the interpretation text and the record's
   `original_text` -- the SAME `engine/text_utils.py::normalize_words()`
   approach `engine/classification.py` and `engine/comparison.py` already
   use. No new matching algorithm invented for V1B.

Every `MemoryRetrievalMatch.matched_signals` lists exactly which of the
above fired, and `why_retrieved` is built directly from that list --
`tests/test_v1b_retrieval.py::test_10_every_retrieval_match_explains_why`
asserts every listed signal literally appears in the explanation text.

## No fabricated precision (order section 14)

There is no numeric similarity score anywhere in `memory/retrieval.py` or
`memory/comparison.py`. A match either has explainable signals or it
doesn't exist in the result -- never a "0.873 relevance" that can't be
audited by reading the code.

## Why comparison is richer than retrieval

Retrieval answers "was this record found, and why." Comparison
(`memory/comparison.py::compare_to_editorial_memory()`) goes further per
match: which canonical relations actually overlap, which topics overlap,
which literal terms overlap (only for full-text records), the record's
`text_completeness` and `publication_status`, and a per-status evidence
boundary note (order section 14, 18). See `docs/V1B_MEMORY_BOUNDARY.md`.
