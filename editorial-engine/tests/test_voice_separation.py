"""
Beslut 29:
    - 'canonical och supported voice inte blandas ihop'
    - 'Style Option kan inte registreras som Voice Core av misstag'
"""

from __future__ import annotations

from schema.enums import VoicePrincipleStatus


def test_canonical_and_supported_principles_are_distinguishable(dataset):
    principles = dataset["voice_principles"]

    canonical = [p for p in principles if p.status == VoicePrincipleStatus.CANONICAL]
    supported = [p for p in principles if p.status == VoicePrincipleStatus.STRONGLY_SUPPORTED]

    assert len(canonical) == 8, "Canonical Voice Core V1 must contain exactly the 8 approved principles."
    assert len(supported) >= 1
    # No principle id can appear in both buckets.
    assert {p.voice_principle_id for p in canonical}.isdisjoint({p.voice_principle_id for p in supported})


def test_style_attribute_and_voice_principle_are_disjoint_types(dataset):
    """
    A StyleAttribute cannot be mistaken for a VoicePrinciple because they are
    different Pydantic model classes with non-overlapping id namespaces and
    no shared `status` vocabulary (VoicePrincipleStatus has no 'style_option'
    value, and StyleAttribute has no `status` field of that type at all) --
    there is no field a producer could set on a StyleAttribute to make it
    register as canonical/supported voice.
    """
    style_ids = {s.style_attribute_id for s in dataset["style_attributes"]}
    voice_ids = {v.voice_principle_id for v in dataset["voice_principles"]}

    assert style_ids.isdisjoint(voice_ids)
    for style_attribute in dataset["style_attributes"]:
        assert not hasattr(style_attribute, "status") or not isinstance(
            getattr(style_attribute, "status", None), type(VoicePrincipleStatus.CANONICAL)
        )
        assert not hasattr(style_attribute, "voice_principle_id")
