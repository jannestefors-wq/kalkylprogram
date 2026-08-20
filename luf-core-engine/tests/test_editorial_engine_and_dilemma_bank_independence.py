from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
CODE_DIRS = ["schema", "adapters", "human_review", "canonical_data"]
IMPORT_PATTERN = re.compile(r"^\s*(from|import)\s+editorial_engine\b", re.MULTILINE)


def test_no_import_from_editorial_engine():
    """Direktorder S21: Editorial Engine stays separate. Core Engine defines an
    interface (adapters/editorial_engine_contract.py) that documents the
    boundary in prose, but no module here contains an actual Python import
    of editorial-engine code."""
    offenders = []
    for dirname in CODE_DIRS:
        for path in (ROOT / dirname).rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            if IMPORT_PATTERN.search(text):
                offenders.append(str(path))
    assert offenders == []


def test_no_dilemma_bank_data_copied_in():
    """Direktorder S22: Dilemma Bank data must not be moved into this repo.
    Docs and tests may discuss the (missing) Dilemma Bank integration in
    prose -- that's the point of this order's inventory-gap reporting. What
    must never appear is actual Dilemma Bank DATA (e.g. a copied dataset)
    outside the single interface-only contract module."""
    scan_dirs = ["schema", "canonical_data", "human_review", "adapters"]
    allowed_names = {"dilemma_bank_contract.py"}
    offenders = [
        str(p)
        for dirname in scan_dirs
        for p in (ROOT / dirname).rglob("*")
        if p.is_file()
        and "dilemma" in p.name.lower()
        and p.name not in allowed_names
        and "__pycache__" not in p.parts
    ]
    assert offenders == []
