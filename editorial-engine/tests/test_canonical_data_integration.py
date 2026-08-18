"""Canonical Data Integration V1 -- validation of the real 16 Series / 8 ThesisFamily
records loaded from canonical_data/source/LUF_Canonical_Data_Pack_V1.json.

Covers order section 14 (validation) and section 15 (regression tests), including
the five project-leadership classification decisions and the "all eight Thesis
Families are strongly_supported" requirement.
"""

from __future__ import annotations

import pytest

from canonical_data.series_registry import load_series_registry
from canonical_data.thesis_family_registry import load_thesis_family_registry
from schema.enums import EvidenceCertainty
from schema.integrity import check_relations


@pytest.fixture(scope="module")
def series_registry():
    return load_series_registry()


@pytest.fixture(scope="module")
def thesis_family_registry():
    return load_thesis_family_registry()


def _by_name(records, name):
    return next(r for r in records if r.name == name)


# ---- counts -----------------------------------------------------------

def test_series_registry_contains_exactly_16(series_registry):
    assert len(series_registry) == 16


def test_thesis_family_registry_contains_exactly_8(thesis_family_registry):
    assert len(thesis_family_registry) == 8


# ---- uniqueness ---------------------------------------------------------

def test_series_ids_are_unique(series_registry):
    ids = [s.series_id for s in series_registry]
    assert len(ids) == len(set(ids))


def test_thesis_family_ids_are_unique(thesis_family_registry):
    ids = [t.thesis_family_id for t in thesis_family_registry]
    assert len(ids) == len(set(ids))


def test_series_and_thesis_family_id_namespaces_do_not_collide(series_registry, thesis_family_registry):
    series_ids = {s.series_id for s in series_registry}
    thesis_ids = {t.thesis_family_id for t in thesis_family_registry}
    assert series_ids.isdisjoint(thesis_ids)


# ---- no leftover placeholders -------------------------------------------

def test_no_series_placeholder_ids_remain(series_registry):
    """The old V1/V1.1 fixture placeholders used ids 'SER-001'/'SER-002' -- these
    must never appear in the real canonical registry."""
    ids = {s.series_id for s in series_registry}
    assert "SER-001" not in ids
    assert "SER-002" not in ids
    # every real id follows the source pack's own naming convention
    assert all(sid.startswith("series-") for sid in ids)


def test_no_thesis_family_placeholder_ids_remain(thesis_family_registry):
    ids = {t.thesis_family_id for t in thesis_family_registry}
    assert "TF-001" not in ids
    assert all(tid.startswith("thesis-") for tid in ids)


def test_fixture_dataset_no_longer_carries_placeholder_series_or_thesis_names(dataset):
    """docs/OPEN_QUESTIONS.md OQ-4 is resolved: fixtures/fixture_dataset.py now
    references the real registry loaded from canonical_data/, not synthetic
    placeholders that duplicate real canonical names."""
    assert len(dataset["series"]) == 16
    assert len(dataset["thesis_families"]) == 8
    series_ids = {s.series_id for s in dataset["series"]}
    thesis_ids = {t.thesis_family_id for t in dataset["thesis_families"]}
    assert "SER-001" not in series_ids and "SER-002" not in series_ids
    assert "TF-001" not in thesis_ids


# ---- the five project-leadership classification decisions (order section 4) ----

def test_decision_a_kara_is_canonical(series_registry):
    s = _by_name(series_registry, "Kära …")
    assert s.provenance.certainty == EvidenceCertainty.VERIFIED


def test_decision_b_valkommen_till_tvartomvarlden_is_canonical(series_registry):
    s = _by_name(series_registry, "Välkommen till tvärtomvärlden")
    assert s.provenance.certainty == EvidenceCertainty.VERIFIED


def test_decision_c_om_du_bara_fick_valja_en_sak_is_strongly_supported_not_upgraded(series_registry):
    s = _by_name(series_registry, "Om du bara fick välja en sak …")
    assert s.provenance.certainty == EvidenceCertainty.STRONGLY_SUPPORTED


def test_decision_d_ubuntu_is_strongly_supported_and_documented_as_series_candidate(series_registry):
    s = _by_name(series_registry, "Ubuntu. det mänskliga")
    assert s.provenance.certainty == EvidenceCertainty.STRONGLY_SUPPORTED
    assert "SERIES CANDIDATE" in (s.provenance.notes or "")


def test_decision_e_easy_to_choose_you_is_strongly_supported_and_documented_as_editorial_track(series_registry):
    s = _by_name(series_registry, "Gör det enkelt att välja dig / Make It Easy To Choose You")
    assert s.provenance.certainty == EvidenceCertainty.STRONGLY_SUPPORTED
    assert "EDITORIAL TRACK" in (s.provenance.notes or "")


def test_no_series_was_upgraded_to_canonical_beyond_the_pack(series_registry):
    """Only series already marked 'canonical' in the source pack may carry
    EvidenceCertainty.VERIFIED -- nothing was upgraded during integration."""
    canonical_names = {
        s.name for s in series_registry if s.provenance.certainty == EvidenceCertainty.VERIFIED
    }
    expected_canonical_names = {
        "Kära …",
        "Diagnos före lösning",
        "Arbetslivets lögner",
        "Alla vet. Ingen säger det.",
        "Det tysta priset",
        "Möten vi borde slippa",
        "Kultur utan filter",
        "Välkommen till tvärtomvärlden",
        "Nu räcker det",
        "Marknadsföring utan filter",
    }
    assert canonical_names == expected_canonical_names


# ---- thesis families: all eight strongly_supported, none upgraded ----------

def test_all_eight_thesis_families_are_strongly_supported(thesis_family_registry):
    for t in thesis_family_registry:
        assert t.provenance.certainty == EvidenceCertainty.STRONGLY_SUPPORTED, t.name


def test_thesis_family_names_match_the_approved_eight(thesis_family_registry):
    names = {t.name for t in thesis_family_registry}
    assert names == {
        "Symptom är inte orsak",
        "Verklighet före berättelse",
        "Det osynliga styr",
        "Ansvar får inte passeras",
        "Relation och resultat hör ihop",
        "Förändring är beteende över tid",
        "Tystnad har ett pris",
        "Tydlighet skapar val",
    }


# ---- core_thesis vs ThesisFamily separation preserved (Beslut 18 / order section 6) --

def test_thesis_family_core_statement_is_the_family_level_wording_not_a_single_text(thesis_family_registry):
    for t in thesis_family_registry:
        assert t.core_statement  # non-empty
        assert t.example_phrasings == []  # none fabricated -- source pack had none to give


# ---- provenance / evidence preserved (order section 9) ---------------------

def test_series_provenance_preserves_language_and_evidence_information(series_registry):
    kara = _by_name(series_registry, "Kära …")
    assert kara.provenance.notes is not None
    assert "Sprak: sv" in kara.provenance.notes
    assert "Evidence:" in kara.provenance.notes

    ubuntu = _by_name(series_registry, "Ubuntu. det mänskliga")
    assert "Sprak: sv, en" in (ubuntu.provenance.notes or "")


def test_thesis_family_provenance_preserves_evidence(thesis_family_registry):
    for t in thesis_family_registry:
        assert t.provenance.notes and "Evidence:" in t.provenance.notes


def test_all_registry_entries_created_by_human_not_ai(series_registry, thesis_family_registry):
    """The pack is curated, project-leadership-approved reference data -- not an AI
    interpretation of raw input -- so Actor.HUMAN is correct and no
    analysis_logic_version is required (Provenance's own validator would reject
    Actor.AI_SYSTEM without one)."""
    from schema.enums import Actor

    for s in series_registry:
        assert s.provenance.created_by == Actor.HUMAN
    for t in thesis_family_registry:
        assert t.provenance.created_by == Actor.HUMAN


# ---- schema validation + relation integrity ---------------------------------

def test_all_24_records_validate_against_schema_v1_1(series_registry, thesis_family_registry):
    """Construction already proves Pydantic validation passed; this additionally
    round-trips every record through JSON serialization/deserialization."""
    from schema import Series, ThesisFamily

    for s in series_registry:
        assert Series.model_validate_json(s.model_dump_json()) == s
    for t in thesis_family_registry:
        assert ThesisFamily.model_validate_json(t.model_dump_json()) == t


def test_canonical_registry_alone_has_no_dangling_relations(series_registry, thesis_family_registry):
    violations = check_relations({"series": series_registry, "thesis_families": thesis_family_registry})
    assert violations == []


def test_registry_loading_is_reproducible(series_registry, thesis_family_registry):
    """Loading the registry twice from the same source pack yields identical data."""
    series_again = load_series_registry()
    families_again = load_thesis_family_registry()
    assert [s.model_dump() for s in series_registry] == [s.model_dump() for s in series_again]
    assert [t.model_dump() for t in thesis_family_registry] == [t.model_dump() for t in families_again]
