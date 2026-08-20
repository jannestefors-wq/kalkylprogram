from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from schema.claims import Claim
from schema.enums import ClaimType


def test_observation_needs_no_derivation(ai_provenance):
    claim = Claim(
        claim_id="c1",
        claim_type=ClaimType.OBSERVATION,
        text="Tre personer kom sent.",
        created_at=datetime(2026, 8, 20, tzinfo=timezone.utc),
        provenance=ai_provenance,
    )
    assert claim.derived_from_claim_ids == []


def test_observation_cannot_carry_derivation(ai_provenance):
    with pytest.raises(ValidationError, match="must not carry derived_from_claim_ids"):
        Claim(
            claim_id="c2",
            claim_type=ClaimType.OBSERVATION,
            text="Tre personer kom sent.",
            derived_from_claim_ids=["c1"],
            created_at=datetime(2026, 8, 20, tzinfo=timezone.utc),
            provenance=ai_provenance,
        )


def test_interpretation_requires_derivation(ai_provenance):
    with pytest.raises(ValidationError, match="must declare at least one derived_from_claim_ids"):
        Claim(
            claim_id="c3",
            claim_type=ClaimType.INTERPRETATION,
            text="De bryr sig inte.",
            created_at=datetime(2026, 8, 20, tzinfo=timezone.utc),
            provenance=ai_provenance,
        )


def test_interpretation_with_derivation_is_valid_and_stays_interpretation(ai_provenance):
    claim = Claim(
        claim_id="c4",
        claim_type=ClaimType.INTERPRETATION,
        text="De bryr sig inte.",
        derived_from_claim_ids=["c1"],
        created_at=datetime(2026, 8, 20, tzinfo=timezone.utc),
        provenance=ai_provenance,
    )
    # An inference can never silently become an observation: the type is a
    # separate, explicit field the caller must set, not derived from shape.
    assert claim.claim_type == ClaimType.INTERPRETATION
    assert claim.claim_type != ClaimType.OBSERVATION
