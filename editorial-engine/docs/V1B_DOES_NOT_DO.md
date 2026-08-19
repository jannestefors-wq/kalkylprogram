# V1B Does Not Do

Mirrors `docs/V1A_DOES_NOT_DO.md`'s discipline for the new memory layer.

## No generator (order section 25)

No LinkedIn post, article, caption, hook, CTA, or signature -- in Swedish
or English -- is produced anywhere in `memory/*.py`. Output stays at
`CandidateAngle` + `RecommendationResult` + (separately, human-called)
`HumanDecision`, exactly like V1A. `V1BPipelineResult` has no `final_text`
or `generated_post` field (`tests/test_v1b_pipeline.py::test_22_*`).

## No Variation Engine yet (order section 26)

Memory is used to assess repetition and prompt a search for contrast --
never to drive rhythm/opening/form/emotional rotation. No such rotation
logic exists in `memory/*.py`.

## No Quality Gate yet (order section 27)

V1B still operates entirely before finished text exists. `schema.QualityAssessment`
is untouched and unused by `memory/*.py`.

## No RAG / embeddings / vector database (order section 13/28)

`memory/retrieval.py` and `memory/comparison.py` use only
`engine/text_utils.py::normalize_words()` -- the same plain word-overlap
approach V1A already uses. No `numpy`, `sklearn`, `torch`, `chromadb`,
`faiss`, `pinecone`, `weaviate`, or any external retrieval service appears
anywhere under `memory/`.

## No UI / API / website integration (order section 29)

Nothing under `memory/` starts a server, exposes an endpoint, or touches
`app/`, the house, Adam, `physical-house.tsx`, navigation, Akademin, Runda
bordet, PR-rummet, SEO, sitemap, or robots. All V1B code lives under
`editorial-engine/`.

## V1A is not rewritten (order section 22)

Zero lines changed in `schema/`, `canonical_data/`, `engine/`, or
`fixtures/`. `memory/pipeline.py::run_v1b_pipeline()` is an ADDITIVE new
function that imports and reuses V1A's existing step functions
(`engine.interpretation`, `engine.classification`, `engine.angles`,
`engine.recommendation`) directly -- `engine/pipeline.py::run_v1a_pipeline`
itself is untouched, and all 127 original tests keep passing unmodified
(`tests/test_v1b_pipeline.py::test_24_v1a_pipeline_still_works_unmodified`).

## Voice Core and Reader Feedback are untouched (order section 23-24)

No file under `memory/` imports anything from `schema/voice.py` or
`canonical_data/reader_feedback_registry.py`
(`tests/test_v1b_pipeline.py::test_20_*`, `test_21_*`). Parastoo's review
stays exactly where Final Canonical Data Closure put it -- it is never
copied into Editorial Memory as if it were author-corpus content.

## No canonical schema change (order section 21)

`schema/*.py` is byte-identical before and after V1B (confirmed via
`git status --porcelain schema/` and JSON Schema regeneration -- see the
V1B Slutrapport).
