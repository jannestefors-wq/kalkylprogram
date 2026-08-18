"""
Fixture dataset (Beslut 28).

Purpose: prove the schema hangs together end-to-end, nothing more. Content
here is either (a) drawn verbatim from the approved Fas 0 material quoted in
the brief (the two example series names, the eight Canonical Voice Core
principles, two Supported Voice Principles, and the "chef avbrot" example
input), or (b) clearly-fictional, structurally-illustrative placeholder
material invented only to exercise fields the approved material didn't
supply an example for (a second Idea/Source/ContentRecord, a placeholder
Thesis Family, a placeholder reader-feedback entry). None of it is a
publish-ready LUF post, and no real third party's words are put in their
mouth: the Parastoo-style ReaderFeedback below is an explicit placeholder,
not a reproduction of her actual review.

This module intentionally does not import Streamlit or anything from the
rest of the repository -- it is self-contained.
"""

from __future__ import annotations

from datetime import datetime, timezone

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
    Series,
    Source,
    ThesisFamily,
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
    SeriesRole,
    SourceReliability,
    SourceType,
    StyleAttributeCategory,
    UsageRights,
    VoicePrincipleStatus,
)
from schema.voice import RepetitionSignal, StyleAttribute

T0 = datetime(2026, 1, 15, 9, 0, tzinfo=timezone.utc)


def _prov(certainty: EvidenceCertainty, method: str, actor_id: str = "fas0_editorial_process") -> Provenance:
    return Provenance(
        created_by=Actor.HUMAN,
        actor_id=actor_id,
        created_at=T0,
        certainty=certainty,
        method=method,
        supporting_source_ids=[],
    )


def build_fixture_dataset() -> dict[str, list]:
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
        series=["SER-002"],
        reliability=SourceReliability.VERIFIED,
        usage_rights=UsageRights.OWNED,
        notes="Fixture source backing RI-001 / IDEA-001.",
    )
    source_2 = Source(
        source_id="SRC-002",
        source_type=SourceType.REVIEW,
        title="Reader feedback compilation (placeholder)",
        author=None,
        date=T0,
        language="en",
        origin="Fixture placeholder -- real feedback to be attached later without schema change.",
        content_reference=None,
        themes=["credit", "recognition"],
        people=[],
        models=[],
        series=[],
        reliability=SourceReliability.REPORTED,
        usage_rights=UsageRights.UNCLEAR,
        notes="Placeholder only. See ReaderFeedback RF-001.",
    )

    # ---- SERIES (2, names taken verbatim from Beslut 17's own examples) ----
    series_1 = Series(
        series_id="SER-001",
        name="Kara ...",
        role=SeriesRole.FORM_BEARING_PILLAR,
        description="Form-bearing pillar series, defined by a recurring address form rather than a topic.",
        created_at=T0,
        provenance=_prov(EvidenceCertainty.VERIFIED, "fas_0a_analysis"),
    )
    series_2 = Series(
        series_id="SER-002",
        name="Det langa spelet",
        role=SeriesRole.TIME_PERSPECTIVE,
        description="Series defined by a long time-horizon perspective on a situation.",
        created_at=T0,
        provenance=_prov(EvidenceCertainty.VERIFIED, "fas_0a_analysis"),
    )

    # ---- THESIS FAMILY (placeholder -- real Fas 0 8-family list pending) --
    thesis_family_1 = ThesisFamily(
        thesis_family_id="TF-001",
        name="Osynligt maktbruk i vardagliga moten (fixture placeholder)",
        core_statement="Makt utovas ofta genom sma, upprepade handlingar snarare an enskilda stora beslut.",
        description="Placeholder thesis family for fixture purposes; not one of the eight approved Fas 0 families.",
        example_phrasings=["En chef avbrot samma medarbetare tre ganger under motet."],
        created_at=T0,
        provenance=_prov(EvidenceCertainty.ANALYTICAL_PROPOSAL, "fixture_placeholder"),
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
            provenance=_prov(EvidenceCertainty.ANALYTICAL_PROPOSAL, "fas_0a_analysis", actor_id="fas0a_pipeline_v1"),
        ),
        related_series=["SER-002"],
        related_thesis_families=["TF-001"],
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
            provenance=_prov(EvidenceCertainty.ANALYTICAL_PROPOSAL, "fas_0a_analysis", actor_id="fas0a_pipeline_v1"),
        ),
        related_series=["SER-001"],
        related_thesis_families=["TF-001"],
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
        thesis_family_id="TF-001",
        primary_variation_dimension=None,
        status=AngleStatus.SELECTED,
        provenance=_prov(EvidenceCertainty.ANALYTICAL_PROPOSAL, "fas_0a_analysis", actor_id="fas0a_pipeline_v1"),
    )

    # ---- READER FEEDBACK (1 placeholder) ---------------------------------
    reader_feedback_1 = ReaderFeedback(
        reader_feedback_id="RF-001",
        source_id="SRC-002",
        content_reference="CONTENT-001",
        feedback_text="[placeholder -- full original review text to be attached later without schema change]",
        feedback_reference=None,
        effect_observations=["reader reported recognizing the situation described"],
        verification_status=FeedbackVerificationStatus.UNVERIFIED,
        date=T0,
        language="en",
        notes="Fixture placeholder standing in for a real future reader review (e.g. Parastoo's).",
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
        voice_core_version_ref="voice-core-1.0",
        series_ids=["SER-002"],
        thesis_family_id="TF-001",
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
                evidence_reader_feedback_ids=["RF-001"],
            ),
        ],
        variation_fingerprint=None,  # filled in below via build_variation_fingerprint
        style_attributes_used=["SA-001"],
        repetition_signals_observed=["RS-001"],
        related_content_ids=[],
        source_ids=["SRC-001"],
        final_text=None,
        provenance=_prov(EvidenceCertainty.ANALYTICAL_PROPOSAL, "draft_generation_fixture", actor_id="fixture"),
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
        voice_core_version_ref="voice-core-1.0",
        series_ids=["SER-001"],
        thesis_family_id="TF-001",
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
        provenance=_prov(EvidenceCertainty.ANALYTICAL_PROPOSAL, "draft_generation_fixture", actor_id="fixture"),
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
        voice_core_version_ref="voice-core-1.0",
        provenance=_prov(EvidenceCertainty.ANALYTICAL_PROPOSAL, "quality_gate_fixture", actor_id="fixture_quality_gate_v0"),
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
        "sources": [source_1, source_2],
        "series": [series_1, series_2],
        "thesis_families": [thesis_family_1],
        "voice_principles": voice_principles,
        "style_attributes": style_attributes,
        "repetition_signals": repetition_signals,
        "reader_effects": reader_effects_catalog,
        "ideas": [idea_1, idea_2],
        "angles": [angle_1],
        "reader_feedback": [reader_feedback_1],
        "content_records": [content_1, content_2],
        "quality_assessments": [quality_assessment_1],
        "human_decisions": [human_decision_1],
    }


if __name__ == "__main__":
    dataset = build_fixture_dataset()
    for key, items in dataset.items():
        print(f"{key}: {len(items)}")
