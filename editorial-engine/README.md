# LUF Editorial Engine

Canonical Foundation V1 (schema + canonical referensdata) plus V1A, den
forsta vertikala motorkedjan (rent domanlogik, ingen generator). Se
`docs/ARCHITECTURE_NOTE.md` for Canonical Foundation, `docs/V1A_PURPOSE.md`
for vad V1A bevisar och `docs/V1A_DOES_NOT_DO.md` for dess avgransning.

## Struktur

```
editorial-engine/
  schema/          kanonisk sanningskalla (Pydantic-modeller) + avledd JSON Schema
  canonical_data/  verklig canonical referensdata (16 Series, 8 ThesisFamily, Territory, Reader Feedback) + kallfiler
  engine/          V1A: Raw Idea -> Interpretation -> Classification -> Comparison -> Angles -> Recommendation -> Human Decision
  fixtures/        litet exempeldataset som bevisar att modellen hanger ihop
  tests/           valideringstester (schema + V1A, inte en framtida generator)
  docs/            arkitektur, entitetskarta, versionering, provenance, open questions, V1A-dokumentation
```

## Kom igang

```bash
cd editorial-engine
pip install -r requirements.txt

# kor testerna
python3 -m pytest -q

# generera JSON Schema (avlett artefakt — redigera aldrig for hand)
python3 -m schema.export_json_schema

# generera fixture-dataset som JSON
python3 -m fixtures.generate_fixture_json
```

## Lasordning

1. `docs/ARCHITECTURE_NOTE.md` — helhetsbild och var sanningen bor.
2. `docs/ENTITY_MAP.md` — objekt, relationer, de fyra variationsdimensionerna.
3. `docs/ENUMS_TAXONOMIES.md` — alla kontrollerade vokabularer.
4. `docs/VERSIONING_STRATEGY.md`, `docs/PROVENANCE_STRATEGY.md`.
5. `docs/OPEN_QUESTIONS.md`, `docs/TECHNICAL_PROPOSALS.md` — allt som
   kravde ett tekniskt beslut, flaggat for granskning.
6. `docs/FINAL_REPORT.md` — slutrapport (Beslut 32).

## Kanonisk kod

`schema/*.py`. Varje fil har en modulniva-docstring som forklarar vilket
Beslut (i uppdragstexten) den representerar och vilka normaliseringar/
TECHNICAL PROPOSALS som gjorts.
