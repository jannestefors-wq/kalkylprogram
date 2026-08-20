from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parent.parent
CODE_DIRS = ["schema", "adapters", "human_review"]
FORBIDDEN_TOKENS = ["anthropic", "openai", "claude"]

# canonical_data/ is deliberately excluded: it legitimately RECORDS, as
# provenance data, which system produced an inventory candidate (e.g.
# provenance.actor_id naming the AI system that did the extraction). That is
# honest audit-trail metadata, not a runtime dependency on a vendor SDK --
# the control-flow code in CODE_DIRS is what must be vendor-neutral.


def test_methodology_code_has_no_vendor_specific_token():
    """
    Direktorder S15/S36.S: Core Engine methodology (schema/, adapters/,
    human_review/, canonical_data/) must not require a specific AI vendor's
    SDK or name to run. adapters/provider.py is the only place an AI vendor
    would ever be wired in, and even there only through the vendor-neutral
    LLMProvider abstraction -- no vendor name appears in code anywhere in
    this tree.
    """
    offenders = []
    for dirname in CODE_DIRS:
        for path in (ROOT / dirname).rglob("*.py"):
            text = path.read_text(encoding="utf-8").lower()
            for token in FORBIDDEN_TOKENS:
                if token in text:
                    offenders.append((str(path), token))
    assert offenders == [], f"vendor-specific token(s) found in methodology code: {offenders}"


def test_no_import_of_a_generative_ai_sdk():
    for dirname in CODE_DIRS:
        for path in (ROOT / dirname).rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            assert "import anthropic" not in text
            assert "import openai" not in text
