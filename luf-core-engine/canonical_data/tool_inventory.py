"""
Loader for canonical_data/source/inventory_candidates.json into validated
CanonicalTool objects (Direktorder S6/S7).

This module NEVER upgrades an entry's canonical_status or confidence beyond
what the JSON source states. Every loaded tool is CANONICAL_CANDIDATE (or
HISTORICAL_LUF_MATERIAL for the process model, per S14's evidence model)
with human_review_status=PENDING -- promotion only happens through
human_review.workflow.promote_to_canonical(), never here.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import TypeAdapter

from schema.enums import CanonicalStatus, ComponentOrderType, ToolConfidence, ToolType
from schema.provenance import Provenance
from schema.sentinels import UNKNOWN
from schema.tool_registry import CanonicalTool

_SOURCE_PATH = Path(__file__).parent / "source" / "inventory_candidates.json"

_FRAMEWORK_KNOWN_BOUNDARIES = (
    "Direktorder S7: 'namnet på ett ramverk är inte tillräckligt för att den byggande "
    "AI:n ska fylla i hur det fungerar.' Only the bare acronym name was provided by the "
    "Direktorder text; no LUF-specific components, order, purpose, or usage context "
    "was supplied or found in any accessible source. Deliberately left UNKNOWN rather "
    "than filled in from this acronym's generic meaning elsewhere in the coaching/"
    "leadership industry, which would misrepresent it as verified LUF material."
)


def _provenance(meta_common: dict) -> Provenance:
    return Provenance(**meta_common)


def load_inventory_candidates() -> list[CanonicalTool]:
    raw = json.loads(_SOURCE_PATH.read_text(encoding="utf-8"))
    prov_common = raw["_meta"]["provenance_common"]
    tools: list[CanonicalTool] = []

    for entry in raw["triangles_and_n_part_models"]:
        tools.append(
            CanonicalTool(
                stable_tool_id=entry["stable_tool_id"],
                canonical_name=entry["canonical_name"],
                tool_type=ToolType.TRIANGLE,
                components=entry["components"],
                component_order=ComponentOrderType.UNVERIFIED,
                source_reference=f"Direktorder LUF Core Engine V1 (2026-08-20), {entry['source_ref']}",
                source_provenance="Verbatim list provided by Jan Stefors in Direktorder LUF Core Engine V1 (2026-08-20); "
                "not yet cross-verified against an independent LUF source document.",
                confidence=ToolConfidence.UNVERIFIED,
                canonical_status=CanonicalStatus.CANONICAL_CANDIDATE,
                known_boundaries=entry.get(
                    "notes_extra",
                    "Component breakdown and name are as given by the Direktorder text only; "
                    "purpose, contexts, and usage direction are UNVERIFIED.",
                ),
                provenance=_provenance(prov_common),
            )
        )

    for entry in raw["process_models"]:
        tools.append(
            CanonicalTool(
                stable_tool_id=entry["stable_tool_id"],
                canonical_name=entry["canonical_name"],
                tool_type=ToolType.PROCESS_MODEL,
                components=entry["components"],
                component_order=ComponentOrderType.CYCLIC,
                purpose=entry.get("purpose", UNKNOWN),
                developmental_use=entry.get("developmental_use", UNKNOWN),
                source_reference=f"Direktorder LUF Core Engine V1 (2026-08-20), {entry['source_ref']}",
                source_provenance="Verbatim from Direktorder LUF Core Engine V1 (2026-08-20), S6 and S12; "
                "not yet cross-verified against an independent LUF source document.",
                confidence=ToolConfidence.UNVERIFIED,
                canonical_status=CanonicalStatus.CANONICAL_CANDIDATE,
                known_boundaries="Direktorder explicitly names this a system motor (S12) but supplies no "
                "operational detail beyond the five-step description; exact trigger conditions and "
                "measurement method are UNVERIFIED.",
                provenance=_provenance(prov_common),
            )
        )

    for entry in raw["framework_acronyms_name_only"]:
        tools.append(
            CanonicalTool(
                stable_tool_id=entry["stable_tool_id"],
                canonical_name=entry["canonical_name"],
                tool_type=ToolType.FRAMEWORK_ACRONYM,
                components=[],
                component_order=ComponentOrderType.UNVERIFIED,
                source_reference="Direktorder LUF Core Engine V1 (2026-08-20), §7",
                source_provenance="Name only, listed in Direktorder LUF Core Engine V1 (2026-08-20), §7, as an "
                "example of a framework to inventory IF verified LUF source material exists. No such "
                "material was found in any repository accessible to this session.",
                confidence=ToolConfidence.UNVERIFIED,
                canonical_status=CanonicalStatus.HISTORICAL_LUF_MATERIAL,
                known_boundaries=_FRAMEWORK_KNOWN_BOUNDARIES,
                provenance=_provenance(prov_common),
            )
        )

    return tools


def validate_all() -> list[CanonicalTool]:
    """Raises if the source JSON cannot be loaded into valid CanonicalTool records."""

    tools = load_inventory_candidates()
    TypeAdapter(list[CanonicalTool]).validate_python(tools)
    ids = [t.stable_tool_id for t in tools]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate stable_tool_id values found in inventory_candidates.json")
    return tools
