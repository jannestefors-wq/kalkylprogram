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

### OQ-5 (LOST i Final Canonical Data Closure): Parastoo-recensionen — JA, importerad
Parastoo Ebrahimzadehs fullstandiga originalrecension av "Leadership
Without Filter" ar mottagen fran projektledningen och integrerad ordagrant
som en verklig `ReaderFeedback`-post
(`canonical_data/reader_feedback_registry.py`,
`canonical_data/source/parastoo_ebrahimzadeh_review_leadership_without_filter.txt`).
Ingen schemaandring kravdes. Den tidigare fixture-platshallaren ar omdopt
till `RF-TEST-ONLY-001` och kan inte langre forvaxlas med den verkliga
posten. Se `docs/FINAL_REPORT_PARASTOO_CLOSURE.md`.

## Fortfarande oppna

### OQ-6: `ReaderFeedback.content_reference` saknar en giltig representation for icke-ContentRecord-evidens (t.ex. bocker)
Upptackt vid integrationen av Parastoos recension: faltet ar obligatoriskt
och dokumenterat som FK -> `ContentRecord.content_id`, men evidens kan
giltigt handla om andra saker an ContentRecord (har: en bok). Ingen
schemaandring gjordes (per uttrycklig instruktion); faltet bar istallet den
ordagranna sentinel-strangen `"UNDERLAG SAKNAS"` for detta enskilda fall.
Fullstandig analys: `docs/PARASTOO_INTEGRATION_GAP_REPORT.md`.
**Beslut som kravs:** ska `content_reference` bli `Optional[str]`, eller
ska ett bredare "evidence subject"-koncept (ContentRecord ELLER Source)
inforas for framtida Reader Feedback som inte galler ett specifikt
content-utkast?

### OQ-7: Reader Effect-taxonomin saknar en post for "atererovrat eget omdome / klarhet"
Parastoos recension stodjer tydligt en effekt i stil med "reconnecting
with one's own judgment" / "regaining clarity" (aftereffect-liknande), men
detta motsvaras inte av nagon befintlig `ReaderEffect`-post (bara RE-001
"obehag" och RE-002 "perspektivskifte" finns annu). Ingen ny `ReaderEffect`
skapades (forbjudet av ordern); effekten ar darfor INTE kopplad till
recensionen. Fullstandig analys: `docs/PARASTOO_INTEGRATION_GAP_REPORT.md`.
**Beslut som kravs:** ska Reader Effect-katalogen utokas med en post for
denna effekt (t.ex. kategori AFTEREFFECT)?
