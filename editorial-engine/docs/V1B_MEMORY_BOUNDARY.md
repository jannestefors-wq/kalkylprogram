# V1B Memory Boundary

This is V1B's most important rule (order section 7: "Detta ska vara
tekniskt skyddat, inte bara dokumenterat").

## What the system knows

Exactly the 21 content units in
`memory/data/LUF_Editorial_Memory_Data_Pack_V1B.json`, ingested via
`memory/ingestion.py`. 12 of them with full, comparable text; 9 with only
partial text (opening lines/titles). This is a small slice of Work
material, conversation drafts, and LinkedIn screenshots -- not a complete
publication history (see `docs/V1B_CORPUS.md` for the exact counts).

## What the system does NOT know

Everything not in that file: the rest of Jan Stefors' actual publication
history, any complete LinkedIn export, exact publication dates (0 verified
in this pack), post URLs/IDs, or the full English corpus. See
`docs/V1B_CORPUS.md`'s "Future Data Enrichment" section for the standing
gap list -- unsolved by design (order section 35: "Los dem inte").

## The technical guarantee, not just the documentation

1. `MemoryComparisonOutcome` / retrieval results only ever say
   `NO_MATCH_IN_AVAILABLE_MEMORY` (or an empty match list) when nothing is
   found -- never a "never published"/"never used" claim. This is enforced
   the same way V1A enforces it: a fixed, immutable note
   (`EDITORIAL_MEMORY_BOUNDARY_NOTE`, `memory/models.py`) is attached to
   EVERY `MemoryRetrievalResult` and `MemoryComparisonResult`, and V1A's
   own `NEVER_PUBLISHED_CLAIM_FORBIDDEN_NOTE` (`engine/models.py`) is
   carried alongside it unchanged, not paraphrased.
2. `MemoryComparisonResult.corpus_size` and `.fulltext_corpus_size` always
   report exactly how many records were actually compared against, so the
   scope of any claim is visible in the data, not just assumed.
3. `tests/test_v1b_paths.py::test_novelty_boundary_path_expresses_no_match_correctly`
   and `tests/test_v1b_retrieval.py::test_11_memory_boundary_note_present_and_never_a_never_published_claim`
   assert this directly, at the object level -- not just by reading prose.

## Publication status is never collapsed

`PublicationStatus` (`memory/models.py`) has three real values --
`published_verified`, `unverified_draft_or_work_material`, `unknown` --
and there is no boolean `published` field anywhere in
`EditorialMemoryRecord`. `memory/comparison.py`'s
`_EVIDENCE_BOUNDARY_BY_STATUS` gives each status its own explicit note
about what it can and cannot support (order section 18), attached to every
match.
