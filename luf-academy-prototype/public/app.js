"use strict";

// LUF Academy. Min ledarskapsresa. Klient.
// Ingen extern kod. Ingen analys från tredje part. All text byggs som
// textnoder, aldrig som HTML, så att deltagarens egna ord aldrig tolkas som kod.

const state = {
  me: null,
  enrollment: null,
  journey: null,
  view: null,
};

const TZ = "Europe/Stockholm";
const fmtDate = (iso) =>
  iso ? new Intl.DateTimeFormat("sv-SE", { day: "numeric", month: "long", timeZone: TZ }).format(new Date(iso)) : "";
const fmtDay = (iso) =>
  iso
    ? new Intl.DateTimeFormat("sv-SE", { weekday: "long", day: "numeric", month: "long", timeZone: TZ }).format(new Date(iso))
    : "";
const fmtTime = (iso) =>
  iso ? new Intl.DateTimeFormat("sv-SE", { hour: "2-digit", minute: "2-digit", timeZone: TZ }).format(new Date(iso)) : "";
const fmtPlainDate = (ymd) => (ymd ? fmtDate(`${ymd}T12:00:00Z`) : "");

// ---------- DOM ----------

function h(tag, attrs, ...children) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v === false || v == null) continue;
    if (k === "class") el.className = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2).toLowerCase(), v);
    else if (k === "text") el.textContent = v;
    else if (k === "style") el.style.cssText = v;
    else el.setAttribute(k, v === true ? "" : v);
  }
  for (const c of children.flat(Infinity)) {
    if (c == null || c === false) continue;
    el.append(c instanceof Node ? c : document.createTextNode(String(c)));
  }
  return el;
}

const $app = () => document.getElementById("app");

function mount(...nodes) {
  const app = $app();
  app.replaceChildren(...nodes);
  app.focus({ preventScroll: true });
  window.scrollTo(0, 0);
}

// ---------- API ----------

async function api(method, path, body, { keepalive = false } = {}) {
  // Förhandsvisningen byter ut nätverket mot sin egen lagring. Samma svar, samma fel.
  if (window.LR_TRANSPORT) return window.LR_TRANSPORT.request(method, path, body);
  const res = await fetch(path, {
    method,
    credentials: "same-origin",
    keepalive,
    headers: body ? { "Content-Type": "application/json", "X-LUF-Academy": "1" } : { "X-LUF-Academy": "1" },
    body: body ? JSON.stringify(body) : undefined,
  });
  let data = null;
  try {
    data = await res.json();
  } catch {
    data = null;
  }
  if (!res.ok) {
    const err = new Error(data?.error || `http_${res.status}`);
    err.status = res.status;
    err.data = data;
    throw err;
  }
  return data;
}

function track(name, step = null, section = null) {
  const body = { name, step, section };
  if (state.enrollment) body.enrollmentId = state.enrollment.id;
  api("POST", "/api/events", body).catch(() => {});
}

// ---------- Autosparning ----------
//
// Varje fält sparas en kort stund efter att deltagaren slutat skriva, och
// direkt när fältet lämnas. Osparad text hålls i webbläsaren tills servern
// har bekräftat den, så att inget försvinner om nätet går ner eller fliken
// stängs. Två enheter som skriver i samma fält upptäcks via revisionsnummer.

const saver = {
  pending: new Map(),
  timers: new Map(),
  inFlight: new Set(),
  failures: 0,
  retryTimer: null,
  lastSavedAt: null,
  conflictHandlers: new Map(),
  failureReported: false,

  storageKey() {
    return state.enrollment ? `lr-osparat:${state.enrollment.id}` : null;
  },
  persist() {
    const key = this.storageKey();
    if (!key) return;
    try {
      if (this.pending.size) localStorage.setItem(key, JSON.stringify(Object.fromEntries(this.pending)));
      else localStorage.removeItem(key);
    } catch {
      // Webbläsaren tillåter inte lagring. Servern är fortfarande primär.
    }
  },
  restore() {
    const key = this.storageKey();
    if (!key) return {};
    try {
      return JSON.parse(localStorage.getItem(key) || "{}");
    } catch {
      return {};
    }
  },
  clearLocal() {
    try {
      for (const k of Object.keys(localStorage)) if (k.startsWith("lr-osparat:")) localStorage.removeItem(k);
    } catch {
      /* ignoreras */
    }
  },

  queue(key, payload, delay = 700) {
    this.pending.set(key, payload);
    this.persist();
    clearTimeout(this.timers.get(key));
    this.timers.set(key, setTimeout(() => this.flush(key), delay));
    renderSaveStatus();
  },

  async flush(key) {
    clearTimeout(this.timers.get(key));
    if (this.inFlight.has(key)) return;
    const payload = this.pending.get(key);
    if (!payload) return;
    this.inFlight.add(key);
    renderSaveStatus();
    try {
      const enr = state.enrollment.id;
      if (payload.kind === "assessment") {
        const out = await api("PUT", `/api/journey/${enr}/assessment`, {
          point: payload.point,
          dimension: payload.dimension,
          value: payload.value,
        });
        ((state.journey.assessments[payload.point] ||= {})[payload.dimension] = payload.value);
        compareBoxes.forEach((b) => (b.isConnected ? b.redraw() : compareBoxes.delete(b)));
        this.lastSavedAt = out.savedAt;
      } else {
        const known = state.journey.entries[`${payload.step}:${payload.field}`];
        const out = await api("PUT", `/api/journey/${enr}/entry`, {
          step: payload.step,
          field: payload.field,
          value: payload.value,
          baseRevision: payload.baseRevision ?? known?.revision ?? 0,
        });
        state.journey.entries[`${payload.step}:${payload.field}`] = {
          value: payload.value,
          revision: out.revision,
          updatedAt: out.savedAt,
        };
        this.lastSavedAt = out.savedAt;
      }
      if (this.pending.get(key) === payload) this.pending.delete(key);
      else {
        // Deltagaren skrev vidare medan vi sparade. Nästa sparning bygger på ny revision.
        const next = this.pending.get(key);
        if (next && next.kind !== "assessment") next.baseRevision = undefined;
      }
      this.failures = 0;
      this.failureReported = false;
      this.persist();
      refreshJourneySoon();
    } catch (err) {
      if (err.status === 409) {
        this.pending.delete(key);
        this.persist();
        this.conflictHandlers.get(key)?.(err.data, payload);
      } else if (err.status === 423) {
        this.pending.delete(key);
        this.persist();
        refreshJourney(true);
      } else if (err.status === 401) {
        this.failures += 1;
        renderSignedOut("Din inloggning har gått ut. Din text finns kvar i den här webbläsaren och sparas när du loggar in igen.");
      } else {
        this.failures += 1;
        if (!this.failureReported) {
          this.failureReported = true;
          track("autosave_failed");
        }
        const wait = [2000, 5000, 10000, 30000][Math.min(this.failures - 1, 3)];
        clearTimeout(this.retryTimer);
        this.retryTimer = setTimeout(() => this.flushAll(), wait);
      }
    } finally {
      this.inFlight.delete(key);
      renderSaveStatus();
      if (this.pending.has(key) && !this.failures) this.timers.set(key, setTimeout(() => this.flush(key), 300));
    }
  },

  flushAll() {
    return Promise.all([...this.pending.keys()].map((k) => this.flush(k)));
  },

  busy() {
    return this.pending.size > 0 || this.inFlight.size > 0;
  },
};

function renderSaveStatus() {
  const el = document.getElementById("save-status");
  if (!el) return;
  if (saver.failures > 0 && saver.pending.size) {
    // Bygg inte om felrutan vid varje nytt försök. Knappen ska stå still.
    if (el.classList.contains("is-error") && !el.classList.contains("is-notice")) return;
    el.className = "save-status is-error";
    el.replaceChildren(
      h("strong", {}, "Inte sparat ännu."),
      " Din text finns kvar här. Vi försöker igen. ",
      h("button", { type: "button", class: "link-button", onclick: () => { saver.failures = 0; saver.flushAll(); } }, "Försök nu"),
    );
    return;
  }
  el.className = "save-status";
  if (saver.busy()) {
    el.classList.add("is-saving");
    el.textContent = "Sparar";
    return;
  }
  if (saver.lastSavedAt) {
    el.classList.add("is-saved");
    el.textContent = `Sparat ${fmtTime(saver.lastSavedAt)}`;
    return;
  }
  el.textContent = "";
}

window.addEventListener("beforeunload", (e) => {
  if (saver.busy()) {
    saver.flushAll();
    e.preventDefault();
    e.returnValue = "";
  }
});
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "hidden" && saver.pending.size && state.enrollment) {
    for (const [key, p] of saver.pending) {
      if (p.kind === "assessment") continue;
      const known = state.journey.entries[`${p.step}:${p.field}`];
      api(
        "PUT",
        `/api/journey/${state.enrollment.id}/entry`,
        { step: p.step, field: p.field, value: p.value, baseRevision: p.baseRevision ?? known?.revision ?? 0 },
        { keepalive: true },
      )
        .then((out) => {
          state.journey.entries[`${p.step}:${p.field}`] = { value: p.value, revision: out.revision, updatedAt: out.savedAt };
          if (saver.pending.get(key) === p) saver.pending.delete(key);
          saver.persist();
          renderSaveStatus();
        })
        .catch(() => {});
    }
  }
});
window.addEventListener("online", () => saver.flushAll());
window.addEventListener("error", () => track("client_error"));

let refreshTimer = null;
function refreshJourneySoon() {
  clearTimeout(refreshTimer);
  refreshTimer = setTimeout(() => refreshJourney(false), 400);
}

async function refreshJourney(rerender) {
  if (!state.enrollment) return;
  try {
    const journey = await api("GET", `/api/journey/${state.enrollment.id}`);
    // Behåll lokalt osparad text framför serverns version.
    for (const [, p] of saver.pending) {
      if (p.kind === "entry") journey.entries[`${p.step}:${p.field}`] = { ...(journey.entries[`${p.step}:${p.field}`] || {}), value: p.value };
    }
    state.journey = journey;
    if (rerender) route();
    else updateRailStatus();
  } catch {
    /* nästa sparning försöker igen */
  }
}

// ---------- Hjälp för resan ----------

const program = () => state.me.program;
const step = (key) => program().steps.find((s) => s.key === key);
const stepBySlug = (slug) => program().steps.find((s) => s.slug === slug);
const weekSteps = () => program().steps.filter((s) => !s.aside);
const stepHref = (stepKey, sectionKey) => `#/${step(stepKey).slug}${sectionKey ? `/${sectionKey}` : ""}`;
const entryValue = (stepKey, path) => state.journey.entries[`${stepKey}:${path}`]?.value || "";
const statusOf = (stepKey, sectionKey) => state.journey.status[`${stepKey}:${sectionKey}`] || null;
const isLocked = (stepKey, sectionKey) => state.journey.locked[`${stepKey}:${sectionKey}`] || null;
const isOpen = (stepKey) => (state.journey.openSteps || []).includes(stepKey);
const activeShare = (stepKey, sectionKey, kind) =>
  state.journey.shares.find((s) => s.step === stepKey && s.section === sectionKey && s.kind === kind);

function nextSectionKey(stepKey) {
  const sections = step(stepKey).sections;
  const begun = sections.some((s) => ["started", "done"].includes(statusOf(stepKey, s.key)));
  if (!begun) return sections[0].key;
  const open = sections.find(
    (s) => s.doneWhen && !s.optional && statusOf(stepKey, s.key) !== "done" && !(s.kind === "return" && !actionChosen(stepKey)),
  );
  return open ? open.key : sections[sections.length - 1].key;
}

function actionChosen(stepKey) {
  return Boolean(entryValue(stepKey, "handling.prova").trim());
}
function returnSection(stepKey) {
  return step(stepKey).sections.find((s) => s.kind === "return");
}
function returnStarted(stepKey) {
  const r = returnSection(stepKey);
  return Boolean(r && r.fields.some((f) => entryValue(stepKey, `${r.key}.${f.key}`).trim()));
}
// Den senaste veckan där deltagaren bestämt sig för något men inte skrivit vad som hände.
function pendingReturn() {
  const open = weekSteps().filter((s) => isOpen(s.key) && returnSection(s.key)).reverse();
  return open.find((s) => actionChosen(s.key) && statusOf(s.key, returnSection(s.key).key) !== "done")?.key || null;
}
function weekProgress(stepKey) {
  const counted = step(stepKey).sections.filter((s) => s.doneWhen && !s.optional);
  const done = counted.filter((s) => statusOf(stepKey, s.key) === "done").length;
  return { done, total: counted.length };
}

// ---------- Router ----------

async function boot() {
  try {
    state.me = await api("GET", "/api/me");
  } catch (err) {
    if (err.status === 401) return renderSignedOut();
    return mount(
      h(
        "section",
        { class: "notice-page" },
        h("h1", {}, "Vi når inte din resa just nu."),
        h("p", {}, "Det du skrivit och inte hunnit spara finns kvar i den här webbläsaren. Det sparas när förbindelsen är tillbaka."),
        h("button", { type: "button", class: "button primary", onclick: () => location.reload() }, "Försök igen"),
      ),
    );
  }
  document.getElementById("prototype-band").hidden = !state.me.prototype;
  renderAccount();
  state.enrollment = state.me.enrollments.find((e) => e.status === "active") || state.me.enrollments[0] || null;
  if (state.enrollment) {
    state.journey = await api("GET", `/api/journey/${state.enrollment.id}`);
    await restoreUnsaved();
  }
  window.addEventListener("hashchange", route);
  route();
}

async function restoreUnsaved() {
  const stored = saver.restore();
  for (const [key, p] of Object.entries(stored)) {
    if (p.kind === "entry") {
      const current = state.journey.entries[`${p.step}:${p.field}`];
      if (current?.value === p.value) continue;
      state.journey.entries[`${p.step}:${p.field}`] = { ...(current || {}), value: p.value };
    }
    saver.pending.set(key, p);
  }
  if (saver.pending.size) {
    saver.persist();
    await saver.flushAll();
  }
}

function route() {
  const hash = location.hash.replace(/^#\/?/, "");
  const [first, second] = hash.split("/");
  if (!state.me) return;
  if (first === "admin" && state.me.roles.programAdmin) return renderAdmin();
  if (first === "jan" && state.me.roles.facilitatorCohorts.length) return renderFacilitator();
  if (!state.enrollment) {
    if (state.me.roles.programAdmin) return renderAdmin();
    if (state.me.roles.facilitatorCohorts.length) return renderFacilitator();
    return mount(
      h("section", { class: "notice-page" }, h("h1", {}, "Du är inte inskriven i någon grupp ännu."), h("p", {}, "Hör av dig till Jan om du tror att det här är fel.")),
    );
  }
  const target = first && stepBySlug(first);
  if (target && target.built && isOpen(target.key)) return renderWeek(target.key, second || nextSectionKey(target.key));
  return renderOverview();
}

function renderAccount() {
  const nav = document.getElementById("account");
  const links = [];
  if (state.me.enrollments.length) links.push(h("a", { href: "#/" }, "Min resa"));
  if (state.me.roles.facilitatorCohorts.length) links.push(h("a", { href: "#/jan" }, "Delat med mig"));
  if (state.me.roles.programAdmin) links.push(h("a", { href: "#/admin" }, "Grupper"));
  nav.replaceChildren(
    ...links,
    h("span", { class: "account-name" }, state.me.user.displayName),
    h("button", { type: "button", class: "link-button", onclick: signOut }, "Logga ut"),
  );
}

async function signOut() {
  if (saver.busy()) {
    await saver.flushAll();
    if (saver.busy()) {
      renderSaveStatus();
      notice("Din senaste text är inte sparad ännu. Vänta ett ögonblick och försök igen.");
      return;
    }
  }
  track("session_ended");
  try {
    await api("POST", "/api/logout", {});
  } catch {
    /* sessionen rensas ändå lokalt */
  }
  saver.clearLocal();
  state.me = state.enrollment = state.journey = null;
  renderSignedOut("Du är utloggad. Allt du skrivit finns kvar till nästa gång.");
}

// Ett meddelande i sidan. Webbläsarens alert() visas inte överallt.
function notice(message) {
  const el = document.getElementById("save-status");
  if (!el) return;
  el.className = "save-status is-error is-notice";
  el.textContent = message;
  setTimeout(() => renderSaveStatus(), 6000);
}

function renderSignedOut(message) {
  document.getElementById("account").replaceChildren();
  const failed = location.hash.includes("inloggning-misslyckades");
  mount(
    h(
      "section",
      { class: "signin" },
      h("p", { class: "kicker" }, "LUF Academy"),
      h("h1", {}, "Ledarskap med hjärta och mod"),
      h("p", { class: "lead" }, "Min ledarskapsresa"),
      message && h("p", { class: "signin-message" }, message),
      failed && h("p", { class: "signin-message is-warning" }, "Länken fungerade inte. Den kan ha gått ut. Be om en ny."),
      window.LR_TRANSPORT?.signIn
        ? h("button", { type: "button", class: "button primary", onclick: () => window.LR_TRANSPORT.signIn() }, window.LR_TRANSPORT.signInLabel)
        : h("p", {}, "Logga in med din personliga länk."),
    ),
  );
}

// ---------- Översikt ----------

function renderOverview() {
  const enr = state.enrollment;
  const current = step(state.journey.currentStep) || step("w1");
  const pending = pendingReturn();

  const main = h(
    "section",
    { class: "overview-hero" },
    h("p", { class: "kicker" }, program().title),
    h("h1", {}, "Min ledarskapsresa"),
    h(
      "dl",
      { class: "meta" },
      h("div", {}, h("dt", {}, "Deltagare"), h("dd", {}, state.me.user.displayName)),
      h("div", {}, h("dt", {}, "Grupp"), h("dd", {}, enr.cohort.name)),
      h("div", {}, h("dt", {}, "Start"), h("dd", {}, fmtPlainDate(enr.cohort.startDate))),
      h("div", {}, h("dt", {}, "Nu"), h("dd", {}, current.label)),
    ),
  );

  let focus;
  if (pending) {
    const ps = step(pending);
    focus = h(
      "section",
      { class: "focus-card is-recall" },
      h("p", { class: "kicker" }, `${ps.label}. Du bestämde dig för att prova`),
      h("blockquote", { class: "own-words" }, entryValue(pending, "handling.prova")),
      entryValue(pending, "handling.nar") && h("p", { class: "muted" }, `Planerat till ${fmtPlainDate(entryValue(pending, "handling.nar"))}.`),
      h("a", { class: "button primary", href: stepHref(pending, returnSection(pending).key) }, returnStarted(pending) ? "Fortsätt skriva om vad som hände" : "Berätta vad som hände"),
      h("a", { class: "button quiet", href: stepHref(current.key, nextSectionKey(current.key)) }, "Fortsätt min ledarskapsresa"),
    );
  } else {
    focus = h(
      "section",
      { class: "focus-card" },
      h("p", { class: "kicker" }, `${current.label}. ${current.title}`),
      h("h2", {}, current.subtitle),
      h("p", { class: "muted" }, state.journey.lastActivityAt ? `Senast du var här: ${fmtDate(state.journey.lastActivityAt)} ${fmtTime(state.journey.lastActivityAt)}.` : "Du har inte börjat ännu. Det tar den tid det tar."),
      h("a", { class: "button primary", href: stepHref(current.key, nextSectionKey(current.key)) }, "Fortsätt min ledarskapsresa"),
    );
  }

  const live = enr.nextLiveSession;
  const bring = state.journey.shares.filter((s) => s.kind === "bring_to_session");
  const liveCard = h(
    "section",
    { class: "card" },
    h("p", { class: "kicker" }, "Nästa träff"),
    live
      ? [
          h("h2", { class: "h3" }, `${cap(fmtDay(live.startsAt))}`),
          h("p", {}, `${fmtTime(live.startsAt)} i Teams. ${live.durationMinutes} minuter.`),
          live.teamsUrl
            ? h("a", { class: "button quiet", href: live.teamsUrl, target: "_blank", rel: "noopener noreferrer" }, "Öppna Teams")
            : h("p", { class: "muted" }, "Länken läggs in före träffen."),
          live.preparation && h("p", { class: "prep" }, live.preparation),
          bring.length
            ? h(
                "div",
                { class: "bring" },
                h("p", { class: "small-heading" }, "Det du valt att ta med"),
                h("ul", {}, bring.map((b) => h("li", {}, h("a", { href: stepHref(b.step, b.section) }, `${step(b.step).label}. ${sectionTitle(b.step, b.section)}`)))),
                h("p", { class: "muted small" }, "Bara en påminnelse för dig. Ingen annan ser den."),
              )
            : null,
        ]
      : h("p", { class: "muted" }, "Ingen träff inlagd ännu."),
  );

  const talk = step("samtal");
  const oneOnOne = enr.oneOnOnes[0];
  const talkCard =
    talk &&
    h(
      "section",
      { class: "card" },
      h("p", { class: "kicker" }, "Samtal med Jan"),
      oneOnOne?.scheduledAt && h("p", {}, `${cap(fmtDay(oneOnOne.scheduledAt))} ${fmtTime(oneOnOne.scheduledAt)}`),
      h("p", { class: "muted" }, "Förbered dig inför ett enskilt samtal, och skriv efteråt vad som blev tydligare."),
      h("a", { class: "button quiet", href: stepHref("samtal", "infor") }, "Inför samtalet"),
    );

  const goals = [1, 2, 3].map((n) => entryValue("w1", `forandring.mal_${n}`)).filter((v) => v.trim());
  const skaver = entryValue("w1", "karta.skaver_mest");
  const goalsCard =
    (goals.length > 0 || skaver) &&
    h(
      "section",
      { class: "card" },
      skaver && [h("p", { class: "kicker" }, "När du började skrev du att det här skavde mest"), h("p", { class: "own-words" }, skaver)],
      goals.length > 0 && [h("p", { class: "kicker" }, "Du ville att människorna runt dig skulle märka"), h("ol", { class: "own-list" }, goals.map((g) => h("li", {}, g)))],
    );

  const journeyList = h(
    "section",
    { class: "card journey-card", "aria-label": "Resan" },
    h("p", { class: "kicker" }, "Resan"),
    h(
      "ol",
      { class: "journey" },
      weekSteps().map((s) => {
        const open = isOpen(s.key);
        const pr = open ? weekProgress(s.key) : null;
        const label = !open ? "Öppnas senare" : pr.done ? `${pr.done} av ${pr.total} skrivna` : s.key === current.key ? "Pågår" : "Öppen";
        const inner = [h("span", { class: "journey-label" }, s.label), h("span", { class: "journey-title" }, s.title), h("span", { class: "journey-state" }, label)];
        return h(
          "li",
          { class: `journey-step ${open ? "is-open" : "is-locked"} ${s.key === current.key ? "is-current" : ""}` },
          open ? h("a", { href: stepHref(s.key, nextSectionKey(s.key)) }, inner) : h("div", { "aria-disabled": "true" }, inner),
        );
      }),
    ),
  );

  mount(
    h(
      "div",
      { class: "overview shell" },
      main,
      h("div", { class: "overview-grid" }, h("div", { class: "col" }, focus, goalsCard, journeyList), h("div", { class: "col" }, liveCard, talkCard, state.me.prototype && testModeCard())),
    ),
  );
  document.title = "Min ledarskapsresa";
}

// Testläge. Finns bara i testversionen. Flyttar dig genom resan utan att veckor behöver gå.
function testModeCard() {
  const select = h("select", { id: "test-step", "aria-label": "Flytta mig till" }, weekSteps().map((s) => h("option", { value: s.key, selected: s.key === state.journey.currentStep ? true : null }, s.label)));
  return h(
    "section",
    { class: "card test-mode" },
    h("p", { class: "kicker" }, "Testläge"),
    h("p", { class: "muted small" }, "Finns bara i testversionen. Flytta dig genom resan utan att veckor behöver gå. Det du skrivit ligger kvar."),
    h(
      "div",
      { class: "test-row" },
      select,
      h("button", {
        type: "button",
        class: "button quiet",
        onclick: async () => {
          await saver.flushAll();
          const out = await api("PUT", `/api/journey/${state.enrollment.id}/test-step`, { step: select.value });
          state.journey = out.entries ? out : await api("GET", `/api/journey/${state.enrollment.id}`);
          route();
        },
      }, "Flytta mig"),
    ),
  );
}

const cap = (s) => (s ? s[0].toUpperCase() + s.slice(1) : s);
const sectionTitle = (stepKey, sectionKey) => step(stepKey).sections.find((s) => s.key === sectionKey)?.title || sectionKey;

// ---------- Vecka ----------

function renderWeek(stepKey, sectionKey) {
  const s = step(stepKey);
  if (!s || !s.built || !isOpen(stepKey)) return renderOverview();
  const index = s.sections.findIndex((x) => x.key === sectionKey);
  if (index < 0) return renderWeek(stepKey, s.sections[0].key);
  const section = s.sections[index];
  const next = s.sections[index + 1];
  const prev = s.sections[index - 1];
  state.view = { stepKey, sectionKey };

  const rail = h(
    "nav",
    { class: "rail", "aria-label": `${s.label}. Moment` },
    h("a", { class: "rail-back", href: "#/" }, "Min ledarskapsresa"),
    h("p", { class: "rail-week" }, s.label),
    h("p", { class: "rail-title" }, s.title),
    h(
      "details",
      { class: "rail-details", open: window.matchMedia("(min-width: 900px)").matches || null },
      h("summary", {}, `Moment ${index + 1} av ${s.sections.length}. ${section.title}`),
      h(
        "ol",
        { class: "rail-list" },
        s.sections.map((sec) =>
          h(
            "li",
            {},
            h(
              "a",
              {
                href: stepHref(stepKey, sec.key),
                class: `rail-item ${sec.key === section.key ? "is-current" : ""}`,
                "aria-current": sec.key === section.key ? "step" : null,
                "data-section": sec.key,
              },
              h("span", { class: `dot ${dotClass(stepKey, sec)}`, "aria-hidden": "true" }),
              h("span", {}, sec.title),
              h("span", { class: "visually-hidden" }, dotLabel(stepKey, sec)),
            ),
          ),
        ),
      ),
    ),
  );

  const body = renderSection(stepKey, section);
  const footer = h(
    "div",
    { class: "section-nav" },
    prev ? h("a", { class: "button quiet", href: stepHref(stepKey, prev.key) }, "Tillbaka") : h("span"),
    next
      ? h("a", { class: "button primary", href: stepHref(stepKey, next.key) }, section.kind === "intro" && index === 0 ? "Börja" : `Vidare: ${next.title}`)
      : h("a", { class: "button primary", href: "#/" }, "Till min översikt"),
  );

  mount(h("div", { class: "week shell" }, rail, h("article", { class: `section section-${section.kind}`, "aria-labelledby": "section-title", "data-step": stepKey }, body, footer)));
  document.title = `${section.title}. ${s.label}`;
  if (section.kind === "return" && actionChosen(stepKey)) track("action_revisited", stepKey, section.key);
}

function dotClass(stepKey, sec) {
  const st = statusOf(stepKey, sec.key);
  return st === "done" ? "is-done" : st === "started" ? "is-started" : st === "empty" ? "is-empty" : "is-info";
}
function dotLabel(stepKey, sec) {
  const st = statusOf(stepKey, sec.key);
  return st === "done" ? "Skrivet" : st === "started" ? "Påbörjat" : st === "empty" ? "Inte påbörjat" : "";
}
function updateRailStatus() {
  const stepKey = state.view?.stepKey;
  if (!stepKey) return;
  document.querySelectorAll(".rail-item[data-section]").forEach((a) => {
    const sec = step(stepKey).sections.find((s) => s.key === a.dataset.section);
    if (!sec) return;
    a.querySelector(".dot").className = `dot ${dotClass(stepKey, sec)}`;
    a.querySelector(".visually-hidden").textContent = dotLabel(stepKey, sec);
  });
}

function sectionHead(section, stepKey) {
  return [
    h("p", { class: "kicker" }, step(stepKey).label),
    h("h1", { id: "section-title" }, section.title),
    section.lead && h("div", { class: "lead-lines" }, section.lead.map((l) => h("p", {}, l))),
    section.note && h("p", { class: "note" }, section.note),
    section.hint && h("p", { class: "book-hint" }, section.hint),
  ];
}

function sourceLine(section) {
  return section.source ? h("p", { class: "source" }, `Källa: ${section.source}`) : null;
}

function renderSection(stepKey, section) {
  switch (section.kind) {
    case "intro":
      return renderIntro(stepKey, section);
    case "reading":
      return renderReading(stepKey, section);
    case "map":
      return renderMap(stepKey, section);
    case "goals":
      return renderGrouped(stepKey, section, (n) => `Förändring ${n}`);
    case "people":
      return renderPeople(stepKey, section);
    case "situation":
      return renderSituation(stepKey, section);
    case "triangle":
      return renderTriangle(stepKey, section);
    case "action":
      return renderAction(stepKey, section);
    case "return":
      return renderReturn(stepKey, section);
    case "bridge":
      return renderBridge(stepKey, section);
    case "halfway":
      return renderHalfway(stepKey, section);
    case "lookback":
      return renderLookback(stepKey, section);
    case "closing":
      return renderClosing(stepKey, section);
    case "live":
      return renderLive(stepKey, section);
    default:
      return h("div", {}, sectionHead(section, stepKey), h("div", { class: "group-card" }, section.fields.map((f) => fieldEl(stepKey, section, f))), sourceLine(section), shareControls(stepKey, section));
  }
}

function renderIntro(stepKey, section) {
  const s = step(stepKey);
  return h(
    "div",
    { class: "intro" },
    h("p", { class: "kicker" }, `${s.label}. ${s.subtitle}`),
    h("h1", { id: "section-title" }, section.title),
    h("div", { class: "intro-lines" }, section.lead.map((l) => h("p", {}, l))),
    section.quote && h("blockquote", { class: "book-quote" }, h("p", {}, `”${section.quote.text}”`), h("footer", {}, `Ledarskap med hjärta och mod, s. ${section.quote.page}`)),
  );
}

function renderReading(stepKey, section) {
  const r = section.reading;
  const chapter = (c) => h("li", {}, h("span", { class: "chapter-title" }, c.title), h("span", { class: "chapter-pages" }, `s. ${c.pages}`), c.note && h("span", { class: "chapter-note" }, c.note));
  return h(
    "div",
    {},
    sectionHead(section, stepKey),
    h(
      "div",
      { class: "reading-card" },
      h("p", { class: "small-heading" }, "Läs"),
      h("ul", { class: "chapters" }, r.chapters.map(chapter)),
      r.note && h("p", {}, r.note),
      r.optional?.length > 0 && [h("p", { class: "small-heading" }, "Om du vill läsa mer"), h("ul", { class: "chapters is-optional" }, r.optional.map(chapter))],
      h("p", { class: "muted small" }, "Ledarskap med hjärta och mod köper du själv. Allt annat finns här. Sidorna är bokens tryckta sidor."),
    ),
  );
}

// ---------- Ledarskapskartan ----------

function renderMap(stepKey, section) {
  const point = section.measurePoint;
  const values = state.journey.assessments[point] || {};
  const locked = isLocked(stepKey, section.key);
  const rows = program().mapDimensions.map((dim) => {
    const current = values[dim.key] || 0;
    const buttons = [];
    const group = h("div", { class: "scale-dots", role: "radiogroup", "aria-label": `${dim.label}. Från ${dim.low} till ${dim.high}` });
    for (let v = 1; v <= program().mapScaleSteps; v += 1) {
      const btn = h("button", {
        type: "button",
        role: "radio",
        class: `scale-dot ${v === current ? "is-selected" : ""}`,
        "aria-checked": v === current ? "true" : "false",
        "aria-label": `${v} av ${program().mapScaleSteps}`,
        tabindex: v === (current || 1) ? "0" : "-1",
        disabled: locked ? true : null,
        "data-value": v,
      });
      btn.addEventListener("click", () => choose(v));
      btn.addEventListener("keydown", (e) => {
        const move = { ArrowRight: 1, ArrowUp: 1, ArrowLeft: -1, ArrowDown: -1 }[e.key];
        if (!move) return;
        e.preventDefault();
        const nv = Math.min(program().mapScaleSteps, Math.max(1, (Number(btn.dataset.value) || 1) + move));
        choose(nv);
        buttons[nv - 1].focus();
      });
      buttons.push(btn);
      group.append(btn);
    }
    function choose(v) {
      buttons.forEach((b, i) => {
        const on = i + 1 === v;
        b.classList.toggle("is-selected", on);
        b.setAttribute("aria-checked", on ? "true" : "false");
        b.tabIndex = on ? 0 : -1;
      });
      saver.queue(`a|${point}|${dim.key}`, { kind: "assessment", point, dimension: dim.key, value: v }, 150);
    }
    return h(
      "div",
      { class: "scale-row" },
      h("p", { class: "scale-label" }, dim.label),
      h("div", { class: "scale" }, h("span", { class: "scale-end is-low" }, dim.low), group, h("span", { class: "scale-end is-high" }, dim.high)),
    );
  });
  const after = section.fields.filter((f) => f.place === "after");
  return h(
    "div",
    {},
    sectionHead(section, stepKey),
    locked && h("p", { class: "lock-note" }, "Startpunkten är satt. Den står kvar så att du kan jämföra i slutet av utbildningen."),
    h("div", { class: "map" }, rows),
    section.compareWith ? mapComparison(section) : point === "start" && h("p", { class: "muted small" }, "Du markerar samma karta igen när utbildningen är slut och 30 dagar senare. Då ser du själv vad som har rört sig."),
    after.length > 0 && h("div", { class: "group-card after-map" }, after.map((f) => fieldEl(stepKey, section, f))),
  );
}

// Deltagarens egen bild av sin förflyttning. Samma skala. Ingen summa, inget betyg.
function mapComparison(section) {
  const points = [...section.compareWith, section.measurePoint];
  const labels = program().measurePointLabels;
  const steps = program().mapScaleSteps;
  const box = h("section", { class: "compare", "aria-label": "Din egen bild av din förflyttning" });
  const draw = () => {
    const values = (p) => state.journey.assessments[p] || {};
    box.replaceChildren(h("div", { class: "compare-inner" },
      h("p", { class: "small-heading" }, "Din egen bild av din förflyttning"),
      h("ul", { class: "compare-legend" }, points.map((p, i) => h("li", {}, h("span", { class: `marker m${i}`, "aria-hidden": "true" }), labels[p]))),
      program().mapDimensions.map((dim) =>
        h(
          "div",
          { class: "compare-row" },
          h("p", { class: "compare-label" }, dim.label),
          h(
            "div",
            { class: "compare-track", role: "img", "aria-label": `${dim.label}. ${points.map((p) => `${labels[p]}: ${values(p)[dim.key] || "ingen markering"}`).join(". ")}` },
            h("span", { class: "compare-end is-low" }, dim.low),
            h("span", { class: "compare-line" }, points.map((p, i) => values(p)[dim.key] ? h("span", { class: `marker m${i}`, style: `left: ${((values(p)[dim.key] - 1) / (steps - 1)) * 100}%` }) : null)),
            h("span", { class: "compare-end is-high" }, dim.high),
          ),
        ),
      ),
      h("p", { class: "muted small" }, "Självskattning. Det är din egen bild, inte ett resultat och inte en poäng."),
    ));
  };
  draw();
  box.redraw = draw;
  compareBoxes.add(box);
  return box;
}
const compareBoxes = new Set();

// ---------- Fält ----------

function fieldEl(stepKey, section, field, { readOnly = false } = {}) {
  const path = `${section.key}.${field.key}`;
  const key = `e|${stepKey}|${path}`;
  const id = `f-${section.key}-${field.key}`;
  const value = entryValue(stepKey, path);
  const wrap = h("div", { class: `field ${field.secondary ? "is-secondary" : ""} ${field.tone ? `tone-${field.tone}` : ""}` });
  const label = h("label", { for: id, class: "field-label" }, field.label);

  if (readOnly) {
    wrap.append(h("p", { class: "field-label" }, field.label), h("p", { class: "own-words" }, field.kind === "date" ? fmtPlainDate(value) || "Inget datum" : value || "Inget skrivet"));
    return wrap;
  }

  if (field.kind === "choice") return choiceField(stepKey, section, field, key, path, value, wrap);

  let input;
  if (field.kind === "date") {
    input = h("input", { id, type: "date", value, class: "input-date" });
  } else if (field.kind === "short") {
    input = h("input", { id, type: "text", value, maxlength: "200", placeholder: field.placeholder || null, autocomplete: "off", class: "input-short" });
  } else {
    input = h("textarea", { id, rows: String(field.rows || 3), maxlength: "8000", class: "input-text" });
    input.value = value;
  }
  const hint = h("p", { class: "field-hint", "aria-live": "polite" });
  const conflict = h("div", { class: "conflict", hidden: true });
  const onInput = () => {
    if (input.tagName === "TEXTAREA") autosize(input);
    if (section.kind === "people" && field.kind === "short") nameHint(input.value, hint);
    saver.queue(key, { kind: "entry", step: stepKey, field: path, value: input.value });
  };
  input.addEventListener("input", onInput);
  input.addEventListener("change", onInput);
  input.addEventListener("blur", () => saver.flush(key));

  saver.conflictHandlers.set(key, (server, mine) => {
    conflict.hidden = false;
    conflict.replaceChildren(
      h("p", {}, h("strong", {}, "Den här texten har ändrats på en annan enhet."), " Välj vilken version som ska gälla. Ingenting försvinner förrän du valt."),
      h("p", { class: "small-heading" }, "Sparad version"),
      h("p", { class: "own-words" }, server.value || "Tomt"),
      h(
        "div",
        { class: "conflict-actions" },
        h("button", {
          type: "button",
          class: "button primary",
          onclick: () => {
            conflict.hidden = true;
            state.journey.entries[`${stepKey}:${path}`] = { value: server.value, revision: server.revision, updatedAt: server.updatedAt };
            saver.queue(key, { kind: "entry", step: stepKey, field: path, value: mine.value, baseRevision: server.revision }, 0);
          },
        }, "Behåll min text"),
        h("button", {
          type: "button",
          class: "button quiet",
          onclick: () => {
            conflict.hidden = true;
            state.journey.entries[`${stepKey}:${path}`] = { value: server.value, revision: server.revision, updatedAt: server.updatedAt };
            input.value = server.value;
            if (input.tagName === "TEXTAREA") autosize(input);
          },
        }, "Använd den sparade"),
      ),
    );
  });

  wrap.append(...[label, field.hint ? h("p", { class: "field-guide" }, field.hint) : null, input, hint, conflict].filter(Boolean));
  if (state.journey.entries[`${stepKey}:${path}`]?.revision > 1) wrap.append(historyToggle(stepKey, path));
  if (input.tagName === "TEXTAREA") requestAnimationFrame(() => autosize(input));
  return wrap;
}

// Ett val bland fasta alternativ. Sparas direkt.
function choiceField(stepKey, section, field, key, path, value, wrap) {
  const group = h("div", { class: "choices", role: "radiogroup", "aria-label": field.label });
  const buttons = field.options.map((opt) =>
    h("button", {
      type: "button",
      role: "radio",
      class: `choice ${opt === value ? "is-on" : ""}`,
      "aria-checked": opt === value ? "true" : "false",
      onclick: () => {
        const next = opt === entryValue(stepKey, path) ? "" : opt;
        buttons.forEach((b) => {
          const on = b.textContent === next;
          b.classList.toggle("is-on", on);
          b.setAttribute("aria-checked", on ? "true" : "false");
        });
        state.journey.entries[`${stepKey}:${path}`] = { ...(state.journey.entries[`${stepKey}:${path}`] || {}), value: next };
        saver.queue(key, { kind: "entry", step: stepKey, field: path, value: next }, 100);
      },
    }, opt),
  );
  group.append(...buttons);
  wrap.append(h("p", { class: "field-label" }, field.label), group);
  return wrap;
}

function autosize(el) {
  el.style.height = "auto";
  el.style.height = `${Math.max(el.scrollHeight + 2, 0)}px`;
}

function nameHint(value, hint) {
  const looksLikeFullName = /^[A-ZÅÄÖÉ][a-zåäöé]+\s+[A-ZÅÄÖÉ][a-zåäöé]+(\s|$)/.test(value.trim());
  hint.textContent = looksLikeFullName ? "Ser ut som ett fullständigt namn. Räcker en roll eller initial?" : "";
}

function historyToggle(stepKey, path) {
  const box = h("div", { class: "history", hidden: true });
  const btn = h("button", {
    type: "button",
    class: "link-button small",
    onclick: async () => {
      if (!box.hidden) {
        box.hidden = true;
        return;
      }
      const data = await api("GET", `/api/journey/${state.enrollment.id}/history?step=${encodeURIComponent(stepKey)}&field=${encodeURIComponent(path)}`);
      box.replaceChildren(
        data.versions.length
          ? h("ol", {}, data.versions.map((v) => h("li", {}, h("p", { class: "muted small" }, `${fmtDate(v.until)} ${fmtTime(v.until)}`), h("p", { class: "own-words" }, v.value))))
          : h("p", { class: "muted small" }, "Inga tidigare versioner ännu. När du kommer tillbaka en annan dag och skriver om, sparas den gamla versionen här."),
      );
      box.hidden = false;
    },
  }, "Tidigare versioner");
  return h("div", { class: "history-wrap" }, btn, box);
}

function renderGrouped(stepKey, section, groupTitle) {
  const groups = [...new Set(section.fields.map((f) => f.group))];
  return h(
    "div",
    {},
    sectionHead(section, stepKey),
    groups.map((g) => h("fieldset", { class: "group-card" }, h("legend", { class: "visually-hidden" }, groupTitle(g)), section.fields.filter((f) => f.group === g).map((f) => fieldEl(stepKey, section, f)))),
  );
}

function renderPeople(stepKey, section) {
  const groups = [...new Set(section.fields.map((f) => f.group))];
  const filled = groups.filter((g) => section.fields.some((f) => f.group === g && entryValue(stepKey, `${section.key}.${f.key}`).trim()));
  let visible = Math.max(2, filled.length ? Math.max(...filled) : 0);
  const list = h("div", { class: "people" });
  const add = h("button", { type: "button", class: "button quiet", onclick: () => { visible += 1; draw(); } }, "Lägg till en person");
  function draw() {
    list.replaceChildren(
      ...groups.slice(0, visible).map((g) =>
        h("fieldset", { class: "group-card person" }, h("legend", { class: "small-heading" }, `Person ${g}`), section.fields.filter((f) => f.group === g).map((f) => fieldEl(stepKey, section, f))),
      ),
    );
    add.hidden = visible >= groups.length;
  }
  draw();
  return h("div", {}, sectionHead(section, stepKey), list, add);
}

function renderSituation(stepKey, section) {
  return h(
    "div",
    {},
    sectionHead(section, stepKey),
    h(
      "div",
      { class: "situation" },
      section.groups.map((g) =>
        h(
          "section",
          { class: `situation-band band-${g.key}`, "aria-labelledby": `band-${g.key}` },
          h("h2", { class: "band-title", id: `band-${g.key}` }, g.title),
          g.hint && h("p", { class: "band-hint" }, g.hint),
          section.fields.filter((f) => f.group === g.key).map((f) => fieldEl(stepKey, section, f)),
        ),
      ),
    ),
    shareControls(stepKey, section),
  );
}

function renderAction(stepKey, section) {
  // Servern är facit, men klienten vet redan om Vad hände? är påbörjat.
  const locked = isLocked(stepKey, section.key) || (section.lockedWhen === "returnStarted" && returnStarted(stepKey));
  return h(
    "div",
    {},
    sectionHead(section, stepKey),
    locked && h("p", { class: "lock-note" }, "Du har börjat skriva om vad som hände. Planen står kvar som du skrev den, så att du kan jämföra."),
    h("div", { class: "group-card" }, section.fields.map((f) => fieldEl(stepKey, section, f, { readOnly: Boolean(locked) }))),
    !locked && actionChosen(stepKey) && h("p", { class: "muted small" }, "När du har provat kommer du tillbaka och skriver vad som hände. Då ligger det här kvar."),
    shareControls(stepKey, section),
  );
}

function planRecall(stepKey, { large = true } = {}) {
  const plan = (k) => entryValue(stepKey, `handling.${k}`);
  return [
    h("blockquote", { class: `own-words ${large ? "large" : ""}` }, plan("prova")),
    plan("situation") && h("p", {}, h("span", { class: "small-heading" }, "Situation "), plan("situation")),
    plan("lagga_marke") && h("p", {}, h("span", { class: "small-heading" }, "Du ville lägga märke till "), plan("lagga_marke")),
    plan("forvantan") && h("p", {}, h("span", { class: "small-heading" }, "Du trodde att "), plan("forvantan")),
    plan("nar") && h("p", { class: "muted" }, `Planerat till ${fmtPlainDate(plan("nar"))}.`),
  ];
}

function renderReturn(stepKey, section) {
  const recall = actionChosen(stepKey)
    ? h("aside", { class: "recall" }, h("p", { class: "kicker" }, "Du bestämde dig för att prova"), planRecall(stepKey))
    : h("aside", { class: "recall is-empty" }, h("p", {}, "Du har inte valt vad du ska prova ännu."), h("a", { class: "button quiet", href: stepHref(stepKey, section.recallFrom) }, "Välj veckans handling"));
  return h(
    "div",
    {},
    h("p", { class: "kicker" }, step(stepKey).label),
    h("h1", { id: "section-title" }, section.title),
    recall,
    h("div", { class: "lead-lines" }, section.lead.map((l) => h("p", {}, l))),
    h("div", { class: "group-card" }, section.fields.map((f) => fieldEl(stepKey, section, f))),
    shareControls(stepKey, section),
  );
}

// ---------- Trianglar ----------
//
// Hörnen ritas i rubrikens läsordning: vänster, mitten (överst), höger.
// För Se · Höra · Känna blir det den fasta regeln: SE vänster, HÖRA mitten,
// KÄNNA höger. På alla skärmar. Fälten följer samma ordning.

function triangleFigure(stepKey, section) {
  const ns = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(ns, "svg");
  svg.setAttribute("viewBox", "0 0 320 190");
  svg.setAttribute("class", "triangle-figure");
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", `Triangel: ${section.corners.map((c) => c.label).join(", ")}. Från vänster till höger.`);
  const pos = [
    { x: 60, y: 150, anchor: "middle" },
    { x: 160, y: 34, anchor: "middle" },
    { x: 260, y: 150, anchor: "middle" },
  ];
  const line = document.createElementNS(ns, "polygon");
  line.setAttribute("points", pos.map((p) => `${p.x},${p.y}`).join(" "));
  line.setAttribute("class", "triangle-edge");
  svg.append(line);
  section.corners.forEach((c, i) => {
    const filled = Boolean(entryValue(stepKey, `${section.key}.${c.key}`).trim());
    const g = document.createElementNS(ns, "g");
    g.setAttribute("class", `corner ${filled ? "is-filled" : ""}`);
    g.setAttribute("data-corner", c.key);
    g.setAttribute("data-position", ["left", "middle", "right"][i]);
    const circle = document.createElementNS(ns, "circle");
    circle.setAttribute("cx", pos[i].x);
    circle.setAttribute("cy", pos[i].y);
    circle.setAttribute("r", 26);
    const text = document.createElementNS(ns, "text");
    text.setAttribute("x", pos[i].x);
    text.setAttribute("y", pos[i].y + 5);
    text.setAttribute("text-anchor", "middle");
    text.textContent = c.label.toUpperCase();
    g.append(circle, text);
    g.addEventListener("click", () => document.getElementById(`f-${section.key}-${c.key}`)?.focus());
    svg.append(g);
  });
  return svg;
}

function renderTriangle(stepKey, section) {
  const pre = section.fields.filter((f) => f.place === "pre");
  const cornerFields = section.corners.map((c) => section.fields.find((f) => f.corner === c.key));
  const post = section.fields.filter((f) => f.place === "post");
  const figure = h("figure", { class: `triangle model-${section.model}` }, triangleFigure(stepKey, section), h("figcaption", {}, section.prompt));
  const refresh = () => {
    const fresh = triangleFigure(stepKey, section);
    figure.firstChild.replaceWith(fresh);
  };
  const corners = h(
    "div",
    { class: "corner-fields" },
    cornerFields.map((f, i) => {
      const el = fieldEl(stepKey, section, f);
      el.classList.add("corner-field");
      el.dataset.position = ["left", "middle", "right"][i];
      el.addEventListener("input", () => setTimeout(refresh, 50));
      return el;
    }),
  );
  return h(
    "div",
    {},
    sectionHead(section, stepKey),
    pre.length > 0 && h("div", { class: "group-card" }, pre.map((f) => fieldEl(stepKey, section, f))),
    figure,
    corners,
    post.length > 0 && h("div", { class: "group-card" }, post.map((f) => fieldEl(stepKey, section, f))),
    sourceLine(section),
    shareControls(stepKey, section),
  );
}

// ---------- Resan kommer ihåg ----------

function renderBridge(stepKey, section) {
  const from = step(section.fromStep);
  const ret = returnSection(from.key);
  const what = (k) => entryValue(from.key, `${ret.key}.${k}`);
  const happened = what("hande") || what("gjorde_faktiskt");
  const learned = what("larde") || what("upptackte");
  return h(
    "div",
    {},
    h("p", { class: "kicker" }, step(stepKey).label),
    h("h1", { id: "section-title" }, "Innan vi går vidare"),
    actionChosen(from.key)
      ? h(
          "aside",
          { class: "recall" },
          h("p", { class: "kicker" }, `${from.label}. Du bestämde dig för att prova`),
          planRecall(from.key, { large: false }),
          happened
            ? [h("p", { class: "small-heading" }, "Efteråt skrev du att det här hände"), h("p", { class: "own-words" }, happened), learned && [h("p", { class: "small-heading" }, "Och det här lärde du dig"), h("p", { class: "own-words" }, learned)]]
            : [h("p", {}, "Du har inte skrivit vad som hände ännu. Gör det först. Det är där lärandet sitter."), h("a", { class: "button primary", href: stepHref(from.key, ret.key) }, "Berätta vad som hände")],
        )
      : h("aside", { class: "recall is-empty" }, h("p", {}, `Du valde ingen handling i ${from.label.toLowerCase()}. Det går att gå tillbaka.`), h("a", { class: "button quiet", href: stepHref(from.key, "handling") }, `Till ${from.label.toLowerCase()}`)),
    h("div", { class: "lead-lines" }, h("p", {}, "Vi börjar med vad du gjorde och vad som hände. Inte med vad du tänkte göra.")),
  );
}

function goalsRecall() {
  const goals = [1, 2, 3].map((n) => ({ g: entryValue("w1", `forandring.mal_${n}`), m: entryValue("w1", `forandring.mal_${n}_marks`) })).filter((x) => x.g.trim());
  if (!goals.length) return h("p", { class: "muted" }, "Du skrev inga förändringsmål i vecka 1. Du kan göra det nu.");
  return h("ol", { class: "own-list" }, goals.map((x) => h("li", {}, x.g, x.m && h("span", { class: "muted small block" }, `Du skulle märka det på: ${x.m}`))));
}

function renderHalfway(stepKey, section) {
  return h(
    "div",
    {},
    sectionHead(section, stepKey),
    h("aside", { class: "recall" }, h("p", { class: "kicker" }, "När du började ville du att människorna runt dig skulle märka"), goalsRecall()),
    h("div", { class: "group-card" }, section.fields.map((f) => fieldEl(stepKey, section, f))),
    sourceLine(section),
  );
}

function startRecall() {
  const items = [
    ["Varför du var här", entryValue("w1", "karta.varfor_har")],
    ["Det som skavde mest", entryValue("w1", "karta.skaver_mest")],
  ].filter(([, v]) => v.trim());
  return items.map(([k, v]) => [h("p", { class: "small-heading" }, k), h("p", { class: "own-words" }, v)]);
}

function actionsRecall() {
  const weeks = weekSteps().filter((s) => returnSection(s.key) && actionChosen(s.key));
  if (!weeks.length) return null;
  return h(
    "ol",
    { class: "timeline" },
    weeks.map((s) => {
      const ret = returnSection(s.key);
      const happened = entryValue(s.key, `${ret.key}.hande`);
      return h(
        "li",
        {},
        h("p", { class: "small-heading" }, s.label),
        h("p", { class: "own-words" }, entryValue(s.key, "handling.prova")),
        happened ? h("p", { class: "muted" }, `Det här hände: ${happened}`) : h("p", { class: "muted" }, "Vad som hände är inte skrivet."),
      );
    }),
  );
}

function renderLookback(stepKey, section) {
  const isD30 = stepKey === "d30";
  const direction = [1, 2, 3].map((n) => ({ f: entryValue("w6", `avslut.fortsatta_${n}`), u: entryValue("w6", `avslut.folja_upp_${n}`) })).filter((x) => x.f.trim());
  const promise = entryValue("w6", "avslut.lofte");
  return h(
    "div",
    {},
    sectionHead(section, stepKey),
    h(
      "aside",
      { class: "recall lookback" },
      h("p", { class: "kicker" }, "Det här var ditt startläge"),
      startRecall(),
      h("p", { class: "small-heading" }, "Det här ville du förändra"),
      goalsRecall(),
      !isD30 && [h("p", { class: "small-heading" }, "Det här provade du, och det här hände"), actionsRecall() || h("p", { class: "muted" }, "Inga handlingar skrivna ännu.")],
      isD30 && direction.length > 0 && [h("p", { class: "small-heading" }, "Din riktning efter sex veckor"), h("ol", { class: "own-list" }, direction.map((x) => h("li", {}, x.f, x.u && h("span", { class: "muted small block" }, `Uppföljning: ${x.u}`))))],
      isD30 && promise && [h("p", { class: "small-heading" }, "Du lovade dig själv att"), h("p", { class: "own-words" }, promise)],
    ),
    isD30 && mapComparison({ compareWith: ["start"], measurePoint: "end" }),
    section.fields.length > 0 && h("div", { class: "group-card" }, section.fields.map((f) => fieldEl(stepKey, section, f))),
    sourceLine(section),
  );
}

function renderClosing(stepKey, section) {
  const groups = [...new Set(section.fields.filter((f) => f.group).map((f) => f.group))];
  const single = section.fields.filter((f) => !f.group);
  return h(
    "div",
    {},
    sectionHead(section, stepKey),
    h("div", { class: "group-card" }, single.filter((f) => f.key !== "lofte").map((f) => fieldEl(stepKey, section, f))),
    h("p", { class: "small-heading" }, "Min riktning framåt"),
    groups.map((g) => h("fieldset", { class: "group-card" }, h("legend", { class: "visually-hidden" }, `Riktning ${g}`), section.fields.filter((f) => f.group === g).map((f) => fieldEl(stepKey, section, f)))),
    h("div", { class: "group-card promise" }, single.filter((f) => f.key === "lofte").map((f) => fieldEl(stepKey, section, f))),
    state.me.prototype && program().diploma && h("aside", { class: "internal" }, h("p", { class: "internal-badge" }, program().diploma.status), h("p", {}, program().diploma.note), h("p", { class: "muted small" }, "Internt. Visas bara i testversionen.")),
    sourceLine(section),
    shareControls(stepKey, section),
  );
}

function renderLive(stepKey, section) {
  const ls = program().liveSupport;
  return h(
    "div",
    {},
    sectionHead(section, stepKey),
    h(
      "div",
      { class: "live-support" },
      h("section", { class: "live-block" }, h("p", { class: "small-heading" }, "Medtränarens fem regler"), h("ol", { class: "rules" }, ls.coachRules.map(([a, b]) => h("li", {}, h("strong", {}, a), " ", b)))),
      h("section", { class: "live-block" }, h("p", { class: "small-heading" }, "Under träffen, när du är medtränare"), h("ul", { class: "rules" }, ls.coachQuestions.map((q) => h("li", {}, q))), h("p", { class: "muted small" }, "Ha frågorna i huvudet. De sparas inte här.")),
      h("section", { class: "live-block" }, h("p", { class: "small-heading" }, "Vårt gemensamma rum"), h("ul", { class: "rules" }, ls.roomRules.map((r) => h("li", {}, r)))),
    ),
    h("div", { class: "group-card" }, section.fields.map((f) => fieldEl(stepKey, section, f))),
    sourceLine(section),
  );
}

// ---------- Delning ----------

function shareControls(stepKey, section) {
  if (!section.shareable) return null;
  const bring = activeShare(stepKey, section.key, "bring_to_session");
  const jan = activeShare(stepKey, section.key, "share_with_facilitator");
  return h(
    "section",
    { class: "share", "aria-label": "Delning" },
    h("p", { class: "small-heading" }, "Privat som standard"),
    h("p", { class: "muted small" }, "Det du skriver här är ditt. Ingen annan ser det om du inte själv väljer att dela."),
    h(
      "div",
      { class: "share-row" },
      h("button", {
        type: "button",
        class: `toggle ${bring ? "is-on" : ""}`,
        "aria-pressed": bring ? "true" : "false",
        onclick: () => setShare(stepKey, section, "bring_to_session", !bring),
      }, bring ? "Markerat: ta med till nästa träff" : "Ta med till nästa träff"),
      h("p", { class: "muted small" }, "En påminnelse bara för dig. Ingenting delas med gruppen."),
    ),
    h(
      "div",
      { class: "share-row" },
      jan
        ? [
            h("p", { class: "shared-state" }, `Delat med Jan sedan ${fmtDate(jan.since)}.`),
            h("button", { type: "button", class: "button quiet", onclick: () => setShare(stepKey, section, "share_with_facilitator", false) }, "Ta tillbaka delningen"),
          ]
        : h("button", { type: "button", class: "toggle", "aria-pressed": "false", onclick: () => confirmShare(stepKey, section) }, "Dela med Jan"),
    ),
  );
}

function confirmShare(stepKey, section) {
  const dialog = document.getElementById("share-dialog");
  dialog.replaceChildren(
    h(
      "form",
      { method: "dialog", class: "dialog-body" },
      h("h2", {}, "Dela med Jan"),
      h("p", {}, `Jan kommer att kunna läsa det du skrivit under ${section.title}:`),
      h("ul", {}, section.fields.map((f) => h("li", {}, f.label))),
      h("p", {}, "Inget annat från din resa. Ingen annan i gruppen. Om du ändrar texten ser Jan den nya versionen. Du kan ta tillbaka delningen när du vill."),
      h(
        "div",
        { class: "dialog-actions" },
        h("button", { value: "cancel", class: "button quiet" }, "Avbryt"),
        h("button", { value: "share", class: "button primary" }, "Dela med Jan"),
      ),
    ),
  );
  dialog.onclose = () => {
    if (dialog.returnValue === "share") setShare(stepKey, section, "share_with_facilitator", true);
  };
  dialog.showModal();
}

async function setShare(stepKey, section, kind, active) {
  await saver.flushAll();
  try {
    const out = await api("PUT", `/api/journey/${state.enrollment.id}/share`, { step: stepKey, section: section.key, kind, active });
    state.journey.shares = out.shares;
    route();
  } catch {
    notice("Det gick inte att ändra delningen just nu. Ingenting har delats. Försök igen.");
  }
}

// ---------- Jan som handledare ----------

async function renderFacilitator() {
  mount(h("p", { class: "loading" }, "Hämtar."));
  const data = await api("GET", "/api/facilitator/shared");
  mount(
    h(
      "div",
      { class: "shell role-view" },
      h("p", { class: "kicker" }, "Handledare"),
      h("h1", {}, "Delat med mig"),
      h("p", { class: "note" }, "Här syns bara det som en deltagare själv har valt att dela med dig. Allt annat är privat och syns inte här."),
      data.cohorts.map((c) =>
        h(
          "section",
          { class: "card" },
          h("h2", { class: "h3" }, `${c.name}. Start ${fmtPlainDate(c.startDate)}`),
          c.participants.map((p) =>
            h(
              "div",
              { class: "participant" },
              h("p", { class: "small-heading" }, p.name),
              p.shared.length
                ? p.shared.map((s) =>
                    h("div", { class: "shared-block" }, h("p", { class: "shared-title" }, `${s.title}. Delat ${fmtDate(s.since)}`), s.fields.filter((f) => f.value).map((f) => h("div", { class: "shared-field" }, h("p", { class: "field-label" }, f.label), h("p", { class: "own-words" }, f.value)))),
                  )
                : h("p", { class: "muted small" }, "Inget delat."),
            ),
          ),
        ),
      ),
    ),
  );
  document.title = "Delat med mig";
}

// ---------- Programadministration ----------

async function renderAdmin() {
  mount(h("p", { class: "loading" }, "Hämtar."));
  const data = await api("GET", "/api/admin/overview");
  const stepLabel = (k) => program().steps.find((s) => s.key === k)?.label || k;
  mount(
    h(
      "div",
      { class: "shell role-view" },
      h("p", { class: "kicker" }, "Programadministration"),
      h("h1", {}, "Grupper"),
      h("p", { class: "note" }, "Du ser grupper, datum, länkar och status. Deltagarnas egna texter syns inte här. Det är avsiktligt."),
      data.cohorts.map((c) => {
        const active = c.participants.filter((p) => ["active", "paused"].includes(p.status)).length;
        return h(
          "section",
          { class: "card" },
          h("h2", { class: "h3" }, c.name),
          h("p", { class: "muted" }, `${fmtPlainDate(c.startDate)} till ${fmtPlainDate(c.endDate)}. ${active} av ${c.maxParticipants} platser. Nu: ${stepLabel(c.currentStep)}.`),
          h(
            "table",
            { class: "table" },
            h("thead", {}, h("tr", {}, h("th", {}, "Deltagare"), h("th", {}, "Status"), h("th", {}, "Senast aktiv"), h("th", {}, "Påbörjat"))),
            h(
              "tbody",
              {},
              c.participants.map((p) =>
                h("tr", {}, h("td", {}, p.name), h("td", {}, p.status), h("td", {}, p.lastActivityAt ? `${fmtDate(p.lastActivityAt)} ${fmtTime(p.lastActivityAt)}` : "Inte ännu"), h("td", {}, p.startedSteps.map(stepLabel).join(", ") || "Inget")),
              ),
            ),
          ),
          h("p", { class: "small-heading" }, "Träffar"),
          c.liveSessions.map((s) => liveSessionEditor(s, stepLabel)),
        );
      }),
    ),
  );
  document.title = "Grupper";
}

function liveSessionEditor(s, stepLabel) {
  const url = h("input", { type: "url", value: s.teamsUrl, placeholder: "https://teams.microsoft.com/...", "aria-label": `Teamslänk ${stepLabel(s.step)}` });
  const msg = h("span", { class: "muted small", role: "status" });
  return h(
    "div",
    { class: "session-row" },
    h("span", { class: "session-when" }, `${stepLabel(s.step)}. ${cap(fmtDay(s.startsAt))} ${fmtTime(s.startsAt)}`),
    url,
    h("button", {
      type: "button",
      class: "button quiet",
      onclick: async () => {
        try {
          await api("PUT", `/api/admin/live-sessions/${s.id}`, { teamsUrl: url.value.trim() });
          msg.textContent = "Sparat.";
        } catch {
          msg.textContent = "Länken måste börja med https://";
        }
      },
    }, "Spara länk"),
    msg,
  );
}

document.addEventListener("DOMContentLoaded", boot);
