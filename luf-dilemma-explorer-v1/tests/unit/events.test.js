import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { HOUSE_EVENTS, emitHouseEvent, onHouseEvent, resetHouseEventListeners } from "../../src/core/events.js";

test("HOUSE_EVENTS exposes exactly the five semantic event names from the spec", () => {
  assert.deepEqual(Object.values(HOUSE_EVENTS).sort(), [
    "dilemma_discovered", "dilemma_explorer_opened", "dilemma_opened", "theme_selected", "thinking_chair_requested",
  ].sort());
});

test("emitHouseEvent delivers name, payload and a timestamp to subscribers", () => {
  resetHouseEventListeners();
  let received = null;
  onHouseEvent(HOUSE_EVENTS.THEME_SELECTED, (detail) => { received = detail; });

  emitHouseEvent(HOUSE_EVENTS.THEME_SELECTED, { theme: "makt" });

  assert.equal(received.name, "theme_selected");
  assert.deepEqual(received.payload, { theme: "makt" });
  assert.equal(typeof received.timestamp, "string");
  assert.ok(!Number.isNaN(Date.parse(received.timestamp)));
});

test("a '*' subscriber receives every event", () => {
  resetHouseEventListeners();
  const seen = [];
  onHouseEvent("*", (detail) => seen.push(detail.name));

  emitHouseEvent(HOUSE_EVENTS.EXPLORER_OPENED, {});
  emitHouseEvent(HOUSE_EVENTS.DILEMMA_OPENED, { dilemma_id: "dil-001" });

  assert.deepEqual(seen, ["dilemma_explorer_opened", "dilemma_opened"]);
});

test("unsubscribe stops further delivery", () => {
  resetHouseEventListeners();
  const seen = [];
  const unsubscribe = onHouseEvent(HOUSE_EVENTS.DILEMMA_OPENED, (d) => seen.push(d));
  emitHouseEvent(HOUSE_EVENTS.DILEMMA_OPENED, { dilemma_id: "dil-001" });
  unsubscribe();
  emitHouseEvent(HOUSE_EVENTS.DILEMMA_OPENED, { dilemma_id: "dil-002" });
  assert.equal(seen.length, 1);
});

test("no light or house-animation logic lives in this module", () => {
  const src = new URL("../../src/core/events.js", import.meta.url);
  // structural guarantee, not just a naming convention: grep the source
  // for anything beyond emitting/subscribing to named semantic events.
  const text = readFileSync(src, "utf8");
  for (const forbidden of ["light", "animate", "brightness", "hue"]) {
    assert.ok(!text.toLowerCase().includes(forbidden), `events.js must not reference "${forbidden}"`);
  }
});
