# V1B Corpus

Source: `LUF_Editorial_Memory_Corpus_Inventory_V1B.md` /
`LUF_Editorial_Memory_Data_Pack_V1B.json` /
`LUF_Editorial_Memory_Readiness_Report_V1B.md`, delivered by Work and
approved by project management. Copied verbatim into
`memory/data/LUF_Editorial_Memory_Data_Pack_V1B.json`.

## The 21 records

| Group | Count | text_completeness | publication_status |
|---|---:|---|---|
| content-work-001..012 | 12 | full | unverified_draft_or_work_material |
| content-other-001..006 | 6 | partial | unknown |
| content-published-001..003 | 3 | partial | published_verified |

## Why only 12 are the fulltext comparison corpus

Order section 4: only the 12 `content-work-*` records have complete,
source-bound text. `memory/comparison.py::compare_to_editorial_memory()`
only ever computes `text_overlap_terms` when
`text_completeness == TextCompleteness.FULL` -- structurally, not by
convention (`tests/test_v1b_comparison.py::test_2_fulltext_comparison_corpus_is_exactly_the_12_work_records`,
`test_15_fulltext_overlap_only_computed_for_full_records`). The other 9
records still participate in retrieval/comparison via canonical relations
and topic labels (metadata signals, not literal running text), never via
a fabricated "as if we had the full text" comparison.

## Version/revision relation

`content-other-005` carries one documented `version_revision` relation
(earlier draft / later revised opening) as a single content record, not
two independent ideas (`memory/models.py::MemoryRelation`,
`tests/test_v1b_comparison.py::test_16_version_revision_relation_is_preserved_as_one_record`).

## Territory

Zero territory relations in this corpus (order section 11). Verified with
the SAME deterministic word-overlap check `engine/classification.py`
already uses against Territory names -- not accepted as-is from Work
without a check (`memory/ingestion.py::_territory_relation_for`,
`tests/test_v1b_ingestion.py::test_8_*`). Confirms Work's own finding
rather than silently trusting it.

## Taxonomy gaps (order section 12 -- not solved here)

Work identified missing canonical taxonomy for: form, opening type, ending
type, emotional register, narrator perspective. V1B does not create a
Format Registry, Opening Registry, Ending Registry, Emotion Registry, or
Narrator Registry. These fields are simply absent from
`EditorialMemoryRecord` -- left empty, not guessed.

## Future Data Enrichment (order section 35 -- documented, not solved)

Blocking for any claim about complete publishing history:
- Complete LinkedIn export or post URLs/IDs and full captions.
- Confirmed public/private status for the 12 full-text WORK items.
- Verified publication dates (0 in this pack).

Not blocking for this bounded V1B memory, but useful later:
- A larger English corpus (currently 3 of 21 records).
- Historic performance data.
- A fuller adaptation/revision graph (currently 1 relation known).
- Canonical form/opening/ending/emotion/narrator taxonomies.

None of these are addressed in V1B. They remain open, exactly as Work's
own Readiness Report already flagged them.
