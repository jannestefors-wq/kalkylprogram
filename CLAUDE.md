# kalkylprogram — riktlinjer för Claude Code

Detta repo innehåller två separata delar. Läs bara det som behövs för
uppgiften, inte allt vid varje session.

## Struktur

- `app.py`, `kalkylprogram.py` — Streamlit-kalkylator för bygg/fastighet.
  Stora filer (~1500 respektive ~1800 rader). Sök efter funktion/symbol
  med Grep innan hela filen läses. Läs hela filen bara vid uppgifter som
  faktiskt kräver helhetsbild (t.ex. strukturell refaktorering).
- `editorial-engine/` — separat Python-paket för LUF Editorial Engine
  (innehållspipeline, inte del av kalkylatorn). Har egen `README.md` med
  läsordning och egna tester (`pytest`). Se den READMEn innan du börjar
  arbeta där — den skiljer numera kanonisk läsning från historiska
  revisionsrapporter.
- `.streamlit/`, `render.yaml`, `requirements.txt` — driftskonfiguration
  för kalkylatorn.

## Arbetssätt

- Targeted read först: lokalisera med Glob/Grep innan du läser en hel fil.
- Ändra aldrig produktkod (`app.py`, `kalkylprogram.py`,
  `editorial-engine/engine|schema|memory|variation`) utan att uppgiften
  uttryckligen kräver det.
- `editorial-engine/schema/json/*.schema.json` är avledda artefakter —
  redigera aldrig för hand, generera om med
  `python3 -m schema.export_json_schema`.
- Kör bara `pytest` i `editorial-engine/` när ändringen faktiskt berör
  den koden. Kalkylatorn har inget testsvit i detta repo — verifiera
  ändringar där genom att läsa den berörda funktionen, inte genom att
  köra hela appen om det inte krävs.
