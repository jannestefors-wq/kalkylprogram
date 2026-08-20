# Architecture Note -- LUF Core Engine V1 Foundation

## What this delivery is

Direktorder S32's 18-item Foundation minimum, built as pure Python +
Pydantic 2, structurally mirroring `editorial-engine/`'s conventions
(schema/, canonical_data/, tests/, docs/) so a developer familiar with one
engine recognizes the other.

```
luf-core-engine/
  schema/            canonical data shapes: Provenance, CanonicalTool (Tool Registry),
                     Claim (observation/interpretation separation), TriangulationSession,
                     ZoomFrame, ToolTrace
  canonical_data/    the actual (candidate) tool inventory + its loader
  human_review/      the ONLY place a tool may become CANONICAL_APPROVED
  adapters/          provider abstraction + integration contracts (Editorial Engine,
                     Dilemma Bank, House Engine) + entitlement boundary
  docs/              this note, the manifest, ownership/independence/backup reports,
                     integration contracts, open questions
  tests/             31 tests covering S34's requirements
```

## What this delivery deliberately is NOT

- **Not** `choose_triangle() -> generate_answer()` (S4). `TriangulationSession`
  holds N `PerspectiveApplication` entries against one situation, each
  tracking confirmed/contradicted/missing/patterns/further-info-needed.
- **Not** a canonical LUF truth. Every inventoried tool is
  `CANONICAL_CANDIDATE` or `HISTORICAL_LUF_MATERIAL`, `confidence=
  UNVERIFIED`, `human_review_status=PENDING`. Nothing in this delivery
  promotes anything to `CANONICAL_APPROVED` -- that requires a `HUMAN`-actor
  `HumanReviewDecision`, enforced at two independent layers (a pydantic
  validator on `CanonicalTool` itself, and `human_review/workflow.py`'s
  `promote_to_canonical`).
- **Not** Tänkarstolen, a training engine, a speaker/workshop engine, or a
  payment system. Those are explicitly out of scope (S33) -- this Foundation
  is built so they CAN be layered on later without changing its shape.
- **Not** tied to Claude or any AI vendor. `adapters/provider.py` is the
  only place an AI backend would be wired in, through `LLMProvider`, an
  abstract interface with no vendor bound to it.

## Why observation/interpretation separation is a validator, not a comment

`schema/claims.py`'s `Claim` model raises `ValidationError` if an
`OBSERVATION` carries a `derived_from_claim_ids` reference, or if an
`INTERPRETATION`/`INFERENCE`/`ASSUMPTION` does NOT. This makes Direktorder
S9's rule a type-level guarantee: "an inference becomes an observation" is
a caught error, not a discipline lapse a future contributor could
accidentally introduce.

## Why Human Review is enforced twice

1. `schema/tool_registry.py`: `CanonicalTool` itself refuses
   `canonical_status=CANONICAL_APPROVED` unless `human_review_status=
   APPROVED` is also set (a model-shape constraint).
2. `human_review/workflow.py`: `promote_to_canonical()` additionally
   requires the `HumanReviewDecision.reviewer_actor == Actor.HUMAN` -- the
   part (1) alone cannot check, since (1) only sees the tool, not who
   decided.

Belt and suspenders deliberately: (1) prevents a malformed object from
existing at all; (2) prevents an AI actor from producing the audit trail
that would satisfy (1).

## Data gap policy

Free-text fields on `CanonicalTool` default to the literal string
`"UNKNOWN"` (see `schema/sentinels.py`), not `None` and not a plausible
guess. This makes gaps greppable in JSON exports, not just invisible
Python-side `None`s.
