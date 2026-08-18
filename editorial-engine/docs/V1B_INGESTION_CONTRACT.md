# V1B Ingestion Contract

`memory/ingestion.py` is the one place the data pack is read. No database,
no external storage -- a deterministic, file-backed, in-memory
representation (order section 10).

## source_facts vs analytical_enrichment (order section 9)

`memory/models.py::MemorySourceFacts` and `MemoryAnalyticalEnrichment` are
two separate Pydantic models, not two groups of fields on one model.
`MemorySourceFacts` is `frozen=True` -- a real technical guarantee, not
just a naming convention, mirroring `schema.RawInput`'s own
`frozen=True`. Re-classifying a record means constructing a NEW
`MemoryAnalyticalEnrichment`; there is no code path that can write into an
existing `MemorySourceFacts` (`tests/test_v1b_ingestion.py::test_6_*`).

| Source facts (immutable) | Analytical enrichment (replaceable) |
|---|---|
| `original_text`, `text_completeness` | `thesis_family_id`, `series_id` |
| `language`, `channel`, `source` | `territory_relation` |
| `publication_status`, `publication_evidence` | `topic_labels` |
| `dates` (raw strings only, order section 19) | `confidence` (`EvidenceCertainty`, reused canonical enum) |
| `url`, `post_id` (always None in this pack) | |

## Validation performed at ingestion (order section 10, TEST 7)

1. Every record's `thesis_family_id` / `series_id`, if set, must exist in
   the REAL canonical registries (`canonical_data/thesis_family_registry.py`,
   `canonical_data/series_registry.py`) -- an unknown id raises
   `MemoryIngestionError`, never a silent pass-through.
2. `content_id` uniqueness is checked.
3. `text_completeness` and `publication_status` must be one of their real
   enum values.
4. `territory_relation` is set ONLY via the same deterministic word-overlap
   check `engine/classification.py` already uses (order section 11) --
   never free redactional interpretation, never accepted un-checked from
   the pack.

## Dates (order section 19)

`MemoryDates` never parses a date into `datetime`. Every field is the raw
string the source actually carries, or `None`. `source_or_created_date`
and `verified_publication_date` are always kept as separate fields, so a
"when this was drafted" date can never be mistaken for a "when this was
published" date.
