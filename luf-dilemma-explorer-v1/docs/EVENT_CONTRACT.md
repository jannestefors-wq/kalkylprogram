# House Engine event-kontrakt

`src/core/events.js` emitterar fem semantiska events. Explorer rör aldrig
ljus, animation eller huset direkt — Work kopplar dessa till House Engine.

Två leveranskanaler, samma payload i båda:

- en DOM `CustomEvent` på `window`, namngiven `luf:<event>` (t.ex.
  `luf:dilemma_opened`), `event.detail = { name, payload, timestamp }`
- en callback-registry via `onHouseEvent(name, callback)` /
  `onHouseEvent("*", callback)` för icke-DOM-värdar

## Events

| Event | När | Payload |
|---|---|---|
| `dilemma_explorer_opened` | Vid appstart | `{ locale }` |
| `theme_selected` | Besökaren väljer ett ämne | `{ theme }` |
| `dilemma_discovered` | Ett eller flera dilemman ytas (slumpat, temaresultat, sökresultat) | `{ dilemma_id, source }` eller `{ dilemma_ids, source, theme? , query? }` |
| `dilemma_opened` | Besökaren öppnar ett specifikt dilemma i läsvyn | `{ dilemma_id, source }` |
| `thinking_chair_requested` | Besökaren klickar "Tänk vidare" | se `CORE_ENGINE_CONTRACT.md` |

`source` är alltid en av `"random" | "theme" | "search"`.

## Exempel: lyssna från Work:s sida

```js
import { onHouseEvent } from "./src/core/events.js";

onHouseEvent("dilemma_opened", ({ payload }) => {
  houseEngine.pulse(payload.dilemma_id); // Work:s egen logik, inte vår
});
```

eller via DOM:

```js
window.addEventListener("luf:dilemma_opened", (e) => {
  houseEngine.pulse(e.detail.payload.dilemma_id);
});
```

Inget i `events.js` refererar till ljus, animation eller huset — det är
en ren emitter/lyssnare-modul, verifierat strukturellt i
`tests/unit/events.test.js`.
