"""
Canonical Territory Registry -- relocated from `fixtures/fixture_dataset.py`
for LUF Editorial Engine V1A.

TECHNICAL NOTE (not a redactional change): "Makt" (Beslut 17's own example
territory) was originally defined inline in the fixture module. V1A's
engine logic (`engine/classification.py`) needs to depend on canonical
reference data, never on test fixtures (fixtures are TEST_ONLY illustration,
per docs/TECHNICAL_PROPOSALS.md TP-11's placement rule). This file moves
the exact same record -- same id, name, description, provenance -- to
`canonical_data/`, alongside `series_registry.py` and
`thesis_family_registry.py`, so `fixtures/fixture_dataset.py` can import it
from here instead of constructing it inline. No field value changed.
"""

from __future__ import annotations

from datetime import datetime, timezone

from schema import Provenance, Territory
from schema.enums import Actor, EvidenceCertainty

TERRITORY_DATE = datetime(2026, 1, 15, 9, 0, tzinfo=timezone.utc)


def load_territory_registry() -> list[Territory]:
    return [
        Territory(
            territory_id="TER-001",
            name="Makt",
            description="Beslut 17's own example of a territory, distinct from the 'Tillit' topic and the "
            "'Kara ...' / 'Det langa spelet' series.",
            created_at=TERRITORY_DATE,
            provenance=Provenance(
                created_by=Actor.HUMAN,
                actor_id="fas0_editorial_process",
                created_at=TERRITORY_DATE,
                certainty=EvidenceCertainty.VERIFIED,
                method="fas_0a_analysis",
                supporting_source_ids=[],
            ),
        ),
    ]


if __name__ == "__main__":
    for t in load_territory_registry():
        print(f"{t.territory_id}: {t.name!r}")
