# V1A Pipeline

Varje steg ar ett eget, separat testbart modul under `engine/`. Ingen mapp
byggdes bara for arkitekturens skull -- strukturen ar flat, samma monster
som `schema/`, `canonical_data/`, `fixtures/`.

```
engine/
  models.py          V1A-only analysis-output-modeller (ej canonical data)
  text_utils.py       delad ord-overlappningshjalp (klassificering + jamforelse)
  provider.py         AnalysisProvider-interface + RuleBasedAnalysisProvider
  interpretation.py   Steg 1-2: Raw Idea -> Interpretation
  classification.py   Steg 3: Canonical Classification
  comparison.py        Steg 4: Existing Content Comparison
  angles.py             Steg 5: Candidate Angles
  recommendation.py     Steg 6: Recommended Angle
  human_decision.py     Steg 7: Human Decision
  pipeline.py            Orkestrerar steg 1-6 (run_v1a_pipeline)
```

## Steg-for-steg-ansvar

### 1-2. Raw Idea -> Interpretation (`interpretation.py`)
- `build_raw_input()` skapar en oforanderlig `schema.RawInput`.
- `build_interpretation_draft()` anropar `AnalysisProvider.interpret()`,
  som returnerar `observation`/`interpretation`/`inference`-lager
  (`engine/models.py::AnalysisLayer`). Kastar `InsufficientContextError`
  om ravaran ar for tunn.
- `render_idea_interpretation()` kondenserar lagren till en canonical
  `schema.IdeaInterpretation`, med `Provenance(created_by=AI_SYSTEM,
  analysis_logic_version="interpretation-v1a-1.0")`.
- `build_idea()` bygger den canonical `schema.Idea`.

### 3. Canonical Classification (`classification.py`)
- `classify()` jamfor tolkningstexten mot de riktiga registren
  (`canonical_data/series_registry.py`, `thesis_family_registry.py`,
  `territory_registry.py`) via enkel ord-overlappning.
- Returnerar `ClassificationResult` med matchningar PER register, eller
  `ClassificationOutcome.NO_CONFIDENT_CANONICAL_MATCH`.
- Skapar aldrig nya registerposter.

### 4. Existing Content Comparison (`comparison.py`)
- `compare_to_existing_content()` jamfor mot vilken `ContentRecord`-lista
  som helst som anroparen skickar in ("tillganglig canonical memory").
- Returnerar `ComparisonResult` med `ComparisonOutcome.MATCHES_FOUND`
  eller `NO_MATCH_IN_AVAILABLE_MEMORY` -- aldrig "aldrig publicerat". Se
  `docs/V1A_MEMORY_LIMITATION.md`.

### 5. Candidate Angles (`angles.py`)
- `propose_candidate_angles()` far seeds fran
  `AnalysisProvider.propose_angle_seeds()` (max 3, aldrig hardkodade --
  parameteriserade av den faktiska tolkningen).
- Varje `CandidateAngle` far en `repetition_risk` (harledd fran
  `comparison.py`s resultat) och en `voice_alignment`-kontroll (harledd
  fran enkla regelbaserade kontroller mot Canonical Voice Core-referenser,
  INTE stilgenerering).

### 6. Recommended Angle (`recommendation.py`)
- `recommend()` summerar en liten, namngiven poangtabell per kandidat
  (`AngleScore.breakdown`) och valjer hogsta poang over en minimigrans.
- Under gransen, eller inga kandidater: `RecommendationOutcome.NO_STRONG_ANGLE`.

### 7. Human Decision (`human_decision.py`)
- `build_human_decision()` bygger en canonical `schema.HumanDecision` --
  manniskan kan acceptera rekommenderad, valja annan kandidat, avvisa
  alla, begara ny interpretation, eller begara mer kontext (se
  `docs/V1A_HUMAN_AUTHORITY.md`).

## Orkestrering

`pipeline.py::run_v1a_pipeline(raw_text, ...)` kor steg 1-6 i foljd och
returnerar en `V1APipelineResult` som bar VARJE mellanstegs utdata --
inte bara slutresultatet. Stoppar tidigt med
`PipelineOutcome.MORE_CONTEXT_REQUIRED` om steg 1-2 inte kan genomforas
ansvarsfullt.
