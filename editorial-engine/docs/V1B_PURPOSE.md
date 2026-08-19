# V1B Purpose

V1A proved the engine could think editorially before writing anything --
interpret, classify, propose angles, recommend, and defer to a human --
against a canonical foundation with no real content memory (comparison
always ran against an empty or test-only `existing_content` list).

V1B proves the next thing: **the engine's editorial judgment actually
changes when it is given real memory of what already exists.** The same
raw idea, run twice -- once with an empty Editorial Memory and once with
the real 21-record corpus loaded -- produces a DIFFERENT recommendation.
That is the whole point of V1B (order section 36), and it is directly
tested (`tests/test_v1b_pipeline.py::test_17_memory_influences_candidate_angles`).

## What V1B adds to the chain

```
Raw Idea -> Interpretation -> Canonical Classification ->
Editorial Memory Retrieval -> Existing Content Comparison ->
Candidate Angles -> Recommended Angle -> Human Decision
```

Two new steps: Editorial Memory Retrieval (`memory/retrieval.py`) and a
memory-aware Comparison (`memory/comparison.py`). Everything else in the
chain is V1A's own, unmodified code, reused directly (see
`docs/V1B_DOES_NOT_DO.md` and `memory/pipeline.py`'s module docstring for
exactly how).

## What V1B does NOT prove

It does not prove the engine knows LUF's full publication history (see
`docs/V1B_MEMORY_BOUNDARY.md`) and it does not produce any finished text
(see `docs/V1B_DOES_NOT_DO.md`). It proves the engine can be handed a
small, real, honestly-bounded piece of memory and let that memory actually
change what it recommends -- the mechanism, not the completeness.
