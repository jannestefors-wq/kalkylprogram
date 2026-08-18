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

### OQ-4 (LOST i Canonical Data Integration V1): riktiga 16 serier + 8 tesfamiljer — JA, integrerade
Work levererade `LUF_Canonical_Data_Pack_V1.json` +
`LUF_Canonical_Data_Pack_V1_Report.md`, granskade och godkanda av
projektledningen. De verkliga 16 serierna och 8 tesfamiljerna ar nu
integrerade i `canonical_data/series_registry.py` /
`thesis_family_registry.py`, och de gamla synteiska platshallarna
(`SER-001`/`SER-002`/`TF-001`) ar helt borttagna fran fixture-datasetet
(som nu refererar det riktiga registret). Se
`docs/DATA_MAPPING_NOTE.md`, `docs/CLASSIFICATION_DECISION_NOTE.md` och
`docs/FINAL_REPORT_DATA_INTEGRATION_V1.md`.

## Fortfarande oppna

### OQ-5: Parastoo-recensionen — schemat verifierat, texten fortfarande utestaende
V1.1-ordern bad oss verifiera att schemat redan kan ta emot Parastoos
fullstandiga originalrecension utan schemaandring. **Verifierat: JA** — se
`docs/FINAL_REPORT_V1_1.md` punkt F och det nya testet
`tests/test_reader_effect_modes.py::test_g_reader_feedback_can_carry_observed_effects_without_becoming_voice_core`,
som konstruerar en avsevart langre `ReaderFeedback.feedback_text` an
platshallaren anvander, utan nagon schemaandring. `ReaderFeedback`
(`RF-001` i fixture-datasetet) forblir en tydligt markerad platshallare —
den innehaller INTE Parastoos faktiska recensionstext. Inte heller
Canonical Data Integration V1-uppdraget medforde nagon originaltext fran
Parastoo (endast de tva Series/Thesis-datapaketsfilerna mottogs).
**Beslut som kravs:** inget scheman-beslut — bara att den faktiska
recensionstexten sa smaningom levereras och skrivs in i `feedback_text`.
**UNDERLAG SAKNAS** (sjalva texten) i denna arbetsmiljo, fortfarande.
