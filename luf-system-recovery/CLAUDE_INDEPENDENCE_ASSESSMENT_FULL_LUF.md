# Claude Independence Assessment -- Whole LUF, 2026-08-20

Direktorder S23: update the prior (Core-Engine-only) assessment to cover
all of LUF, and separate four independence dimensions per component:

1. **Build independence** -- can a human (no AI) build/modify this from
   the delivered source?
2. **Runtime independence** -- does running it require Claude or any AI
   vendor?
3. **Maintenance independence** -- is there enough documentation for a
   different developer, with no access to this session, to carry it
   forward?
4. **Data independence** -- does the data exist outside any AI vendor's
   storage, in the owner's own structure?

| Component | Build indep. | Runtime indep. | Maintenance indep. | Data indep. |
|---|---|---|---|---|
| Kalkylprogram | ✅ always has been | ✅ no AI | ✅ own README | ✅ user-local files |
| Editorial Engine | ✅ verified this session | ✅ no AI, grep-confirmed | ✅ extensive docs/, written for a developer without Claude access | ✅ git-tracked JSON |
| LUF Core Engine | ✅ verified this session | ✅ no AI, test-enforced (`test_no_vendor_specific_runtime.py`) | ✅ docs/ written to the same standard | ✅ git-tracked JSON |
| Canonical Tool Registry content | ➖ n/a (data, not code) | ➖ n/a | ✅ documented as UNVERIFIED, not hidden | ✅ git-tracked, but sourced only from this order's text |
| Website / Physical House / Adam / House Engine / Academy / Round Table / Dilemma Bank | ❓ UNKNOWN | ❓ UNKNOWN | ❓ UNKNOWN | ❓ UNKNOWN |

## What changed since the prior assessment

The prior assessment (`luf-core-engine/docs/CLAUDE_INDEPENDENCE_ASSESSMENT.md`)
covered only Kalkylprogram, Editorial Engine, and Core Engine, and reached
the same conclusion for each: fully independent at runtime. This pass adds
nothing new for those three -- confirmed again via a second, independent
restore test (bundle-based, not just live-clone-based) with the same
result (336 + 31 tests green).

What's new here is the explicit acknowledgment that **"UNKNOWN" is not
"independent."** The prior report already flagged the website/Adam/House
Engine/Dilemma Bank as `NOT_ASSESSABLE`; this pass makes clear that
`NOT_ASSESSABLE` fails all four independence dimensions by default, not
just the runtime one -- an unreachable system cannot be shown to be
build-independent, maintainable, or data-independent either, however
likely that might be.

## Bottom line

Everything this session could reach is fully Claude-independent across all
four dimensions, verified twice. Everything it could not reach remains a
genuine unknown on all four dimensions -- not a pass, not a fail, an open
question that only access (or an owner-provided export) can close.
