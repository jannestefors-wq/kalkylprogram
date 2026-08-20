# DilemmaSource-kontrakt

`src/core/DilemmaSource.js` exporterar basklassen `DilemmaSource` och V1:s
enda implementation, `FixtureDilemmaSource`. UI:t importerar bara
interfacet — aldrig fixtures eller en databas direkt.

## Interface

```js
class DilemmaSource {
  async getRandom(locale)          // → Dilemma
  async getByTheme(themeId, locale) // → Dilemma[]
  async search(query, locale)       // → Dilemma[] (rankad relevans, hög→låg)
  async getById(id, locale)         // → Dilemma | null
  async listThemes(locale)          // → { id, label }[]
  async getRelated(id, locale)      // → Dilemma[] (skattsökar-upptäckt)
}
```

Alla metoder är `async` — även fixture-implementationen — så att en
framtida nätverks-/D1-baserad implementation är en drop-in-ersättning
utan att UI:t ändras.

## Dilemma-formen

```json
{
  "id": "dil-004",
  "title": "Resultat före människor",
  "dilemma": "Fullständig dilemma-text …",
  "conflict": "Kort spänningsbeskrivning.",
  "themes": ["resultat", "manniskan"],
  "tags": ["resultat före människor", "prestation", "utmattning"],
  "perspectives": [{ "label": "…", "text": "…" }],
  "related_ids": ["dil-012", "dil-009"],
  "academy_ref": "academy://prestation-och-halsa"
}
```

`academy_ref` är enbart en referens-sträng (kontrakt, inte funktion) —
Work kopplar den till riktigt Academy-material eller tar bort fältet om
det inte används.

## Hur Work kopplar in den verkliga Dilemma Bank

1. Skriv en ny klass, t.ex. `D1DilemmaSource extends DilemmaSource`, som
   implementerar samma sex metoder mot D1/den verkliga databasen.
2. Byt ut anropet i `src/ui/app.js`, funktionen `createSource(...)` (en
   enda plats) mot den nya klassen.
3. UI:t, sökningen, temanavigeringen och event-emissionen kräver noll
   ändringar — de känner bara till interfacet.

`FixtureDilemmaSource` rör aldrig `fetch`, filsystem utöver sin egen
konstruktor-payload, D1 eller `process.env` — verifierat av ett
strukturellt test i `tests/unit/dilemmaSource.test.js`.
