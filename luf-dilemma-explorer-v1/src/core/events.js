/**
 * House Engine event contract.
 *
 * The Explorer never touches illumination, animation, or the physical
 * house directly. It only emits semantic events. Work wires these into the real
 * House Engine later (see docs/EVENT_CONTRACT.md for the full payload spec).
 *
 * Two delivery channels, both carrying the same payload, so Work can pick
 * whichever fits the House Engine's existing wiring:
 *  - a DOM CustomEvent dispatched on `window` (event name prefixed "luf:")
 *  - a plain JS callback registry (`onEvent`) for non-DOM/back-end hosts
 */

export const HOUSE_EVENTS = Object.freeze({
  EXPLORER_OPENED: "dilemma_explorer_opened",
  THEME_SELECTED: "theme_selected",
  DILEMMA_DISCOVERED: "dilemma_discovered",
  DILEMMA_OPENED: "dilemma_opened",
  THINKING_CHAIR_REQUESTED: "thinking_chair_requested",
});

const listeners = new Map();

/**
 * Emit a semantic House Engine event.
 * @param {string} name - one of HOUSE_EVENTS values
 * @param {object} payload - event-specific payload, see EVENT_CONTRACT.md
 */
export function emitHouseEvent(name, payload = {}) {
  const detail = { name, payload, timestamp: new Date().toISOString() };

  if (typeof window !== "undefined" && typeof window.dispatchEvent === "function") {
    window.dispatchEvent(new CustomEvent(`luf:${name}`, { detail }));
  }

  for (const callback of listeners.get(name) || []) {
    callback(detail);
  }
  for (const callback of listeners.get("*") || []) {
    callback(detail);
  }
}

/**
 * Subscribe to a House Engine event without touching the DOM.
 * Pass "*" to receive every event. Returns an unsubscribe function.
 */
export function onHouseEvent(name, callback) {
  if (!listeners.has(name)) listeners.set(name, new Set());
  listeners.get(name).add(callback);
  return () => listeners.get(name)?.delete(callback);
}

/** Test/utility helper: drop all registered listeners. */
export function resetHouseEventListeners() {
  listeners.clear();
}
