"""
Step 5: Candidate Angles (order section 11-14).

Wraps provider-generated angle seeds into `CandidateAngle` (engine/models.py),
each carrying a real canonical `schema.Angle`, a repetition-risk assessment
derived from `comparison.py`'s result, and a `VoiceAlignmentCheck` derived
from Canonical Voice Core V1 -- used only as an assessment reference
(order section 14), never as a prose style generator: nothing here writes
finished sentences in a particular voice, it only checks a handful of
structural properties of text the provider already produced.

Never more than 3 candidates (order section 11), and never padded: if the
provider legitimately proposes fewer, fewer are returned.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from schema import Angle, Provenance
from schema.enums import Actor, AngleStatus, EvidenceCertainty

from .comparison import ComparisonResult
from .models import CandidateAngle, ClassificationResult, ConfidenceLevel, RepetitionRiskLevel, VoiceAlignmentCheck
from .provider import AnalysisProvider

MAX_CANDIDATE_ANGLES = 3

_ABSTRACTION_WORDS = {"synergier", "paradigm", "holistiskt", "helhetsgrepp", "optimera", "leverage"}
_DIRECTIVE_WORDS = {"maste", "alltid", "bevisar", "garanterat", "obligatoriskt"}
_HUMAN_WORDS = {
    "chef", "chefen", "medarbetare", "medarbetaren", "kollega", "kollegan", "person", "personen",
    "manniska", "manniskan", "den", "lasaren",
}
_PATTERN_WORDS = {"monster", "upprepas", "upprepade", "over tid", "monstret"}
_SYMPTOM_WORDS = {"synlig", "synliga", "symptom", "handelse", "handelsen"}
_CAUSE_WORDS = {"djupare", "underliggande", "orsak", "bakomliggande"}


def _check_voice_alignment(text: str) -> VoiceAlignmentCheck:
    lowered = text.lower()
    words = set(lowered.replace(".", " ").replace(",", " ").split())

    return VoiceAlignmentCheck(
        stays_close_to_the_human=bool(_HUMAN_WORDS & words),
        makes_a_pattern_visible=any(p in lowered for p in _PATTERN_WORDS),
        distinguishes_symptom_from_possible_cause=any(s in lowered for s in _SYMPTOM_WORDS) and any(c in lowered for c in _CAUSE_WORDS),
        avoids_unnecessary_abstraction=not bool(_ABSTRACTION_WORDS & words),
        leaves_room_for_reader_judgment=not bool(_DIRECTIVE_WORDS & words),
        notes="Regelbaserad kontroll mot Canonical Voice Core-referenser (Beslut 11) -- ingen stilgenerering.",
    )


def _repetition_risk_for(canonical_relations: list[str], comparison: ComparisonResult) -> tuple[RepetitionRiskLevel, str]:
    if comparison.outcome.value == "NO_MATCH_IN_AVAILABLE_MEMORY":
        return RepetitionRiskLevel.LOW, "Inga narliggande poster hittades i tillganglig canonical memory."

    strong_overlaps = [
        m for m in comparison.matches
        if (set(m.shared_thesis_family_ids) & set(canonical_relations)) or (set(m.shared_territory_ids) & set(canonical_relations))
    ]
    if strong_overlaps:
        ids = ", ".join(m.content_id for m in strong_overlaps)
        return (
            RepetitionRiskLevel.HIGH,
            f"HIGH eftersom denna vinkels canonical-relationer delas med befintligt material ({ids}).",
        )

    if comparison.matches:
        ids = ", ".join(m.content_id for m in comparison.matches)
        return (
            RepetitionRiskLevel.MEDIUM,
            f"MEDIUM: viss termoverlappning med befintligt material ({ids}), men ingen delad Thesis Family/Territory for denna vinkel.",
        )

    return RepetitionRiskLevel.LOW, "Ingen overlappning med de jamforda posterna."


def propose_candidate_angles(
    idea_id: str,
    interpretation_texts: dict[str, str],
    classification: ClassificationResult,
    comparison: ComparisonResult,
    provider: AnalysisProvider,
    analysis_logic_version: str,
    actor_id: str = "v1a_rule_based_provider",
) -> list[CandidateAngle]:
    seeds = provider.propose_angle_seeds(interpretation_texts)[:MAX_CANDIDATE_ANGLES]

    canonical_relation_ids = [m.canonical_id for m in (classification.thesis_family_matches + classification.territory_matches)]
    best_thesis_family_id = classification.thesis_family_matches[0].canonical_id if classification.thesis_family_matches else None

    candidates: list[CandidateAngle] = []
    for seed in seeds:
        angle_id = f"ANGLE-V1A-{uuid.uuid4().hex[:8]}"
        evidence_keys = [k for k in seed.get("evidence_keys", "").split(",") if k]
        evidence_basis = [interpretation_texts[k] for k in evidence_keys if interpretation_texts.get(k)]

        angle = Angle(
            angle_id=angle_id,
            idea_id=idea_id,
            created_at=datetime.now(timezone.utc),
            title=seed["title"],
            description=seed["core"],
            thesis_family_id=best_thesis_family_id,
            primary_variation_dimension=None,
            status=AngleStatus.PROPOSED,
            provenance=Provenance(
                created_by=Actor.AI_SYSTEM,
                actor_id=actor_id,
                created_at=datetime.now(timezone.utc),
                certainty=EvidenceCertainty.ANALYTICAL_PROPOSAL,
                method="v1a_rule_based_angle_proposal",
                analysis_logic_version=analysis_logic_version,
                supporting_source_ids=[],
            ),
        )

        repetition_risk, repetition_rationale = _repetition_risk_for(canonical_relation_ids, comparison)
        voice_alignment = _check_voice_alignment(seed["core"] + " " + seed["why_relevant"])

        candidates.append(
            CandidateAngle(
                angle=angle,
                core=seed["core"],
                why_relevant=seed["why_relevant"],
                canonical_relations=canonical_relation_ids,
                differentiation=seed["differentiation"],
                repetition_risk=repetition_risk,
                repetition_rationale=repetition_rationale,
                evidence_basis=evidence_basis,
                confidence=classification.thesis_family_matches[0].confidence if classification.thesis_family_matches else ConfidenceLevel.LOW,
                voice_alignment=voice_alignment,
            )
        )

    return candidates
