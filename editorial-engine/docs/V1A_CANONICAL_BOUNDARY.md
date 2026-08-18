# V1A Canonical Boundary

**Canonical data** = `schema/*.py` sanningsformer, fyllda med verkligt
innehall i `canonical_data/` (16 Series, 8 Thesis Families, 1 Territory,
Voice Core, Parastoo Ebrahimzadehs ReaderFeedback). Detta ar redaktionell
sanning, godkand av projektledningen, och andras aldrig av V1A.

**Analysis output** = allt i `engine/models.py`
(`ClassificationResult`, `ComparisonResult`, `CandidateAngle`,
`RecommendationResult`, `InterpretationDraft`, `V1APipelineResult`, ...).
Detta ar en enskild korknings resultat -- inte sanning, inte
publiceringsbart, och sparas ingenstans i `canonical_data/`.

## Konkreta regler

1. `engine/*.py` importerar ENDAST `load_*()`-funktioner fran
   `canonical_data/` -- konstruerar aldrig `Series(...)`,
   `ThesisFamily(...)`, `Territory(...)` eller `ReaderFeedback(...)`
   sjalv. Verifierat strukturellt av
   `tests/test_v1a_canonical_boundary.py::test_17_engine_module_never_imports_or_writes_to_canonical_data_source`.
2. `CandidateAngle.angle` ar en riktig `schema.Angle` -- men den skrivs
   aldrig in i `canonical_data/`. Den ar en analysprodukt tills en
   manniska godkanner den (och annu da hanteras skrivningen av ett
   framtida, separat beslutat lager -- se
   `docs/V1A_FUTURE_EXTENSION_POINTS.md`).
3. `ConfidenceLevel` (engine-only) ar ALDRIG samma sak som
   `EvidenceCertainty`/`VoicePrincipleStatus` (canonical). Ett
   `CanonicalMatch` med `confidence=HIGH` andrar INTE den matchade
   Thesis Familyns/Territoryts egen `Provenance.certainty`.
4. `RepetitionRiskLevel` (engine-only) ar inte samma sak som
   `RepetitionSignal` (canonical katalog over kanda risker). En hog
   repetitionsrisk for EN kandidatvinkel i EN korning skriver inte till
   den canonical katalogen.
5. Klassificering skapar aldrig en ny `Series`/`ThesisFamily`/`Territory`
   -- om inget matchar returneras `NO_CONFIDENT_CANONICAL_MATCH`
   (`tests/test_v1a_classification.py::test_classification_never_invents_a_new_thesis_family_series_or_territory`).

## Testat, inte bara dokumenterat

`tests/test_v1a_canonical_boundary.py` laser om registren fore/efter en
pipeline-korning och kraver bit-for-bit identisk JSON. Se ocksa
`tests/test_v1a_classification.py` och
`tests/test_v1a_canonical_boundary.py::test_18_no_content_record_is_ever_constructed_by_the_pipeline`.
