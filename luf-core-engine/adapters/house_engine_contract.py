"""
House Engine event contract (Direktorder S24/S25).

Core Engine emits semantic events. House Engine (not built in this order,
and not present in any repo accessible to this session) owns translating
them into light, projection, sound, or any other physical/visual effect.
`HouseEvent` therefore carries meaning only -- no color, CSS, brightness,
duration, or any other presentation property may be added to this model.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from schema.enums import HouseEventType


class HouseEvent(BaseModel):
    model_config = {"extra": "forbid"}

    event_type: HouseEventType
    session_id: str
    occurred_at: datetime
    semantic_payload: dict[str, str] = {}
    """Meaning-only key/value pairs, e.g. {"dimension": "trygghet"}. Never a
    presentation property (color/light/css/projection/...) -- enforced by
    tests/test_house_events_semantic_only.py."""
