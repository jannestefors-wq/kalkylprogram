# V1C Human Authority

Mirrors `docs/V1B_MEMORY_BOUNDARY.md`'s and `docs/V1A_HUMAN_AUTHORITY.md`'s
discipline for the variation layer.

## No canonical model change

`variation/human_decision.py::build_human_variation_decision()` builds an
ordinary `schema.HumanDecision` -- the exact canonical model V1A already
uses, completely unmodified. `target_type` is always
`DecisionTargetType.ANGLE` (an existing value; no new target type was
added) and `target_id` is the selected angle's own id. This was checked
against the order's explicit gate (order section 26: "Om befintlig
HumanDecision-modell maste andras semantiskt: STOPP") -- it did not need
to change, so nothing was changed.

## Six actions, four canonical decision types

| Human action | `HumanVariationAction` | `HumanDecisionType` |
|---|---|---|
| Accept recommended variation | `ACCEPT_RECOMMENDED_VARIATION` | `APPROVE` |
| Choose a different variation | `CHOOSE_DIFFERENT_VARIATION` | `APPROVE` |
| Keep original expression | `KEEP_ORIGINAL_EXPRESSION` | `HOLD` |
| Reject all variations | `REJECT_ALL_VARIATIONS` | `REJECT` |
| Request new variation analysis | `REQUEST_NEW_VARIATION_ANALYSIS` | `REWORK` |
| Request more context | `REQUEST_MORE_CONTEXT` | `HOLD` |

Two actions share `HOLD` -- disambiguated via the free-text `reason`
field, the exact same pattern `engine/human_decision.py` already
established for V1A's own five actions onto four enum values. No new
`HumanDecisionType` member was added (which would have required a STOP
per order section 26).

## AI cannot be the decision-maker

`HumanDecision.decided_by_actor` inherits Canonical Foundation V1's
existing hard validator (`Actor.HUMAN` required) -- untouched, not
reimplemented. `tests/test_v1c_human_decision.py::test_25_*` verifies
this directly against V1C's own construction path.

## No automatic loop

`build_human_variation_decision()` constructs exactly one `HumanDecision`
and returns it. Nothing in `variation/` re-invokes
`run_v1c_variation_analysis()` automatically after a rejection -- a new
analysis is a separate, explicit call by whatever code owns the pipeline
(order section 27), identical to V1A/V1B's own no-loop guarantee.
