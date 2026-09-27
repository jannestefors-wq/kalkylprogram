import { FIELDS, TALKS, BOOK } from "./content-v3.mjs";
import { MIRROR_FIXTURES, FIXTURE_ID } from "../preview/testdata-v3.mjs";
export class V3Error extends Error {
  constructor(status, message) { super(message); this.status = status; }
}
const fail = (message, status = 400) => { throw new V3Error(status, message); };
const text = (value, max = 8000) => {
  if (typeof value !== "string" || value.length > max) fail("Ogiltig text.");
  return value.trim();
};
const required = (value, label) => { const s = text(value); if (!s) fail(label); return s; };
const key = value => {
  if (typeof value !== "string" || !/^[a-zA-Z0-9_-]{1,80}$/.test(value)) fail("Ogiltig nyckel.");
  return value;
};
function fields(kind, data) {
  if (!data || typeof data !== "object" || Array.isArray(data)) fail("Ogiltiga fält.");
  const allowed = FIELDS[kind]?.map(x => x[0]);
  if (!allowed || Object.keys(data).some(k => !allowed.includes(k))) fail("Okänt fält.");
  return Object.fromEntries(allowed.map(k => [k, text(data[k] ?? "")]));
}
export function initialState() {
  return { fixture: FIXTURE_ID, day: -7, focus: [], actions: [], notes: {}, drafts: {}, shares: [], reviews: [], coreEnd: null, recommendations: [], mirrors: [] };
}
export const currentFocus = s => s.focus.find(x => x.active) || null;
export function material(s, target) {
  const [kind, id] = target.split(":");
  if (kind === "focus") return s.focus.find(x => x.id === id) || null;
  if (kind === "action") return s.actions.find(x => x.id === id) || null;
  if (kind === "mirror") return s.mirrors.find(x => x.id === id) || null;
  if (kind === "note" && s.notes[id]?.kind !== "cotrainer") return s.notes[id] || null;
  return null;
}
export function reduceState(previous, event) {
  if (previous.fixture !== FIXTURE_ID) fail("Endast syntetisk Human Test.", 403);
  const s = structuredClone(previous);
  if (!event || typeof event !== "object") fail("Ogiltig ändring.");
  const d = event.data;
  switch (event.type) {
    case "draft": {
      const id = key(event.id);
      if (!Object.hasOwn(FIELDS, event.kind)) fail("Okänd arbetsyta.");
      s.drafts[id] = { kind: event.kind, data: fields(event.kind, d) };
      break;
    }
    case "focus": {
      const value = fields("focus", d);
      required(value.title, "Skriv ditt primära fokus.");
      const active = currentFocus(s);
      if (active) required(value.reason, "Vad gör att du byter fokus?");
      if (s.focus.some(x => x.id === event.id)) fail("Fokus finns redan.", 409);
      s.focus.forEach(x => { x.active = false; });
      s.focus.push({ id: key(event.id), ...value, active: true, day: s.day });
      delete s.drafts.focus;
      break;
    }
    case "keep": {
      if (!currentFocus(s)) fail("Välj ett fokus först.");
      s.reviews.push({ focusId: currentFocus(s).id, reason: text(d.reason), day: s.day });
      delete s.drafts["keep-focus"];
      break;
    }
    case "action": {
      const focus = currentFocus(s);
      if (!focus) fail("Välj ditt primära fokus först.");
      const value = fields("action", d);
      required(value.what, "Vad vill du prova?");
      required(value.situation, "I vilken verklig situation?");
      required(value.when, "När vill du prova?");
      if (s.actions.some(x => x.id === event.id)) fail("Handlingen finns redan.", 409);
      s.actions.push({ id: key(event.id), focusId: focus.id, ...value, day: s.day, outcome: null });
      delete s.drafts.action;
      break;
    }
    case "outcome": {
      const action = s.actions.find(x => x.id === event.id);
      if (!action) fail("Handlingen finns inte.", 404);
      const value = fields("outcome", d);
      if (!["Ja", "Delvis", "Nej"].includes(value.result)) fail("Välj Ja, Delvis eller Nej.");
      if (value.result === "Nej") {
        required(value.blocked, "Vad stoppade dig?");
        value.happened = ""; value.evidence = "";
      } else { value.blocked = ""; }
      action.outcome = { ...value, day: s.day };
      delete s.drafts["outcome-" + event.id];
      break;
    }
    case "note": {
      const id = key(event.id);
      if (!["reflection", "talk", "d30", "three", "summary", "cotrainer"].includes(event.kind)) fail("Okänd anteckning.");
      if (event.kind === "talk" && !TALKS.some(t => id === "talk-" + t.id)) fail("Okänt samtal.");
      if (event.kind === "d30" && s.day < 72) fail("30 dagar öppnas efter kärnresan.");
      if (event.kind === "three" && s.day < 134) fail("Tre månader öppnas efter kärnresan.");
      if (id === "talk-three" && s.day < 134) fail("Tre månader öppnas efter kärnresan.");
      if (s.notes[id] && s.notes[id].kind !== event.kind) fail("Anteckningstypen får inte ändras.");
      s.notes[id] = { id, kind: event.kind, data: fields(event.kind, d), day: s.day };
      break;
    }
    case "mirror": {
      if (![1,2].includes(event.round)) fail("Okänd Spegel.");
      if (event.round === 2 && s.day < 134) fail("Spegeln 2 hör till tremånadersuppföljningen.");
      // Klienten får inte leverera svar eller relationsdata.
      if (d !== undefined) fail("Spegeln tar endast fasta syntetiska svar.");
      const fixtures = MIRROR_FIXTURES.filter(x => x.round === event.round);
      for (const item of fixtures) if (!s.mirrors.some(x => x.id === item.id)) s.mirrors.push(structuredClone(item));
      break;
    }
    case "share": {
      if (typeof event.target !== "string" || !material(s, event.target)) fail("Materialet kan inte delas.");
      if (typeof event.enabled !== "boolean") fail("Välj dela eller återkalla.");
      s.shares = s.shares.filter(x => x !== event.target);
      if (event.enabled) s.shares.push(event.target);
      break;
    }
    case "clock": {
      if (![-7,0,21,42,72,134].includes(event.day)) fail("Okänd testtid.");
      if (event.day >= 42 && !s.coreEnd) {
        s.coreEnd = { focus: structuredClone(currentFocus(s)), action: structuredClone(s.actions.at(-1) || null), next: s.notes["talk-end"]?.data.next || s.actions.at(-1)?.outcome?.next || "" };
      }
      s.day = event.day;
      break;
    }
    default: fail("Ändringen stöds inte.");
  }
  return s;
}
export function recommend(s, title) {
  if (!BOOK.optional.some(x => x.title === title)) fail("Bokhänvisningen är inte verifierad.");
  const next = structuredClone(s);
  if (!next.recommendations.includes(title)) next.recommendations.push(title);
  return next;
}
export function projectState(s, role) {
  if (role === "participant") return structuredClone(s);
  if (role === "program_admin") return {
    mirrors: [1,2].map(round => ({ round, started: s.mirrors.some(x => x.round === round), count: s.mirrors.filter(x => x.round === round).length, ready: s.mirrors.filter(x => x.round === round).length === 4 }))
  };
  if (role === "facilitator") return {
    shared: s.shares.map(target => ({ target, value: material(s, target) })).filter(x => x.value),
    recommendations: s.recommendations
  };
  fail("Ingen åtkomst.", 403);
}
