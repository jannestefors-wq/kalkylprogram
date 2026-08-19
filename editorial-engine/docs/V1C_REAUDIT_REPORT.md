# V1C Riktad Re-Audit Report

**Order:** "ÅTERUPPTA OCH SLUTFÖR V1C RIKTAD RE-AUDIT"
**Branch:** `claude/editorial-variation-v1c`, HEAD vid audit-start `33c1651`
**Evidence Owner:** Work. Evidence Packet och Handoff Manifest är read-only,
verifierade via SHA-256, oförändrade av denna audit.
**Föregående dokument (bevaras oförändrade):** `V1C_AUDIT_REPORT.md`,
`V1C_CORRECTION_REPORT.md`

---

## 0. Materialiseringscheckpoint

| Kontroll | Resultat |
|---|---|
| Commit `33c1651` finns i branchhistoriken | JA |
| Evidence Pack SHA-256 | `1fa4d36d5215dcc14f6d0fa7e4473f1bae136a621df3f15941a977c13c3933b2` — exakt match |
| Manifest SHA-256 | `b58f83039048a645084e160fb50df6e9821dffc1f5e1bc89d31ddcf4e4cbff69` — exakt match |
| Baseline före re-audit | 234/234 PASS |
| Worktree | Rent vid start |

## 1. N06 evidence gap (permanent, ej blockerande)

Ursprunglig N06 saknas med source fidelity (dokumenterat i tidigare
provenance-undersökning: filen `test_v1c_correction.py` skapades och
committades i ett enda steg, `537293c`, utan att git någonsin fångade en
mellanliggande version). Detta är en accepterad, permanent
evidenslucka. Den justerade N06 i `tests/test_v1c_correction.py` kvarstår
som ett correction-test, men har **inte** använts som PR-gate eller som
källa till någon slutsats i denna audit. Gapet kompenseras genom
D1–D3 (körda direkt från den frysta Evidence Pack-mastern mot verklig
corpustext) och 34 nya, oberoende adversarial-scenarier (avsnitt 4-5).

## 2. Structural Movement — auditerad mot fryst evidens

### 2.1 Mekanism (verifierad i aktuell kod, `variation/profiler.py`)

- Text segmenteras i upp till 5 grupper via `_segment_sentences()`, endast
  om texten har `>= 3` meningar (`_MIN_SENTENCES_FOR_MOVEMENT`).
- Varje segment klassificeras oberoende (`_classify_movement_segment()`)
  mot en liten, fast nyckelordslista per `MovementStage` (12 värden inkl.
  `unknown`).
- Konsekutiva identiska steg slås ihop.
- `structural_arc` härleds sekundärt från sekvensens första/sista kända
  steg — aldrig tvärtom.
- Jämförelse (`compare_structural_movements()`) använder longest-common-
  subsequence (ordningskänslig, tolerant för infogade/borttagna steg),
  med `INSUFFICIENT_EVIDENCE` när jämförbar längd `< 2`.

**Svar på Fråga A:** Mekanismen observerar genuint en ORDNAD flerstegssekvens
när texten bär tillräckligt signal — bekräftat empiriskt (avsnitt 2.2).
Den är dock fortfarande nyckelordsdriven per segment, inte en semantisk
modell. Vid otillräcklig signal faller segment tillbaka på den generiska
etiketten `observation`, vilket kan komprimera en riktig sekvens till en
kortare eller mindre informativ en.

### 2.2 Empiriska fynd

- **Ordning betyder något (order sektion 12):** ett par med samma
  rörelseelement i omvänd ordning (`concrete_situation→tension→consequence`
  vs. `consequence→tension→observation→concrete_situation`) klassades
  korrekt `STRUCTURALLY_DISTINCT`. Ordningskänslighet bekräftad.
- **Samma entry+closure, olika mittparti (3 nya par):** samtliga 3 höll sig
  under `TOO_SIMILAR` (`PARTIALLY_DISTINCT` i alla tre), i linje med
  Structural Arc Blocker-fixet.
- **Korta FULL-texter (3 par):** `structural_movement.sufficient_evidence`
  blev korrekt `False` för alla ensemensiga texter -- men den ÖVRIGA
  sex-dimensionella jämförelsen (som inte kräver `structural_movement`)
  kunde ändå ge `TOO_SIMILAR`/`False Variation=True` för två *innehållsligt
  orelaterade* korta texter ("Bra ledarskap kräver mod." vs. "Det blev
  fel.") -- se avsnitt 3 (samma rotorsak som redan dokumenterad
  "default-value coincidence" i `V1C_AUDIT_REPORT.md`, kvarstående efter
  korrigeringen).

### 2.3 Verdikt: Structural Movement

**ACCEPTABLE PROTOTYPE HEURISTIC** -- mekanismen observerar genuint en
ordnad, flerstegs rörelse (inte bara en utökad entry/closure-mappning),
är ordningskänslig, och håller "samma entry+closure" ifrån att
automatiskt bli `TOO_SIMILAR`. Den kvarstående svagheten (nyckelords-
beroende segmentklassificering, generisk `observation`-fallback under
tunn signal) är korrekt disclosad som en gräns för en prototyp, inte ett
dolt sanningsanspråk.

## 3. False Variation — auditerad mot fryst evidens

### 3.1 D1–D3, körda exakt från fryst Evidence Pack (order sektion 9)

Version A = den verkliga corpustexten (W06/W11/W03, hämtad ordagrant ur
`memory/data/LUF_Editorial_Memory_Data_Pack_V1B.json`, content-id
`content-work-006`/`content-work-011`/`content-work-003`). Version B =
Evidence Pack-tabellens parafras, ordagrant, oförändrad.

| Par | Källa | Rörelse A | Rörelse B | Movement-jämförelse | `assess_false_variation()` | Evidence Pack förväntar |
|---|---|---|---|---|---|---|
| D1 | W06 | `[observation, concrete_situation, observation]` | `[observation]` | `INSUFFICIENT_EVIDENCE` (jämförbar längd 1) | **`False`** | `STRONGLY_SIMILAR` / hög risk |
| D2 | W11 | `[observation, tension]` | `[observation]` | `INSUFFICIENT_EVIDENCE` | **`False`** | `STRONGLY_SIMILAR` / hög risk |
| D3 | W03 | `[observation, tension]` | `[observation]` | `INSUFFICIENT_EVIDENCE` | **`False`** | `STRONGLY_SIMILAR` / hög risk |

**Alla tre D1-D3 missas: 0 av 3.** Rotorsak: Evidence Pack-parafraserna
(kort, medvetet formulerade för att undvika uppenbara ord) klassificeras
av `_classify_movement_segment()` till en enda generisk `observation`-
etikett efter dedup. Jämförbar längd blir då 1, vilket triggar
`INSUFFICIENT_EVIDENCE` snarare än `STRONGLY_SIMILAR`, och varken den
platta sex-dimensionella tröskeln eller korroboreringsregeln kan då ge
`True`. Detta är INTE en specialkodningseffekt (ingen produktionskod
refererar D1/D2/D3 eller W01-W12, verifierat i avsnitt 6) -- det är en
genuin, generell svaghet: parafraser som undviker den lilla mängd
nyckelord `_classify_movement_segment()` känner till kollapsar till för
lite observerbar struktur för att korroboreringsregeln ska kunna slå
till.

### 3.2 Bredare adversarial-batteri (34 nya, oberoende scenarier)

| Kategori | Antal | Korrekt resultat | Felresultat |
|---|---:|---:|---|
| Low lexical / high structural (bör flaggas) | 5 | 1 (LL2) | 4 falska negativ (missad repetition) |
| High lexical / low structural (bör INTE flaggas) | 5 | 4 | 1 falsk positiv (HL4) |
| Same entry+closure/different middle (bör ej TOO_SIMILAR) | 3 | 3 | 0 |
| Short FULL text (default-coincidence-risk) | 3 | 1 (SF3) | 2 falska positiv (SF1, SF2) |
| Near-threshold (bör flaggas som repetition) | 5 | 1 (NT2) | 4 falska negativ |
| False Positive-kontroll (bör INTE flaggas) | 5 | 5 | 0 |
| Same Thesis/New Treatment (bör ej TOO_SIMILAR) | 3 | 3 | 0 |
| Different Thesis/Same Construction (bör flaggas) | 3 | 3 | 0 |
| Human Situation Boundary | 2 | 1 | 1 (HSB1, se nedan) |
| **D1-D3 (fryst Evidence Pack)** | 3 | 0 | 3 falska negativ |
| **TOTALT** | **37** | **22** | **15** |

**Falska negativ (missad genuin repetition), mönster:** D1-D3, LL1/LL3/LL4/LL5,
NT1/NT3/NT4/NT5 -- alla delar samma rotorsak som 3.1: en realistisk,
väl utförd parafras som undviker de kända nyckelorden kollapsar
rörelsesekvensen till för kort/generisk för att korroboreringsregeln
(kräver `STRONGLY_SIMILAR`, inte bara `PARTIALLY_SIMILAR`) ska kunna slå
till, samtidigt som den platta sex-dimensionella räkningen inte ensam
når `TOO_SIMILAR` när flera ytliga nyckelord samtidigt bytts ut.

**Falska positiv, två distinkta mönster:**
1. **Kort text, "default-value coincidence"** (SF1, SF2): två *innehållsligt
   orelaterade* enmeningstexter delar samma lågkonfidens-standardvärden
   på flera dimensioner och klassas `TOO_SIMILAR`/`False Variation=True`.
   Detta var redan känt och dokumenterat i `V1C_AUDIT_REPORT.md` -- kvarstår
   efter korrigeringen eftersom korrigeringen inte adresserade denna
   specifika defekt.
2. **Kort, delad öppning, olika fortsättning** (HL4, HSB1): när den ena
   sekvensen är kortare än den andra (t.ex. en kort text vars rörelse
   "råkar ta slut" tidigt), jämför LCS bara den GEMENSAMMA, förkortade
   längden -- vilket kan dölja att den längre sekvensens FORTSÄTTNING
   divergerar helt. Två texter som delar en identisk öppning ("Tre
   personer kom sent till...") men sedan går åt helt olika håll (en
   arbetsplatskonflikt som eroderar förtroende vs. en fest som fortsätter
   som vanligt) klassas ändå `STRONGLY_SIMILAR`/`False Variation=True`.
   Detta är ett NYTT fynd, inte tidigare dokumenterat.

### 3.3 Hardcoding-kontroll för D1-D3-resultatet

Grep bekräftar noll förekomst av `W01`-`W12`, `B04`, `B05`, `D1`, `D2`, `D3`
eller längre karakteristiska Evidence Pack-formuleringar i
produktionskoden (`variation/*.py`). Resultatet ovan är alltså den
faktiska, ospecialkodade produktionslogikens beteende.

### 3.4 Verdikt: False Variation

**PROTOTYPE LIMITATION REQUIRES CORRECTION.**

Grund: Precisionen är god (få falska positiv på tydligt olika innehåll
-- FP-batteriet 5/5, STNT 3/3, DTSC 3/3, SEC 3/3), men **recall är
otillräcklig**: samtliga tre av Evidence Packets egna D1-D3-kontrollfall
missas (0/3), och i det bredare 34-scenariers batteriet missas 8 av 13
fall som var konstruerade för att kräva upptäckt av genuin repetition
under realistisk parafras (~15 % träffsäkerhet på just den kategorin).
Dessutom kvarstår det redan kända "default-value coincidence"-felet för
korta texter, och ett nytt falsk-positiv-mönster upptäcktes för par med
delad öppning men divergerande fortsättning. Detta är INTE ett
arkitektoniskt genombrott som skulle kräva ny infrastruktur (embeddings,
RAG etc, vilket är förbjudet ändå) -- det är en bounded, korrigerbar
svaghet i den lilla nyckelordsvokabulären och i LCS-jämförelsens
hantering av korta/asymmetriska sekvenser. Men den är för materiell för
att kallas "acceptabel" i nuvarande skick.

## 4. Gränser (boundaries) -- samtliga verifierade

| Gräns | Metod | Resultat |
|---|---|---|
| Voice ≠ Variation | grep "voice"/"Voice" i `variation/*.py` | 0 träffar |
| Reader Feedback ≠ Variation Rule | grep "reader_feedback"/"Parastoo" | 0 träffar |
| Angle ≠ Expression | grep `CandidateAngle(`/`Angle(` | 0 träffar (endast referens till `.angle.angle_id`) |
| AI ≠ Human Variation Decision | `build_human_variation_decision()`-signatur exponerar ingen `Actor`-parameter | Bekräftat |
| Sustained Narrative Form ej implementerad | grep dialog/story/narrative-engine/scene-mode/longform/storytelling | 0 träffar i produktionskod |
| `disclosure_pace`/`emotional_temperature` beslutsisolerade | grep, endast `models.py`+`profiler.py` | Bekräftat, oförändrat sedan korrigeringen |
| Memory Boundary (inga absoluta påståenden) | grep "never used"/"first time"/"completely new"/"unique"/"helt ny" | 0 träffar |
| Controlled Variation Options = direction plans | 5 nya stickprov, alla `proposed_changes`-värden | Max 16 tecken, ingen prosa |
| Golden Path ej hårdkodad | grep känd golden-path-text + `if ... ==`-mönster | 0 träffar |

## 5. Testgrupper (verkliga antal)

| Grupp | Antal | Resultat |
|---|---:|---|
| Canonical | 76 | PASS |
| V1A | 51 | PASS |
| V1B | 47 | PASS |
| Ursprungliga V1C | 39 | PASS |
| Correction | 21 | PASS |
| **Totalt (befintlig svit)** | **234** | **PASS** |

Denna re-audit lade INTE till några nya permanenta tester i
`tests/`-katalogen -- alla 37 adversarial-scenarier i avsnitt 3.2 kördes
som fristående auditscript (inte committade som pytest-tester), eftersom
resultatet var ett verkligt blockerande fynd som enligt order sektion 7
inte får repareras inom denna audit. Att committa nya tester som
FÖRVÄNTAR SIG det nuvarande (bristfälliga) beteendet skulle permanent
kodifiera en känd defekt; att committa tester som förväntar sig det
KORREKTA beteendet skulle omedelbart göra svitens 234/234-baseline röd.
Ingetdera är lämpligt inom en ren audit-order. Full rådata för samtliga
37 scenarier finns i denna rapport (avsnitt 3.1-3.2) och kan
reproduceras exakt av nästa session.

## 6. JSON Schema

Regenererat från Pydantic, `git status` visar noll skillnad mot befintlig
`schema/json/`. Canonical Foundation, V1A (`engine/`), V1B (`memory/`)
bekräftat oförändrade mot `origin/main` (`git diff --stat` blankt).

## 7. Förbjuden funktionalitet

Grep efter generator/Quality Gate/RAG/embeddings/UI/API/publish-mönster i
`variation/*.py`: noll träffar (oförändrat sedan korrigeringen).

## 8. Slutsats

**Fråga A (Structural Movement): ACCEPTABLE PROTOTYPE HEURISTIC.**
**Fråga B (False Variation): PROTOTYPE LIMITATION REQUIRES CORRECTION.**

PR-gaten (order sektion 21/23) kräver att BÅDA är
`ACCEPTABLE PROTOTYPE HEURISTIC`. Eftersom False Variation inte
uppfyller detta: **ingen PR skapas.**

## 9. Kvarvarande begränsningar (för nästa korrigeringsorder)

1. **Nyckelordsvokabulären i `_classify_movement_segment()` är för smal**
   för att stå emot realistisk, väl utförd parafras -- Evidence Packets
   egna D1-D3 visar detta direkt. En bredare, mer generell (fortfarande
   liten och transparent) signalmängd, eller en mindre strikt
   `compared_length`-tröskel för korroborering, skulle sannolikt förbättra
   recall utan att offra precision.
2. **Default-value coincidence för korta texter** (redan känd sedan
   `V1C_AUDIT_REPORT.md`) kvarstår -- den ursprungliga korrigeringen löste
   `structural_arc`-slotens del av detta problem men inte de fem övriga
   dimensionernas låg-konfidens-standardvärden.
3. **LCS-jämförelse av asymmetriska sekvenslängder** kan ge falska
   positiv när en kortare sekvens råkar matcha en längre sekvens BÖRJAN
   men den längre sekvensens fortsättning aldrig jämförs. Ett nytt,
   tidigare odokumenterat fynd (HL4, HSB1).

Ingen av dessa har åtgärdats i denna audit, i enlighet med ordern.
