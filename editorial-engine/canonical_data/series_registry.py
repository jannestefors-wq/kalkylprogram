"""
Canonical Series Registry V1 -- loads the real 16 series/tracks from
`canonical_data/source/LUF_Canonical_Data_Pack_V1.json` (delivered by Work,
approved by project management) and maps them to Schema V1.1's `Series`
model. See docs/DATA_MAPPING_NOTE.md for the full field-by-field mapping
rationale; this docstring covers only the parts that required a genuine
technical judgment call.

WHY `role` (SeriesRole, mandatory on `Series`) IS NOT IN THE SOURCE PACK:
`SeriesRole` is a Schema V1.1-internal classifier (V1 TECHNICAL PROPOSAL,
not a Fas 0A concept) and the source pack carries no equivalent field. To
avoid inventing a role classification for the 14 series where no canonical
text supports one (which would be new redactional analysis, forbidden by
this order's section 12), only the two series whose ROLE was already
explicitly stated in previously-approved canonical material get a specific
value:
    - "series-dear-001" (Kara ...): FORM_BEARING_PILLAR -- stated directly
      in the original V1 brief's own Beslut 17 example, and confirmed by
      this pack's own description ("formen ar brevet/pelaren").
    - "series-long-game-001" (Det langa spelet): TIME_PERSPECTIVE -- same
      V1 Beslut 17 example ("serie med tidsperspektiv"), confirmed by this
      pack's description ("Val over tid ...").
All other 14 series receive `SeriesRole.OTHER` -- the enum's own neutral
"not further classified" value, not a specific claim.

WHY `status` (canonical Data Pack field, not a Schema V1.1 Series field) IS
MAPPED TO `Provenance.certainty`: Schema V1.1's `Series` model has no
canonical/strongly_supported distinction of its own (only `active: bool`,
sufficient for a registry that only grows). `Provenance.certainty`
(`EvidenceCertainty`) already contains exactly the needed values --
`VERIFIED` and `STRONGLY_SUPPORTED` -- so the pack's `status: "canonical"`
maps to `EvidenceCertainty.VERIFIED` and `status: "strongly_supported"`
maps to `EvidenceCertainty.STRONGLY_SUPPORTED`. No schema change was needed
or made. See docs/DATA_MAPPING_NOTE.md.

The five project-leadership classification decisions (order section 4) are
recorded verbatim in `Provenance.notes` for the five affected series, since
Schema V1.1 has no dedicated "SERIES CANDIDATE" / "EDITORIAL TRACK" field
and the order explicitly forbids adding one just for this. See
docs/CLASSIFICATION_DECISION_NOTE.md.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from schema import Provenance, Series
from schema.enums import Actor, EvidenceCertainty, SeriesRole

SOURCE_PATH = Path(__file__).parent / "source" / "LUF_Canonical_Data_Pack_V1.json"

PACK_DATE = datetime(2026, 8, 18, tzinfo=timezone.utc)  # from the pack's own "source_basis"
PACK_METHOD = "work_canonical_data_pack_v1"
PACK_ACTOR_ID = "work_fas0a_editorial_process"

# Explicitly source-supported role assignments -- see module docstring.
_EXPLICIT_ROLES: dict[str, SeriesRole] = {
    "series-dear-001": SeriesRole.FORM_BEARING_PILLAR,
    "series-long-game-001": SeriesRole.TIME_PERSPECTIVE,
}

# The five project-leadership classification decisions (order section 4),
# recorded verbatim into Provenance.notes for the affected series.
_CLASSIFICATION_DECISIONS: dict[str, str] = {
    "series-dear-001": (
        "Projektledarbeslut A (Canonical Data Integration V1): behall som SERIES, status canonical. "
        "Formbarande pelare som kan bara flera amnen -- hindrar inte att den samtidigt ar ett etablerat "
        "redaktionellt seriesspar."
    ),
    "series-upside-down-world-001": (
        "Projektledarbeslut B (Canonical Data Integration V1): behall som SERIES, status canonical. "
        "Perspektivvandningen ar seriens aterkommande redaktionella identitet."
    ),
    "series-one-thing-001": (
        "Projektledarbeslut C (Canonical Data Integration V1): behall som SERIES, status strongly_supported. "
        "Aterkommande frageformat som kan anvandas over flera territorier. Ingen uppgradering till canonical."
    ),
    "series-ubuntu-human-001": (
        "Projektledarbeslut D (Canonical Data Integration V1): klassificerad som SERIES CANDIDATE, status "
        "strongly_supported. Identifierat som koncept men annu inte verifierat som etablerad publicerad serie. "
        "Schema V1.1 saknar ett separat tekniskt falt for SERIES CANDIDATE; klassificeringen bevaras har i "
        "metadata/notes per uttrycklig instruktion, ingen ny enum skapad."
    ),
    "series-easy-to-choose-001": (
        "Projektledarbeslut E (Canonical Data Integration V1): klassificerad som SERIES / EDITORIAL TRACK, "
        "status strongly_supported. Ingen uppgradering till canonical. Schema V1.1 saknar ett separat tekniskt "
        "falt for EDITORIAL TRACK; klassificeringen bevaras har i metadata/notes per uttrycklig instruktion, "
        "ingen ny enum skapad."
    ),
}


def _certainty_from_status(status: str, series_id: str) -> EvidenceCertainty:
    if status == "canonical":
        return EvidenceCertainty.VERIFIED
    if status == "strongly_supported":
        return EvidenceCertainty.STRONGLY_SUPPORTED
    raise ValueError(f"Unrecognized source status {status!r} for {series_id!r} -- refusing to guess a mapping.")


def _build_notes(record: dict) -> str:
    parts: list[str] = []
    languages = record.get("known_language") or []
    if languages:
        parts.append(f"Sprak: {', '.join(languages)}.")
    evidence = record.get("evidence") or []
    if evidence:
        parts.append("Evidence: " + " | ".join(evidence))
    notes = record.get("notes") or []
    if notes:
        parts.append("Notes: " + " | ".join(notes))
    decision = _CLASSIFICATION_DECISIONS.get(record["series_id"])
    if decision:
        parts.append(decision)
    return " ".join(parts)


def load_series_registry(source_path: Path = SOURCE_PATH) -> list[Series]:
    """Build the 16 canonical Series objects from the Work data pack. Pure technical
    mapping -- see module docstring for the two judgment calls this function makes."""

    pack = json.loads(source_path.read_text(encoding="utf-8"))
    records = pack["series"]

    result: list[Series] = []
    for record in records:
        series_id = record["series_id"]
        provenance = Provenance(
            created_by=Actor.HUMAN,
            actor_id=PACK_ACTOR_ID,
            created_at=PACK_DATE,
            certainty=_certainty_from_status(record["status"], series_id),
            method=PACK_METHOD,
            analysis_logic_version=None,
            supporting_source_ids=[],
            notes=_build_notes(record) or None,
        )
        result.append(
            Series(
                series_id=series_id,
                name=record["canonical_name"],
                role=_EXPLICIT_ROLES.get(series_id, SeriesRole.OTHER),
                description=record.get("description"),
                created_at=PACK_DATE,
                provenance=provenance,
                active=True,
            )
        )
    return result


if __name__ == "__main__":
    registry = load_series_registry()
    print(f"Loaded {len(registry)} series")
    for s in registry:
        print(f"  {s.series_id}: {s.name!r} [{s.role.value}] certainty={s.provenance.certainty.value}")
