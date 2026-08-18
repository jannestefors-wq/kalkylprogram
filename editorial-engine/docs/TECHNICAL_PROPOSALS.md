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

## TP-2: `idea_id`, `angle_id`, `voice_core_version_ref` pa `ContentRecord`
**Var:** `schema/content.py`
**Vad:** Tre falt som inte star i Beslut 8:s fallista.
**Varfor:** Utan `idea_id`/`angle_id` gar det inte att sparka en
`ContentRecord` tillbaka genom ANGLE till IDEA, vilket hela kedjan i
Beslut 2 forutsatter. Utan `voice_core_version_ref` gar det inte att senare
svara "den har texten bedomdes mot Voice Core 1.0" (Beslut 22:s explicita
exempel).

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

## TP-7: `topic`/`territory` som fria taggar, inte egna entiteter
**Var:** `schema/content.py` (`ContentWhat.topic`), `docs/ENUMS_TAXONOMIES.md`
**Vad:** Topic och territory fick inga egna registertabeller i V1.
**Varfor:** Beslut 26 varnar uttryckligen for att bygga ett monster. Om
`territory` senare behover egen metadata (t.ex. en beskrivning eller
relation till fler serier) blir det en enkel MINOR-schemaandring
(`docs/VERSIONING_STRATEGY.md`). Se ocksa OQ-3.
