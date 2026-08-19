"""
V1B Correction Order TEST D, E, F -- permanent regression tests for the
genericity defect found by V1B Final Audit (docs/V1B_AUDIT_REPORT.md) and
fixed per docs/V1B_CORRECTION_REPORT.md: a shared canonical relation alone
(with no content-level corroboration) or a single incidental shared word
must never drive HIGH repetition risk or NO_STRONG_ANGLE.

Also covers order section 13's six additional generalization inputs, none
of which are hardcoded content-ids/phrases in production code -- see
memory/comparison.py and memory/bridge.py.
"""

from __future__ import annotations

from engine.models import PipelineOutcome, RecommendationOutcome, RepetitionRiskLevel
from memory.pipeline import run_v1b_pipeline

GOLDEN_LIKE_TEXT = "En chef avbrot samma medarbetare tre ganger under motet, men bad efteratt om arlig feedback."

RELEVANT_TEXT = (
    "Chefen gjorde en tydlig observation om vad som hande pa kontoret tre ganger, "
    "men var forsta tolkning av situationen visade sig vara helt fel."
)


def test_d_genuinely_relevant_memory_can_still_reach_high():
    """TEST D: an input genuinely close to real fulltext material (shared canonical
    relation AND real, named vocabulary overlap) can still get HIGH when the
    evidence supports it -- the fix must not have thrown out real signal too."""

    r = run_v1b_pipeline(RELEVANT_TEXT)
    assert r.outcome == PipelineOutcome.COMPLETED
    strong = [m for m in r.memory_comparison.matches if m.repetition_signal_strength == "strong"]
    assert strong, "expected at least one genuinely corroborated (canonical + content) match"
    for m in strong:
        assert m.shared_thesis_family_ids or m.shared_territory_ids
        assert m.topic_overlap or m.text_overlap_terms
    assert any(c.repetition_risk == RepetitionRiskLevel.HIGH for c in r.candidate_angles)


def test_e_unrelated_material_does_not_get_high_from_lexical_noise():
    """TEST E: material with no genuine relation to the corpus must not get HIGH
    repetition merely because generic terms happen to overlap."""

    unrelated = "Det regnade i tre dagar sa vi stannade hemma och spelade bradspel med barnen istallet for att aka ut."
    r = run_v1b_pipeline(unrelated)
    assert r.outcome == PipelineOutcome.COMPLETED
    strong = [m for m in r.memory_comparison.matches if m.repetition_signal_strength == "strong"]
    assert strong == [], f"unrelated input produced a 'strong' match: {strong}"
    assert all(c.repetition_risk != RepetitionRiskLevel.HIGH for c in r.candidate_angles)


def test_f_lexical_noise_alone_cannot_reach_high_or_no_strong_angle():
    """TEST F: input sharing only common/generic words with the corpus (no
    canonical relation, no specific vocabulary) must not reach HIGH or force
    NO_STRONG_ANGLE on that basis alone."""

    noise_only = "Det var en vanlig dag och vi gjorde det vi alltid gor pa kontoret utan nagot speciellt."
    r = run_v1b_pipeline(noise_only)
    assert r.outcome == PipelineOutcome.COMPLETED
    assert all(c.repetition_risk != RepetitionRiskLevel.HIGH for c in r.candidate_angles)
    assert r.recommendation.outcome != RecommendationOutcome.NO_STRONG_ANGLE or not r.candidate_angles


def test_lone_canonical_relation_alone_is_insufficient_for_high():
    """The precise mechanism the audit found: GOLDEN_LIKE_TEXT triggers canonical
    classification matches (thesis-reality-before-story-001 etc.) via the
    provider's own boilerplate, but shares no real, specific vocabulary with the
    raw input for any single record. Must never reach HIGH on canonical-match
    alone against the real, full corpus."""

    r = run_v1b_pipeline(GOLDEN_LIKE_TEXT)
    assert r.outcome == PipelineOutcome.COMPLETED
    assert r.classification.thesis_family_matches or r.classification.territory_matches  # canonical signal IS present
    strong = [m for m in r.memory_comparison.matches if m.repetition_signal_strength == "strong"]
    assert strong == []
    assert all(c.repetition_risk != RepetitionRiskLevel.HIGH for c in r.candidate_angles)


# --- Six additional generalization inputs (order section 13), none hardcoded
# in production code (memory/*.py contains no content-id or phrase special-cases). ---


def test_generalization_relevant_leadership_topic():
    text = "Vi matte samma resultat tre ganger men diskuterade aldrig vilket ansvar och vilken konsekvens som lag bakom."
    r = run_v1b_pipeline(text)
    assert r.outcome == PipelineOutcome.COMPLETED
    # Shares content-work-002's own topic labels -- may legitimately show up as
    # weak (content-only) or strong evidence, but must never be silently ignored.
    assert r.memory_comparison.matches


def test_generalization_unrelated_everyday_activity():
    text = "Vi malade om koket i helgen och valde tre olika ljusare fargprover an vad vi hade fore."
    r = run_v1b_pipeline(text)
    assert r.outcome in (PipelineOutcome.COMPLETED, PipelineOutcome.MORE_CONTEXT_REQUIRED)
    if r.outcome == PipelineOutcome.COMPLETED:
        strong = [m for m in r.memory_comparison.matches if m.repetition_signal_strength == "strong"]
        assert strong == []


def test_generalization_shared_word_different_meaning_is_a_known_limitation():
    """Documented, accepted residual limitation (docs/V1B_CORRECTION_REPORT.md):
    exact word-overlap matching cannot distinguish word SENSE, only word FORM.
    "konsekvens" (consequence) in an administrative-rule sentence can still
    coincide with content-work-008's topic label of the same spelling. This is
    NOT the systemic defect the audit found (which affected every input
    unconditionally) -- it is an occasional, explainable homonym collision, and
    it remains explainable: the match still names exactly which word matched."""

    text = "Det blev konsekvens av regeln att alla fick nya passerkort, en enkel administrativ atgard tre veckor senare."
    r = run_v1b_pipeline(text)
    assert r.outcome == PipelineOutcome.COMPLETED
    for m in r.memory_comparison.matches:
        if m.repetition_signal_strength == "strong":
            # Whatever fired, it is fully explainable -- not a silent/opaque match.
            assert m.why_relevant
            assert m.topic_overlap or m.text_overlap_terms


def test_generalization_common_words_no_real_theme():
    text = "Det var en vanlig dag och vi gjorde det vi alltid gor pa kontoret utan nagot speciellt tre ganger i veckan."
    r = run_v1b_pipeline(text)
    assert r.outcome == PipelineOutcome.COMPLETED
    strong = [m for m in r.memory_comparison.matches if m.repetition_signal_strength == "strong"]
    assert strong == []
    assert all(c.repetition_risk != RepetitionRiskLevel.HIGH for c in r.candidate_angles)


def test_generalization_near_symptom_cause_theme():
    text = "Vi ser lag lonsamhet och kvalitetsbrister men letar sallan efter den bakomliggande orsaken tre kvartal i rad."
    r = run_v1b_pipeline(text)
    assert r.outcome == PipelineOutcome.COMPLETED
    # No assertion on the exact strength tier here -- only that whatever tier is
    # assigned is genuinely explainable (never an opaque/unmotivated HIGH).
    for m in r.memory_comparison.matches:
        assert m.why_relevant


def test_generalization_near_trust_silence_different_angle():
    text = "Tystnaden i teamet handlade inte om radsla utan om att ingen visste vem som skulle prata forst av de tre."
    r = run_v1b_pipeline(text)
    assert r.outcome == PipelineOutcome.COMPLETED
    strong = [m for m in r.memory_comparison.matches if m.repetition_signal_strength == "strong"]
    for m in strong:
        assert m.shared_thesis_family_ids or m.shared_territory_ids
        assert m.topic_overlap or m.text_overlap_terms
