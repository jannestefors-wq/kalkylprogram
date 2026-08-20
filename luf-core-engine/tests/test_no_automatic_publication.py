from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parent.parent
CODE_DIRS = ["schema", "adapters", "human_review", "canonical_data"]
NETWORK_TOKENS = ["requests.", "urllib.request", "httpx.", "socket.", "http.client"]


def test_no_outbound_network_calls_in_methodology_code():
    """Nothing in this foundation publishes, posts, or syncs data anywhere on its
    own -- no accidental auto-publication path exists to test against."""
    offenders = []
    for dirname in CODE_DIRS:
        for path in (ROOT / dirname).rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for token in NETWORK_TOKENS:
                if token in text:
                    offenders.append((str(path), token))
    assert offenders == []
