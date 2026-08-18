"""
Derived-artifact generator (Beslut 27).

Truth layer decision: the Pydantic models under `editorial-engine/schema/`
ARE the canonical schema. This script does not define anything new -- it
exports each top-level model's `model_json_schema()` to
`editorial-engine/schema/json/<Model>.schema.json` purely so a non-Python
component (or a human reviewer) can read the contract without a Python
runtime.

Run: python3 -m schema.export_json_schema   (from editorial-engine/)

Do not hand-edit the generated .json files -- they are overwritten on every
run and any manual change would silently drift from the Pydantic models,
which is exactly the two-representations problem flagged in Beslut 27.
"""

from __future__ import annotations

import json
from pathlib import Path

from . import (
    Angle,
    ContentRecord,
    HumanDecision,
    Idea,
    QualityAssessment,
    RawInput,
    ReaderEffect,
    ReaderFeedback,
    Series,
    Source,
    Territory,
    ThesisFamily,
    VariationFingerprint,
    VoiceCoreSnapshot,
    VoicePrinciple,
)
from .voice import RepetitionSignal, StyleAttribute

CANONICAL_TOP_LEVEL_MODELS = {
    "RawInput": RawInput,
    "Idea": Idea,
    "Source": Source,
    "Series": Series,
    "Territory": Territory,
    "ThesisFamily": ThesisFamily,
    "VoicePrinciple": VoicePrinciple,
    "VoiceCoreSnapshot": VoiceCoreSnapshot,
    "StyleAttribute": StyleAttribute,
    "RepetitionSignal": RepetitionSignal,
    "Angle": Angle,
    "ReaderEffect": ReaderEffect,
    "ReaderFeedback": ReaderFeedback,
    "ContentRecord": ContentRecord,
    "VariationFingerprint": VariationFingerprint,
    "QualityAssessment": QualityAssessment,
    "HumanDecision": HumanDecision,
}


def main() -> None:
    out_dir = Path(__file__).parent / "json"
    out_dir.mkdir(exist_ok=True)
    for name, model in CANONICAL_TOP_LEVEL_MODELS.items():
        schema = model.model_json_schema()
        (out_dir / f"{name}.schema.json").write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {len(CANONICAL_TOP_LEVEL_MODELS)} derived JSON Schema files to {out_dir}")


if __name__ == "__main__":
    main()
