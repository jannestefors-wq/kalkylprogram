from __future__ import annotations

from datetime import datetime, timezone

from adapters.house_engine_contract import HouseEvent
from schema.enums import HouseEventType


def test_house_event_has_no_presentation_fields():
    """Direktorder S24/S25: Core Engine emits meaning; House Engine owns light/
    projection/CSS. HouseEvent must carry no presentation-layer property."""
    forbidden = ("color", "colour", "css", "light", "brightness", "projection", "hue", "style")
    for field_name in HouseEvent.model_fields:
        lowered = field_name.lower()
        assert not any(token in lowered for token in forbidden), f"HouseEvent.{field_name} looks presentational"


def test_house_event_round_trips():
    event = HouseEvent(
        event_type=HouseEventType.DIMENSION_OPENED,
        session_id="sess-1",
        occurred_at=datetime(2026, 8, 20, tzinfo=timezone.utc),
        semantic_payload={"dimension": "trygghet"},
    )
    assert HouseEvent.model_validate_json(event.model_dump_json()) == event
