"""V1B order section 31-34: Golden Memory Path, Novelty Boundary Path,
Repetition Path, Publication-Evidence Path. Fake/stub provider only
(RuleBasedAnalysisProvider) -- no real LLM used anywhere in this file."""

from __future__ import annotations

from engine.models import PipelineOutcome, RecommendationOutcome, RepetitionRiskLevel
from memory.comparison import MemoryComparisonOutcome
from memory.ingestion import load_editorial_memory
from memory.models import PublicationStatus
from memory.pipeline import run_v1b_pipeline


def test_golden_memory_path_end_to_end():
    """Order section 31: full chain, with a raw idea deliberately close to several
    of the 12 full-text WORK records (thesis-reality-before-story-001)."""

    raw_text = "En chef avbrot samma medarbetare tre ganger under motet, men bad efteratt om arlig feedback."
    r = run_v1b_pipeline(raw_text)

    assert r.outcome == PipelineOutcome.COMPLETED
    assert r.raw_input.text == raw_text  # raw input preserved verbatim
    assert r.idea is not None
    assert r.interpretation_draft is not None
    assert r.classification is not None
    assert r.memory_retrieval is not None
    assert r.memory_comparison is not None
    assert r.recommendation is not None

    # Memory retrieval actually found real, explainable records.
    assert r.memory_retrieval.matches
    for m in r.memory_retrieval.matches:
        assert m.why_retrieved and m.matched_signals

    assert r.memory_comparison.outcome == MemoryComparisonOutcome.MATCHES_FOUND
    assert {"content-work-001", "content-work-005", "content-work-006", "content-work-012"} <= {
        m.content_id for m in r.memory_comparison.matches
    }

    assert 1 <= len(r.candidate_angles) <= 3


def test_novelty_boundary_path_expresses_no_match_correctly():
    """Order section 32: a scenario where no relevant memory record exists. The
    system must say 'no relevant match in available Editorial Memory' (the
    machine representation NO_MATCH_IN_AVAILABLE_MEMORY), never 'this has
    never been written about before'.

    Constructed with an explicitly empty memory corpus -- the real 21-record
    corpus is small enough that the provider's fixed vocabulary (order section
    22 forbids changing it) almost always finds SOME overlap, so the boundary
    behavior itself is isolated here rather than relying on finding a real
    raw idea that happens to miss all 21 records."""

    raw_text = "En chef avbrot samma medarbetare tre ganger under motet, men bad efteratt om arlig feedback."
    r = run_v1b_pipeline(raw_text, memory_records=[])

    assert r.outcome == PipelineOutcome.COMPLETED
    assert r.memory_retrieval.matches == []
    assert r.memory_comparison.outcome == MemoryComparisonOutcome.NO_MATCH_IN_AVAILABLE_MEMORY

    combined_notes = (r.memory_retrieval.boundary_note + " " + r.memory_comparison.memory_limitation_note).lower()
    assert "never written about" in combined_notes  # named, so the boundary is explicit about what's forbidden
    assert "never that the idea was" in combined_notes  # ...but only inside the negation that forbids it
    assert "no match was found in the available editorial memory" in combined_notes  # the ALLOWED phrasing


def test_repetition_path_finds_contrast_or_abstains():
    """Order section 33: a scenario very close to real material. Repetition
    risk must become HIGH when evidence supports it, and Candidate Angles
    must then either find a genuinely different defensible direction or
    return NO_STRONG_ANGLE -- never silently recommend the repeat."""

    raw_text = "En chef avbrot samma medarbetare tre ganger under motet, men bad efteratt om arlig feedback."
    r = run_v1b_pipeline(raw_text)  # full real corpus -- strong overlap on thesis-reality-before-story-001

    assert any(c.repetition_risk == RepetitionRiskLevel.HIGH for c in r.candidate_angles)
    assert r.recommendation.outcome in (RecommendationOutcome.NO_STRONG_ANGLE, RecommendationOutcome.RECOMMENDED)
    if r.recommendation.outcome == RecommendationOutcome.RECOMMENDED:
        # If something WAS recommended despite HIGH-risk siblings, it must not itself be the
        # high-risk one -- i.e. the system found genuine contrast, not a repeat.
        recommended = next(c for c in r.candidate_angles if c.angle.angle_id == r.recommendation.recommended_angle_id)
        assert recommended.repetition_risk != RepetitionRiskLevel.HIGH
    else:
        assert r.recommendation.recommended_angle_id is None


def test_publication_evidence_path_distinguishes_all_three_statuses():
    """Order section 34: proves the engine can use published_verified, unverified
    work material, and unknown-status material simultaneously as different kinds
    of evidence without conflating their status."""

    from engine.models import ClassificationOutcome, ClassificationResult
    from memory.comparison import compare_to_editorial_memory

    records = load_editorial_memory()
    work = next(r for r in records if r.content_id == "content-work-001")  # unverified_draft_or_work_material, FULL
    published = next(r for r in records if r.content_id == "content-published-003")  # published_verified, PARTIAL
    unknown = next(r for r in records if r.content_id == "content-other-001")  # unknown, PARTIAL

    interpretation_text = "foretagsutveckling och verklighet samt truth and leadership samt tystnad"
    classification = ClassificationResult(outcome=ClassificationOutcome.NO_CONFIDENT_CANONICAL_MATCH)
    result = compare_to_editorial_memory(interpretation_text, classification, [work, published, unknown])

    statuses_seen = {m.content_id: m.publication_status for m in result.matches}
    assert statuses_seen == {
        "content-work-001": PublicationStatus.UNVERIFIED_DRAFT_OR_WORK_MATERIAL,
        "content-published-003": PublicationStatus.PUBLISHED_VERIFIED,
        "content-other-001": PublicationStatus.UNKNOWN,
    }
    # All three statuses are DISTINCT values on the result -- never collapsed into one boolean.
    assert len(set(statuses_seen.values())) == 3

    notes = {m.content_id: m.evidence_boundary_note for m in result.matches}
    assert "INTE" in notes["content-work-001"]  # work material is explicitly NOT proof of publication
    assert "publiceringsevidens" in notes["content-published-003"]  # published_verified IS real evidence
    assert "unknown" in notes["content-other-001"].lower()  # unknown stays unknown, neither assumed
