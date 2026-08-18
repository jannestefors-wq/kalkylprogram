# I. Open Questions

Endast fragor som faktiskt kraver ett projektledarbeslut — inte
retoriska fragor.

## OQ-1: Ska Voice Core fa ett eget versionerat "snapshot"-objekt?
`voice_core_version_ref` (se `docs/VERSIONING_STRATEGY.md`) ar just nu en
fri etikett-konvention, inte en egen tabell. Det racker for V1:s syfte
("vilken version bedomdes den har texten mot"), men om Editorial Engine
senare behover lista *exakt vilka principer* som gallde vid ett givet
`voice-core-1.0`-tillfalle (t.ex. for att visa en historisk diff), racker
inte etiketten ensam — det kravs antingen (a) en regel om att
`VoicePrinciple.version` aldrig far andras i efterhand for en redan
publicerad version, bara supersedas, eller (b) ett explicit
`VoiceCoreSnapshot`-objekt som listar vilka `voice_principle_id` som ingick.
**Beslut som kravs:** racker etikett + "andra aldrig, bara supersedas"-regeln,
eller behovs ett explicit snapshot-objekt redan i V1?

## OQ-2: Ska `analysis_logic_version` vara ett hart valideringskrav?
Just nu ar `Provenance.analysis_logic_version` valfritt men dokumenterat
som "kravs i praktiken nar `created_by == AI_SYSTEM`". Det finns ingen
validator som tvingar detta (jamfor med `HumanDecision.decided_by_actor`
som AR hart validerad). Att lagga till en sadan validator ar en liten
andring men paverkar all framtida AI-skriven data.
**Beslut som kravs:** ska detta bli en hard validator (brytande for all
framtida AI-genererad Provenance utan angivet `analysis_logic_version`),
eller kvarsta som konvention + dokumentation?

## OQ-3: Behover `territory` bli ett eget register?
Beslut 17 namner `territory` (t.ex. "Makt") som ett eget begrepp skilt fran
`topic` och `series`, men ger ingen fullstandig lista och inget krav pa
egen metadata utover namnet. V1 modellerar det som en oppen tagg (se TP-7).
**Beslut som kravs:** finns en fardig territory-lista fran Fas 0 som bor
kanoniseras som ett eget register redan nu, eller racker oppen tagg tills
vidare?

## OQ-4: Fullstandig lista over de 16 serierna och de atta tesfamiljerna
Uppdragstexten anger antalet (16 respektive 8) och ger namn pa TVA serier
som exempel ("Kara ...", "Det langa spelet"), men inte den fullstandiga
listan, och inga namn alls for de atta tesfamiljerna. Fixture-datasetet
(Beslut 28) innehaller darfor bara de tva namngivna serierna plus EN
tydligt flaggad platshallar-tesfamilj (`TF-001`, markerad som
"fixture placeholder" i `fixtures/fixture_dataset.py`) — inte de verkliga
atta.
**Beslut som kravs:** projektledningen behover leverera den fullstandiga
Series Registry- och Thesis Family-listan sa att `Series`/`ThesisFamily`-
raderna kan fyllas i med riktigt innehall innan Editorial Engine borjar
anvandas pa riktigt.

## OQ-5: Parastoo-recensionen
`ReaderFeedback` (`RF-001` i fixture-datasetet) ar en tydligt markerad
platshallare — den innehaller INTE Parastoos faktiska recensionstext,
eftersom den inte fanns i det material som lamnades till detta uppdrag.
**Beslut som kravs:** nar den fullstandiga recensionstexten finns
tillganglig kan den laggas till i `feedback_text` utan schemaandring
(exakt som Beslut 16 kraver) — ingen atgard behovs fran projektledningen
forran den texten ska in.
