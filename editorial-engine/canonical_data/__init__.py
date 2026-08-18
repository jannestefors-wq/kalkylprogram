"""
Canonical reference data for the LUF Editorial Engine (Canonical Data Integration V1).

TECHNICAL PLACEMENT DECISION (order section 13): Schema V1.1 did not yet define
a physical location for real canonical reference data (as opposed to test
fixtures under `fixtures/`). This package is the minimal placement chosen:
real Series and ThesisFamily registries live here, built from the
project-leadership-approved source pack under `canonical_data/source/`, and
are imported BY `fixtures/fixture_dataset.py` rather than duplicated into it.
This is a data/module placement choice, not new engine architecture.

- `canonical_data/source/` -- the two files delivered by Work, unmodified,
  kept for provenance traceability.
- `canonical_data/series_registry.py` -- `load_series_registry()` returns the
  16 real `Series` objects.
- `canonical_data/thesis_family_registry.py` -- `load_thesis_family_registry()`
  returns the 8 real `ThesisFamily` objects.

See docs/DATA_MAPPING_NOTE.md for the field-by-field mapping from the source
pack's generic JSON shape to Schema V1.1's Pydantic models, and
docs/CLASSIFICATION_DECISION_NOTE.md for how the five project-leadership
classification decisions are represented technically.
"""
