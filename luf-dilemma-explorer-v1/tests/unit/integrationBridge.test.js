import { test } from "node:test";
import assert from "node:assert/strict";
import { HOUSE_EVENTS, onHouseEvent, resetHouseEventListeners } from "../../src/core/events.js";
import {
  openInThinkingChair, requestCoreEngine, setThinkingChairHandler, resetThinkingChairHandler,
} from "../../src/core/integrationBridge.js";

test("requestCoreEngine emits thinking_chair_requested with the full contract payload", () => {
  resetHouseEventListeners();
  resetThinkingChairHandler();
  let received = null;
  onHouseEvent(HOUSE_EVENTS.THINKING_CHAIR_REQUESTED, (detail) => { received = detail; });

  const payload = { dilemma_id: "dil-004", theme: ["resultat", "manniskan"], source: "search", language: "sv", context: { query: "resultat" } };
  requestCoreEngine(payload);

  assert.deepEqual(received.payload, payload);
});

test("with no handler registered, the request fails soft and reports it", () => {
  resetThinkingChairHandler();
  const result = requestCoreEngine({ dilemma_id: "dil-001", theme: [], source: "random", language: "sv", context: {} });
  assert.deepEqual(result, { delivered: false, reason: "no_handler_registered" });
});

test("once Work registers a handler, requests are delivered to it", () => {
  resetThinkingChairHandler();
  let handled = null;
  setThinkingChairHandler((payload) => { handled = payload; });

  const result = requestCoreEngine({ dilemma_id: "dil-002", theme: ["tillit"], source: "theme", language: "en", context: {} });

  assert.deepEqual(result, { delivered: true });
  assert.equal(handled.dilemma_id, "dil-002");
  resetThinkingChairHandler();
});

test("openInThinkingChair (section 2's simple contract) builds a full payload from just an id", () => {
  resetThinkingChairHandler();
  let handled = null;
  setThinkingChairHandler((payload) => { handled = payload; });

  openInThinkingChair("dil-005", { theme: ["tystnad"], source: "random", language: "sv", context: { title: "Tystnaden i rummet" } });

  assert.equal(handled.dilemma_id, "dil-005");
  assert.deepEqual(handled.theme, ["tystnad"]);
  assert.equal(handled.source, "random");
  assert.equal(handled.language, "sv");
  assert.deepEqual(handled.context, { title: "Tystnaden i rummet" });
  resetThinkingChairHandler();
});

test("openInThinkingChair fills sensible defaults when called with only an id", () => {
  resetThinkingChairHandler();
  let handled = null;
  setThinkingChairHandler((payload) => { handled = payload; });

  openInThinkingChair("dil-001");

  assert.deepEqual(handled, { dilemma_id: "dil-001", theme: [], source: "random", language: "sv", context: {} });
  resetThinkingChairHandler();
});
