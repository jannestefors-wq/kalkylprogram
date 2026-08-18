"""
Step 6: Recommended Angle (order section 13, 17).

A small, fully transparent point system -- "regelbaserad bedomning framfor
falsk matematisk precision" (order section 13). Every point is named in
`AngleScore.breakdown`; nothing here is a learned weight or a similarity
score a human can't audit by reading the numbers.

Criteria weighed (order section 13's own list):
    - repetition risk (LOW preferred, HIGH penalized)
    - evidence grounding (evidence_basis non-empty)
    - closeness to canonical Voice Core reference (voice_alignment.score)
    - classification confidence (a weak proxy for "how well is this idea understood")

If no candidate clears the minimum bar, or there are no candidates at all,
the result is `RecommendationOutcome.NO_STRONG_ANGLE` -- never a forced
pick (order section 17).
"""

from __future__ import annotations

from .models import AngleScore, CandidateAngle, ConfidenceLevel, RecommendationOutcome, RecommendationResult, RepetitionRiskLevel

MINIMUM_SCORE_TO_RECOMMEND = 3

_REPETITION_POINTS = {
    RepetitionRiskLevel.LOW: 2,
    RepetitionRiskLevel.MEDIUM: 0,
    RepetitionRiskLevel.HIGH: -3,
}
_CONFIDENCE_POINTS = {
    ConfidenceLevel.HIGH: 2,
    ConfidenceLevel.MEDIUM: 1,
    ConfidenceLevel.LOW: 0,
}


def _score(candidate: CandidateAngle) -> AngleScore:
    breakdown = {
        "voice_alignment": candidate.voice_alignment.score,
        "repetition_risk": _REPETITION_POINTS[candidate.repetition_risk],
        "evidence_grounded": 1 if candidate.evidence_basis else 0,
        "classification_confidence": _CONFIDENCE_POINTS[candidate.confidence],
    }
    return AngleScore(angle_id=candidate.angle.angle_id, score=sum(breakdown.values()), breakdown=breakdown)


def recommend(candidates: list[CandidateAngle]) -> RecommendationResult:
    if not candidates:
        return RecommendationResult(
            outcome=RecommendationOutcome.NO_STRONG_ANGLE,
            recommended_angle_id=None,
            scores=[],
            rationale="Inga kandidatvinklar att rekommendera bland.",
        )

    scores = [_score(c) for c in candidates]
    best = max(scores, key=lambda s: s.score)

    if best.score < MINIMUM_SCORE_TO_RECOMMEND:
        return RecommendationResult(
            outcome=RecommendationOutcome.NO_STRONG_ANGLE,
            recommended_angle_id=None,
            scores=scores,
            rationale=(
                f"Basta kandidat ({best.angle_id}) nadde poang {best.score}, under minimigransen "
                f"{MINIMUM_SCORE_TO_RECOMMEND}. Ingen kandidat ar stark nog for att rekommenderas."
            ),
        )

    return RecommendationResult(
        outcome=RecommendationOutcome.RECOMMENDED,
        recommended_angle_id=best.angle_id,
        scores=scores,
        rationale=(
            f"{best.angle_id} rekommenderas med poang {best.score} "
            f"(breakdown: {best.breakdown}), hogst av {len(candidates)} kandidat(er)."
        ),
    )
