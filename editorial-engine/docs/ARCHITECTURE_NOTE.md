# A. Architecture Note — Canonical Editorial Schema V1 (V1.1)

**V1.1-tillagg (se `docs/OPEN_QUESTIONS.md` for de losta fragorna och
`docs/FINAL_REPORT_V1_1.md` for korrigeringsrundans fulla rapport):**
`VoiceCoreSnapshot` (OQ-1), hart validerat `analysis_logic_version` for
AI-provenance (OQ-2), `Territory` som eget register (OQ-3), och en rattning
av Voice-dokumentationens formulering sa den inte foregriper en annu
icke-byggd generators beteende (se avsnitt "Voice Core -- vad schemat
uttalar sig om" nedan). Grundarkitekturen fran V1 ar oforandrad.

## Vad detta ar

Ett isolerat, maskinlasbart, versionsbart kontrakt for LUF Editorial Engine.
Det representerar kedjan

```
RAW INPUT -> IDEA -> ANALYSIS -> SOURCES -> ANGLES -> VARIATION -> CONTENT -> QUALITY -> HUMAN DECISION
```

utan att lagren blandas ihop, och utan att nagon generator, motor eller
integration byggs ovanpa det. Se `docs/OPEN_QUESTIONS.md` och
`docs/TECHNICAL_PROPOSALS.md` for allt som kravde ett tekniskt beslut
projektledningen bor se.

## Var sanningen bor (Beslut 27)

**Pydantic-modellerna under `schema/*.py` AR den kanoniska sanningskallan.**
JSON Schema (`schema/json/*.schema.json`) ar ett **avlett artefakt**,
genererat av `schema/export_json_schema.py`. Filerna i `schema/json/` ska
aldrig handredigeras — de skrivs over vid varje korning. Detta ar det
medvetna valet for att undvika Adam-problemet (tva representationer som
sakta glider isar): det finns bara en plats dar ett falt definieras.

Varfor Pydantic och inte TypeScript/Zod: den befintliga kodbasen ar Python
(Streamlit). Att lagga till ett separat Node/TypeScript-verktygslager enbart
for schemat hade skapat exakt den risk for divergens som Beslut 27 varnar
for, utan nagon motsvarande vinst i V1 — inget JS-baserat komponent
konsumerar schemat annu. Om/nar en framtida komponent behover TypeScript-typer
kan de genereras fran `schema/json/*.schema.json` (t.ex. via
`json-schema-to-typescript`) enligt samma "generera, redigera aldrig for
hand"-princip. Se TECHNICAL PROPOSAL TP-1 i `docs/TECHNICAL_PROPOSALS.md`.

Pydantic ger dessutom kors-validering (`model_validator`, `field_validator`)
som anvands for att gora tva redaktionella regler **testbara i modellen**,
inte bara dokumenterade:

- `RawInput` ar `frozen=True` -> ett forsok att skriva over `text` i efterhand
  kastar ett fel (se Beslut 5).
- `HumanDecision.decided_by_actor` maste vara `Actor.HUMAN` -> ett forsok
  att lata ett AI-system representeras som ett manskligt beslut kastar ett
  fel (se Beslut 20).

## Hur kedjan haller ihop utan att blandas ihop

| Lager | Kanoniskt objekt | Fil |
|---|---|---|
| RAW INPUT | `RawInput` (immutable) | `schema/raw_input.py` |
| IDEA / ANALYSIS | `Idea` + `IdeaInterpretation` | `schema/idea.py` |
| SOURCES | `Source` | `schema/source.py` |
| ANGLES | `Angle` | `schema/angle.py` |
| VARIATION | `VariationFingerprint`, `StyleAttribute`, `RepetitionSignal` | `schema/content.py`, `schema/voice.py` |
| CONTENT | `ContentRecord` | `schema/content.py` |
| QUALITY | `QualityAssessment` | `schema/quality.py` |
| HUMAN DECISION | `HumanDecision` | `schema/decision.py` |
| (stodjande) | `Series`, `Territory`, `ThesisFamily`, `VoicePrinciple`, `VoiceCoreSnapshot`, `ReaderEffect`, `ReaderFeedback` | `schema/series.py`, `schema/territory.py`, `schema/voice.py`, `schema/reader_effect.py` |

Separationen ar strukturell, inte bara namngiven:

1. **raw_input != interpretation** — `Idea.raw_input_id` ar en FK till en
   `frozen` `RawInput`-rad. `Idea.interpretation` ar ett eget
   `IdeaInterpretation`-objekt med egen `Provenance`
   (`analysis_logic_version`, `created_at`, `certainty`). Att skriva om
   tolkningen kan aldrig rora originaltexten, eftersom de ar olika rader.
2. **canonical vs. supported vs. analytical_proposal** — ett enda falt,
   `VoicePrinciple.status` (`VoicePrincipleStatus`), bar hela distinktionen.
   Samma modelltyp anvands for bade Canonical Voice Core V1 och Supported
   Voice Principles; det ar samma sorts objekt i olika bekraftelsegrad, inte
   tva object typer som riskerar att glida isar.
3. **Voice Core vs. Style Options** — helt olika modelltyper
   (`VoicePrinciple` resp. `StyleAttribute`) med icke-overlappande
   id-namnrymder. Ingen StyleAttribute har ett `status`-falt av typen
   `VoicePrincipleStatus`; det finns inget falt en producent kan satta for
   att fa en formegenskap att registreras som Voice Core av misstag
   (se `tests/test_voice_separation.py`).
4. **Repetition Risks** ar en egen katalog (`RepetitionSignal`), lankad men
   inte identisk med `StyleAttribute` — en teknik blir en risk genom
   overanvandning, inte genom att existera.
5. **intended vs. observed Reader Effect** — `ReaderEffectAssociation.mode`
   (`ReaderEffectMode`). En `ContentRecord` kan ha 0..N associationer;
   samma `reader_effect_id` kan forekomma bade som INTENDED och separat som
   OBSERVED utan att kollapsa till en rad.
6. **Human Decision vs. AI Assessment** — helt olika modelltyper
   (`HumanDecision` resp. `QualityAssessment`). `HumanDecision` kan referera
   en `QualityAssessment` (`based_on_quality_assessment_id`) men ingenting
   tvingar `HumanDecision.decision` att spegla `QualityAssessment.result` —
   manniskan kan alltid ga emot AI:ns rekommendation.
7. **Series != Topic != Territory != Form** — `Series` och (sedan V1.1)
   `Territory` ar bada egna register (`SeriesRole` skiljer pelar-typer
   inom Series; Territory har ingen motsvarande subtyp-enum). `topic`
   forblir en oppen, fri tagg pa `Idea`/`ContentRecord` (V1.1-beslut:
   forblir sa, till skillnad fran territory). Ingen av dem ar nagonsin en
   `series_id` eller en `territory_id`. `form` ar variationsdimensionen +
   de strukturella falten pa `ContentForm`. Se `docs/ENUMS_TAXONOMIES.md`
   och `tests/test_territory.py`.
8. **VoiceCoreSnapshot referererar, duplicerar inte** (V1.1, OQ-1) —
   `VoiceCoreSnapshot.voice_principle_ids` ar en lista `voice_principle_id`,
   aldrig kopior av `definition`/`anti_definition`. `ContentRecord` och
   `QualityAssessment` pekar pa ett snapshot (`voice_core_snapshot_id`),
   inte pa en fri etikett-strang som tidigare. Se TP-9 och
   `docs/VERSIONING_STRATEGY.md`.

## Voice Core — vad schemat uttalar sig om (V1.1-rattning)

`VoicePrinciple` (`schema/voice.py`) beskriver vad canonical Voice
Core-data BETYDER: en canonical, versionerad, evidensburen redaktionell
referens, obligatorisk input till varje framtida sparbar bedomning som
anvander den. Schemat uttalar sig INTE om HUR en annu icke byggd generator
later anvander den (t.ex. om en sadan komponent nagonsin kan "valja bort"
Voice Core) — det ar ett separat, senare beslut, inte kodat har. En
tidigare formulering i `schema/voice.py`s docstring ("a generator cannot
'turn these off'") foregrep ett sadant generatorbeteende och ar rattad i
V1.1.

## Placering och isolering (Beslut 30)

Hela paketet ligger under `editorial-engine/` och importerar ingenting fran
resten av repot (`app.py`, `kalkylprogram.py`); inget i resten av repot
importerar `editorial-engine/`. `editorial-engine/schema/__init__.py` har
ingen extern repo-dependency utover `pydantic`. Detta repo innehaller inga
`physical-house.tsx`-liknande filer, Adam, sitemap/robots/SEO eller publik
navigation att undvika — de namngivna skyddsreglerna i Beslut 30 ar darmed
trivialt uppfyllda genom isoleringen, och ingen sadan fil har rorts.

## Vad som INTE byggts

Ingen Angle Engine, Variation Engine, Quality Gate-motor, AI-agent,
promptsystem, RAG, embeddings, vector database, publiceringsmotor,
LinkedIn-integration, analyticsmotor, adminportal, UI, API eller
hemsideintegration. `schema/integrity.py` ar en enkel referensintegritets-
kontroll (finns id:n som refereras?) for att bevisa att relationer ar
kontrollerbara i testerna — den gor ingen redaktionell bedomning och ar
flaggad som TECHNICAL PROPOSAL, inte ett kanoniskt objekt.
