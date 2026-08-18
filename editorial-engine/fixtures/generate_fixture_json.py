"""Dump the fixture dataset to fixtures/fixture_dataset.json for human/non-Python inspection.
Run: python3 -m fixtures.generate_fixture_json   (from editorial-engine/)
"""

from __future__ import annotations

import json
from pathlib import Path

from fixtures.fixture_dataset import build_fixture_dataset


def main() -> None:
    dataset = build_fixture_dataset()
    serializable = {
        key: [json.loads(item.model_dump_json()) for item in items] for key, items in dataset.items()
    }
    out_path = Path(__file__).parent / "fixture_dataset.json"
    out_path.write_text(json.dumps(serializable, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
