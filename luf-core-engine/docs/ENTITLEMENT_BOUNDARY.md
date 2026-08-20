# Entitlement / Access Boundary

Direktorder S23: FREE/DEEP (or a generic entitlement model) must be
supportable from day one, but payment logic must never be built into LUF
methodology, and Core Engine must be the same motor regardless of
subscription.

## Design

- `schema/enums.py` defines `AccessTier` (`FREE`, `DEEP`).
- `adapters/entitlement.py` is the ONLY module allowed to gate anything by
  tier: `is_permitted(feature, tier)` plus `register_feature_tier(feature,
  minimum_tier)`. No payment provider is implemented (not required by this
  order).
- `schema/`, `canonical_data/`, and `human_review/` contain zero fields
  named anything resembling tier/entitlement/subscription/paywall/plan --
  enforced by `tests/test_entitlement_boundary.py`, which introspects
  `CanonicalTool`, `TriangulationSession`, and `ToolTrace`'s field names
  directly against pydantic's `model_fields`.

## What this buys

A `CanonicalTool`, a `TriangulationSession`, or a `ToolTrace` produced under
a FREE session is byte-for-byte the same shape as one produced under DEEP.
Access decisions happen entirely at the call-site boundary (a future
API/UI layer), never inside the methodology objects themselves.

## Not built in this order

Any actual payment integration, account/login system, or UI-level gating.
Direktorder S23 and S33 both explicitly exclude this.
