# Arkitektur

## Lager

```
src/ui/app.js  (state machine + rendering, ingen affärslogik)
      │
      ├── src/core/DilemmaSource.js     ← ENDA kontaktytan mot dilemma-data
      │       └── FixtureDilemmaSource  ← V1:s enda implementation
      │
      ├── src/core/searchEngine.js      ← ren funktion, ingen I/O
      ├── src/core/locale.js            ← sv/en, ingen duplicerad komponent
      ├── src/core/events.js            ← House Engine-kontrakt (semantiska events)
      └── src/core/integrationBridge.js ← Tänkarstolen/Core Engine-kontrakt
```

UI:t (`app.js`) pratar **aldrig** direkt med JSON-filer, fetch-anrop till
en databas, eller något annat system. Allt går via `DilemmaSource`. Det är
den enda punkt Work behöver byta ut för att koppla in den verkliga
Dilemma Bank — se `DILEMMA_SOURCE_CONTRACT.md`.

## Varför fixtures, inte den verkliga Dilemma Bank

Den här sessionen hade inte tillgång till Dilemma Bank, Core Engine,
Tänkarstolen eller House Engine som körande system eller kod — bara till
`kalkylprogram`-repot. Det är också precis vad uppdraget bad om: V1 ska
byggas mot ett tydligt adapter-interface med enbart lokala fixtures, så
att Work kan koppla in det verkliga systemet utan att UI:t skrivs om.
Inget i arkitekturen antar att fixtures är den permanenta datakällan.

De 11 ämnena (Ledarskap, Tillit, Makt, Tystnad, Ansvar, Konflikt, Kultur,
Förändring, Människan, System, Resultat) och de fyra exempel-sökningarna
kommer direkt ur uppdragstexten — inget canonical LUF-taxonomi har
hittats på. De 15 dilemma-fixturerna i `src/data/dilemmas.sv.json` är
nyskrivet exempelinnehåll i LUF:s anda, tydligt märkt som fixtures, inte
verklig Dilemma Bank-data.

## State machine, inte ett ramverk

`app.js` är en liten hand-skriven state machine (skärmar: HOME, RANDOM →
DILEMMA, THEME_LIST → THEME_RESULTS → DILEMMA, SEARCH → DILEMMA) med
event-delegering och en historik-stack för "Tillbaka". Inget React, Vue
eller bundler — detta är en medveten portabilitetsavvägning: Work vet
inte vilket ramverk den riktiga hemsidan/kioskmiljön använder, så
komponenten är dependency-fri HTML/CSS/JS som kan bäddas in i vad som
helst (iframe, web component-wrapper, eller porteras logikrad-för-rad
till Work:s stack). `src/core/*` är ren, ramverksoberoende logik som
fungerar identiskt inbäddad i valfritt ramverk.

## Vad som medvetet INTE byggts (spec §15)

- Betalning, login, användarkonton.
- D1 eller någon annan databas — läs `docs/DILEMMA_SOURCE_CONTRACT.md`
  för var Work kopplar in D1 senare.
- Permanent historik eller spårning av enskilda besökare.
- Tänkarstolen på nytt — endast ett anropskontrakt, se
  `THINKING_CHAIR_CONTRACT.md`.
- Academy på nytt — endast en referens-sträng (`academy_ref`) per
  dilemma, ingen Academy-logik.
- House Engine — endast semantiska events, ingen ljus- eller
  animationslogik, se `EVENT_CONTRACT.md`.
- Produktionsdeployment av något slag.

## Skattsökarmentalitet, hållet subtilt (spec §6)

Varje dilemma-vy har en `<details>`-sektion (native HTML, ingen JS-lib)
för "Andra perspektiv" och "Relaterade dilemman" — stängd som standard,
ingen poäng, inga badges. Relaterade dilemman kommer från `related_ids`
i fixture-datan, med fallback till dilemman som delar tema om
`related_ids` saknas (se `DilemmaSource.getRelated`).
