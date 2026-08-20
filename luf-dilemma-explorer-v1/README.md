# LUF Dilemma Explorer V1

Fristående komponent byggd för datorn i **Runda bordet**, Ledarskap utan
filter. Besökaren utforskar dilemman på tre sätt — slumpat, via ämne eller
fritextsökning — och kan sedan gå vidare till Tänkarstolen.

Detta är en **leverans till Work**, inte en produktionsdeployment. Se
[`WORK_INTEGRATION_PACKAGE.md`](./WORK_INTEGRATION_PACKAGE.md) för vad Work
ska ta in och koppla.

## Snabbstart

```bash
npm run serve        # startar en lokal statisk server på :8080
# öppna http://localhost:8080/src/ui/index.html
```

Inga byggsteg. Ingen bundler. Ingen backend. Se [`docs/INSTALL.md`](./docs/INSTALL.md)
för fullständiga instruktioner, inklusive hur testerna körs.

## Vad detta är

- En komplett, testad UI-komponent (`src/ui/`) för tre resor: slumpat
  dilemma, ämnesnavigering, fritextsökning.
- Ett adapter-interface, `DilemmaSource` (`src/core/DilemmaSource.js`), med
  en enda implementation i V1: `FixtureDilemmaSource`, som läser lokal
  JSON i `src/data/`.
- Ett event-kontrakt mot House Engine (`src/core/events.js`) och ett
  integrationskontrakt mot Tänkarstolen/Core Engine
  (`src/core/integrationBridge.js`) — båda utan att duplicera någon logik
  från de systemen.
- Fullt tvåspråkigt (sv/en) från en och samma kodbas.

## Vad detta inte är

Ingen D1. Ingen nätverksanrop. Ingen produktionskod. Ingen betalning,
inget login, ingen permanent historik, ingen ombyggd Tänkarstol eller
Academy. Se [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md) för
avgränsningen i sin helhet.

## Struktur

```
luf-dilemma-explorer-v1/
  src/
    core/           DilemmaSource, sök, locale, events, integrationBridge
    data/           fixture-JSON: dilemman (sv/en), ämnen, UI-strängar
    ui/             index.html, app.js, styles.css — hela UI:t
  tests/
    unit/           Node-tester för kärnlogiken (32 tester)
    e2e/            Playwright-resor RESA A/B/C, sv/en, mobil 375px
  docs/
    ARCHITECTURE.md
    DILEMMA_SOURCE_CONTRACT.md
    EVENT_CONTRACT.md
    CORE_ENGINE_CONTRACT.md
    THINKING_CHAIR_CONTRACT.md
    INSTALL.md
  WORK_INTEGRATION_PACKAGE.md
```
