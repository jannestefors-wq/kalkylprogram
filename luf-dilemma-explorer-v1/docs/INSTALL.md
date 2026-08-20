# Installation & tester

## Köra appen

Inga byggsteg. Kräver bara att filerna serveras över HTTP (inte `file://`,
eftersom `app.js` hämtar JSON-fixturerna med `fetch`).

```bash
npm run serve
# öppna http://localhost:8080/src/ui/index.html
```

`npm run serve` kräver `http-server` (devDependency). Vilken statisk
filserver som helst fungerar lika bra — servera `luf-dilemma-explorer-v1/`
som rot och öppna `/src/ui/index.html`.

Språk kan tvingas fram med `?lang=en` eller `?lang=sv` i URL:en, annars
vilar appen på svenska (se `docs/ARCHITECTURE.md`, avsnittet om locale).

## Enhetstester (32 st, Node:s inbyggda testrunner, inga externa beroenden)

```bash
npm run test:unit
```

Kör `DilemmaSource`, sökmotorn, temafiltrering, locale-växling och
event-kontraktet — allt utan nätverk, utan D1.

## End-to-end-tester (Playwright, RESA A/B/C + sv/en + mobil 375px)

```bash
npm install                       # installerar playwright + http-server lokalt
npx playwright install chromium   # bara om browsern inte redan finns
npm run test:e2e
```

Skärmdumpar från varje resa sparas i `tests/e2e/screenshots/`.

Om `npm install` inte har nätverksåtkomst i din miljö men Playwright
redan finns globalt installerat (`npm ls -g`), räcker det att peka ett
lokalt `node_modules/playwright`-alias mot den globala installationen —
`npm install` behövs bara för att hämta paketen, inte för att köra dem.

## Beroenden

Appen själv (`src/`) har **noll** runtime-beroenden — ren HTML/CSS/JS-moduler.
`playwright` och `http-server` används enbart av testverktygen/lokal
utveckling, inte av den levererade komponenten.
