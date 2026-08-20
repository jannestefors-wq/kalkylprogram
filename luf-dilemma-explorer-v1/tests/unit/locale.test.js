import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { SUPPORTED_LOCALES, DEFAULT_LOCALE, isSupportedLocale, resolveInitialLocale, createTranslator } from "../../src/core/locale.js";

test("sv and en are supported, sv is the default", () => {
  assert.deepEqual([...SUPPORTED_LOCALES].sort(), ["en", "sv"]);
  assert.equal(DEFAULT_LOCALE, "sv");
  assert.ok(isSupportedLocale("sv"));
  assert.ok(isSupportedLocale("en"));
  assert.ok(!isSupportedLocale("de"));
});

test("resolveInitialLocale prefers explicit override, then browser language, then default", () => {
  assert.equal(resolveInitialLocale({ override: "en", navigatorLanguage: "sv-SE" }), "en");
  assert.equal(resolveInitialLocale({ navigatorLanguage: "en-US" }), "en");
  assert.equal(resolveInitialLocale({ navigatorLanguage: "de-DE" }), "sv");
  assert.equal(resolveInitialLocale({}), "sv");
});

test("createTranslator interpolates placeholders", () => {
  const t = createTranslator({ "hello": "Hej {name}" });
  assert.equal(t("hello", { name: "Jan" }), "Hej Jan");
});

test("createTranslator resolves .one/.many by count, falling back to the bare key", () => {
  const t = createTranslator({
    "theme.count.one": "1 dilemma",
    "theme.count.many": "{count} dilemman",
    "search.button": "Sök",
  });
  assert.equal(t("theme.count", { count: 1 }), "1 dilemma");
  assert.equal(t("theme.count", { count: 5 }), "5 dilemman");
  assert.equal(t("search.button"), "Sök");
});

test("unknown key falls back to the key itself rather than throwing", () => {
  const t = createTranslator({});
  assert.equal(t("does.not.exist"), "does.not.exist");
});

test("every string key used by strings.sv.json exists with the same shape in strings.en.json", () => {
  const dataDir = fileURLToPath(new URL("../../src/data/", import.meta.url));
  const sv = JSON.parse(readFileSync(dataDir + "strings.sv.json", "utf8"));
  const en = JSON.parse(readFileSync(dataDir + "strings.en.json", "utf8"));
  assert.deepEqual(Object.keys(sv).sort(), Object.keys(en).sort());
});
