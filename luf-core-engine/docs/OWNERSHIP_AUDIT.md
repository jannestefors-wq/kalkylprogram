# LUF Ownership Audit -- 2026-08-20

Response to Direktorder LUF Core Engine V1, S2 ("Ägarprincipen gäller även
befintlig hemsida") and S27 (dataägande). Scope: what this Claude Code
session can actually see and verify, as of baseline commit `b8f004d`.

**No changes were made to the public website, Adam, or any hosted system.
This is an inventory only.**

## What is accessible to this session

GitHub access was scoped to `jannestefors-wq/kalkylprogram` only. A
repository listing call additionally surfaced one more repository on the
same account:

| Repository | Visibility | Accessed this session | Apparent relevance to LUF |
|---|---|---|---|
| `jannestefors-wq/kalkylprogram` | public | Yes -- full read/write | Contains `editorial-engine/` (real LUF work) + `kalkylprogram.py`/`app.py` (unrelated construction-cost calculator) |
| `jannestefors-wq/byggledning` | private | No -- not opened | Name suggests construction project management; relevance to LUF unconfirmed (see OPEN_QUESTIONS.md OQ-6) |

No other repository, hosting account, database, CMS, DNS registrar, domain
registrar, or cloud project was discoverable from within this session.

## Inventory of `jannestefors-wq/kalkylprogram`

```
kalkylprogram.py, app.py, ...   Bygg & Entreprenad calculation tool (tkinter/Streamlit).
                                 Unrelated to LUF except shared authorship credit
                                 ("Utvecklat av Jan Stefors -- Ledarskap utan filter").
editorial-engine/               LUF Editorial Engine: Canonical Foundation V1, V1A, V1B,
                                 V1C. Pure Python (Pydantic 2), 336 tests, all passing at
                                 baseline. Self-contained: no network calls, no AI vendor
                                 SDK imports, no external database.
luf-core-engine/                This delivery.
```

## What could NOT be verified (S2's actual request)

The Direktorder asks this audit to confirm control over: full source, all
assets, "alla rum" (all rooms), Adam, content, configuration, build process,
deployment, external dependencies, domain-related technical dependencies,
data layer, any external runtime, backup, restore -- **for the existing
public website.**

None of the following were found in any repository accessible to this
session:

- The public LUF website's source code (framework, templates, styling).
- Any image/media/asset store for the website.
- "Adam" (any code, config, or content referencing this by that name).
- House Engine, lighting/projection control, or "rum" (room) state.
- Tänkarstolen, Runda bordet, Akademin as deployed products.
- Dilemma Bank V1 (only the string "dilemma" appears once, unrelatedly, as
  an enum value inside editorial-engine's structural-arc classification --
  see `editorial-engine/variation/models.py:114`).
- Any deployment config, hosting account reference, domain registrar
  reference, or CDN/CMS reference for a public LUF website.
- Any secrets, API keys, or `.env`-style files anywhere in the accessible
  repository (confirmed by both a filename search and a content grep for
  `anthropic|claude|openai|api[_-]?key` -- zero matches; `.gitignore`
  already excludes `.env`).

**Conclusion: this session cannot audit the public website's ownership,
because it cannot see it.** This is the single largest gap relative to
S2/S36's requirements and is the top item in
`CLAUDE_INDEPENDENCE_ASSESSMENT.md`'s recommended next step.

## What IS verifiably owned (within accessible scope)

- `editorial-engine/` and `luf-core-engine/`: full source, full canonical
  data, full test suite, full documentation, all committed to a GitHub
  repository the project owner (jannestefors-wq) controls. No AI vendor
  dependency at runtime (see `CLAUDE_INDEPENDENCE_ASSESSMENT.md`).
- `kalkylprogram.py`/`app.py`: standalone Python, no AI dependency, no
  network dependency beyond what pandas/openpyxl/reportlab need locally.

## Recommendation

Before any further LUF Core Engine work integrates with the website, Adam,
House Engine, or Dilemma Bank, project management should either (a) attach
the actual repositories/hosting accounts for those systems to a Claude Code
session with read access, or (b) supply an export/inventory of them through
another channel, so a real ownership audit -- not just an absence report --
can be produced.
