# D. Enums / Taxonomies

Kallfil: `schema/enums.py` (kanonisk — denna sida ar en lasbar
sammanfattning, inte en andra sanningskalla).

## Redaktionella taxonomier (transkriberade fran Fas 0A/0B, andra inte
betydelsen utan att flagga i `OPEN_QUESTIONS.md`)

### VoicePrincipleStatus
`canonical` · `strongly_supported` · `analytical_proposal` · `deprecated`*

\* `deprecated` ar en TECHNICAL PROPOSAL-tillagg (livscykel-utgang for en
principle som senare dras tillbaka), inte ett Fas 0B-begrepp.

### StyleAttributeCategory
`opening` · `structure` · `rhetorical_device` · `scene_or_dialogue` ·
`framing` · `ending`

### RepetitionSignalType (Beslut 14, samtliga sju)
`short_thesis_opening` · `thesis_plus_contrast` · `triad_or_quartet` ·
`opposing_pair` · `visually_structured_frame` · `closing_question` ·
`repeated_short_line_rhythm`

### ReaderEffectCategory (Beslut 15)
`immediate` · `cognitive` · `emotional` · `aftereffect`

### ReaderEffectMode
`intended` · `observed`

### SeriesRole (Beslut 17 — klassificerar EN series, ersatter inte den)
`form_bearing_pillar` · `time_perspective` · `recurring_character_or_voice` ·
`thematic_track` · `other`

## Canonical register (V1.1 tillskott)

### Territory (`schema/territory.py`)
Inget kontrollerat enum-varde — `Territory` ar en RADPOST-baserad
registertabell (som `Series`/`ThesisFamily`), inte en enum, eftersom
listan over territories forvantas vaxa redaktionellt over tid pa samma
satt som Series-listan gor. V1.1 (OQ-3): flyttat hit fran "oppna, fria
vokabularer" nedan — se `docs/OPEN_QUESTIONS.md` (loste OQ-3) och TP-7.
Fixture-exempel: `TER-001` "Makt" (Beslut 17:s eget exempel).

## Oppna, fria vokabularer (medvetet INTE enums eller register i V1)

Dessa halls som fria strangar for att undvika att lasa fast en lista som
vaxer ofta eller vars fullstandiga innehall inte fanns i det godkanda
underlaget:

- **topic** (`ContentWhat.topic`, `ContentForm`-relaterat) — t.ex. "Tillit".
  V1.1 (Beslut 12 i V1.1-ordern): explicit bekraftat att detta FORTSATT
  ska vara fri text, till skillnad fran territory.
- **form** (`ContentForm.form`) — t.ex. "linkedin_post", "letter".
- **opening_type**, **dramaturgy**, **paragraph_pattern**, **signature_type**,
  **key_phrases**, **rhetorical_patterns** — fri text/lista, eftersom Fas 0
  inte gav en sluten uppraknad lista for dessa.

## Strukturella enums (tekniska, stodjer schema-fait men ar inte
redaktionell sanning i sig)

`EvidenceCertainty`, `Actor`, `InputType`, `SourceType`, `SourceReliability`,
`UsageRights`, `VariationDimension`, `FeedbackVerificationStatus`,
`NarrativeMode`, `PointOfView`, `LengthClass`, `RhythmPattern`,
`EmotionalRegister`, `DegreeLevel`, `EndingType`, `CtaType`, `IdeaStatus`,
`AngleStatus`, `ContentStatus`, `QualityAssessmentResult`, `QualitySeverity`,
`ReturnPoint`, `HumanDecisionType`, `DecisionTargetType`,
`EditorialPotential`, `NoveltyRisk`.

Se docstrings i `schema/enums.py` for definitioner och `Null ar battre an
pahitt`-regeln (Beslut 24): ingen av dessa enums har ett dolt
"unknown"-varde; osakerhet uttrycks antingen genom `Optional[...] = None`
pa faltet, eller — for pastaenden som kraver en uttrycklig
sakerhetsgrad — genom `EvidenceCertainty.UNCONFIRMED`.
