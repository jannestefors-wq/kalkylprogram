from __future__ import annotations

from adapters.entitlement import is_permitted, register_feature_tier
from schema.enums import AccessTier
from schema.tool_registry import CanonicalTool
from schema.triangulation import TriangulationSession
from schema.tool_trace import ToolTrace


def test_methodology_models_have_no_entitlement_field():
    """Direktorder S23: Core Engine is the same motor regardless of subscription --
    payment/tier concepts must not leak into the methodology schema."""
    forbidden_substrings = ("tier", "entitlement", "subscription", "paywall", "plan")
    for model in (CanonicalTool, TriangulationSession, ToolTrace):
        for field_name in model.model_fields:
            lowered = field_name.lower()
            assert not any(token in lowered for token in forbidden_substrings), (
                f"{model.__name__}.{field_name} looks like an entitlement field"
            )


def test_entitlement_gate_is_independent_of_methodology():
    register_feature_tier("deep_reflection_mode", AccessTier.DEEP)
    assert is_permitted("deep_reflection_mode", AccessTier.FREE) is False
    assert is_permitted("deep_reflection_mode", AccessTier.DEEP) is True
    # Unregistered features default open at FREE tier already.
    assert is_permitted("unregistered_feature", AccessTier.FREE) is True
