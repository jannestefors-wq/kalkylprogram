"""
V1B Correction Order TEST A, B, C -- permanent regression tests for the
verbatim-text defect found by V1B Final Audit (docs/V1B_AUDIT_REPORT.md):
two records had curly apostrophes silently normalized to straight
apostrophes during data-pack transcription. This must never recur.

No normalization of any kind before comparison -- exact Unicode string
equality (Python str == is exact codepoint-by-codepoint comparison; both
files are read as UTF-8 text, so this is a genuine byte-for-byte check for
these Unicode strings, not a visual approximation).
"""

from __future__ import annotations

import json
from pathlib import Path

from memory.ingestion import DEFAULT_DATA_PACK_PATH, load_editorial_memory

# The approved Work Data Pack, exactly as delivered by project leadership for the
# original V1B order -- a pristine, never-edited, repo-local reference copy (see
# memory/data/approved_source/README.md). This is the independent source of truth
# this test checks memory/data/LUF_Editorial_Memory_Data_Pack_V1B.json against --
# not itself modified by ingestion or by this test.
_APPROVED_SOURCE_PATH = Path(__file__).parent.parent / "memory" / "data" / "approved_source" / "LUF_Editorial_Memory_Data_Pack_V1B.json"


def _approved_records() -> dict[str, dict]:
    pack = json.loads(_APPROVED_SOURCE_PATH.read_text(encoding="utf-8"))
    return {r["content_id"]: r for r in pack["records"]}


def test_a_content_other_006_exact_against_source():
    approved = _approved_records()["content-other-006"]["source_facts"]["original_text"]
    records = load_editorial_memory()
    record = next(r for r in records if r.content_id == "content-other-006")
    assert record.source_facts.original_text == approved
    # The specific typographic apostrophe the audit found normalized away.
    assert "‘" in approved and "’" in approved
    assert "‘" in record.source_facts.original_text
    assert "’" in record.source_facts.original_text


def test_b_content_published_003_exact_against_source():
    approved = _approved_records()["content-published-003"]["source_facts"]["original_text"]
    records = load_editorial_memory()
    record = next(r for r in records if r.content_id == "content-published-003")
    assert record.source_facts.original_text == approved
    assert "’" in approved
    assert "’" in record.source_facts.original_text


def test_c_all_21_records_exact_against_source():
    approved = _approved_records()
    records = load_editorial_memory()
    assert len(records) == 21
    assert set(approved) == {r.content_id for r in records}
    for record in records:
        expected = approved[record.content_id]["source_facts"]["original_text"]
        assert record.source_facts.original_text == expected, (
            f"{record.content_id}: original_text does not match the approved source verbatim"
        )


def test_ingested_data_pack_file_is_byte_identical_to_approved_source():
    """A stronger check at the file level: the raw JSON pack this repo ships
    (memory/data/LUF_Editorial_Memory_Data_Pack_V1B.json) must be structurally
    identical to the approved source pack -- not just each record's text."""

    approved = json.loads(_APPROVED_SOURCE_PATH.read_text(encoding="utf-8"))
    ingested = json.loads(DEFAULT_DATA_PACK_PATH.read_text(encoding="utf-8"))
    assert approved == ingested
