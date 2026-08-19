# V1B Final Audit + PR Readiness

Independent audit of the reported V1B implementation on
`claude/editorial-memory-v1b` (commit `2344e9f`). This is a review, not
continued development -- no retrieval/comparison logic was changed to
"fix" anything found here. Two real defects were found. Both are reported,
neither is patched in this round.

## Scope

Read code, data, tests. Ran the existing suite and new, additive
audit-only checks (ad hoc verification scripts, not new permanent test
files, since no new permanent behavior needed asserting beyond what
already-written V1B tests cover -- the audit's job was to independently
re-derive and stress-test the CLAIMS, not add coverage). No file under
`engine/`, `schema/`, `canonical_data/`, or `fixtures/` was touched. No
retrieval/comparison/angle logic was changed.

## Branch and baseline

- Branch: `claude/editorial-memory-v1b`. HEAD: `2344e9f` (matches the
  reported commit exactly, no drift).
- Base: `origin/main` @ `6ae8032` -- confirmed current, no commits landed
  on `main` since the branch was created.

## Diff review

`git diff --stat origin/main origin/claude/editorial-memory-v1b`: 21 files
changed, all under `editorial-engine/`. Explicitly confirmed:
- `git diff --name-only ... | grep -v '^editorial-engine/'` -> empty.
- `git diff --stat origin/main HEAD -- schema/ canonical_data/ engine/ fixtures/` -> empty.

No house code, no Adam code, no Canonical Foundation change, no V1A code
change. The slutrapport's claim on this point is correct.

## Work Data Pack verbatim verification -- **DEFECT FOUND**

Compared `memory/data/LUF_Editorial_Memory_Data_Pack_V1B.json` field-by-field
against the approved source pack (`LUF_Editorial_Memory_Data_Pack_V1B.json`
attached to the original V1B order) via a structural JSON diff, not a
visual read.

**19 of 21 records are byte-identical.** Two are not:

| content_id | Approved (source) | Ingested (repo) |
|---|---|---|
| `content-other-006` | `Ubuntu is a simple word with a deep human truth: 'I am because we are.'` (curly quotes U+2018/U+2019) | `Ubuntu is a simple word with a deep human truth: 'I am because we are.'` (straight apostrophes) |
| `content-published-003` | `...ISN'T ABOUT...IT'S ABOUT...` (curly apostrophe U+2019) | `...ISN'T ABOUT...IT'S ABOUT...` (straight apostrophe) |

This happened during the transcription of the approved pack into
`memory/data/LUF_Editorial_Memory_Data_Pack_V1B.json` in the prior
implementation round -- exactly the "tyst normalisering" the order
forbids (order section 3, and by extension the whole project's standing
verbatim-text discipline established for Parastoo's review). It does not
change matching BEHAVIOR (`normalize_words()` strips both quote styles
identically, confirmed by re-running the affected records' retrieval/
comparison paths before and after a temporary in-memory correction), but
it is a genuine evidence-fidelity defect: two records' `original_text` is
not what the approved source actually says, character for character.

**Per order section 3, this is a hard STOP condition. It is reported, not
fixed, in this audit.**

## Fulltext boundary -- verified in execution, not just in the model

Traced actual execution, not just field presence: `memory/comparison.py::compare_to_editorial_memory()`
only computes `text_overlap_terms` inside the `if sf.text_completeness ==
TextCompleteness.FULL:` branch -- confirmed by re-running
`tests/test_v1b_comparison.py::test_3_partial_records_never_produce_text_overlap_terms`
and `test_15_fulltext_overlap_only_computed_for_full_records`, and by an
independent ad hoc call feeding a partial record a raw idea sharing a
literal word with that partial record's own text: `text_overlap_terms`
stayed `[]`. Exactly the 12 `content-work-*` records are the fulltext set
(`{content-work-001..012}` == `{r.content_id for r in records if
text_completeness == FULL}`, verified directly). No partial record can
enter fulltext comparison via any code path found.

## Publication uncertainty -- verified in execution

Ran `compare_to_editorial_memory()` against one record of each status
simultaneously (`content-work-001` / `content-published-003` /
`content-other-001`). All three appear in the SAME result with three
DISTINCT `publication_status` values and three distinct
`evidence_boundary_note` texts (`work-001`: "...INTE som bevis for
publicering"; `published-003`: "...verklig publiceringsevidens";
`other-001`: "varken publicerat eller opublicerat far antas"). No boolean
`published` field exists on `MemorySourceFacts` at all -- `unknown` cannot
collapse into `false` because there is no `false` to collapse into.

## Memory Boundary -- verified in execution, adversarial attempt made

Actively tried to force an absolute historical claim: ran the pipeline
with `memory_records=[]` against a normally-matching raw idea. Result:
`MemoryComparisonOutcome.NO_MATCH_IN_AVAILABLE_MEMORY`, `memory_retrieval.matches
== []`. Searched all of `memory/*.py` for `never published|never
written|never used|first time|completely new|unique in our history` --
the only hits are inside `EDITORIAL_MEMORY_BOUNDARY_NOTE` itself, where
the forbidden phrasing is NAMED in order to forbid it ("...never that the
idea was 'never written about'..."), never asserted as fact. The note is
attached as a real field on every result object, not just prose
documentation. This part of the slutrapport's claim holds.

## Retrieval transparency -- verified

Every match in a real run carries non-empty `matched_signals` (e.g.
`thesis_family:thesis-reality-before-story-001`, `topic:verklighet`,
`term:tid`) and a `why_retrieved` string built directly from that list --
confirmed each signal string literally appears inside the explanation
text. No numeric score anywhere. Genuinely explainable, not just claimed
to be.

## Lexical-noise audit -- **CRITICAL DEFECT FOUND (mergekritisk)**

This is the audit's central finding.

Nine varied, deliberately non-Golden-Path raw ideas were run against the
real, full 21-record corpus -- office chat about vacation plans, a
customer complaint, a workshop-planning note, weather and board games, a
broken-down car, and others with no intended thematic relation to the
corpus:

| Input (truncated) | Thesis match includes `thesis-change-over-time-001`? | Repetition risk | Recommendation |
|---|---|---|---|
| "En ledare och en person pratade om semesterplaner..." | YES | HIGH/HIGH/HIGH | NO_STRONG_ANGLE |
| "Chefen och ledaren diskuterade nya rutiner..." | YES | -- | NO_STRONG_ANGLE |
| "Gruppen samlades for att fira ett bra kvartal..." | YES | -- | NO_STRONG_ANGLE |
| "Kunden horde av sig med klagomal om leveransen..." | YES | -- | NO_STRONG_ANGLE |
| "Vi planerar en workshop om kreativitet..." | YES | -- | NO_STRONG_ANGLE |
| Audit Input A (deliberately close to corpus theme) | YES | HIGH/HIGH/HIGH | NO_STRONG_ANGLE |
| Audit Input B2 ("regnade i tre dagar... brädspel med barnen") | YES | HIGH/HIGH/HIGH | NO_STRONG_ANGLE |
| Audit Input C ("bilen gick sonder pa vagen dit" -- pure noise) | YES | HIGH/HIGH/HIGH | NO_STRONG_ANGLE |

**Every single one** of these thematically unrelated inputs produced the
identical outcome: HIGH repetition on all candidates and
`NO_STRONG_ANGLE`. Root cause, traced to source:

`engine/provider.py::RuleBasedAnalysisProvider.interpret()` ends with an
UNCONDITIONAL inference line (no `if` guard):

```python
text=f"Mojlig konsekvens (hypotes): {affected_party} kan over tid lagga fram farre ideer eller synpunkter. Inte verifierat."
```

This means the literal word **"konsekvens" appears in every single
successful interpretation, for every input that passes `is_sufficient()`,
with no exception found.** `engine/classification.py::classify()` matches
a Thesis Family on just ONE overlapping term, so this unconditionally
matches `thesis-change-over-time-001` every time. Two full-text Editorial
Memory records (`content-work-007`, `content-work-008`) both carry
`thesis_family_id == thesis-change-over-time-001`. `engine/angles.py`
applies the SAME `canonical_relation_ids` (all of classification's
matches) to every one of the 3 candidate angles, not per-angle. The net
effect: once real Editorial Memory is loaded, a "strong" repetition match
against `content-work-007`/`content-work-008` is a structural certainty
for any sufficiently-worded input, **independent of genuine thematic
relevance.**

Separately, `QUANTITY_WORDS` in `engine/provider.py` includes bare `"en"`
and `"ett"` -- the ordinary Swedish indefinite articles ("a"/"an"),
among the most common words in the language -- which alone satisfies
`is_sufficient()`'s "concrete marker" branch and triggers the
"verklighet"/"makt" interpretation clauses too, compounding the effect
with `thesis-reality-before-story-001` (matched by `content-work-001/005/006/012`).

**This is precisely the failure mode order section 8 asks to test for and
instructs a STOP for if confirmed: a single common/structural artifact
materially and near-universally drives repetition risk and
`NO_STRONG_ANGLE`, not genuine relevance.** Root cause sits in V1A's
`engine/provider.py` (a file this audit is expressly forbidden from
changing, and which V1B was told not to rewrite either) -- it was an
accepted V1A limitation when comparison ran against an empty/synthetic
corpus, but wiring it to real memory in V1B exposes it as a **decision-
grade failure**, not a cosmetic one, because it now drives an actual
recommendation outcome shown to a human as if evidence-based.

## Empty-memory vs. loaded-memory audit

The reported behavioral difference (LOW/RECOMMENDED empty vs. HIGH/HIGH/HIGH/
NO_STRONG_ANGLE loaded) is real and reproducible -- confirmed
independently, not taken on faith. However, per the Lexical-Noise Audit
above, the loaded-memory side of that difference is **not** reliably
caused by case-specific relevant evidence -- it is caused by the same
structural artifact for virtually any sufficient input. The mechanism
order section 9 asks to rule out ("ett enda generiskt ord") is exactly
what was found. The empty-vs-loaded proof, as currently implemented, does
not yet demonstrate genuine evidence-driven judgment -- it demonstrates
that loading memory always makes the outcome worse, regardless of content.

## Three new audit inputs (order section 10)

- **Audit Input A (relevant memory)**: "Vi matte resultatet varje manad
  men forstod aldrig vad som egentligen paverkade det innan det redan
  hade hant." -- deliberately close to `content-work-007`/`008`'s
  measure/consequence theme. Result: MATCHES_FOUND, HIGH/HIGH/HIGH,
  NO_STRONG_ANGLE. Directionally correct, BUT indistinguishable from
  Input C below.
- **Audit Input B (unrelated)**: "Det regnade i tre dagar sa vi stannade
  hemma och spelade bradspel med barnen istallet for att aka ut." --
  weather and board games, no organizational/leadership theme at all.
  Result: MATCHES_FOUND, HIGH/HIGH/HIGH, NO_STRONG_ANGLE. **Should have
  looked materially different from Input A. It did not.**
- **Audit Input C (lexical noise)**: "En person sa att en annan skulle
  komma imorgon men det blev inte av eftersom bilen gick sonder pa vagen
  dit." -- a car breaking down, chosen specifically for zero thematic
  overlap. Result: MATCHES_FOUND, HIGH/HIGH/HIGH, NO_STRONG_ANGLE.
  **Identical to both A and B.**

All three produced the same outcome. This is the direct, concrete
confirmation of the Lexical-Noise Audit finding above using the order's
own required test design.

## Repetition risk audit

LOW verified (empty corpus). MEDIUM verified in isolation (a single
weak-topic-only memory record, `content-work-002`, in isolation).
HIGH verified -- but per above, HIGH is not gated on genuinely relevant
evidence in current practice; it fires on `thesis-change-over-time-001`
essentially unconditionally once the full corpus is loaded. Rationale
text is generated from the actual signals used (no post-hoc mismatch
found), but the signals themselves are too weakly discriminating.

## Candidate Angle influence audit

No hardcoded `content-work-*`/`content-other-*`/`content-published-*` id,
and no Golden Path phrase, found anywhere in `memory/*.py` production
code (only inside a docstring comment, non-executable). The mechanism is
genuinely generic -- the problem is that "generic" here means "generic
enough to also fire on irrelevant input," not that it secretly special-
cases the demo scenario.

## Version/revision audit

`content-other-005` is one record with one `MemoryRelation(type="version_revision",
...)`, confirmed loaded as a single record (not duplicated into two).
Handled responsibly as reported.

## Reader Feedback separation

Confirmed: no file under `memory/` references "parastoo" (case-insensitive
grep across `memory/*.py`, zero hits). Parastoo's `ReaderFeedback` record
is untouched in `canonical_data/reader_feedback_registry.py` (zero diff
vs. `origin/main`) and is not among Editorial Memory's 21 `content_id`s.

## Voice Core separation

Confirmed: zero occurrences of "voice" (case-insensitive) anywhere in
`memory/*.py`. No `VoiceCoreSnapshot`, `VoicePrinciple`, or
`schema.voice` import exists under `memory/`.

## Canonical Foundation integrity

`git diff --stat origin/main HEAD -- schema/ canonical_data/ engine/
fixtures/` is empty. Zero semantic or structural change.

## V1A integrity

Test files separated and counted independently:
- Canonical Foundation + V1A tests (everything except `tests/test_v1b_*.py`):
  **127 collected, 127 passed.**
- V1A-only subset (`test_v1a_*.py` files): **51 collected** (subset of the
  127 above, confirming the reported 76 + 51 = 127 split).
- V1B tests (`tests/test_v1b_*.py`): **32 collected, 32 passed.**
- Combined: **159 collected, 159 passed**, clean run, 0.51s, zero external
  network/AI dependency.

## Forbidden functionality scan

Grepped `memory/*.py` for web frameworks, HTTP clients, AI vendor
SDKs/API keys, vector/embeddings libraries, and generator-shaped function
names (`def generate_`, `def publish_`, `final_text =`, `caption =`,
`cta_text`, `hook_text`, LinkedIn-post generation). **Zero matches.**
`requirements.txt` unchanged (`pydantic`, `pytest` only).

## JSON Schema

Regenerated twice; md5-identical across both runs. `git status --porcelain
schema/` clean after regeneration -- **zero canonical schema change.**

## Known limitations (non-blocking, already documented)

- Simple word-overlap retrieval/comparison is an accepted, DOCUMENTED V1A
  design choice (not new to V1B).
- Data gaps already flagged in `docs/V1B_CORPUS.md` (LinkedIn export,
  dates, URLs, English corpus, taxonomies) remain open by design.

## PR readiness decision

The real question per order section 22 is not "are the tests green" --
159/159 are, and that is not in dispute. The question is whether V1B is
**truthful, general, and transparent enough** to become the next stable
baseline. On the five weighted criteria:

1. **Memory Boundary** -- PASS. Technically enforced, verified adversarially.
2. **Lexikalt brus** -- **FAIL.** Confirmed materially and repeatedly:
   ordinary, thematically unrelated Swedish sentences produce the same
   HIGH-repetition / NO_STRONG_ANGLE outcome as genuinely close material.
3. **Publication uncertainty** -- PASS.
4. **Empty-memory vs. loaded-memory** -- **FAIL as currently evidenced.**
   The difference is real, but not yet shown to be driven by relevant,
   case-specific evidence rather than a structural artifact.
5. **Generalization beyond the Golden Path** -- **FAIL.** Nine
   independent, non-Golden-Path inputs, including the three inputs this
   very audit was ordered to construct, could not be distinguished from
   each other by the system's own output.
6. **Memory genuinely changing judgment for the right reasons** -- **FAIL.**
   It changes judgment, but largely for the wrong (structural, not
   evidential) reason.

Two real defects were found: a verbatim-text integrity gap on 2 of 21
records, and a decision-grade genericity defect rooted in V1A's rule-based
provider that this audit is not authorized to fix. Neither is hidden;
neither is patched here.

## SLUTSTATUS

**STOPP. V1B ÄR INTE REDO FÖR PR**
