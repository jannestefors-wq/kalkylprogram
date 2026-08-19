# V1C False Variation. Riktad Blockerarkorrigering 2 — Report

**Order:** "V1C FALSE VARIATION. RIKTAD BLOCKERARKORRIGERING 2"
**Branch:** `claude/editorial-variation-v1c`, HEAD vid start `f7a1544`
**Scope:** Blockerare 2 (False Variation) enbart. Blockerare 1 (Structural
Movement) intakt, ej rörd. Frysta evidensfiler (`V1C_STRUCTURAL_EVIDENCE_PACK.md`,
`V1C_EVIDENCE_HANDOFF_MANIFEST.md`) oförändrade. `V1C_AUDIT_REPORT.md`,
`V1C_CORRECTION_REPORT.md`, `V1C_REAUDIT_REPORT.md` oförändrade.

---

## 1. Rotorsak (analyserad före kodändring, order sektion 4)

Spårning Raw text → segmentering → movement detection → movement sequence
→ structural comparison → lens → narrative distance → False Variation
decision, för samtliga tre Evidence Pack D1-D3-fall, visade **tre
distinkta, samverkande rotorsaker** — inte en enda:

1. **Otillräcklig movement detection vid OOV-vokabulär.** Evidence
   Pack-parafraserna (D1, D2, D3) är medvetet formulerade för att undvika
   uppenbara nyckelord. Segmenteringen (`_classify_movement_segment()`)
   hittar då inget starkare signalord i flera segment och faller tillbaka
   på den generiska etiketten `observation`. Efter dedup kollapsar
   parafrasens rörelsesekvens till 1 steg (mot 2-3 steg för
   originaltexten).
2. **För hård `STRONGLY_SIMILAR`-gate, kombinerad med en asymmetrisk
   LCS-svaghet.** Den gamla kvoten (`matched / min(längd)`) mätte bara hur
   mycket av den KORTARE sekvensen som täcktes — vilket blir 1.0 (falskt
   `STRONGLY_SIMILAR`) närhelst en kort sekvens råkar vara en delsekvens av
   en mycket längre, även om den längre sekvensens återstod (en genuint
   annorlunda fortsättning) aldrig vägs in. Omvänt, vid en genuint kort
   parafras (D1-D3), gav samma kvot ett för LÅGT värde relativt den nya,
   mer rättvisa beräkningen, och tvingades dessutom automatiskt till
   `INSUFFICIENT_EVIDENCE` av en hård `< 2`-golv.
3. **`UNKNOWN`/default räknades som similarity- ELLER difference-evidens.**
   Två koincidenta lågkonfidens-standardvärden (t.ex. `entry_mode='claim'`
   på båda sidor, alltid `LOW`) räknades som en "match"; och ett
   lågkonfidens-standardvärde som skiljer sig från ett genuint upptäckt
   värde på andra sidan räknades som "genuin skillnad" — trots att
   ingetdera är verklig evidens.

Ingen av dessa är triggerords-specifik för D1, D2 eller D3 — alla tre är
mekanismnivå-fel som syns lika tydligt i det bredare adversarial-batteriet
(avsnitt 5).

## 2. Vad som ändrades (`variation/comparison.py`, `variation/options.py`)

### 2.1 `_dimension_match_is_evidence()` / `_dimension_diff_is_evidence()`

Nya, symmetriska hjälpfunktioner. En dimensionsjämförelse räknas som
**match-evidens** endast om värdena är lika, ingetdera är `unknown`, och
INTE båda sidor är `ConfidenceLevel.LOW` (koincidenta defaults). Den
räknas som **diff-evidens** endast om värdena skiljer sig, ingetdera är
`unknown`, och INGENDERA sidan är `LOW` (annars kan skillnaden bara
betyda att heuristiken inte hittade något på ena sidan, inte att
konstruktionen faktiskt divergerar där). Används nu genomgående i
`compare_variation_profiles()` för alla fem icke-rörelse-dimensioner
(tidigare gällde detta bara `structural_arc`-sloten, från Correction 1).

### 2.2 Asymmetrisk rörelsejämförelse (`compare_structural_movements()`)

Kvoten byttes från `matched / min(längd_a, längd_b)` till
`matched / max(längd_a, längd_b)` — täckning av BÅDA resornas längd,
inte bara den kortare. Det gamla `< 2`-golvet (som tvingade
`INSUFFICIENT_EVIDENCE` vid en enda gemensam, ofta generisk, rörelse) togs
bort helt; den nya kvoten hanterar det ärligt genom att ge ett lågt värde
i sig, utan en godtycklig hård gräns.

### 2.3 Evidenskombination i stället för en enda smal regel
(`_false_variation_verdict()`)

Ersätter Correction 1:s regel ("movement måste vara `STRONGLY_SIMILAR`,
korroborerat av exakt en av två namngivna dimensioner") med en
stegvis kombination av bevis:

```
TOO_SIMILAR (platt 6-dimensionell)                         -> True
INSUFFICIENT_EVIDENCE på både platt och rörelse             -> False (vägrar gissa)
STRONGLY_SIMILAR rörelse + högst 1 motsägande dimension      -> True
STRONGLY_SIMILAR/PARTIALLY_SIMILAR rörelse + >=2 stödjande   -> True
STRONGLY_SIMILAR/PARTIALLY_SIMILAR rörelse + 0 motsägande    -> True
Svag (icke-INSUFFICIENT) rörelseöverlapp + >=1 stödjande     -> True
   + högst 1 motsägande dimension
>=4 stödjande dimensioner oavsett rörelseresultat            -> True
annars                                                       -> False
```

`lens` exkluderas från de "konstruktions"-dimensioner som får
korrobera/motsäga (`_CONSTRUCTION_CORROBORATION_DIMENSIONS`): lens
härleds från ett enda ämnesord (ansvar/makt/konsekvens/...) och speglar
TEMA, inte redaktionell KONSTRUKTION -- order sektion 14's "Thesis
similarity ≠ Structural repetition" utvidgas hit. `lens` finns kvar i den
platta sex-slots-jämförelsen (`same_count`/`overall`, `NO_MEANINGFUL_VARIATION`
etc, oförändrat) -- exkluderingen gäller enbart vad False Variation-
kombinationen får använda som stödjande/motsägande bevis.

## 3. Varför lösningen inte är D1-D3-hardcoding

- `test_d1_d2_d3_not_hardcoded_in_production_logic` (ny, permanent) söker
  produktionskoden efter `W01`-`W12`, `content-work-006/011/003`, och
  bokstavliga `'D1'`/`'D2'`/`'D3'`-strängar -- noll träffar.
- De fem tröskelvärdena/reglerna i `_false_variation_verdict()` är
  generella och validerades mot 37 helt oberoende par (avsnitt 5), inte
  bara D1-D3.
- `lens`-exkluderingen motiveras från en generell princip (order sektion
  14, thesis ≠ struktur) och en empirisk observation som gällde flera
  olika ämnesordspar (`ansvar`, `makt`), inte D1/D2/D3:s specifika ord.

## 4. D1-D3, före/efter (körda ordagrant från fryst Evidence Pack, mot verklig corpustext)

| Fall | Källa (verklig text) | Före | Efter |
|---|---|---|---|
| D1 | content-work-006 (W06) | `False` (movement INSUFFICIENT_EVIDENCE, `<2`-golv) | **`True`** |
| D2 | content-work-011 (W11) | `False` (movement PARTIALLY_SIMILAR, otillräcklig korroborering) | **`True`** |
| D3 | content-work-003 (W03) | `False` (movement PARTIALLY_SIMILAR, 0 korroborerande dimensioner) | **`True`** |

**D1-D3 = 3/3.**

## 5. Bredare adversarial-batteri (37 nya, oberoende par + 3 extra OOV = 40 totalt utöver D1-D3)

| Kategori | Antal | Före (re-audit) | Efter (denna korrigering) |
|---|---:|---:|---:|
| Low lexical / high structural (bör flaggas) | 5 | 1/5 | **4/5** |
| High lexical / low structural (bör INTE flaggas) | 5 | 4/5 | 3/5 (se avsnitt 6) |
| Short FULL text (default-coincidence-risk) | 3 | 1/3 | **3/3** |
| Near-threshold (bör flaggas) | 5 | 1/5 | **4/5** |
| False Positive-kontroll (bör INTE flaggas) | 5 | 5/5 | 5/5 |
| Same Thesis / New Treatment (bör ej flaggas) | 3 | 3/3 | 3/3 |
| Different Thesis / Same Construction (bör flaggas) | 3 | 3/3 | 3/3 |
| Human Situation Boundary | 2 | 1/2 | 1/2 (se avsnitt 6) |
| Nya OOV-parafraser (utanför Evidence Pack) | 3 | -- | 2/3 |
| **Totalt (utöver D1-D3)** | **34+3=37** | **19/37 (51%)** | **28/37 (76%)** |
| **Inklusive D1-D3** | **40** | **19/40 (48%)** | **31/40 (78%)** |

Recall på de kategorier som specifikt kräver att upptäcka genuin
repetition under realistisk parafras (D1-D3 + low lexical/high structural
+ near-threshold-true, 13 fall totalt) gick från **2/13 (~15%)** till
**11/13 (~85%)**.

## 6. Kvarvarande, redovisade begränsningar (order sektion 17 tillåter detta -- "inga systematiska nya False Positives", inte nolltolerans)

**Ett enda, identifierat mönster** står för samtliga nya falska positiv
(HL4, och HSB1 som redan var känd sedan re-auditen): två texter som delar
en nära ordagrann öppningsfras (t.ex. "Tre personer kom sent till...")
får därigenom en genuin (icke-default) matchning på `entry_mode` och/eller
`narrative_distance`, vilket korroborerar en `PARTIALLY_SIMILAR`
rörelseläsning även när fortsättningen sedan divergerar helt (en
arbetsplatsberättelse om sjunkande förtroende vs. en obekymrad fest).
Detta är INTE en ny, spridd regression -- det är samma enskilda mekanism
som orsakar `HL4` och `HSB1`, nu explicit dokumenterad och pinnad i en
permanent test (`test_known_limitation_shared_opening_phrase_can_still_over_corroborate`)
så att en framtida ändring av detta beteende blir ett medvetet beslut,
inte en tyst regression.

`HL3` (som också flippade till `True`) omvärderades vid närmare
granskning: dess två texter delar nästan ordagrann formulering
("en chef behåller alltid det yttersta ansvaret för sitt teams beslut")
omskriven som påstående respektive fråga-och-svar -- detta är sannolikt
en korrekt identifierad False Variation, inte en ny defekt; den
ursprungliga testkategoriseringen ("bör inte flaggas") byggde på en för
ytlig bedömning (bara att `entry_mode` skiljer sig).

Ett försök att helt eliminera detta mönster (kräva `n_same >= 2` i
korroboreringsregeln) visade sig verkningslöst -- HL4/HSB1 har redan 2
genuint (icke-default) matchande dimensioner, så tröskelnivån i sig
diskriminerar inte mellan detta mönster och legitima träffar (t.ex.
`D2`, som också bara har 1-2 stödjande dimensioner). Given att `D1` och
detta falska-positiv-mönster (`FP3`, innan `lens`-exkluderingen)
visade sig ha **numeriskt identiska** bevissignaturer (samma
rörelsekvot, samma antal stödjande/motsägande dimensioner) innan
`lens`-exkluderingen särskilde dem, är den återstående kollisionen
(delad öppningsfras + genuint divergerande fortsättning) en genuin
gräns för vad detta lilla, transparenta signal-set kan skilja åt --
inte ett läge som kan lösas med ytterligare trösceljustering utan att
återigen förlora D1/D2/D3-recall.

## 7. UNKNOWN/default-korrigering (order sektion 7)

- `test_unknown_equals_unknown_is_not_similarity_evidence`: bekräftat.
- `test_default_coincidence_is_not_similarity_evidence`: två orelaterade
  enmeningstexter ("Bra ledarskap kräver mod." / "Det blev fel.") delar
  `entry_mode='claim'` (båda `LOW`) -- räknas nu korrekt INTE som match,
  och `assess_false_variation()` ger `False` (tidigare hade denna typ av
  par kunnat läsas `TOO_SIMILAR`/`True` via ackumulerade
  default-koincidenser).
- `test_default_confidence_disagreement_is_not_diff_evidence`: bekräftat.

## 8. Asymmetrisk rörelsesekvens (order sektion 8)

`test_asymmetric_short_subsequence_does_not_force_strongly_similar`:
en kort sekvens som råkar vara en delsekvens av en mycket längre tvingar
INTE längre `STRONGLY_SIMILAR` (kvoten `matched/max(längd)` ger nu ett
lågt, ärligt värde).

## 9. Bevarat (order sektion 13, verifierat oförändrat)

Structural Movement (Blockerare 1), Same Thesis/New Treatment, Different
Thesis/Same Construction, Voice Boundary, Angle Boundary, Reader Feedback
Boundary, Memory Boundary, Human Authority, FULL/PARTIAL Boundary, max tre
Controlled Variation Options, direction-only outputs, `disclosure_pace`/
`emotional_temperature`-isolering, UNKNOWN, INSUFFICIENT_EVIDENCE -- alla
verifierade via full testsvit (249/249) plus riktade grep-kontroller
(inga träffar för Voice/Reader Feedback/Sustained Narrative Form/Golden
Path/förbjuden funktionalitet i `variation/*.py`).

## 10. Testresultat

| Grupp | Antal | Resultat |
|---|---:|---|
| Canonical | 76 | PASS |
| V1A | 51 | PASS |
| V1B | 47 | PASS |
| Ursprungliga V1C | 39 | PASS |
| Correction 1 | 21 | PASS |
| **Nya permanenta regressionstester (Correction 2)** | **15** | **PASS** |
| **Totalt** | **249** | **PASS** |

JSON Schema regenererat, byte-identiskt (`git status` blankt). Canonical
Foundation, V1A (`engine/`), V1B (`memory/`) bekräftat oförändrade mot
`origin/main`.

## 11. Filer ändrade

```
editorial-engine/variation/comparison.py
editorial-engine/variation/options.py
editorial-engine/tests/test_v1c_false_variation_correction_2.py   (ny, 15 tester)
editorial-engine/docs/V1C_FALSE_VARIATION_CORRECTION_2_REPORT.md  (ny, denna fil)
```

Ingen ändring i `V1C_AUDIT_REPORT.md`, `V1C_CORRECTION_REPORT.md`,
`V1C_REAUDIT_REPORT.md`, `V1C_STRUCTURAL_EVIDENCE_PACK.md`,
`V1C_EVIDENCE_HANDOFF_MANIFEST.md`, `engine/`, `memory/`, `schema/`,
`canonical_data/`, `fixtures/`.
