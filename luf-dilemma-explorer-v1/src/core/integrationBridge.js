/**
 * Integration contract toward the Thinking Chair (Tänkarstolen) and the
 * LUF Core Engine. This file contains no method logic from either system —
 * it only shapes the payload and emits the semantic events Work will wire
 * up on the real integration. See docs/THINKING_CHAIR_CONTRACT.md and
 * docs/CORE_ENGINE_CONTRACT.md.
 *
 * V1 default behavior: emit the event and, if no handler is registered,
 * fail soft (no crash, no dead link) — see chair.unavailable string.
 */

import { HOUSE_EVENTS, emitHouseEvent } from "./events.js";

let thinkingChairHandler = null;

/**
 * Work registers the real handler once Tänkarstolen/Core Engine is wired
 * up (e.g. navigating to the Thinking Chair route, or calling its API).
 * Until then, requests are only observable via the emitted House event.
 * @param {(payload: CoreEngineRequest) => void} handler
 */
export function setThinkingChairHandler(handler) {
  thinkingChairHandler = handler;
}

/**
 * @typedef {object} CoreEngineRequest
 * @property {string} dilemma_id
 * @property {string[]} theme
 * @property {"random"|"theme"|"search"} source - how the visitor arrived at this dilemma
 * @property {"sv"|"en"} language
 * @property {object} context - free-form context, e.g. { query, theme_id }
 */

/**
 * Section 2's contract: open_in_thinking_chair(dilemma_id).
 * Thin wrapper around requestCoreEngine for callers that only have an id.
 * @param {string} dilemmaId
 * @param {object} [meta]
 */
export function openInThinkingChair(dilemmaId, meta = {}) {
  return requestCoreEngine({
    dilemma_id: dilemmaId,
    theme: meta.theme || [],
    source: meta.source || "random",
    language: meta.language || "sv",
    context: meta.context || {},
  });
}

/**
 * Section 9's contract: the full payload the Explorer can hand to the
 * Thinking Chair / Core Engine.
 * @param {CoreEngineRequest} payload
 */
export function requestCoreEngine(payload) {
  emitHouseEvent(HOUSE_EVENTS.THINKING_CHAIR_REQUESTED, payload);

  if (typeof thinkingChairHandler === "function") {
    thinkingChairHandler(payload);
    return { delivered: true };
  }
  return { delivered: false, reason: "no_handler_registered" };
}

/** Test/utility helper. */
export function resetThinkingChairHandler() {
  thinkingChairHandler = null;
}
