"""
Fixture dataset (Beslut 28; extended for V1.1).

Purpose: prove the schema hangs together end-to-end, nothing more. Content
here is either (a) drawn verbatim from the approved Fas 0 material quoted in
the brief (the two example series names, the eight Canonical Voice Core
principles, two Supported Voice Principles, the "chef avbrot" example
input, and "Makt" as the Beslut 17 example territory), or (b)
clearly-fictional, structurally-illustrative placeholder material invented
only to exercise fields the approved material didn't supply an example for
(a second Idea/Source/ContentRecord, a placeholder Thesis Family, a
placeholder reader-feedback entry). None of it is a publish-ready LUF post,
and no real third party's words are put in their mouth: the Parastoo-style
ReaderFeedback below is an explicit placeholder, not a reproduction of her
actual review.

V1.1 additions: a Territory ("Makt", TER-001), a VoiceCoreSnapshot
(SNAP-001, bundling the 8 canonical principles), and AI-attributed
Provenance (Actor.AI_SYSTEM + analysis_logic_version) on the records that
genuinely represent an AI-produced interpretation (IdeaInterpretation,
Angle, the QualityAssessment, and the two draft ContentRecords) -- the
Fas 0B-sourced registry entries (Series, ThesisFamily, VoicePrinciple,
StyleAttribute, RepetitionSignal, ReaderEffect, Territory) stay
Actor.HUMAN, since they represent project-leadership-approved editorial
truth, not an automated reading of raw input.

Canonical Data Integration V1: the two synthetic Series placeholders
("SER-001"/"SER-002", named "Kara ..."/"Det langa spelet") and the one
synthetic ThesisFamily placeholder ("TF-001") that previously stood in for
the real Fas 0A registries are REMOVED from this fixture entirely -- their
names duplicated real canonical series names, which is exactly the
confusion the integration order prohibits leaving behind. `series` and
`thesis_families` below are now the REAL 16 series / 8 thesis families,
loaded from `canonical_data/` (see docs/DATA_MAPPING_NOTE.md).

`content_1`/`content_2` and `idea_1`/`idea_2`/`angle_1` link to the FIRST
and SECOND entries of the real registries (by the source pack's own
order) purely to prove the FK mechanism works against real reference data.
This is a positional, arbitrary technical choice for fixture-construction
purposes -- it is NOT an editorial classification of this fixture's
illustrative (non-canonical, never-published) content, and must not be
read as one.

This module intentionally does not import Streamlit or anything from the
rest of the repository -- it is self-contained.
"""

from __future__ import annotations

from datetime import datetime, timezone

from canonical_data.reader_feedback_registry import load_book_source, load_parastoo_reader_feedback
from canonical_data.series_registry import load_series_registry
from canonical_data.thesis_family_registry import load_thesis_family_registry
from schema import (
    Angle,
    ContentForm,
    ContentRecord,
    ContentWhat,
    HumanDecision,
    Idea,
    IdeaInterpretation,
    Provenance,
    QualityAssessment,
    QualityRuleFinding,
    RawInput,
    ReaderEffect,
    ReaderEffectAssociation,
    ReaderFeedback,
    Source,
    Territory,
    VoiceCoreSnapshot,
    VoicePrinciple,
    build_variation_fingerprint,
)
from schema.enums import (
    Actor,
    AngleStatus,
    ContentStatus,
    CtaType,
    DecisionTargetType,
    DegreeLevel,
    EditorialPotential,
    EmotionalRegister,
    EndingType,
    EvidenceCertainty,
    FeedbackVerificationStatus,
    HumanDecisionType,
    IdeaStatus,
    InputType,
    LengthClass,
    NarrativeMode,
    NoveltyRisk,
    PointOfView,
    QualityAssessmentResult,
    QualitySeverity,
    ReaderEffectCategory,
    ReaderEffectMode,
    RepetitionSignalType,
    ReturnPoint,
    RhythmPattern,
    SourceReliability,
    SourceType,
    StyleAttributeCategory,
    UsageRights,
    VoicePrincipleStatus,
)
from schema.voice import RepetitionSignal, StyleAttribute

T0 = datetime(2026, 1, 15, 9, 0, tzinfo=timezone.utc)


def _prov(
    certainty: EvidenceCertainty,
    method: str,
    actor_id: str = "fas0_editorial_process",
    actor: Actor = Actor.HUMAN,
    analysis_logic_version: str | None = None,
) -> Provenance:
    return Provenance(
        created_by=actor,
        actor_id=actor_id,
        created_at=T0,
        certainty=certainty,
        method=method,
        analysis_logic_version=analysis_logic_version,
        supporting_source_ids=[],
    )


def _ai_prov(certainty: EvidenceCertainty, method: str, actor_id: str, analysis_logic_version: str) -> Provenance:
    """V1.1 (OQ-2): AI-attributed provenance always carries analysis_logic_version -- Provenance's own
    validator (schema/provenance.py) rejects Actor.AI_SYSTEM without it, so this helper cannot forget it."""
    return _prov(certainty, method, actor_id=actor_id, actor=Actor.AI_SYSTEM, analysis_logic_version=analysis_logic_version)


def build_fixture_dataset() -> dict[str, list]:
    # ---- CANONICAL REGISTRIES (real 16 series / 8 thesis families) --------
    # Loaded first so their ids are available to every other fixture record below.
    # See canonical_data/ and docs/DATA_MAPPING_NOTE.md.
    series_registry = load_series_registry()
    thesis_family_registry = load_thesis_family_registry()
    fixture_series_1_id = series_registry[0].series_id  # "series-dear-001" -- positional, see module docstring
    fixture_series_2_id = series_registry[1].series_id  # "series-diagnosis-before-solution-001"
    fixture_thesis_family_1_id = thesis_family_registry[0].thesis_family_id  # "thesis-symptom-cause-001"
    fixture_thesis_family_2_id = thesis_family_registry[1].thesis_family_id  # "thesis-reality-before-story-001"

    # ---- CANONICAL READER FEEDBACK (Final Canonical Data Closure) ---------
    # Parastoo Ebrahimzadeh's real, full original review -- see canonical_data/reader_feedback_registry.py.
    parastoo_book_source = load_book_source()
    parastoo_reader_feedback = load_parastoo_reader_feedback()

    # ---- RAW INPUT (2) -----------------------------------------------
    raw_input_1 = RawInput(
        raw_input_id="RI-001",
        captured_at=T0,
        text="En chef avbrot samma medarbetare tre ganger under motet.",
        input_type=InputType.OBSERVATION,
        origin_note="Janne, observation from a leadership meeting.",
        language="sv",
    )
    raw_input_2 = RawInput(
        raw_input_id="RI-002",
        captured_at=T0,
        text=(
            "A team lead presented an idea in the all-hands. It was the same idea a junior "
            "colleague had already raised twice in earlier meetings, without follow-up either time."
        ),
        input_type=InputType.OBSERVATION,
        origin_note="Fixture placeholder observation (illustrative only).",
        language="en",
    )

    # ---- SOURCE (2) ----------------------------------------------------
    source_1 = Source(
        source_id="SRC-001",
        source_type=SourceType.EXPERIENCE,
        title="Leadership meeting observation log",
        author="Janne Stefors",
        date=T0,
        language="sv",
        origin="Direct observation",
        content_reference=None,
        themes=["power", "voice", "interruption"],
        people=[],
        models=[],
        series=[fixture_series_1_id],
        reliability=SourceReliability.VERIFIED,
        usage_rights=UsageRights.OWNED,
        notes="Fixture source backing RI-001 / IDEA-001.",
    )
    source_2 = Source(
        source_id="SRC-002",
        source_type=SourceType.REVIEW,
        title="Reader feedback compilation (TEST_ONLY placeholder)",
        author=None,
        date=T0,
        language="en",
        origin="TEST_ONLY fixture placeholder -- not a real source.",
        content_reference=None,
        themes=["credit", "recognition"],
        people=[],
        models=[],
        series=[],
        reliability=SourceReliability.REPORTED,
        usage_rights=UsageRights.UNCLEAR,
        notes="TEST_ONLY. See ReaderFeedback RF-TEST-ONLY-001. The real Parastoo Ebrahimzadeh review "
        "is in canonical_data/, backed by its own Source (source-book-leadership-without-filter).",
    )

    # ---- TERRITORY (V1.1, OQ-3 -- "Makt" is Beslut 17's own example) ------
    territory_1 = Territory(
        territory_id="TER-001",
        name="Makt",
        description="Beslut 17's own example of a territory, distinct from the 'Tillit' topic and the "
        "'Kara ...' / 'Det langa spelet' series.",
        created_at=T0,
        provenance=_prov(EvidenceCertainty.VERIFIED, "fas_0a_analysis"),
    )

    # ---- VOICE PRINCIPLES (Canonical Voice Core V1, verbatim; Supported subset) --
    canonical_texts = [
        ("VP-C1", "Manniskan forblir synlig i systemet.", None),
        ("VP-C2", "Ansvar ska bli mojligt och konkret.", None),
        ("VP-C3", "Verkligheten gar fore den bekvama berattelsen.", None),
        ("VP-C4", "Det osynliga ska fa sprak.", None),
        ("VP-C5", "Symptom ska leda blicken mot samband och karna.", None),
        ("VP-C6", "Relation och resultat halls ihop.", None),
        ("VP-C7", "Lasaren ska fa behalla sitt omdome.", None),
        ("VP-C8", "LUF talar med lasaren, aldrig over lasaren.", None),
    ]
    canonical_principles = [
        VoicePrinciple(
            voice_principle_id=vid,
            name=text,
            definition=text,
            anti_definition=None,
            status=VoicePrincipleStatus.CANONICAL,
            evidence=[_prov(EvidenceCertainty.VERIFIED, "fas_0b_analysis")],
            version="1.0",
            valid_from=T0,
        )
        for vid, text, _ in canonical_texts
    ]

    supported_texts = [
        ("VP-S1", "Makt ar relationell, inte bara formell."),
        ("VP-S2", "Klarhet utan forenkling."),
    ]
    supported_principles = [
        VoicePrinciple(
            voice_principle_id=vid,
            name=text,
            definition=text,
            status=VoicePrincipleStatus.STRONGLY_SUPPORTED,
            evidence=[_prov(EvidenceCertainty.STRONGLY_SUPPORTED, "fas_0b_analysis")],
            version="1.0",
            valid_from=T0,
        )
        for vid, text in supported_texts
    ]
    voice_principles = canonical_principles + supported_principles

    # ---- VOICE CORE SNAPSHOT (V1.1, OQ-1) --------------------------------
    # References the 8 canonical principles by id -- does not duplicate their text.
    voice_core_snapshot_1 = VoiceCoreSnapshot(
        snapshot_id="SNAP-001",
        version="1.0",
        created_at=T0,
        voice_principle_ids=[p.voice_principle_id for p in canonical_principles],
        active=True,
        provenance=_prov(EvidenceCertainty.VERIFIED, "voice_core_snapshot_compilation"),
        notes="Bundles Canonical Voice Core V1 (the 8 canonical principles) as the 'voice-core-1.0' reference.",
    )

    # ---- STYLE ATTRIBUTE (2 of the Fas 0B options) ----------------------
    style_short_opening = StyleAttribute(
        style_attribute_id="SA-001",
        name="Kort deklarativ oppning",
        category=StyleAttributeCategory.OPENING,
        description="A short declarative sentence opens the text.",
        example="Han avbrot henne igen.",
        created_at=T0,
        provenance=_prov(EvidenceCertainty.STRONGLY_SUPPORTED, "fas_0b_analysis"),
    )
    style_closing_question = StyleAttribute(
        style_attribute_id="SA-002",
        name="Slutfraga",
        category=StyleAttributeCategory.ENDING,
        description="The text ends on a direct question to the reader.",
        example="Vad hande sist du blev avbruten?",
        created_at=T0,
        provenance=_prov(EvidenceCertainty.STRONGLY_SUPPORTED, "fas_0b_analysis"),
    )
    style_attributes = [style_short_opening, style_closing_question]

    # ---- REPETITION SIGNAL (matching two of the above) -------------------
    repetition_signals = [
        RepetitionSignal(
            repetition_signal_id="RS-001",
            signal_type=RepetitionSignalType.SHORT_THESIS_OPENING,
            related_style_attribute_id="SA-001",
            description="Short declarative thesis-style opening, flagged in Fas 0A/0B as overused.",
            detection_notes="Future: count occurrences of this opening pattern across last N publications.",
            created_at=T0,
            provenance=_prov(EvidenceCertainty.VERIFIED, "fas_0a_analysis"),
        ),
        RepetitionSignal(
            repetition_signal_id="RS-002",
            signal_type=RepetitionSignalType.CLOSING_QUESTION,
            related_style_attribute_id="SA-002",
            description="Closing question, flagged in Fas 0A/0B as overused.",
            detection_notes="Future: count occurrences of ending_type=OPEN_QUESTION / cta_type=EXPLICIT_QUESTION.",
            created_at=T0,
            provenance=_prov(EvidenceCertainty.VERIFIED, "fas_0a_analysis"),
        ),
    ]

    # ---- READER EFFECT (2) -------------------------------------------
    reader_effects_catalog = [
        ReaderEffect(
            reader_effect_id="RE-001",
            category=ReaderEffectCategory.EMOTIONAL,
            name="obehag",
            description="Discomfort.",
            examples=["obehag", "discomfort"],
            created_at=T0,
            provenance=_prov(EvidenceCertainty.VERIFIED, "fas_0b_analysis"),
        ),
        ReaderEffect(
            reader_effect_id="RE-002",
            category=ReaderEffectCategory.COGNITIVE,
            name="perspektivskifte",
            description="Perspective shift -- language for pattern, symptom vs. cause.",
            examples=["perspektivskifte", "sprak for monster"],
            created_at=T0,
            provenance=_prov(EvidenceCertainty.VERIFIED, "fas_0b_analysis"),
        ),
    ]

    # ---- IDEA (2) -------------------------------------------------------
    idea_1 = Idea(
        idea_id="IDEA-001",
        created_at=T0,
        raw_input_id="RI-001",
        input_type=InputType.OBSERVATION,
        source_id="SRC-001",
        language="sv",
        intended_market="SE",
        interpretation=IdeaInterpretation(
            observed_situation="En medarbetare avbryts upprepade ganger av sin chef under ett mote.",
            human_subject="Medarbetaren som avbryts.",
            human_experience="Att formuleringar tystnar innan de hinner fardigt.",
            visible_problem="Avbrotten.",
            hidden_conflict="Vem som har ratt att avsluta en tanke i rummet.",
            possible_root_causes=["Informell maktordning", "Otränad motesledning"],
            power_dimension="Formell roll (chef) anvands for att kontrollera talutrymme.",
            relationship_dimension="Upprepningen eroderar tillit over tid.",
            system_dimension="Ingen i rummet ingriper -- monstret ar tyst accepterat.",
            possible_consequence="Medarbetaren slutar lagga fram ideer.",
            provenance=_ai_prov(
                EvidenceCertainty.ANALYTICAL_PROPOSAL, "fas_0a_analysis", "fas0a_pipeline_v1", "fas0a-analysis-logic-1.0"
            ),
        ),
        related_series=[fixture_series_1_id],
        related_thesis_families=[fixture_thesis_family_1_id],
        editorial_potential=EditorialPotential.HIGH,
        novelty_risk=NoveltyRisk.MEDIUM,
        status=IdeaStatus.ANALYZED,
    )
    idea_2 = Idea(
        idea_id="IDEA-002",
        created_at=T0,
        raw_input_id="RI-002",
        input_type=InputType.OBSERVATION,
        source_id=None,
        language="en",
        intended_market="US",
        interpretation=IdeaInterpretation(
            observed_situation="A junior colleague's idea is re-presented by a team lead and only then taken seriously.",
            human_subject="The junior colleague whose idea was not credited.",
            human_experience="Watching your own words become audible only once someone else says them.",
            visible_problem="Repetition without attribution.",
            hidden_conflict="Whose voice counts as a source vs. whose voice counts as an echo.",
            possible_root_causes=["Status-based listening", "No norm for crediting"],
            power_dimension="Hierarchy determines whose words are heard as original.",
            relationship_dimension="Erodes the junior colleague's willingness to speak up again.",
            system_dimension="No meeting norm exists for acknowledging prior contributions.",
            possible_consequence="Junior colleague disengages from future idea-sharing.",
            provenance=_ai_prov(
                EvidenceCertainty.ANALYTICAL_PROPOSAL, "fas_0a_analysis", "fas0a_pipeline_v1", "fas0a-analysis-logic-1.0"
            ),
        ),
        related_series=[fixture_series_2_id],
        related_thesis_families=[fixture_thesis_family_2_id],
        editorial_potential=EditorialPotential.MEDIUM,
        novelty_risk=NoveltyRisk.LOW,
        status=IdeaStatus.ANGLED,
    )

    # ---- ANGLE (1, on IDEA-001) ------------------------------------------
    angle_1 = Angle(
        angle_id="ANGLE-001",
        idea_id="IDEA-001",
        created_at=T0,
        title="Ratten att avsluta en tanke",
        description="Angle focused on the moment of interruption itself as the unit of analysis, rather than the outcome of the meeting.",
        thesis_family_id=fixture_thesis_family_1_id,
        primary_variation_dimension=None,
        status=AngleStatus.SELECTED,
        provenance=_ai_prov(
            EvidenceCertainty.ANALYTICAL_PROPOSAL, "fas_0a_analysis", "fas0a_pipeline_v1", "fas0a-analysis-logic-1.0"
        ),
    )

    # ---- READER FEEDBACK (TEST_ONLY fixture illustration) -----------------
    # Final Canonical Data Closure: renamed from "RF-001" to make unmistakably
    # clear this is NOT Parastoo's real review (that is now
    # canonical_data.reader_feedback_registry.load_parastoo_reader_feedback(),
    # loaded into this dataset separately below) -- it never has been; it is a
    # structurally-illustrative fixture row exercising the intended/observed
    # split, kept distinct so it can never be mistaken for canonical data.
    reader_feedback_1 = ReaderFeedback(
        reader_feedback_id="RF-TEST-ONLY-001",
        source_id="SRC-002",
        content_reference="CONTENT-001",
        feedback_text="[TEST_ONLY fixture illustration -- not a real review. See canonical_data/ for the real Parastoo Ebrahimzadeh ReaderFeedback.]",
        feedback_reference=None,
        effect_observations=["reader reported recognizing the situation described"],
        verification_status=FeedbackVerificationStatus.UNVERIFIED,
        date=T0,
        language="en",
        notes="TEST_ONLY -- fixture illustration for schema-proof purposes, not derived from any real review.",
    )

    # ---- CONTENT RECORD (2) ----------------------------------------------
    content_1 = ContentRecord(
        content_id="CONTENT-001",
        created_at=T0,
        published_at=None,
        language="sv",
        market="SE",
        platform="linkedin",
        status=ContentStatus.QUALITY_REVIEW,
        idea_id="IDEA-001",
        angle_id="ANGLE-001",
        voice_core_snapshot_id="SNAP-001",
        series_ids=[fixture_series_1_id],
        territory_ids=["TER-001"],
        thesis_family_id=fixture_thesis_family_1_id,
        what=ContentWhat(
            topic="Tillit",
            subtopics=["moteskultur", "avbrott"],
            core_thesis="Ratten att avsluta en tanke ar en form av makt.",
            human_conflict="Medarbetaren tystnas upprepade ganger.",
            hidden_pattern="Monstret upprepas utan att nagon namner det.",
            root_cause="Informell maktordning som aldrig görs synlig.",
            perspective="Den som avbryts.",
        ),
        form_detail=ContentForm(
            form="linkedin_post",
            narrative_mode=NarrativeMode.SCENE,
            point_of_view=PointOfView.OBSERVER,
            opening_type="kort_deklarativ_oppning",
            opening_text="Han avbrot henne igen.",
            dramaturgy="single_scene_then_reflection",
            paragraph_pattern="short_paragraphs",
            sentence_rhythm=RhythmPattern.MIXED,
            length_class=LengthClass.MEDIUM,
            emotional_register=EmotionalRegister.DISCOMFORT,
            personal_presence=DegreeLevel.LOW,
            solution_degree=DegreeLevel.NONE,
            question_count=0,
            contrast_usage=DegreeLevel.MEDIUM,
            metaphor_usage=DegreeLevel.NONE,
            dialogue_usage=DegreeLevel.LOW,
            scene_usage=DegreeLevel.HIGH,
            ending_type=EndingType.UNRESOLVED_SCENE,
            cta_type=CtaType.NONE,
            signature_type="none",
            key_phrases=["avbrot henne igen"],
            rhetorical_patterns=["scene_then_silence"],
        ),
        reader_effects=[
            ReaderEffectAssociation(reader_effect_id="RE-001", mode=ReaderEffectMode.INTENDED),
            ReaderEffectAssociation(
                reader_effect_id="RE-001",
                mode=ReaderEffectMode.OBSERVED,
                evidence_reader_feedback_ids=["RF-TEST-ONLY-001"],
            ),
        ],
        variation_fingerprint=None,  # filled in below via build_variation_fingerprint
        style_attributes_used=["SA-001"],
        repetition_signals_observed=["RS-001"],
        related_content_ids=[],
        source_ids=["SRC-001"],
        final_text=None,
        provenance=_ai_prov(EvidenceCertainty.ANALYTICAL_PROPOSAL, "draft_generation_fixture", "fixture", "draft-gen-fixture-0.1"),
    )
    content_1 = content_1.model_copy(
        update={"variation_fingerprint": build_variation_fingerprint(content_1, T0)}
    )

    content_2 = ContentRecord(
        content_id="CONTENT-002",
        created_at=T0,
        published_at=T0,
        language="en",
        market="US",
        platform="linkedin",
        status=ContentStatus.PUBLISHED,
        idea_id="IDEA-002",
        angle_id=None,
        voice_core_snapshot_id="SNAP-001",
        series_ids=[fixture_series_2_id],
        thesis_family_id=fixture_thesis_family_2_id,
        what=ContentWhat(
            topic="Recognition",
            subtopics=["credit", "meetings"],
            core_thesis="An idea is not 'new' just because a more senior voice said it second.",
            human_conflict="The junior colleague watches their own idea gain legitimacy only once repeated.",
            hidden_pattern="Attribution follows hierarchy, not chronology.",
            root_cause="No norm exists for naming where an idea first came from.",
            perspective="The junior colleague.",
        ),
        form_detail=ContentForm(
            form="linkedin_post",
            narrative_mode=NarrativeMode.ARGUMENT,
            point_of_view=PointOfView.FIRST_PERSON,
            opening_type="direct_address",
            opening_text="You've had this happen to you.",
            dramaturgy="claim_then_example",
            paragraph_pattern="mixed",
            sentence_rhythm=RhythmPattern.FLOWING,
            length_class=LengthClass.SHORT,
            emotional_register=EmotionalRegister.RECOGNITION,
            personal_presence=DegreeLevel.MEDIUM,
            solution_degree=DegreeLevel.LOW,
            question_count=1,
            contrast_usage=DegreeLevel.LOW,
            metaphor_usage=DegreeLevel.NONE,
            dialogue_usage=DegreeLevel.NONE,
            scene_usage=DegreeLevel.LOW,
            ending_type=EndingType.OPEN_QUESTION,
            cta_type=CtaType.EXPLICIT_QUESTION,
            signature_type="none",
            key_phrases=["said it second"],
            rhetorical_patterns=["direct_address_then_question"],
        ),
        reader_effects=[
            ReaderEffectAssociation(reader_effect_id="RE-002", mode=ReaderEffectMode.INTENDED),
        ],
        variation_fingerprint=None,
        style_attributes_used=["SA-002"],
        repetition_signals_observed=["RS-002"],
        related_content_ids=["CONTENT-001"],
        source_ids=[],
        final_text="You've had this happen to you. [...] (fixture placeholder -- not a publish-ready post)",
        provenance=_ai_prov(EvidenceCertainty.ANALYTICAL_PROPOSAL, "draft_generation_fixture", "fixture", "draft-gen-fixture-0.1"),
    )
    content_2 = content_2.model_copy(
        update={"variation_fingerprint": build_variation_fingerprint(content_2, T0)}
    )

    # ---- QUALITY ASSESSMENT (1, on CONTENT-002) ---------------------------
    quality_assessment_1 = QualityAssessment(
        quality_assessment_id="QA-001",
        content_id="CONTENT-002",
        created_at=T0,
        result=QualityAssessmentResult.REWORK,
        findings=[
            QualityRuleFinding(
                triggered_rule="repetition.closing_question.overused",
                evidence="RS-002 observed on CONTENT-002; also present on 2 of last 5 publications (fixture claim).",
                severity=QualitySeverity.MODERATE,
            )
        ],
        recommended_return_point=ReturnPoint.GENERATION,
        voice_core_snapshot_id="SNAP-001",
        provenance=_ai_prov(
            EvidenceCertainty.ANALYTICAL_PROPOSAL, "quality_gate_fixture", "fixture_quality_gate_v0", "quality-gate-fixture-0.1"
        ),
    )

    # ---- HUMAN DECISION (1) ------------------------------------------------
    human_decision_1 = HumanDecision(
        decision_id="HD-001",
        target_type=DecisionTargetType.CONTENT_RECORD,
        target_id="CONTENT-002",
        decision=HumanDecisionType.REWORK,
        decided_by="Janne Stefors",
        decided_at=T0,
        based_on_quality_assessment_id="QA-001",
        reason="Haller med Quality Assessment: slutfragan ar overanvand just nu.",
    )

    return {
        "raw_inputs": [raw_input_1, raw_input_2],
        "sources": [source_1, source_2, parastoo_book_source],
        "series": series_registry,
        "territories": [territory_1],
        "thesis_families": thesis_family_registry,
        "voice_principles": voice_principles,
        "voice_core_snapshots": [voice_core_snapshot_1],
        "style_attributes": style_attributes,
        "repetition_signals": repetition_signals,
        "reader_effects": reader_effects_catalog,
        "ideas": [idea_1, idea_2],
        "angles": [angle_1],
        "reader_feedback": [reader_feedback_1, parastoo_reader_feedback],
        "content_records": [content_1, content_2],
        "quality_assessments": [quality_assessment_1],
        "human_decisions": [human_decision_1],
    }


if __name__ == "__main__":
    dataset = build_fixture_dataset()
    for key, items in dataset.items():
        print(f"{key}: {len(items)}")
