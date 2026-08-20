# Single Points of Failure -- 2026-08-20

Direktorder S19. Only covers what this session could inspect; everything
inaccessible (website, Adam, House Engine, Dilemma Bank) is a SPOF by
definition of being unverifiable, listed separately at the bottom rather
than ranked, since severity can't be judged for something unseen.

## CRITICAL

1. **The entire public-facing LUF system (website, Physical House, Adam,
   Academy, Round Table, Dilemma Bank) exists in no repository or hosting
   account reachable by this Claude Code GitHub connector.** If this
   reflects the real, current state of access (not just this session's
   configuration), then whoever *can* reach these systems today is a
   single point of failure for all of them at once. **Action**: confirm
   with the project owner whether access can be granted, or whether these
   systems are intentionally hosted/owned elsewhere.

## HIGH

2. **`jannestefors-wq/kalkylprogram` is a single GitHub account/repo** with
   no verified secondary copy until this session's bundle delivery. A full
   bundle (SHA-256 `3f5fca53...`) was generated and handed directly to the
   project owner this session -- this closes the gap **only once the owner
   stores it somewhere other than the machine it landed on**. Until
   confirmed stored externally, this remains HIGH, not resolved.
3. **Editorial Engine's 336 tests and Core Engine's 31 tests are the only
   evidence that either engine's logic is correct.** No CI pipeline was
   found wired to GitHub Actions or any other automated runner -- tests
   only run when a human or an AI session runs them manually. A silent
   regression could ship undetected between sessions.
4. **The Tool Registry's 30 candidates depend entirely on this order's own
   text as their only source.** If this conversation's content were lost
   before being committed, the record of what was extracted and from where
   would be gone too. (Mitigated: it IS committed, in
   `luf-core-engine/canonical_data/source/inventory_candidates.json`.)

## MEDIUM

5. **No CI/build automation** reproduces `pip install && pytest` on every
   push -- reproducibility currently depends on a human or AI session
   remembering to run it (as this session did, twice, manually).
6. **`byggledning`'s relevance was checked but its data was not backed up
   by this order** (correctly out of scope) -- flagged only so it isn't
   mistaken for "handled."

## LOW

7. **`render.yaml` exists at repo root** (for the calculation tool's
   Streamlit deployment) but was not inspected for correctness or
   currency -- out of this order's scope, noted for completeness.

## Not ranked -- severity unknowable

- Website, Physical House, Adam, House Engine, Academy, Round Table,
  Dilemma Bank, "Historical Idea Bank" (4,589 units), "Verified Editorial
  History": all `NOT_ACCESSIBLE` or `UNKNOWN`. A system that cannot be
  seen cannot be triaged -- these are reported as blockers in
  `LUF_SYSTEM_MAP.md`, not scored here, so as not to imply a false
  precision about risks that are actually just unknowns.
