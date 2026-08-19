# V1C Does Not Do

Mirrors `docs/V1A_DOES_NOT_DO.md` and `docs/V1B_DOES_NOT_DO.md`'s
discipline for the variation-analysis layer.

## No generator (order section 32)

Nothing in `variation/` writes a hook, opening, scene, closing line, CTA,
signature, caption, or any Swedish/English publication text.
`ControlledVariationOption.proposed_changes` maps a dimension name to a
short enum-style value (e.g. `"entry_mode": "question"`) -- never prose
(`tests/test_v1c_pipeline.py::test_30_*` asserts every proposed value is
under 60 characters). V1C can say "use `scene_to_insight` with
`close_human` distance and `unresolved_tension` closure" -- it cannot and
does not write the scene.

## No Quality Gate (order section 33)

V1C never judges whether a finished text is good, publishable, or
authentic -- there is no finished text yet at this stage of the chain.

## No RAG / embeddings / vector database (order section 34)

`variation/comparison.py` and `variation/options.py` use only plain
Python dict/set operations over enum values -- no `numpy`, `sklearn`,
`torch`, `chromadb`, `faiss`, `pinecone`, `weaviate`, and no external
retrieval or similarity service anywhere in `variation/`.

## No canonical schema change (order section 35)

`schema/`, `canonical_data/`, and `fixtures/` are byte-identical before
and after this order (confirmed via `git diff` and
`tests/test_v1c_pipeline.py::test_27_*`). No new canonical entity was
created for Entry Mode, Lens, Narrative Distance, Structural Arc,
Disclosure Pace, Rhetorical Pressure, Emotional Temperature, Closure
Mode, or Sustained Narrative Form (order section 4) -- all nine remain,
at most, plain Python enums inside `variation/models.py`.

## V1A and V1B are not rewritten (order section 1)

Zero lines changed in `engine/`, `memory/`, `schema/`, `canonical_data/`,
or `fixtures/`. `variation/pipeline.py::run_v1c_variation_analysis()`
imports `engine.models.CandidateAngle` and `memory.models.EditorialMemoryRecord`
for reuse only -- it never modifies either module. All 174 pre-existing
tests (76 canonical + 51 V1A + 47 V1B) pass unmodified alongside V1C's
own 39.

## Sustained Narrative Form is not implemented

No dialog engine, no storytelling engine, no scene generator, no
narrator engine -- Work classified this dimension EXPLORATORY, and
`variation/models.py` has no enum, no field, and no code path for it
anywhere (order section 6, 29).

## Voice Core and Reader Feedback are untouched

No file under `variation/` imports anything from `schema/voice.py` or
`canonical_data/reader_feedback_registry.py`
(`tests/test_v1c_comparison.py::test_23_*`,
`tests/test_v1c_pipeline.py::test_8_*`). Parastoo's review is never used
to choose an opening, structural arc, emotional temperature, or closure
(order section 30) -- Reader Feedback stays evidence about reader effect,
never a Variation Rule.

## No UI / API / website integration

Nothing under `variation/` starts a server, exposes an endpoint, or
touches `app/`, the house, Adam, `physical-house.tsx`, navigation,
Akademin, Runda bordet, PR-rummet, SEO, sitemap, or robots. All V1C code
lives under `editorial-engine/`.

## Future extension points (documented, not built -- order section 45)

- A larger, more representative corpus before any dimension is
  considered for canonical promotion.
- Better structural retrieval than plain dimension-matching.
- A full Variation Engine that actually varies finished text.
- A generator, once Variation + Quality Gate both exist.
- A revision/adaptation graph richer than V1B's single known relation.
- Multilingual variation analysis (only 3 of 21 source records are
  English).
