"""
Canonical Thesis Family Registry V1 -- loads the real 8 thesis families from
`canonical_data/source/LUF_Canonical_Data_Pack_V1.json` and maps them to
Schema V1.1's `ThesisFamily` model. See docs/DATA_MAPPING_NOTE.md for the
full field-by-field mapping; this docstring covers the judgment calls.

All eight source records carry `status: "strongly_supported"` -- per the
order (section 5): "Samtliga ska behalla status: strongly_supported. Ingen
av dem ska uppgraderas till canonical. Det ar ett medvetet
projektledarbeslut." Mapped uniformly to `Provenance.certainty =
EvidenceCertainty.STRONGLY_SUPPORTED` for all eight, for the same reason
described in `series_registry.py` (ThesisFamily has no canonical/
strongly_supported field of its own; Provenance.certainty already carries
that distinction schema-wide).

WHY the source pack's `related_topics` list is mapped into `description`:
`ThesisFamily` has no dedicated "related topics" field, and the source pack
has no separate "description" field for thesis families (only `definition`,
which maps to `core_statement`). Rather than drop `related_topics`
(forbidden -- order section 9: "Forlora inte information"), it is rendered
into the otherwise-unused `description` field as a labelled list. This is a
reformatting choice, not a redactional one: the topic words themselves are
carried verbatim.

`example_phrasings` (a real ThesisFamily field) is left as an empty list:
the source pack has no equivalent field, and inventing example phrasings
would be new redactional content, not technical mapping.
"""

from __future__ import annotations

import json
from pathlib import Path

from schema import Provenance, ThesisFamily
from schema.enums import Actor, EvidenceCertainty

from .series_registry import PACK_ACTOR_ID, PACK_DATE, PACK_METHOD, SOURCE_PATH


def _certainty_from_status(status: str, thesis_family_id: str) -> EvidenceCertainty:
    if status == "strongly_supported":
        return EvidenceCertainty.STRONGLY_SUPPORTED
    if status == "canonical":
        return EvidenceCertainty.VERIFIED
    raise ValueError(f"Unrecognized source status {status!r} for {thesis_family_id!r} -- refusing to guess a mapping.")


def _build_description(record: dict) -> str | None:
    topics = record.get("related_topics") or []
    if not topics:
        return None
    return "Relaterade teman: " + ", ".join(topics) + "."


def _build_notes(record: dict) -> str:
    parts: list[str] = []
    evidence = record.get("evidence") or []
    if evidence:
        parts.append("Evidence: " + " | ".join(evidence))
    notes = record.get("notes") or []
    if notes:
        parts.append("Notes: " + " | ".join(notes))
    return " ".join(parts)


def load_thesis_family_registry(source_path: Path = SOURCE_PATH) -> list[ThesisFamily]:
    """Build the 8 canonical ThesisFamily objects from the Work data pack."""

    pack = json.loads(source_path.read_text(encoding="utf-8"))
    records = pack["thesis_families"]

    result: list[ThesisFamily] = []
    for record in records:
        thesis_family_id = record["thesis_family_id"]
        provenance = Provenance(
            created_by=Actor.HUMAN,
            actor_id=PACK_ACTOR_ID,
            created_at=PACK_DATE,
            certainty=_certainty_from_status(record["status"], thesis_family_id),
            method=PACK_METHOD,
            analysis_logic_version=None,
            supporting_source_ids=[],
            notes=_build_notes(record) or None,
        )
        result.append(
            ThesisFamily(
                thesis_family_id=thesis_family_id,
                name=record["canonical_name"],
                core_statement=record["definition"],
                description=_build_description(record),
                example_phrasings=[],
                created_at=PACK_DATE,
                provenance=provenance,
                active=True,
            )
        )
    return result


if __name__ == "__main__":
    registry = load_thesis_family_registry()
    print(f"Loaded {len(registry)} thesis families")
    for t in registry:
        print(f"  {t.thesis_family_id}: {t.name!r} certainty={t.provenance.certainty.value}")
