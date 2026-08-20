import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { searchDilemmas } from "../../src/core/searchEngine.js";

const dataDir = fileURLToPath(new URL("../../src/data/", import.meta.url));
const readJSON = (name) => JSON.parse(readFileSync(dataDir + name, "utf8"));
const dilemmasSv = readJSON("dilemmas.sv.json");
const dilemmasEn = readJSON("dilemmas.en.json");
const themesSv = readJSON("themes.sv.json");
const themesEn = readJSON("themes.en.json");

test("the four example queries from the spec each return a relevant top result", () => {
  const cases = [
    ["informella ledare", "dil-001"],
    ["chef som inte lyssnar", "dil-002"],
    ["medarbetare som gjort fel", "dil-003"],
    ["resultat före människor", "dil-004"],
  ];
  for (const [query, expectedTopId] of cases) {
    const results = searchDilemmas(dilemmasSv, query, themesSv);
    assert.ok(results.length > 0, `query "${query}" returned no results`);
    assert.equal(results[0].id, expectedTopId, `query "${query}" expected top result ${expectedTopId}, got ${results[0].id}`);
  }
});

test("english equivalents of the example queries also resolve", () => {
  const cases = [
    ["informal leaders", "dil-001"],
    ["manager who doesn't listen", "dil-002"],
    ["employee who made a mistake", "dil-003"],
    ["results before people", "dil-004"],
  ];
  for (const [query, expectedTopId] of cases) {
    const results = searchDilemmas(dilemmasEn, query, themesEn);
    assert.ok(results.length > 0, `query "${query}" returned no results`);
    assert.equal(results[0].id, expectedTopId);
  }
});

test("search matches across title, dilemma text, theme labels and tags", () => {
  const byTitle = searchDilemmas(dilemmasSv, "Tystnaden i rummet", themesSv);
  assert.equal(byTitle[0].id, "dil-005");

  const byThemeLabel = searchDilemmas(dilemmasSv, "Tystnad", themesSv);
  assert.ok(byThemeLabel.some((d) => d.id === "dil-005"));

  const byBodyText = searchDilemmas(dilemmasSv, "bonussystemet belönar", themesSv);
  assert.equal(byBodyText[0].id, "dil-009");
});

test("accented and unaccented spelling both match", () => {
  const accented = searchDilemmas(dilemmasSv, "förändring", themesSv);
  const unaccented = searchDilemmas(dilemmasSv, "forandring", themesSv);
  assert.ok(accented.length > 0);
  assert.deepEqual(accented.map((d) => d.id), unaccented.map((d) => d.id));
});

test("empty or whitespace-only query returns no results, never the full list", () => {
  assert.deepEqual(searchDilemmas(dilemmasSv, "", themesSv), []);
  assert.deepEqual(searchDilemmas(dilemmasSv, "   ", themesSv), []);
});

test("nonsense query returns no results", () => {
  assert.deepEqual(searchDilemmas(dilemmasSv, "xyzxyzintemodel", themesSv), []);
});

test("search is a pure function: same input always yields the same order", () => {
  const a = searchDilemmas(dilemmasSv, "ansvar", themesSv).map((d) => d.id);
  const b = searchDilemmas(dilemmasSv, "ansvar", themesSv).map((d) => d.id);
  assert.deepEqual(a, b);
});
