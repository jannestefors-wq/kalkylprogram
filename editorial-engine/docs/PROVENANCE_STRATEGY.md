# F. Provenance Strategy (Beslut 23, 24)

Kallfil: `schema/provenance.py`.

## Vardeobjektet `Provenance`

Varje falt som bar en redaktionell tolkning (inte bara ett rakt citat) har
en inbaddad `Provenance`:

| Falt | Svarar pa |
|---|---|
| `created_by` (`Actor`) | Manniska, AI-system, eller import? |
| `actor_id` | Vem/vilket system, konkret |
| `created_at` | Nar |
| `certainty` (`EvidenceCertainty`) | verified / strongly_supported / analytical_proposal / unconfirmed |
| `method` | T.ex. `"fas_0a_analysis"`, `"manual_entry"`, `"ai_inference"` |
| `analysis_logic_version` | Vilken version av analyslogiken (kravs nar `created_by == AI_SYSTEM`, se nedan) |
| `supporting_source_ids` | Vilka `Source`-poster stodjer pastaendet |
| `schema_version` | Under vilket schema-kontrakt provenance-posten skapades |

`Provenance` ar ett vardeobjekt (inbaddat, ingen egen id) eftersom
proveniens alltid beskriver exakt en agande post — den har ingen egen
livscykel att spara separat.

## Tre-stegs sakerhetsgrad, byggd in i datan (Beslut 23)

`EvidenceCertainty` haller `verified` / `strongly_supported` /
`analytical_proposal` isar som ett vardeenum, inte bara som ett
dokumentationsbegrepp. Samma enum anvands konsekvent for:

- Kallors tillforlitlighet (`Source.reliability` anvander dock den
  separata `SourceReliability`, se nedan — se motivering).
- En tolknings sakerhetsgrad (`IdeaInterpretation.provenance.certainty`).
- En Voice Principle-nivas stod (`VoicePrinciple.evidence[].certainty`).
- Ett Quality Assessment-fynds ursprung (`QualityAssessment.provenance`).

**Varfor `Source.reliability` ar ett eget enum (`SourceReliability`) och
inte samma `EvidenceCertainty`:** de svarar pa olika fragor. `Evidence-
Certainty` beskriver hur sakert ETT PASTAENDE ar. `SourceReliability`
beskriver hur palitlig SJALVA KALLAN ar oavsett vad man later hamta ur den
(en verifierad kalla kan anda tolkas fel; en opalitlig kalla kan anda ge en
starkt stodd tolkning om den korsverifieras pa annat hall). Att slapa ihop
dem hade gjort det omojligt att skilja "kallan ar svag" fran "tolkningen ar
svag" — exakt den sammanblandning Beslut 7 forbjuder ("kalla och tolkning
av kalla ska inte vara samma sak").

## "NULL ar battre an pahitt" (Beslut 24) — den konsekventa regeln

**Regel:** ett falt ar `Optional[...] = None` narhelst vardet genuint kan
saknas. Inget falt anvander ett dolt "unknown"-medlemsvarde i sitt enum som
en forklad gissning. Dar en uttrycklig sakerhetsgrad kravs (snarare an bara
franvaro av ett varde) anvands `EvidenceCertainty.UNCONFIRMED` — en
medveten "vi vet, och det vi vet ar att vi inte vet"-markering, skild fran
ett tomt falt.

Konkret i koden:
- `Idea.editorial_potential: Optional[EditorialPotential] = None` — inte
  `EditorialPotential.MEDIUM` som pafallande standard.
- `Source.reliability: Optional[SourceReliability] = None` (se
  `tests/test_versioning_required.py::test_source_does_not_require_a_speculative_reliability_value`).
- `ContentForm.question_count: Optional[int] = None` — noll fragor och
  "raknat inte annu" ar olika saker och far inte se likadana ut.

## Vem/vad skapade tolkningen, och nar (Beslut 5, 23)

`analysis_logic_version` pa `Provenance` ar obligatoriskt-i-praktiken for
AI-genererade tolkningar (dokumenterat, se `docs/OPEN_QUESTIONS.md` OQ-2 for
om detta ska bli en hard validator likt `HumanDecision.decided_by_actor`).
Tillsammans med `created_at` och `created_by`/`actor_id` racker det for att
alltid kunna svara: *vem eller vad gjorde den har tolkningen, nar, och med
vilken logik.*
