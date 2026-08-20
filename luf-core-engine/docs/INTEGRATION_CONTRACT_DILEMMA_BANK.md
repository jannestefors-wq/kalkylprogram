# Integration Contract: LUF Core Engine <-> Dilemma Bank

Direktorder S22. **Status: blocked on inventory, not on design.**

No Dilemma Bank source, schema, or data was found in any repository
accessible to this session -- only `jannestefors-wq/kalkylprogram` was in
scope, and a repo-wide filename/content search for "dilemma" found a single
unrelated hit (`editorial-engine/variation/models.py:114`, an enum value
`DILEMMA_TO_OPEN_END` inside Editorial Engine's structural-arc
classification, nothing to do with a dilemma content bank).

## What this document CAN commit to

`adapters/dilemma_bank_contract.py` declares `DilemmaBankBoundary`, a
`Protocol` with one illustrative method,
`get_dilemma_summary(dilemma_id) -> dict[str, str]` -- the shape Core Engine
would call against a real Dilemma Bank once one is locatable. Deliberately
minimal: until the real schema is inspected, a wider contract would be
guessing at Dilemma Bank's actual field names, which Direktorder S5
forbids.

## What this document explicitly does NOT do

- Move, copy, or recreate any Dilemma Bank content into `luf-core-engine/`
  (would break Dilemma Bank's own provenance -- S22's explicit warning).
- Assume Dilemma Bank's schema, ID format, or storage technology.
- Assume Dilemma Bank V1 is even a code artifact rather than, e.g., a
  spreadsheet or CMS collection.

## Action needed before further work

Project management should point a future session at the actual Dilemma
Bank V1 repository or data store. Once inspected, this contract should be
revised to match Dilemma Bank's real identifiers and fields, and this
placeholder note removed.
