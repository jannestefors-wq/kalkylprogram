# LUF System Manifest

Direktorder LUF Core Engine V1, S29: this document must make the system
understandable to a competent developer who has never seen the Claude
session that produced it. Last updated 2026-08-20, baseline commit
`b8f004d`, this delivery's commits on branch `claude/luf-core-engine-v1-p3uws7`.

## 1. System components and where they live

| Component | Repository | Path | Status |
|---|---|---|---|
| Kalkylprogram (Bygg & Entreprenad) | `jannestefors-wq/kalkylprogram` | `/kalkylprogram.py`, `/app.py` | Existing, unrelated to LUF, unchanged by this order |
| LUF Editorial Engine (Canonical Foundation, V1A, V1B, V1C) | `jannestefors-wq/kalkylprogram` | `/editorial-engine/` | Existing, unchanged by this order |
| LUF Core Engine V1 Foundation | `jannestefors-wq/kalkylprogram` | `/luf-core-engine/` | New, this delivery |
| Public LUF website | **UNKNOWN** | **UNKNOWN** | Not accessible to this session -- see OWNERSHIP_AUDIT.md |
| Adam | **UNKNOWN** | **UNKNOWN** | Not accessible to this session |
| House Engine (lighting/projections) | **UNKNOWN** | **UNKNOWN** | Not accessible to this session; contract-only stub at `adapters/house_engine_contract.py` |
| Dilemma Bank V1 | **UNKNOWN** | **UNKNOWN** | Not accessible to this session; contract-only stub at `adapters/dilemma_bank_contract.py` |
| Tänkarstolen, Runda bordet, Akademin | **UNKNOWN** | **UNKNOWN** | Not built; not accessible to this session |
| `jannestefors-wq/byggledning` | `jannestefors-wq/byggledning` (private) | n/a | Discovered, not opened, relevance to LUF unconfirmed (OPEN_QUESTIONS.md OQ-6) |

## 2. Responsibilities

- **Kalkylprogram**: standalone construction-cost calculation tool. No LUF
  methodology content. No dependency on the other components.
- **Editorial Engine**: canonical editorial judgment (Idea → Interpretation
  → Classification → Comparison → Angles → Recommendation → Human
  Decision), plus bounded Editorial Memory (V1B) and a Controlled Variation
  prototype (V1C). Owns its own Human Authority and canonical data (16
  Series, 8 Thesis Families, Territory, Reader Feedback).
- **LUF Core Engine**: the shared methodology motor described by Direktorder
  S1 -- Canonical Tool Registry, triangulation representation,
  observation/interpretation separation, Tool Trace, Human Review workflow,
  provider/entitlement/integration adapters. Does not itself run any
  end-user-facing feature; everything downstream (Tänkarstolen, training,
  speaker/workshop tooling) is meant to be a future adapter on top of it.

## 3. Data layers and canonical sources

| Data | Owner location | Provenance model |
|---|---|---|
| Editorial Engine canonical data (Series, Thesis Family, Territory, Reader Feedback) | `editorial-engine/canonical_data/` (JSON + Python registries, git-tracked) | `editorial-engine/schema/provenance.py` (`Provenance`, `Actor`, `EvidenceCertainty`) |
| Editorial Memory (V1B) | `editorial-engine/memory/data/LUF_Editorial_Memory_Data_Pack_V1B.json` | Same as above |
| LUF Core Engine tool inventory (candidates only) | `luf-core-engine/canonical_data/source/inventory_candidates.json` (git-tracked) | `luf-core-engine/schema/provenance.py` (`Provenance`, `Actor`, `ToolConfidence`) |
| Future: Tool Trace / session data | Not yet generated; schema defined at `luf-core-engine/schema/tool_trace.py`. No storage backend chosen -- must be the project owner's own data layer per S27, not left inside a chat session. |
| Website content, Dilemma Bank, House state | **UNKNOWN** -- not accessible to this session |

## 4. Integration boundaries

- Editorial Engine <-> Core Engine: `luf-core-engine/adapters/
  editorial_engine_contract.py` (interface only, no import either
  direction). See `docs/INTEGRATION_CONTRACT_EDITORIAL_ENGINE.md`.
- Dilemma Bank <-> Core Engine: `luf-core-engine/adapters/
  dilemma_bank_contract.py` (interface only; Dilemma Bank itself not
  located). See `docs/INTEGRATION_CONTRACT_DILEMMA_BANK.md`.
- House Engine <-> Core Engine: `luf-core-engine/adapters/
  house_engine_contract.py` (semantic `HouseEvent` only, no presentation
  fields). See `docs/HOUSE_ENGINE_EVENT_CONTRACT.md`.
- Entitlement <-> Core Engine: `luf-core-engine/adapters/entitlement.py`
  (tier gating fully separate from methodology schema). See
  `docs/ENTITLEMENT_BOUNDARY.md`.

## 5. External services and dependencies

- **AI providers**: none required at runtime by any accessible component.
  `luf-core-engine/adapters/provider.py` defines a vendor-neutral
  `LLMProvider` interface for future use; no concrete vendor is wired in.
  See `docs/CLAUDE_INDEPENDENCE_ASSESSMENT.md`.
- **Provider replacement**: swapping or adding an AI vendor means writing a
  new `LLMProvider` subclass in `adapters/provider.py` (or a new adapter
  module); no other file in `schema/`, `canonical_data/`, or
  `human_review/` should need to change.
- **Package dependencies**: `pydantic>=2.6`, `pytest>=8.0` for both
  `editorial-engine/` and `luf-core-engine/`; `pandas`, `openpyxl`,
  `reportlab` for the calculation tool. No paid/licensed dependency found.
- **Secrets/configuration**: none found anywhere in the accessible
  repository (confirmed by grep and filename search, see
  `OWNERSHIP_AUDIT.md`). `.gitignore` already excludes `.env`.

## 6. Build, test, deployment

- **Editorial Engine**: `cd editorial-engine && pip install -r
  requirements.txt && python3 -m pytest -q` (336 tests at baseline).
- **LUF Core Engine**: `cd luf-core-engine && pip install -r
  requirements.txt && python3 -m pytest -q` (31 tests, this delivery).
- **Kalkylprogram**: `pip install pandas openpyxl reportlab && python
  kalkylprogram.py`; Windows EXE via `bygg_exe.bat`.
- **Deployment**: `render.yaml` exists at repo root (Render.com config for
  the calculation tool's web variant, `app.py`/Streamlit) -- not inspected
  further, out of scope for this order. No deployment config found for
  either engine (neither is currently deployed as a service; both are
  libraries pending a future consuming application).

## 7. Versioning and migrations

- No formal SemVer scheme yet for `luf-core-engine/`; `stable_tool_id`
  values in the tool registry are the durable identifier across future
  schema changes (never reused for a different tool).
- Editorial Engine has its own `schema/versioning.py` / `SCHEMA_VERSION`;
  Core Engine does not yet need one (no shipped consumer to version
  against) -- flagged as a decision to make before a second component
  starts depending on Core Engine's schema shape.
- No database migrations exist because no live database exists yet for
  either engine (data lives in git-tracked JSON + Python registries).

## 8. Known blockers (see also OPEN_QUESTIONS.md)

1. No accessible repository for the public website, Adam, House Engine, or
   Dilemma Bank -- ownership, backup, and integration cannot be verified
   beyond interface stubs until access is granted.
2. `luf-tool-0009`'s "Påhöraren" spelling is unverified (possible source
   typo for "Åhöraren").
3. `ZoomLevel` taxonomy and the seven framework acronyms (RACE/RISE/STAR/
   SOAP/CLEAR/GROW/PASTOR) have no verified LUF-specific source material.
4. `jannestefors-wq/byggledning`'s relevance to LUF is unconfirmed.
