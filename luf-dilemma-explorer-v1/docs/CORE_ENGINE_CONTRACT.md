# Core Engine-kontrakt

`src/core/integrationBridge.js` innehåller ingen metodlogik från Core
Engine eller Tänkarstolen — bara payload-formen och event-emissionen.

## Payload (spec §9)

```ts
type CoreEngineRequest = {
  dilemma_id: string;
  theme: string[];               // dilemmats teman, t.ex. ["resultat","manniskan"]
  source: "random" | "theme" | "search";
  language: "sv" | "en";
  context: Record<string, unknown>; // fritt, t.ex. { query, theme_id, title }
};
```

## Funktioner

```js
requestCoreEngine(payload: CoreEngineRequest)
// → { delivered: true } om Work registrerat en handler, annars
//   { delivered: false, reason: "no_handler_registered" }

openInThinkingChair(dilemmaId, meta?)
// tunn wrapper (spec §2) som bygger payloaden ovan från bara ett id
```

Båda emitterar `thinking_chair_requested` (se `EVENT_CONTRACT.md`)
**oavsett** om en handler är registrerad — så House Engine kan reagera på
önskan att gå vidare även innan Tänkarstolen faktiskt är kopplad.

## Hur Work kopplar in Tänkarstolen

```js
import { setThinkingChairHandler } from "./src/core/integrationBridge.js";

setThinkingChairHandler((payload) => {
  // Work:s egen routing/API-anrop till Tänkarstolen/Core Engine.
  // Explorer vet inget om hur detta görs.
  navigateToThinkingChair(payload);
});
```

Utan registrerad handler visar V1 texten "Tänkarstolen är inte ansluten i
den här versionen" (`chair.unavailable` i `strings.sv.json`/`strings.en.json`)
— fail-soft, ingen krasch, ingen död länk.
