# Claude Independence Assessment -- 2026-08-20

Direktorder LUF Core Engine V1, S35: *"Om Claude-abonnemanget avslutas idag,
vilka delar av LUF fortsätter fungera?"*

## Method

For each accessible component: (1) grep for any import of an AI vendor SDK
or any network call, (2) confirm it runs and its tests pass using only
open-source dependencies (`pip install -r requirements.txt`), (3) state
explicitly whether continued *development* (not just runtime) depends on a
human being able to read the code without a Claude session.

## `editorial-engine/`

- **Runtime dependency on Claude/any AI vendor: NONE.** Grep for
  `anthropic|claude|openai|api[_-]?key` across all `.py` files in the repo
  (root scope) returns zero matches. No network calls in the engine code.
- Runs and its 336 tests pass with `pip install -r requirements.txt` alone
  (verified this session, baseline commit `b8f004d`).
- **Verdict: fully functions if the Claude subscription ends today.**
  Future *development* is a human-readability question, not a runtime one
  -- addressed by its own extensive `docs/` (ARCHITECTURE_NOTE.md,
  ENTITY_MAP.md, etc.), written specifically so "en annan kompetent
  utvecklare utan tillgång till Claude-sessionen" can pick it up (its own
  README states this goal).

## `luf-core-engine/` (this delivery)

- **Runtime dependency on Claude/any AI vendor: NONE.** Same grep, zero
  matches in this delivery's code (enforced going forward by
  `tests/test_no_vendor_specific_runtime.py`, which fails the build if a
  vendor-specific token appears in `schema/`, `adapters/`, or
  `human_review/`).
- `adapters/provider.py` defines `LLMProvider` as an abstract interface with
  no vendor bound to it. No generative AI is called anywhere in this
  Foundation.
- 31 tests pass with `pip install -r requirements.txt` alone.
- **Verdict: fully functions if the Claude subscription ends today.**
  Continued development is supported by `docs/LUF_SYSTEM_MANIFEST.md` and
  the per-module docstrings, written to the same standard as
  editorial-engine's.

## `kalkylprogram.py` / `app.py` (the calculation tool)

- No AI dependency at all; a standalone desktop/Streamlit tool. Confirmed
  by the same grep. Fully independent of Claude, always has been.

## The public LUF website, Adam, House Engine, Dilemma Bank, Tänkarstolen,
## Runda bordet, Akademin

- **Cannot be assessed.** None of these are present in any repository
  accessible to this session (see `OWNERSHIP_AUDIT.md`). It is therefore
  impossible from here to state whether their runtime, content, or
  operation depends on Claude, another AI vendor, or any specific person.
  This is a genuine unknown, not a "no" -- reported as `NOT_ASSESSABLE`
  rather than assumed safe.

## Summary table

| Component | Runtime needs Claude? | Verified this session |
|---|---|---|
| `kalkylprogram.py` / `app.py` | No | Yes (grep + inspection) |
| `editorial-engine/` | No | Yes (grep + 336/336 tests green) |
| `luf-core-engine/` | No | Yes (grep + 31/31 tests green, enforced by test) |
| Public website | NOT_ASSESSABLE | No -- not accessible |
| Adam | NOT_ASSESSABLE | No -- not accessible |
| House Engine | NOT_ASSESSABLE | No -- not accessible |
| Dilemma Bank | NOT_ASSESSABLE | No -- not accessible |
| Tänkarstolen / Runda bordet / Akademin | NOT_ASSESSABLE | No -- not accessible |

**Bottom line:** everything this session actually built or could inspect
survives Claude's disappearance with zero runtime impact. Whether the same
is true of the rest of the LUF ecosystem is the single open question this
assessment cannot close -- see `OWNERSHIP_AUDIT.md`'s recommendation.
