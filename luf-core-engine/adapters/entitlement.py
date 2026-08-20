"""
Access / entitlement boundary (Direktorder S23).

Payment/entitlement logic must never leak into schema/, canonical_data/, or
human_review/ -- Core Engine is the same motor regardless of subscription.
This module is intentionally the only place AccessTier is used for gating.
No payment provider is implemented here (Direktorder S33: not required for
this order).
"""

from __future__ import annotations

from schema.enums import AccessTier

# Deliberately generic: a feature name -> minimum tier required. Real feature
# names and their tiers are a product decision, not a Core Engine Foundation
# concern; this dict is illustrative scaffolding, not a canonical feature list.
_FEATURE_MINIMUM_TIER: dict[str, AccessTier] = {}


def is_permitted(feature: str, tier: AccessTier) -> bool:
    required = _FEATURE_MINIMUM_TIER.get(feature, AccessTier.FREE)
    order = {AccessTier.FREE: 0, AccessTier.DEEP: 1}
    return order[tier] >= order[required]


def register_feature_tier(feature: str, minimum_tier: AccessTier) -> None:
    _FEATURE_MINIMUM_TIER[feature] = minimum_tier
