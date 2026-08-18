"""
Referential-integrity checker (TECHNICAL PROPOSAL -- see docs/TECHNICAL_PROPOSALS.md).

This is a validation UTILITY, not a canonical entity and not an engine: it
walks a dict of fixture/dataset objects and confirms that every field which
names another object's id (e.g. `Idea.related_series`, `ContentRecord.
source_ids`) actually points at an id that exists in the same dataset. It
performs no editorial judgement and makes no decisions -- it only answers
"does this id exist," which is the minimum needed to prove the schema's
relations are checkable at all (Beslut 29: "invalid relation IDs fangas").
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RelationViolation:
    object_type: str
    object_id: str
    field: str
    missing_id: str

    def __str__(self) -> str:  # pragma: no cover - convenience only
        return f"{self.object_type}[{self.object_id}].{self.field} -> missing '{self.missing_id}'"


def check_relations(dataset: dict[str, list]) -> list[RelationViolation]:
    ids = {
        "series": {s.series_id for s in dataset.get("series", [])},
        "thesis_families": {t.thesis_family_id for t in dataset.get("thesis_families", [])},
        "sources": {s.source_id for s in dataset.get("sources", [])},
        "ideas": {i.idea_id for i in dataset.get("ideas", [])},
        "angles": {a.angle_id for a in dataset.get("angles", [])},
        "content_records": {c.content_id for c in dataset.get("content_records", [])},
        "reader_effects": {r.reader_effect_id for r in dataset.get("reader_effects", [])},
        "reader_feedback": {r.reader_feedback_id for r in dataset.get("reader_feedback", [])},
        "style_attributes": {s.style_attribute_id for s in dataset.get("style_attributes", [])},
        "repetition_signals": {r.repetition_signal_id for r in dataset.get("repetition_signals", [])},
        "quality_assessments": {q.quality_assessment_id for q in dataset.get("quality_assessments", [])},
        "raw_inputs": {r.raw_input_id for r in dataset.get("raw_inputs", [])},
    }

    violations: list[RelationViolation] = []

    def _check(object_type: str, object_id: str, field: str, value: str | None, pool: str) -> None:
        if value and value not in ids[pool]:
            violations.append(RelationViolation(object_type, object_id, field, value))

    def _check_many(object_type: str, object_id: str, field: str, values: list[str], pool: str) -> None:
        for v in values:
            _check(object_type, object_id, field, v, pool)

    for idea in dataset.get("ideas", []):
        _check("Idea", idea.idea_id, "raw_input_id", idea.raw_input_id, "raw_inputs")
        _check("Idea", idea.idea_id, "source_id", idea.source_id, "sources")
        _check_many("Idea", idea.idea_id, "related_series", idea.related_series, "series")
        _check_many("Idea", idea.idea_id, "related_thesis_families", idea.related_thesis_families, "thesis_families")

    for angle in dataset.get("angles", []):
        _check("Angle", angle.angle_id, "idea_id", angle.idea_id, "ideas")
        _check("Angle", angle.angle_id, "thesis_family_id", angle.thesis_family_id, "thesis_families")

    for content in dataset.get("content_records", []):
        _check("ContentRecord", content.content_id, "idea_id", content.idea_id, "ideas")
        _check("ContentRecord", content.content_id, "angle_id", content.angle_id, "angles")
        _check("ContentRecord", content.content_id, "thesis_family_id", content.thesis_family_id, "thesis_families")
        _check_many("ContentRecord", content.content_id, "series_ids", content.series_ids, "series")
        _check_many("ContentRecord", content.content_id, "source_ids", content.source_ids, "sources")
        _check_many(
            "ContentRecord", content.content_id, "style_attributes_used", content.style_attributes_used, "style_attributes"
        )
        _check_many(
            "ContentRecord",
            content.content_id,
            "repetition_signals_observed",
            content.repetition_signals_observed,
            "repetition_signals",
        )
        for assoc in content.reader_effects:
            _check("ContentRecord", content.content_id, "reader_effects[].reader_effect_id", assoc.reader_effect_id, "reader_effects")
            _check_many(
                "ContentRecord",
                content.content_id,
                "reader_effects[].evidence_reader_feedback_ids",
                assoc.evidence_reader_feedback_ids,
                "reader_feedback",
            )

    for qa in dataset.get("quality_assessments", []):
        _check("QualityAssessment", qa.quality_assessment_id, "content_id", qa.content_id, "content_records")

    for hd in dataset.get("human_decisions", []):
        _check(
            "HumanDecision",
            hd.decision_id,
            "based_on_quality_assessment_id",
            hd.based_on_quality_assessment_id,
            "quality_assessments",
        )

    return violations
