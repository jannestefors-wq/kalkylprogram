# V1A Human Authority

Kedjan slutar alltid hos en manniska. `engine/human_decision.py` ar det
enda stallet i V1A dar `schema.HumanDecision` byggs, och det atervander
Canonical Foundation V1:s befintliga, harda validering: `HumanDecision.
decided_by_actor` maste vara `Actor.HUMAN` (`schema/decision.py`) --
inget nytt gjordes for att uppna detta i V1A, garantin arvdes.

## De fem manskliga handlingarna (order sektion 18)

| Manniskans handling | `HumanAction` | `HumanDecisionType` | `target_type` |
|---|---|---|---|
| Acceptera rekommenderad vinkel | `ACCEPT_RECOMMENDED` | `APPROVE` | `ANGLE` (den rekommenderade) |
| Valj en annan kandidat | `CHOOSE_DIFFERENT_CANDIDATE` | `APPROVE` | `ANGLE` (den valda) |
| Avvisa samtliga kandidater | `REJECT_ALL` | `REJECT` | `IDEA` |
| Begar ny interpretation | `REQUEST_NEW_INTERPRETATION` | `REWORK` | `IDEA` |
| Begar mer kontext | `REQUEST_MORE_CONTEXT` | `HOLD` | `IDEA` |

Ingen ny `HumanDecisionType`-medlem skapades (skulle ha kravt STOPP per
order sektion 33) -- de fem handlingarna mappas pa den BEFINTLIGA
sex-varde-enumen, disambiguerat via det fria `reason`-faltet nar det
behovs.

## AI rekommenderar, manniskan beslutar

`RecommendationResult` (engine/models.py) ar en REKOMMENDATION -- AI:ns
bedomning av vilken kandidat som star starkast. Den ar aldrig ett beslut.
Ingenting i `engine/human_decision.py` later en `RecommendationResult`
automatiskt bli en `HumanDecision`; en manniska maste uttryckligen anropa
`build_human_decision()` med sitt eget namn i `decided_by`.

## Ingen automatisk loop

Om manniskan avvisar samtliga kandidater eller begar ny interpretation,
gor `engine/human_decision.py` INGET ytterligare pa egen hand. Den bygger
exakt ett `HumanDecision`-objekt och returnerar det. Ett nytt
`run_v1a_pipeline()`-anrop ar ett separat, explicit beslut av den kod
(manniska eller framtida orkestrering) som ager kedjan -- aldrig
automatiskt trigged harifran (order sektion 19).

Testat i `tests/test_v1a_human_decision.py` och
`tests/test_v1a_pipeline_paths.py`.
