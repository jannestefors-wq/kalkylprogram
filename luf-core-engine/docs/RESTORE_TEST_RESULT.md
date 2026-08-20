# Restore Test Result

Performed 2026-08-20, this session, in an isolated scratch directory
outside the working repository. No production system, branch, or file in
`/home/user/kalkylprogram` was touched by this test.

## Procedure

```
git clone /home/user/kalkylprogram <scratch>/kalkylprogram-clone
cd <scratch>/kalkylprogram-clone && git rev-parse HEAD
cd editorial-engine  && pip install -r requirements.txt && python3 -m pytest -q
cd ../luf-core-engine && pip install -r requirements.txt && python3 -m pytest -q
cd .. && python3 -m py_compile kalkylprogram.py app.py
```

## Result

| Step | Result |
|---|---|
| Clone commit | `b7f384298fd87246f2a728b1b5b839bed50d6e4d` |
| Clone working tree status | clean |
| `editorial-engine` tests | **336 passed** |
| `luf-core-engine` tests | **31 passed** |
| `kalkylprogram.py` / `app.py` | compile cleanly |

## Conclusion

`RESTORE VERIFIED SAFE`: source, canonical data, and tests for both
engines, plus the calculation tool, reconstruct fully from the git
repository alone -- no dependency on this Claude session, no dependency on
any data outside the repository. Scratch clone was deleted after the test;
nothing from it was merged back.

This test does not and cannot cover the public website, Adam, House
Engine, or Dilemma Bank -- see `OWNERSHIP_AUDIT.md`.
