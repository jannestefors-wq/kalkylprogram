# I. Open Questions

Endast fragor som faktiskt kraver ett projektledarbeslut — inte
retoriska fragor.

## Loste i V1.1 (projektledarbeslut mottaget och implementerat)

### OQ-1 (LOST): Voice Core-snapshot — JA, infort
Beslut: infor explicit `VoiceCoreSnapshot`. Implementerat i
`schema/voice.py` (`VoiceCoreSnapshot`), refererad fran
`ContentRecord.voice_core_snapshot_id` och
`QualityAssessment.voice_core_snapshot_id` (bada ersatter den tidigare
fria etiketten `voice_core_version_ref`). Se `docs/VERSIONING_STRATEGY.md`.

### OQ-2 (LOST): `analysis_logic_version` — JA, hart valideringskrav
Beslut: obligatoriskt nar `created_by == AI_SYSTEM`. Implementerat som en
`model_validator` pa `Provenance` (`schema/provenance.py`), sa regeln
galler overallt dar `Provenance` anvands, inte bara pa ett enskilt objekt.
Manskligt skapad provenance far fortfarande ha faltet som `None`. Testat i
`tests/test_analysis_logic_version.py` (Test A, B).

### OQ-3 (LOST): Territory — JA, eget canonical register
Beslut: `territory` far ett eget register, skilt fran `topic` (fortsatt
fri text) och fran `series`. Implementerat i `schema/territory.py`
(`Territory`), refererad fran `ContentRecord.territory_ids` och
`Idea.related_territories`. Testat i `tests/test_territory.py` (Test E, F).

## Fortfarande oppna

### OQ-4: Fullstandig lista over de 16 serierna och de atta tesfamiljerna
Fortfarande olost i V1.1 — inget nytt underlag mottogs for detta i denna
korrigeringsrunda. Uppdragstexten anger antalet (16 respektive 8) och ger
namn pa TVA serier som exempel ("Kara ...", "Det langa spelet"), men inte
den fullstandiga listan, och inga namn alls for de atta tesfamiljerna.
Fixture-datasetet innehaller darfor fortfarande bara de tva namngivna
serierna plus EN tydligt flaggad platshallar-tesfamilj (`TF-001`,
markerad "fixture placeholder" i `fixtures/fixture_dataset.py`) — inte de
verkliga atta. Per V1.1-ordern punkt 5: platshallarna ligger kvar
oforandrade; ingen rekonstruktion har forsokts.
**Beslut som kravs:** projektledningen behover leverera den fullstandiga
Series Registry- och Thesis Family-listan sa att `Series`/`ThesisFamily`-
raderna kan fyllas i med riktigt innehall.
**UNDERLAG SAKNAS** i denna arbetsmiljo — se `docs/FINAL_REPORT_V1_1.md`
punkt O/P.

### OQ-5: Parastoo-recensionen — schemat verifierat, texten fortfarande utestaende
V1.1-ordern bad oss verifiera att schemat redan kan ta emot Parastoos
fullstandiga originalrecension utan schemaandring. **Verifierat: JA** — se
`docs/FINAL_REPORT_V1_1.md` punkt F och det nya testet
`tests/test_reader_effect_modes.py::test_g_reader_feedback_can_carry_observed_effects_without_becoming_voice_core`,
som konstruerar en avsevart langre `ReaderFeedback.feedback_text` an
platshallaren anvander, utan nagon schemaandring. `ReaderFeedback`
(`RF-001` i fixture-datasetet) forblir en tydligt markerad platshallare —
den innehaller INTE Parastoos faktiska recensionstext, eftersom den inte
fanns i det material som lamnades till detta uppdrag.
**Beslut som kravs:** inget scheman-beslut — bara att den faktiska
recensionstexten sa smaningom levereras och skrivs in i `feedback_text`.
**UNDERLAG SAKNAS** (sjalva texten) i denna arbetsmiljo.
