# Work Integration Package — LUF Dilemma Explorer V1

Denna fil är den enda Work borde behöva läsa för att ta komponenten in i
huset. Detaljerade kontrakt länkas nedan i stället för att upprepas.

## 1. Vilka filer Work ska ta in

Hela mappen `luf-dilemma-explorer-v1/`, i sin helhet:

```
src/core/       6 filer — all logik, ramverksoberoende JS-moduler
src/data/       6 JSON-filer — fixture-dilemman, ämnen, UI-strängar (sv+en)
src/ui/         index.html, app.js, styles.css — referens-UI
tests/          32 enhetstester + 26 e2e-checkar (RESA A/B/C, sv/en, 375px)
docs/           kontrakt och arkitektur
```

Inget i `src/core/` eller `src/data/` beror på `src/ui/`. Work kan
antingen:

- **(a)** bädda in `src/ui/` rakt av (iframe eller egen route) och bara
  koppla in de tre kontrakten nedan, eller
- **(b)** återanvända bara `src/core/*` och `src/data/*` och bygga ett
  eget UI-lager i husets befintliga stack — `DilemmaSource`,
  `searchEngine`, `locale` och `events` är rena moduler utan DOM-beroenden
  (bara `integrationBridge.js` och `app.js` rör `window`, och även de
  degraderar snyggt utan DOM — se `events.js`).

## 2. Dependencies

**Noll runtime-beroenden.** Ren HTML/CSS/JS (ES-moduler), ingen bundler,
inget npm-paket krävs för att köra komponenten. `playwright` och
`http-server` i `package.json` är enbart dev-verktyg för test/lokal
serving — se `docs/INSTALL.md`.

Krav på värdmiljön: filerna måste serveras över HTTP(S) (inte
`file://`), eftersom `app.js` hämtar JSON-fixturerna med `fetch`.

## 3. Interfaces att koppla

Tre kopplingspunkter, i prioritetsordning:

| Kontrakt | Fil | Vad Work gör |
|---|---|---|
| `DilemmaSource` | `src/core/DilemmaSource.js` | Skriv en ny klass som ärver `DilemmaSource`, byt ut i `app.js` → `createSource(...)`. Se `docs/DILEMMA_SOURCE_CONTRACT.md`. |
| Tänkarstolen/Core Engine | `src/core/integrationBridge.js` | Anropa `setThinkingChairHandler(payload => …)`. Se `docs/THINKING_CHAIR_CONTRACT.md` och `docs/CORE_ENGINE_CONTRACT.md`. |
| House Engine | `src/core/events.js` | Lyssna med `onHouseEvent(name, cb)` eller `window.addEventListener("luf:<event>", …)`. Se `docs/EVENT_CONTRACT.md`. |

## 4. Events som finns

`dilemma_explorer_opened`, `theme_selected`, `dilemma_discovered`,
`dilemma_opened`, `thinking_chair_requested` — fullständig payload-form i
`docs/EVENT_CONTRACT.md`. Inget annat emitteras. Ingen ljus- eller
animationslogik finns i Explorer — Work äger den tolkningen helt.

## 5. Hur Dilemma Bank ansluts

Se `docs/DILEMMA_SOURCE_CONTRACT.md` i sin helhet. Kort version: skriv
`class D1DilemmaSource extends DilemmaSource { … }` som implementerar de
sex metoderna (`getRandom`, `getByTheme`, `search`, `getById`,
`listThemes`, `getRelated`) mot den verkliga banken, och byt ut
instansieringen i `app.js`. UI:t, sökningen och navigeringen kräver noll
ändringar.

**Viktigt:** V1:s 15 fixture-dilemman (`src/data/dilemmas.sv.json` /
`.en.json`) är nyskrivet exempelinnehåll, inte verklig Dilemma Bank-data
— den här sessionen hade inte tillgång till den verkliga banken. De 11
ämnena är dock tagna direkt ur uppdragstexten, inte påhittade.

## 6. Hur Tänkarstolen ansluts

Se `docs/THINKING_CHAIR_CONTRACT.md`. En rad, i princip:

```js
setThinkingChairHandler((payload) => navigateToThinkingChair(payload));
```

`payload` innehåller redan `dilemma_id`, `theme`, `source`, `language`,
`context` — allt Tänkarstolen/Core Engine behöver för att ta vid.

## 7. Hur locale ansluts

Explorer stödjer sv/en från en och samma kodbas (ingen duplicerad
komponent). Fixtures och UI-strängar är keyade per locale i `src/data/`.
Standard är svenska (kioskdatorn sniffar inte webbläsarspråk — se
`docs/ARCHITECTURE.md`). Work kan:

- låta besökaren växla med språkknappen som redan finns i UI:t, eller
- sätta `window.__LUF_LOCALE__ = "en"` innan `app.js` laddas för att låsa
  språket, eller
- lägga till `?lang=en`/`?lang=sv` i URL:en.

För att lägga till fler språk: lägg till `dilemmas.<locale>.json`,
`themes.<locale>.json`, `strings.<locale>.json` och lägg till koden i
`SUPPORTED_LOCALES` (`src/core/locale.js`). Ingen annan kod behöver
ändras.

## 8. Vad Work får ändra visuellt

Allt i `src/ui/styles.css` och `src/ui/index.html` är fritt att
anpassa/temasätta till rummets faktiska visuella integration (spec §13).
Färgpalett, typsnitt, animationer, layoutdensitet — inget av det är en
del av kontraktet. Behåll gärna känslan "gammalt bibliotek möter modern
intelligens" (inte SaaS-dashboard, inte chattbubblor, inte
terminal-estetik), men det är en rekommendation, inte en spärr.

**Rör inte** `data-action`-attributen i `app.js`:s renderfunktioner om ni
bara temasätter CSS — de är kopplade till event-delegeringen. Byt
gärna ut hela rendering-lagret om ni vill, så länge det fortsätter prata
med `DilemmaSource`, `integrationBridge` och `events` som de är.

## 9. Vad som är Core-kontrakt och INTE ska dupliceras

- `src/core/DilemmaSource.js` — interfacet, inte innehållet. Work
  duplicerar inte sökmotorlogik eller relaterade-dilemman-logik i en ny
  källa; de återanvänds via `searchEngine.js`/`FixtureDilemmaSource`s
  fallback-logik om det är rimligt, annars implementeras samma
  *kontrakt* på nytt mot D1 — inte samma metod kopierad.
- `src/core/integrationBridge.js` — payload-formen mot Tänkarstolen/Core
  Engine. Ingen metodlogik från Tänkarstolen eller Core Engine finns
  här eller ska läggas till här; det är en tunn kontraktsfil, inte en
  ny implementation av deras logik.
- `src/core/events.js` — event-namnen och payload-formen är kontraktet.
  Husets faktiska ljus-/animationslogik hör hemma i House Engine, inte
  här.

## 10. Tester Work kan köra direkt

```bash
npm run test:unit   # 32 tester, ren logik
npm run test:e2e     # 26 checkar: RESA A/B/C × sv/en × mobil 375px
```

Båda är gröna i denna leverans (se rapportens avsnitt Q och
`tests/e2e/screenshots/` för visuellt bevis).
