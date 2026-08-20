# LUF Ownership Matrix -- 2026-08-20

Direktorder "LUF System Recovery & Ownership Consolidation", S18. Legend:
✅ = yes/verified, ❌ = no, ➖ = not applicable, ❓ = unknown (not
accessible, not "no").

| Komponent | Source ägd | Data ägd | Assets ägda | Build dokumenterad | Backup | Restore testad | Externt beroende | Status |
|---|---|---|---|---|---|---|---|---|
| Website | ❓ | ❓ | ❓ | ❓ | ❓ | ❌ | ❓ | NOT_ACCESSIBLE |
| Physical House | ❓ | ❓ | ❓ | ❓ | ❓ | ❌ | ❓ | NOT_ACCESSIBLE |
| Adam | ❓ | ❓ | ❓ | ❓ | ❓ | ❌ | ❓ | NOT_ACCESSIBLE |
| Editorial Engine | ✅ | ✅ | ✅ (source files) | ✅ | ✅ | ✅ (twice, live + bundle) | ❌ none | VERIFIED |
| Historical Idea Bank | ❓ | ❓ | ➖ | ❓ | ❓ | ❌ | ❓ | UNKNOWN (discrepancy -- see LUF_SYSTEM_MAP.md) |
| Verified Editorial History | ❓ | ❓ | ➖ | ❓ | ❓ | ❌ | ❓ | UNKNOWN (discrepancy) |
| Dilemma Bank | ❓ | ❓ | ➖ | ❓ | ❓ | ❌ | ❓ | NOT_ACCESSIBLE (cited commit not found) |
| LUF Core Engine | ✅ | ✅ | ➖ | ✅ | ✅ | ✅ (twice) | ❌ none | VERIFIED |
| Canonical Tool Registry | ✅ (structure) | ⚠️ content UNVERIFIED, 0/30 promoted | ➖ | ✅ | ✅ | ✅ | ❌ none | PARTIAL |
| Tool Trace storage (future) | ✅ (schema) | ➖ no data yet | ➖ | ✅ | ➖ | ➖ | ❌ none | NOT_YET_IMPLEMENTED |
| Academy | ❓ | ❓ | ❓ | ❓ | ❓ | ❌ | ❓ | NOT_ACCESSIBLE |
| Round Table | ❓ | ❓ | ❓ | ❓ | ❓ | ❌ | ❓ | NOT_ACCESSIBLE |
| House Engine | ❓ | ❓ | ❓ | ❓ | ❓ | ❌ | ❓ | DISTRIBUTED_FUNCTIONALITY (per S7 -- may not be a separate component at all) |

## Reading this matrix

- Every ❓ in this matrix is identical in meaning: **this session has no
  access to the system in question**, not "the system doesn't own this."
  Ownership cannot be verified OR disproven from here.
- The only row with a clean, fully-backed ✅ set is Editorial Engine and
  LUF Core Engine -- both directly inspected, tested, and restore-verified
  this session, with a bundle now in the project owner's own hands (see
  `BACKUP_BUNDLE_RECORD.md`).
- Canonical Tool Registry is marked ⚠️ deliberately: the STRUCTURE (schema,
  storage, review workflow) is fully owned and tested, but the CONTENT
  (30 tool candidates) has confidence=UNVERIFIED across the board --
  ownership of the container is not the same as ownership of verified
  methodology.
