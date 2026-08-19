# V1B Correction Report

Targeted correction of the two blockers V1B Final Audit found
(`docs/V1B_AUDIT_REPORT.md`, SLUTSTATUS: STOPP). This report documents
what was wrong, why, and exactly what changed. `V1B_AUDIT_REPORT.md`
itself is left untouched -- it remains the historical record of why this
correction was needed.

## DEFECT 1: Verbatim-text normalization

**What**: Two Editorial Memory records (`content-other-006`,
`content-published-003`) had their typographic (curly) apostrophes
(`'`/`'`) silently replaced with straight apostrophes (`'`) during the
original data-pack transcription into
`memory/data/LUF_Editorial_Memory_Data_Pack_V1B.json`.

**Root cause**: Manual transcription of the approved source pack did not
preserve the exact Unicode characters -- a straightforward typing/encoding
slip, not a deliberate normalization step anywhere in code (ingestion
itself, `memory/ingestion.py`, does no text transformation at all).

**Fix**: `memory/data/LUF_Editorial_Memory_Data_Pack_V1B.json` was
rewritten programmatically, copying `source_facts.original_text` for
those two records directly from the approved source pack (byte-for-byte,
via `json.load`/re-serialize, never hand-typed) -- verified with
`approved_pack == ingested_pack` (full structural equality) after the
fix, not just the two affected fields.

**Guard against recurrence**: `memory/data/approved_source/LUF_Editorial_Memory_Data_Pack_V1B.json`
is now a permanent, never-edited, repo-local copy of the approved source
(see its own `README.md`). `tests/test_v1b_verbatim.py` checks every one
of the 21 ingested records' `original_text` against it with exact Unicode
string equality (TEST A/B/C from the correction order, plus a full
file-level structural-equality check) -- this class of defect will now
fail a test instead of passing silently.

## DEFECT 2: Generic lexical evidence polluted repetition risk

**What**: V1B Final Audit found that nine independently constructed,
thematically unrelated raw ideas -- including all three of the audit's
own required test inputs -- produced the identical HIGH/HIGH/HIGH
repetition risk and `NO_STRONG_ANGLE` outcome as genuinely relevant
material.

**Root cause, exact**: Two compounding issues, both traced to
`engine/provider.py::RuleBasedAnalysisProvider`:

1. `QUANTITY_WORDS` included bare `"en"`/`"ett"` (Swedish "a"/"an" -- the
   indefinite articles, among the most common words in the language).
   These mean SINGULAR, the opposite of the repeated-occurrence signal
   the set exists to detect, but their presence made
   `is_sufficient()`/`detected_repetition` fire on almost any Swedish
   sentence regardless of whether anything was actually described as
   repeated.
2. `interpret()`'s final inference line -- the one that produces the word
   "konsekvens" -- was unconditional (no `if` guard), unlike every
   sibling clause. This meant "konsekvens" appeared in essentially EVERY
   successful interpretation. `engine/classification.py::classify()`
   matches a Thesis Family on a single overlapping term, so this
   unconditionally matched `thesis-change-over-time-001` -- a Thesis
   Family two real, full-text Editorial Memory records
   (`content-work-007`, `content-work-008`) both carry. Combined with
   `engine/angles.py` applying the SAME canonical relations to all 3
   candidate angles (not per-angle), a "strong" repetition match against
   those two records became a structural certainty for any sufficiently-
   worded input, independent of genuine thematic relevance.

A second, related issue was found and fixed WHILE verifying the first fix
(not itself part of the audit's original finding, but the same class of
problem): a lone incidental shared word between a raw input and a memory
record's fulltext (e.g. both happening to use the Swedish number "tre")
could also read as content-level evidence on its own.

**Fix, in three parts**:

1. **`engine/provider.py`** (the one V1A file this correction touched,
   narrowly, per the order's explicit authorization): `QUANTITY_WORDS` no
   longer contains `"en"`/`"ett"`. The "konsekvens" inference line is now
   gated on `detected_repetition or detected_interruption` -- the same
   condition its sibling clause already used -- so it only appears when
   the input actually describes something repeated or interrupted.
   V1A's 127 tests (76 canonical + 51 V1A) pass unmodified; every one of
   them exercises `GOLDEN` ("... tre gånger ...", a real repetition
   marker), so none depended on the removed words.

2. **`memory/comparison.py` / `memory/retrieval.py`**: content-level
   signals (topic-label overlap, literal fulltext-term overlap) are now
   computed against the RAW INPUT TEXT, never against the provider's
   generated interpretation text. The interpretation text is templated
   boilerplate that repeats the same handful of words on most sufficient
   inputs regardless of theme; using it as "content evidence" let that
   boilerplate masquerade as input-specific relevance. Canonical
   classification itself (`classification.thesis_family_matches`/
   `territory_matches`) still runs on the interpretation text, unchanged
   -- only the CONTENT half of the evidence moved to raw input.
   A `repetition_signal_strength` of `"strong"` now REQUIRES both a
   canonical signal AND a content signal; a lone canonical match, or a
   single incidental shared word (below
   `MIN_FULLTEXT_OVERLAP_TERMS_FOR_CONTENT_SIGNAL = 2`), is `"weak"` or
   `"none"`.

3. **`memory/bridge.py`**: `to_legacy_comparison_result()` now only
   passes a match's canonical relation IDs through to V1A's (unmodified)
   `_repetition_risk_for()` when the match is `"strong"`. A `"weak"`
   match with genuine content-level evidence (topic label or 2+ literal
   terms) but no canonical relation is still surfaced via `shared_terms`
   (MEDIUM-eligible). A `"weak"`/`"none"` match with only a canonical
   relation and no content corroboration, or only a single incidental
   word, is dropped from V1A's scoring entirely -- still fully visible in
   the richer `MemoryComparisonResult` for transparency.

**No special-casing anywhere**: no content-id, no Golden Path phrase, no
manual exception for "regn"/"brädspel"/"bilproblem"/"konsekvens" exists in
`memory/*.py` or `engine/provider.py`. The fix is a general threshold and
a general change of which text content-level signals are computed
against -- verified by re-running nine independent, non-hardcoded test
scenarios (three from the audit, six new per this order's section 13),
none of which appear as a literal string anywhere in production code.

**LIMITATION (documented, not solved)**: retrieval/comparison remain
exact word-overlap matching -- no stemming, no semantic understanding, no
disambiguation of word sense. A raw input using a word in one sense (e.g.
"konsekvens" meaning an administrative rule's consequence) can still
coincidentally match a memory record's topic label spelled the same way
but meaning something else (e.g. "konsekvens" as a leadership-accountability
theme). This is an occasional, explainable homonym collision -- the match
still names exactly which word fired -- not the systemic, unconditional
defect the audit found (which affected every sufficient input). Do not
describe this retrieval as "semantic understanding": it is not. See
`tests/test_v1b_correction_regression.py::test_generalization_shared_word_different_meaning_is_a_known_limitation`.

## Verification performed

- V1A regression: 76 canonical + 51 V1A = 127/127 green, run in isolation
  before touching any V1B file, and again after.
- V1B: 33/33 green (32 original + `test_14b`, added to make the
  "lone canonical relation is insufficient" behavior explicit).
- New permanent regression tests: 14 (4 verbatim + 10 correction/
  generalization, `tests/test_v1b_verbatim.py` and
  `tests/test_v1b_correction_regression.py`).
- Full suite: **174/174 green**.
- JSON Schema: regenerated twice, byte-identical; `schema/`/`canonical_data/`
  show zero diff -- no canonical change.
- Independent adversarial re-check (order section 22): genuinely relevant
  input reached `strong`/HIGH; a fully unrelated input and a lexical-noise
  input both stayed `LOW`/`RECOMMENDED` with zero `strong` matches; empty
  vs. loaded memory differed for the relevant input and did not differ
  for the unrelated/noise inputs.
