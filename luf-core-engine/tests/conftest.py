from __future__ import annotations

from datetime import datetime, timezone

import pytest

from schema.enums import Actor, ToolConfidence
from schema.provenance import Provenance


@pytest.fixture
def human_provenance() -> Provenance:
    return Provenance(
        created_by=Actor.HUMAN,
        actor_id="test-human-reviewer",
        created_at=datetime(2026, 8, 20, tzinfo=timezone.utc),
        confidence=ToolConfidence.VERIFIED,
        method="manual_entry",
    )


@pytest.fixture
def ai_provenance() -> Provenance:
    return Provenance(
        created_by=Actor.AI_SYSTEM,
        actor_id="test-ai",
        created_at=datetime(2026, 8, 20, tzinfo=timezone.utc),
        confidence=ToolConfidence.UNVERIFIED,
        method="directorder_text_extraction",
    )
