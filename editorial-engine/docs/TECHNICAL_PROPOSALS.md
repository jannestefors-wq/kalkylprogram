# J. Technical Proposals

Allt nedan ar tillagg som INTE kommer direkt fran det godkanda underlaget
(Fas 0A/0B, Blueprint V1, eller sjalva uppdragstexten). Markerade
**TECHNICAL PROPOSAL. NOT CANONICAL UNTIL APPROVED.** per Beslut 4.
Ingen av dem andrar redaktionell betydelse — de loser ren dataintegritet
eller sparbarhet.

## TP-1: JSON Schema-export som avlett artefakt
**Var:** `schema/export_json_schema.py`, `schema/json/*.schema.json`
**Vad:** Ett skript som genererar JSON Schema fran Pydantic-modellerna, for
konsumtion av framtida icke-Python-komponenter, utan att skapa en andra
handredigerad sanningskalla.
**Varfor:** Beslut 27 kraver att vi valjer en sanningskalla och undviker
Adam-problemet. Se `docs/ARCHITECTURE_NOTE.md`.

## TP-2 (uppdaterad i V1.1): `idea_id`, `angle_id`, `voice_core_snapshot_id` pa `ContentRecord`
**Var:** `schema/content.py`, `schema/quality.py`
**Vad:** Tre falt som inte star i Beslut 8:s fallista.
**Varfor:** Utan `idea_id`/`angle_id` gar det inte att sparka en
`ContentRecord` tillbaka genom ANGLE till IDEA, vilket hela kedjan i
Beslut 2 forutsatter.
**V1.1-uppdatering:** faltet hette tidigare `voice_core_version_ref` (en
fri etikett-strang). Efter OQ-1-beslutet (infor `VoiceCoreSnapshot`) ar det
omdopt till `voice_core_snapshot_id` och ar nu en riktig FK mot
`VoiceCoreSnapshot.snapshot_id`, kontrollerad av `schema/integrity.py`.
Samma bytt genomfort pa `QualityAssessment`.

## TP-3: `schema/integrity.py` — referensintegritets-kontroll
**Var:** `schema/integrity.py`
**Vad:** En funktion som gar igenom en datamangd och kontrollerar att
alla `*_id`-referenser pekar pa nagot som finns.
**Varfor:** Beslut 29 kraver ett test som bevisar att "invalid relation IDs
fangas." Detta ar ett hjalpverktyg for validering/tester, inte en motor —
den gor ingen redaktionell bedomning, rankar inget och genererar inget.

## TP-4: `RawInput.content_hash`
**Var:** `schema/raw_input.py`
**Vad:** En sha256-hash av `text`, stamplad vid skapande.
**Varfor:** Later ett test bevisa byte-for-byte-oforanderlighet
(`tests/test_raw_input_immutability.py`) utan att bara lita pa att ingen
rad kod nagonsin anropar en setter. Bar ingen redaktionell betydelse.

## TP-5: `VoicePrincipleStatus.DEPRECATED`
**Var:** `schema/enums.py`
**Vad:** Ett fjarde status-varde utover `canonical` / `strongly_supported`
/ `analytical_proposal`.
**Varfor:** Beslut 22 sager att Voice Core kommer utvecklas. Utan ett
utgangsvarde finns inget satt att pensionera en principle utan att radera
historik. Kraver inget beslut nu — paverkar inga befintliga principer —
men bor godkannas explicit innan den forsta principen nagonsin satts till
`deprecated`.

## TP-6: Normalisering av `Idea` (raw_input_id + `IdeaInterpretation`) och
`Series`/`ContentRecord` (grupperade `ContentWhat`/`ContentForm`)
**Var:** `schema/idea.py`, `schema/content.py`
**Vad:** De platta faltlistorna i Beslut 6 och Beslut 8 ar tekniskt
omgrupperade (se respektive fils docstring for exakt mappning). Inget
falt saknas eller har fatt ny betydelse.
**Varfor:** Uttryckligen tillatet i Beslut 6 ("Du far normalisera eller
dela upp detta tekniskt om det ger battre dataintegritet"), och den
konkreta anledningen ar Beslut 5:s krav att `raw_input != interpretation`
strukturellt, samt Beslut 8:s egen motivering ("vad texten sager" vs. "hur
texten ar byggd").

## TP-7 (SUPERSEDED i V1.1 for territory-delen): `topic`/`territory` som fria taggar
**Var:** `schema/content.py` (`ContentWhat.topic`), `schema/territory.py`, `docs/ENUMS_TAXONOMIES.md`
**Ursprungligt forslag (V1):** bade topic och territory fick fria taggar,
inga egna registertabeller.
**V1.1-beslut (OQ-3):** `topic` forblir fri text (oforandrat, godkant), men
`territory` blev ett eget canonical register (`Territory`,
`schema/territory.py`), refererat via `ContentRecord.territory_ids` och
`Idea.related_territories`. TP-7 galler darfor nu bara halften av det
ursprungliga forslaget (topic); territory-halften ar ersatt av ett
godkant, implementerat beslut, inte langre en oppen teknisk proposal.

## TP-8 (V1.1): "status" pa Territory och VoiceCoreSnapshot realiserat som `active` + `superseded_by`, ingen ny enum
**Var:** `schema/territory.py`, `schema/voice.py` (`VoiceCoreSnapshot`)
**Vad:** Bade V1.1-ordern (avsnitt 2 och 4) namner "status" som ett
minimifalt for dessa tva objekt. Ingen ny statusenum skapades; istallet
aterandvands exakt samma monster som redan finns pa `Series`,
`ThesisFamily`, `StyleAttribute` och `RepetitionSignal` (`active: bool`),
plus samma `superseded_by: Optional[str]`-monster som redan finns pa
`VoicePrinciple`, for `VoiceCoreSnapshot`.
**Varfor:** V1.1-ordern avsnitt 9 kravde uttryckligen: "Atervanand
befintliga canonical statusbegrepp dar de passar. Skapa separat enum
endast om lifecycle faktiskt skiljer sig." Bade Territorys livscykel
(vaxer, pensioneras ibland) och VoiceCoreSnapshots livscykel (skapas,
blir eventuellt ersatt av en nyare snapshot) matchar redan befintliga
monster exakt — att uppfinna en ny enum for att bokstavligen heta "status"
hade skapat den parallella statusmodell ordern varnar for.

## TP-9 (V1.1): `VoiceCoreSnapshot` refererar principer, duplicerar dem inte
**Var:** `schema/voice.py` (`VoiceCoreSnapshot.voice_principle_ids`)
**Vad:** Snapshot lagrar bara en lista `voice_principle_id`-varden, inte
kopior av `definition`/`anti_definition`.
**Varfor:** Uttryckligen efterfragat i V1.1-ordern avsnitt 2
("Dokumentera valet"). En princips kanoniska text har exakt ett hem
(`VoicePrinciple`); att duplicera den i varje snapshot den nagonsin ingatt
i hade aterskapat precis det tva-representationer-glider-isar-problem
detta schema finns for att undvika (Beslut 27). Att slippa upp "vad sa
princip X i snapshot Y" ar en enkel lookup (och `VoicePrinciple.version`/
`valid_from` svarar redan pa "vid vilken tidpunkt"), sa duplicering
skulle inte kopa nagot.

## TP-10 (Canonical Data Integration V1): Series/ThesisFamily `status` (canonical/strongly_supported) mappat till `Provenance.certainty`, ingen ny enum
**Var:** `canonical_data/series_registry.py`, `canonical_data/thesis_family_registry.py`
**Vad:** Work-pack:ens per-post `status`-falt (`"canonical"` /
`"strongly_supported"`) mappas till `Series.provenance.certainty` resp.
`ThesisFamily.provenance.certainty`, med `"canonical" -> EvidenceCertainty.VERIFIED`
och `"strongly_supported" -> EvidenceCertainty.STRONGLY_SUPPORTED`.
**Varfor:** Varken `Series` eller `ThesisFamily` hade nagot eget
canonical/strongly_supported-falt i V1/V1.1 (bara `active: bool`, avsett
for register som bara vaxer utan konfidensgrad per rad). Att lagga till ett
nytt `status: SeriesStatus`-liknande falt hade varit en verklig
schemaandring -- exakt det ordern (avsnitt 16) sager ska STOPPAS och
rapporteras, inte goras tyst. Losningen som undvek detta: `EvidenceCertainty`
(Beslut 23, redan i schemat sedan V1) hade redan bade `VERIFIED` och
`STRONGLY_SUPPORTED` som varden, med precis den innebord som behovdes.
Ingen ny enum-medlem, inget nytt falt. Se `docs/DATA_MAPPING_NOTE.md` for
den fullstandiga mappningstabellen.

## TP-11 (Canonical Data Integration V1): `editorial-engine/canonical_data/` — TECHNICAL PLACEMENT DECISION
**Var:** `canonical_data/__init__.py`, `canonical_data/source/`,
`canonical_data/series_registry.py`, `canonical_data/thesis_family_registry.py`
**Vad:** En ny katalog under `editorial-engine/`, skild fran `fixtures/`,
for verklig canonical referensdata (de 16 serierna, de 8 tesfamiljerna) och
dess kalla (Work:s tva leveransfiler, bevarade orort).
**Varfor:** Ordern (avsnitt 13) kraver strukturell separation mellan
canonical referensdata och testfixturer, och att en minsta mojliga
placering foreslas om ingen redan finns -- uttryckligen flaggat som
TECHNICAL PLACEMENT DECISION, inte ny motorarkitektur. `fixtures/
fixture_dataset.py` IMPORTERAR nu registret harifran (`load_series_registry()`,
`load_thesis_family_registry()`) istallet for att duplicera eller bara gömma
den riktiga datan i testdata. Ingen databas, inget API, ingen laddningsmotor
-- bara tva rena mappningsfunktioner som lasger in en JSON-fil och bygger
Pydantic-objekt.
