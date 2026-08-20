import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { FixtureDilemmaSource, DilemmaSource } from "../../src/core/DilemmaSource.js";

const dataDir = fileURLToPath(new URL("../../src/data/", import.meta.url));
const readJSON = (name) => JSON.parse(readFileSync(dataDir + name, "utf8"));

const dilemmasByLocale = { sv: readJSON("dilemmas.sv.json"), en: readJSON("dilemmas.en.json") };
const themesByLocale = { sv: readJSON("themes.sv.json"), en: readJSON("themes.en.json") };

function makeSource() {
  return new FixtureDilemmaSource({ dilemmasByLocale, themesByLocale });
}

test("fixture data: sv and en have matching ids and theme sets", () => {
  const svIds = dilemmasByLocale.sv.map((d) => d.id).sort();
  const enIds = dilemmasByLocale.en.map((d) => d.id).sort();
  assert.deepEqual(svIds, enIds, "sv and en fixtures must cover the same dilemma ids");

  const themeIds = new Set(themesByLocale.sv.map((t) => t.id));
  for (const locale of ["sv", "en"]) {
    for (const d of dilemmasByLocale[locale]) {
      for (const theme of d.themes) {
        assert.ok(themeIds.has(theme), `${locale}/${d.id} references unknown theme "${theme}"`);
      }
      for (const relId of d.related_ids || []) {
        assert.ok(dilemmasByLocale[locale].some((x) => x.id === relId), `${locale}/${d.id} related_id "${relId}" must exist`);
      }
    }
  }
});

test("fixture data: every theme from the spec's example list is covered by at least one dilemma", () => {
  const specThemes = ["ledarskap", "tillit", "makt", "tystnad", "ansvar", "konflikt", "kultur", "forandring", "manniskan", "system", "resultat"];
  const themeIds = themesByLocale.sv.map((t) => t.id).sort();
  assert.deepEqual(themeIds, [...specThemes].sort());
  for (const theme of specThemes) {
    assert.ok(dilemmasByLocale.sv.some((d) => d.themes.includes(theme)), `no sv dilemma covers theme "${theme}"`);
  }
});

test("DilemmaSource base class throws NotImplemented for every contract method", async () => {
  const base = new DilemmaSource();
  for (const [method, args] of [
    ["getRandom", ["sv"]], ["getByTheme", ["makt", "sv"]], ["search", ["chef", "sv"]],
    ["getById", ["dil-001", "sv"]], ["listThemes", ["sv"]], ["getRelated", ["dil-001", "sv"]],
  ]) {
    await assert.rejects(() => base[method](...args));
  }
});

test("getRandom returns a dilemma from the requested locale", async () => {
  const source = makeSource();
  const d = await source.getRandom("sv");
  assert.ok(dilemmasByLocale.sv.some((x) => x.id === d.id));
});

test("getByTheme returns only dilemmas tagged with that theme", async () => {
  const source = makeSource();
  const results = await source.getByTheme("tystnad", "sv");
  assert.ok(results.length > 0);
  for (const d of results) assert.ok(d.themes.includes("tystnad"));
});

test("getById resolves per-locale, and returns null for unknown ids", async () => {
  const source = makeSource();
  const sv = await source.getById("dil-002", "sv");
  const en = await source.getById("dil-002", "en");
  assert.equal(sv.id, "dil-002");
  assert.equal(en.id, "dil-002");
  assert.notEqual(sv.title, en.title, "sv/en titles should actually differ, proving locale content is separate");
  assert.equal(await source.getById("dil-999", "sv"), null);
});

test("getRelated prefers explicit related_ids and falls back to shared theme", async () => {
  const source = makeSource();
  const related = await source.getRelated("dil-001", "sv");
  assert.deepEqual(related.map((d) => d.id).sort(), ["dil-006", "dil-013"]);

  // synthetic dilemma with no related_ids to exercise the fallback path
  const synthetic = new FixtureDilemmaSource({
    dilemmasByLocale: {
      sv: [
        { id: "a", title: "A", dilemma: "...", conflict: "...", themes: ["makt"], tags: [], related_ids: [] },
        { id: "b", title: "B", dilemma: "...", conflict: "...", themes: ["makt"], tags: [], related_ids: [] },
      ],
    },
    themesByLocale: { sv: themesByLocale.sv },
  });
  const fallback = await synthetic.getRelated("a", "sv");
  assert.deepEqual(fallback.map((d) => d.id), ["b"]);
});

test("listThemes returns the locale-labeled theme list", async () => {
  const source = makeSource();
  const sv = await source.listThemes("sv");
  const en = await source.listThemes("en");
  assert.equal(sv.find((t) => t.id === "makt").label, "Makt");
  assert.equal(en.find((t) => t.id === "makt").label, "Power");
});

test("no method ever reads a network, D1 binding, or filesystem beyond the constructor payload", () => {
  // Structural guarantee: FixtureDilemmaSource holds only the data handed
  // to its constructor and never imports fetch/fs/D1 client code itself.
  const src = readFileSync(fileURLToPath(new URL("../../src/core/DilemmaSource.js", import.meta.url)), "utf8");
  for (const forbidden of ["fetch(", "require(\"fs\"", "from \"fs\"", "D1Database", "env.DB", "process.env"]) {
    assert.ok(!src.includes(forbidden), `DilemmaSource.js must not reference "${forbidden}"`);
  }
});
