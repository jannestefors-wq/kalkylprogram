# Tänkarstolen-kontrakt

Explorer bygger inte om Tänkarstolen (spec §2, §15). Den enda kopplingen
är funktionsanropet nedan plus House-eventet `thinking_chair_requested`
(`EVENT_CONTRACT.md`).

```js
import { openInThinkingChair } from "./src/core/integrationBridge.js";

openInThinkingChair(dilemmaId, {
  theme: ["tystnad"],
  source: "search",        // "random" | "theme" | "search"
  language: "sv",
  context: { title: "Tystnaden i rummet" },
});
```

`meta` är valfritt — utan det skickas rimliga defaults
(`{ theme: [], source: "random", language: "sv", context: {} }`), se
testet `openInThinkingChair fills sensible defaults` i
`tests/unit/integrationBridge.test.js`.

## Vad Work behöver göra

1. Registrera en handler via `setThinkingChairHandler(payload => …)`
   (samma funktion som i `CORE_ENGINE_CONTRACT.md` — det är samma
   mottagare, sektion 2 och 9 i uppdraget beskriver samma koppling från
   två vinklar).
2. I handlern: navigera till/starta den riktiga Tänkarstolen med
   `payload.dilemma_id` och resten av kontexten.

Tills handlern är registrerad fail:ar knappen "Tänk vidare" mjukt och
visar ett statusmeddelande — se `chair.pending`/`chair.unavailable` i
`src/data/strings.*.json`.
