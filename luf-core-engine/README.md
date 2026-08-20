# LUF Core Engine

V1 Foundation (Direktorder LUF Core Engine V1, 2026-08-20). The shared
methodology motor for Ledarskap utan filter -- Canonical Tool Registry,
triangulation representation, observation/interpretation separation, Tool
Trace, Human Review workflow, and adapter contracts toward Editorial
Engine, Dilemma Bank, House Engine, and a future generative-AI provider.

This is infrastructure, not a product: no public-facing feature (Tänkarstolen,
training modules, speaker/workshop tooling) is built here. Those are meant
to become future adapters on top of this Foundation, per Direktorder S33.

## Struktur

```
schema/          canonisk sanningskälla (Pydantic-modeller): Provenance,
                  CanonicalTool (Tool Registry), Claim (observation/
                  interpretation-separation), TriangulationSession, ZoomFrame,
                  ToolTrace
canonical_data/   det faktiska (candidate) tool-inventoriet + dess loader
human_review/     den enda platsen ett verktyg kan bli CANONICAL_APPROVED
adapters/         provider-abstraktion + integrationskontrakt (Editorial
                  Engine, Dilemma Bank, House Engine) + entitlement-gräns
docs/             manifest, ownership/independence/backup-rapporter,
                  integrationskontrakt, öppna frågor
tests/            31 tester som täcker Direktorderns S34-krav
```

## Kom igång

```bash
cd luf-core-engine
pip install -r requirements.txt
python3 -m pytest -q
```

## Läsordning

1. `docs/ARCHITECTURE_NOTE.md` -- vad detta är och inte är.
2. `docs/LUF_SYSTEM_MANIFEST.md` -- hela systemet, repos, ägande, blockerare.
3. `docs/OWNERSHIP_AUDIT.md`, `docs/CLAUDE_INDEPENDENCE_ASSESSMENT.md`.
4. `docs/OPEN_QUESTIONS.md` -- allt som kräver Human Review eller mer källmaterial.
5. `docs/INTEGRATION_CONTRACT_EDITORIAL_ENGINE.md`,
   `docs/INTEGRATION_CONTRACT_DILEMMA_BANK.md`,
   `docs/HOUSE_ENGINE_EVENT_CONTRACT.md`, `docs/ENTITLEMENT_BOUNDARY.md`.
6. `docs/BACKUP_RESTORE_DESIGN.md`, `docs/RESTORE_TEST_RESULT.md`.
7. `docs/DEFINITION_OF_DONE.md` -- den globala regeln (S31) från och med denna order.

## Kanonisk kod

`schema/*.py`, `human_review/workflow.py`. Varje modul har en docstring som
förklarar vilket Beslut/Direktorder-S den representerar.
