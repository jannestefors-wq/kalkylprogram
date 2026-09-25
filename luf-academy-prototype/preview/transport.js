"use strict";

// Förhandsvisning för Human Test. Samma arbetsyta som prototypen, men i
// stället för Node-servern lagras allt i sidans egen claude.ai-databas.
//
// Datagränser (upprätthålls av plattformen, inte av den här koden):
//   data/users/<id>/...   deltagarens privata resa. Ingen annan kan läsa den,
//                         inte ens sidans ägare.
//   shared/<id>/items/..  avsnitt deltagaren aktivt delat. Läses bara av
//                         sidans ägare (testrollen handledare) och deltagaren själv.
//   roster/<id>           status utan fritext. Läses bara av ägaren.
//   requests/<id>         förfrågan om samtal: bara att deltagaren vill boka
//                         ett samtal och när. Ingen text. Läses bara av ägaren
//                         (testrollen Jan) och deltagaren själv.
//   testdata/cohort       testgruppen. Alla läser, bara ägaren skriver.
//
// Version 2: den privata vägledningen efter två Nej i rad räknas fram ur
// deltagarens egna svar i webbläsaren. Deltagarens svar på rutan ligger i den
// privata resan. Att rutan visas sparas aldrig.
//
// Ingen analys. Inga anrop lämnar sidan.

(function () {
  const PROGRAM = window.LR_PROGRAM;
  // Samma regler som servern använder (server/rules.mjs), inlagda av byggsteget.
  const R = window.LR_RULES;
  const STEPS = PROGRAM.steps;
  const DIMS = PROGRAM.mapDimensions;
  const ENROLLMENT_ID = "min-resa";
  const SESSION_KEY = "lr-preview-inloggad";
  const GAP_MS = 30 * 60 * 1000;
  const MAX_HISTORY = 30;

  const httpError = (status, code, extra = {}) => {
    const e = new Error(code);
    e.status = status;
    e.data = { error: code, ...extra };
    return e;
  };

  let ready = null;
  function connect() {
    ready ||= (async () => {
      const claude = window.claude;
      const db = claude ? await claude.use("db") : null;
      const user = claude ? await claude.use("user") : null;
      const uid = user ? await user.id() : null;
      const isOwner = user ? await user.isOwner() : false;
      return { db, user, uid, isOwner };
    })();
    return ready;
  }

  function signedIn() {
    try {
      return localStorage.getItem(SESSION_KEY) === "1";
    } catch {
      return true;
    }
  }
  function setSignedIn(on) {
    try {
      if (on) localStorage.setItem(SESSION_KEY, "1");
      else localStorage.removeItem(SESSION_KEY);
    } catch {
      /* utan lagring är man inloggad så länge sidan är öppen */
    }
  }

  const step = (key) => PROGRAM.steps.find((s) => s.key === key) || null;
  const section = (stepKey, sectionKey) => step(stepKey)?.sections.find((s) => s.key === sectionKey) || null;
  function findField(stepKey, path) {
    const [sectionKey, fieldKey] = String(path).split(".");
    const sec = section(stepKey, sectionKey);
    const field = sec?.fields.find((f) => f.key === fieldKey && f.kind !== "info");
    return field ? { section: sec, field } : null;
  }

  const entryDocId = (stepKey, path) => `e:${stepKey}:${path}`;
  const shareDocId = (stepKey, sectionKey) => `${stepKey}~${sectionKey}`;

  async function ctx() {
    const c = await connect();
    if (!c.db || !c.uid) throw httpError(503, "preview_unavailable");
    if (!signedIn()) throw httpError(401, "not_signed_in");
    return c;
  }
  const own = (c) => c.db.collection(`data/users/${c.uid}`);

  async function cohort(c) {
    const snap = await c.db.doc("testdata/cohort").get();
    if (!snap.exists) throw httpError(503, "test_cohort_missing");
    return snap.data();
  }

  async function loadOwn(c) {
    const snap = await own(c).get();
    const entries = {};
    let assessments = {};
    let shares = [];
    let profile = null;
    let support = { handled: [], talkRequestedAt: null };
    for (const d of snap.docs) {
      const body = d.data();
      if (d.id.startsWith("e:")) {
        const [, stepKey, ...rest] = d.id.split(":");
        entries[`${stepKey}:${rest.join(":")}`] = body;
      } else if (d.id === "assessments") assessments = body.points || {};
      else if (d.id === "shares") shares = body.items || [];
      else if (d.id === "profile") profile = body;
      else if (d.id === "support") support = { handled: body.handled || [], talkRequestedAt: body.talkRequestedAt || null };
    }
    return { entries, assessments, shares, profile, support };
  }

  // Steget testpersonen står i. Testläget lagras i personens egen profil.
  const currentStepOf = (co, data) => data.profile?.testStep || co.currentStep;
  const lockedFor = (co, data) => R.lockedSections(STEPS, currentStepOf(co, data), data.entries);

  async function touch(c, data) {
    const now = new Date().toISOString();
    // Bara veckorna. Startsamtalet och Samtal med Jan syns aldrig för administratören.
    const startedSteps = STEPS.filter((s) => s.built && !s.aside && R.anyInStep(s.key, data.entries, data.assessments, STEPS)).map((s) => s.key);
    const started = startedSteps.join(",");
    const last = data.profile?.lastActivityAt ? Date.parse(data.profile.lastActivityAt) : 0;
    // Senast aktiv behöver inte vara exakt på sekunden. Skriv högst var femte minut.
    if (data.profile && Date.now() - last < 5 * 60 * 1000 && data.profile.started === started) return;
    data.profile = { ...(data.profile || { enrolledAt: now }), lastActivityAt: now, started };
    await own(c).doc("profile").set(data.profile);
    // Status utan fritext, för testrollen programadministratör.
    await c.db.doc(`roster/${c.uid}`).set({ lastActivityAt: now, startedSteps });
  }

  // Delat avsnitt hålls levande: Jan ser texten som den är nu.
  async function syncShared(c, data, stepKey, sectionKey) {
    const active = data.shares.some((s) => s.step === stepKey && s.section === sectionKey && s.kind === "share_with_facilitator");
    const ref = c.db.doc(`shared/${c.uid}/items/${shareDocId(stepKey, sectionKey)}`);
    if (!active) return ref.delete();
    const sec = section(stepKey, sectionKey);
    const since = data.shares.find((s) => s.step === stepKey && s.section === sectionKey && s.kind === "share_with_facilitator").since;
    // Samma som servern: bara synliga fält, området som nummer.
    return ref.set({
      step: stepKey,
      section: sectionKey,
      title: sec.title,
      since,
      fields: R.visibleFields(stepKey, sec, data.entries).map((f) => {
        const raw = data.entries[`${stepKey}:${sec.key}.${f.key}`]?.value || "";
        let value = raw;
        if (f.kind === "area" && raw) value = raw === "nytt" ? f.newLabel : `Förändringsområde ${raw}`;
        if (f.kind === "check") value = raw === "ja" ? "Ja" : "";
        return { label: f.label, value };
      }),
    });
  }

  // ---------- Handlers ----------

  async function me() {
    const c = await ctx();
    const co = await cohort(c);
    const data = await loadOwn(c);
    const now = new Date().toISOString();
    const next = (co.liveSessions || []).find((s) => new Date(Date.parse(s.startsAt) + s.durationMinutes * 60000).toISOString() > now) || null;
    return {
      user: { id: c.uid, displayName: "Testdeltagare", email: "" },
      roles: { programAdmin: c.isOwner, facilitatorCohorts: c.isOwner ? [co.id] : [] },
      prototype: true,
      program: PROGRAM,
      enrollments: [
        {
          id: ENROLLMENT_ID,
          status: "active",
          lastActivityAt: data.profile?.lastActivityAt || null,
          cohort: { id: co.id, name: co.name, startDate: co.startDate, endDate: co.endDate, currentStep: currentStepOf(co, data), groupStep: co.currentStep, status: co.status },
          nextLiveSession: next,
          reunion: (co.liveSessions || []).find((s) => s.step === "d30") || null,
          oneOnOnes: [],
        },
      ],
    };
  }

  async function journey(c, data, co) {
    data ||= await loadOwn(c);
    co ||= await cohort(c);
    const current = currentStepOf(co, data);
    return {
      enrollmentId: ENROLLMENT_ID,
      currentStep: current,
      openSteps: R.openStepKeys(STEPS, current),
      entries: Object.fromEntries(Object.entries(data.entries).map(([k, e]) => [k, { value: e.value, revision: e.revision, updatedAt: e.updatedAt }])),
      assessments: data.assessments,
      shares: data.shares,
      locked: lockedFor(co, data),
      status: R.allStatuses(STEPS, data.entries, data.assessments, DIMS),
      support: supportState(data),
      lastActivityAt: data.profile?.lastActivityAt || null,
    };
  }

  function supportState(data) {
    return {
      promptFor: R.supportPromptFor(STEPS, data.entries, data.support.handled),
      talkRequestedAt: data.support.talkRequestedAt,
    };
  }

  // Förfrågan om samtal. Bara tidpunkten skrivs där Jan kan läsa den.
  async function requestTalk(c, data, now) {
    const last = data.support.talkRequestedAt;
    if (last && Date.parse(now) - Date.parse(last) < 24 * 3600 * 1000) return;
    data.support.talkRequestedAt = now;
    await c.db.doc(`requests/${c.uid}`).set({ requestedAt: now });
  }

  async function putTalkRequest(body) {
    const c = await ctx();
    if (Object.keys(body || {}).length) throw httpError(400, "unknown_key");
    const data = await loadOwn(c);
    await requestTalk(c, data, new Date().toISOString());
    await own(c).doc("support").set(data.support);
    return { support: supportState(data) };
  }

  async function putSupport(body) {
    const c = await ctx();
    const { action, step: streakStep, ...rest } = body || {};
    if (Object.keys(rest).length) throw httpError(400, "unknown_key");
    if (!["not_now", "request"].includes(action)) throw httpError(400, "unknown_action");
    const data = await loadOwn(c);
    const current = supportState(data).promptFor;
    if (!current || current !== streakStep) throw httpError(409, "no_prompt");
    data.support.handled = [...new Set([...data.support.handled, streakStep])];
    if (action === "request") await requestTalk(c, data, new Date().toISOString());
    await own(c).doc("support").set(data.support);
    return { support: supportState(data) };
  }

  function assertOwn(enrollmentId) {
    if (enrollmentId !== ENROLLMENT_ID) throw httpError(404, "not_found");
  }

  async function putEntry(body) {
    const c = await ctx();
    const { step: stepKey, field: path, value, baseRevision } = body || {};
    const st = step(stepKey);
    if (!st) throw httpError(400, "unknown_step");
    const found = findField(stepKey, path);
    if (!found) throw httpError(400, "unknown_field");
    const invalid = R.validateValue(found.field, value);
    if (invalid) throw httpError(invalid === "too_long" ? 413 : 400, invalid);

    const co = await cohort(c);
    const data = await loadOwn(c);
    if (!R.isStepOpen(STEPS, stepKey, currentStepOf(co, data))) throw httpError(403, "step_not_open");
    if (lockedFor(co, data)[`${stepKey}:${found.section.key}`]) throw httpError(423, "locked");

    const key = `${stepKey}:${path}`;
    const existing = data.entries[key];
    const now = new Date().toISOString();
    const ref = own(c).doc(entryDocId(stepKey, path));
    let result;
    if (!existing) {
      if (baseRevision && baseRevision > 0) throw httpError(409, "conflict", { revision: 0, value: "", updatedAt: null });
      if (value === "") return { revision: 0, savedAt: now };
      data.entries[key] = { value, revision: 1, createdAt: now, updatedAt: now, history: [] };
      result = { revision: 1, savedAt: now };
    } else {
      // Samma kontrakt som servern: ett befintligt svar ändras bara mot känd revision.
      if (baseRevision == null) throw httpError(428, "base_revision_required");
      if (Number(baseRevision) !== existing.revision) {
        throw httpError(409, "conflict", { revision: existing.revision, value: existing.value, updatedAt: existing.updatedAt });
      }
      if (existing.value === value) return { revision: existing.revision, savedAt: existing.updatedAt };
      const history = [...(existing.history || [])];
      if (Date.parse(now) - Date.parse(existing.updatedAt) > GAP_MS && existing.value.trim()) {
        history.push({ value: existing.value, from: history.at(-1)?.until || existing.createdAt, until: existing.updatedAt });
        while (history.length > MAX_HISTORY) history.shift();
      }
      data.entries[key] = { ...existing, value, revision: existing.revision + 1, updatedAt: now, history };
      result = { revision: existing.revision + 1, savedAt: now };
    }
    await ref.set(data.entries[key]);
    await touch(c, data);
    await syncShared(c, data, stepKey, found.section.key);
    return result;
  }

  async function putAssessment(body) {
    const c = await ctx();
    const { point, dimension, value } = body || {};
    if (!DIMS.some((d) => d.key === dimension)) throw httpError(400, "unknown_dimension");
    if (!Number.isInteger(value) || value < 1 || value > 6) throw httpError(400, "invalid_value");
    const co = await cohort(c);
    const data = await loadOwn(c);
    const found = R.mapSectionFor(STEPS, point, currentStepOf(co, data));
    if (!found || found.closed) throw httpError(403, "measure_point_not_open");
    if (lockedFor(co, data)[`${found.step.key}:${found.section.key}`]) throw httpError(423, "locked");
    const now = new Date().toISOString();
    const points = { ...data.assessments, [point]: { ...(data.assessments[point] || {}), [dimension]: value } };
    const meta = { ...((await own(c).doc("assessments").get()).data()?.meta || {}) };
    meta[point] ||= { assessedAt: now };
    meta[point].updatedAt = now;
    await own(c).doc("assessments").set({ points, meta });
    data.assessments = points;
    await touch(c, data);
    return { savedAt: now };
  }

  async function putShare(body) {
    const c = await ctx();
    const { step: stepKey, section: sectionKey, kind, active } = body || {};
    const sec = section(stepKey, sectionKey);
    if (!sec || !sec.shareable) throw httpError(400, "not_shareable");
    if (!["share_with_facilitator", "bring_to_session"].includes(kind)) throw httpError(400, "unknown_kind");
    const data = await loadOwn(c);
    data.shares = data.shares.filter((s) => !(s.step === stepKey && s.section === sectionKey && s.kind === kind));
    if (active === true) data.shares.push({ step: stepKey, section: sectionKey, kind, since: new Date().toISOString() });
    await own(c).doc("shares").set({ items: data.shares });
    await syncShared(c, data, stepKey, sectionKey);
    return { shares: data.shares };
  }

  async function history(url) {
    const c = await ctx();
    const stepKey = url.searchParams.get("step");
    const path = url.searchParams.get("field");
    if (!findField(stepKey, path)) throw httpError(400, "unknown_field");
    const snap = await own(c).doc(entryDocId(stepKey, path)).get();
    if (!snap.exists) return { current: null, versions: [] };
    const e = snap.data();
    return { current: { value: e.value, since: e.createdAt, updatedAt: e.updatedAt }, versions: e.history || [] };
  }

  // Testläge. Bara i förhandsvisningen. Flyttar testpersonen genom resan.
  async function putTestStep(body) {
    const c = await ctx();
    const target = body?.step ?? null;
    const def = target === null ? null : step(target);
    if (target !== null && (!def || def.aside)) throw httpError(400, "unknown_step");
    const data = await loadOwn(c);
    data.profile = { ...(data.profile || { enrolledAt: new Date().toISOString() }), testStep: target };
    await own(c).doc("profile").set(data.profile);
    return journey(c, data);
  }

  async function participantIds(c) {
    const snap = await c.db.collection("roster").get();
    return snap.docs.map((d) => d.id);
  }

  async function names(c, ids) {
    const profiles = c.user && ids.length ? await c.user.profiles(ids) : {};
    return (id) => (id === c.uid ? "Testdeltagare (du)" : profiles[id]?.name || "Deltagare");
  }

  async function facilitatorShared() {
    const c = await ctx();
    if (!c.isOwner) throw httpError(403, "forbidden");
    const co = await cohort(c);
    const ids = await participantIds(c);
    const nameOf = await names(c, ids);
    const participants = [];
    for (const id of ids) {
      const items = await c.db.collection(`shared/${id}/items`).get();
      const req = await c.db.doc(`requests/${id}`).get();
      participants.push({ name: nameOf(id), talkRequestedAt: req.exists ? req.data().requestedAt || null : null, shared: items.docs.map((d) => d.data()) });
    }
    return { cohorts: [{ id: co.id, name: co.name, startDate: co.startDate, participants }] };
  }

  async function adminOverview() {
    const c = await ctx();
    if (!c.isOwner) throw httpError(403, "forbidden");
    const co = await cohort(c);
    const roster = await c.db.collection("roster").get();
    const nameOf = await names(c, roster.docs.map((d) => d.id));
    return {
      cohorts: [
        {
          id: co.id,
          name: co.name,
          startDate: co.startDate,
          endDate: co.endDate,
          currentStep: co.currentStep,
          status: co.status,
          maxParticipants: co.maxParticipants,
          liveSessions: co.liveSessions || [],
          participants: roster.docs.map((d) => ({
            name: nameOf(d.id),
            email: "",
            status: "active",
            lastActivityAt: d.data().lastActivityAt || null,
            startedSteps: d.data().startedSteps || [],
          })),
        },
      ],
    };
  }

  async function adminUpdateLiveSession(id, body) {
    const c = await ctx();
    if (!c.isOwner) throw httpError(403, "forbidden");
    const co = await cohort(c);
    const s = (co.liveSessions || []).find((x) => x.id === id);
    if (!s) throw httpError(404, "not_found");
    if (body.teamsUrl !== undefined) {
      if (typeof body.teamsUrl !== "string" || (body.teamsUrl && !/^https:\/\/[^\s]+$/.test(body.teamsUrl))) throw httpError(400, "invalid_url");
      s.teamsUrl = body.teamsUrl;
    }
    await c.db.doc("testdata/cohort").set(co);
    return s;
  }

  async function request(method, path, body) {
    const url = new URL(path, "https://preview.local");
    const p = url.pathname;
    let m;
    if (p === "/api/me" && method === "GET") return me();
    if (p === "/api/logout" && method === "POST") {
      setSignedIn(false);
      return { ok: true };
    }
    // Ingen mätning i förhandsvisningen. Ingenting lagras, ingenting skickas.
    if (p === "/api/events" && method === "POST") return { ok: true };
    if (p === "/api/facilitator/shared" && method === "GET") return facilitatorShared();
    if (p === "/api/admin/overview" && method === "GET") return adminOverview();
    if ((m = p.match(/^\/api\/admin\/live-sessions\/([\w-]+)$/)) && method === "PUT") return adminUpdateLiveSession(m[1], body || {});
    if ((m = p.match(/^\/api\/journey\/([\w-]+)(\/[a-z-]+)?$/))) {
      assertOwn(m[1]);
      const sub = m[2] || "";
      if (!sub && method === "GET") {
        const c = await ctx();
        return journey(c);
      }
      if (sub === "/entry" && method === "PUT") return putEntry(body);
      if (sub === "/assessment" && method === "PUT") return putAssessment(body);
      if (sub === "/share" && method === "PUT") return putShare(body);
      if (sub === "/history" && method === "GET") return history(url);
      if (sub === "/test-step" && method === "PUT") return putTestStep(body);
      if (sub === "/support" && method === "PUT") return putSupport(body);
      if (sub === "/talk-request" && method === "PUT") return putTalkRequest(body);
    }
    throw httpError(404, "not_found");
  }

  // Databasen saknar transaktioner. Skrivningar körs därför en i taget, så
  // att två snabba klick i kartan aldrig skriver över varandra.
  let queue = Promise.resolve();
  function serialized(fn) {
    const run = queue.then(fn, fn);
    queue = run.catch(() => {});
    return run;
  }

  window.LR_TRANSPORT = {
    request: async (method, path, body) => {
      try {
        return await (method === "GET" ? request(method, path, body) : serialized(() => request(method, path, body)));
      } catch (e) {
        if (e.status) throw e;
        // Plattformsfel. Behandlas som nätfel: texten ligger kvar och sparas igen.
        throw httpError(503, e?.code || "unavailable");
      }
    },
    signInLabel: "Logga in som testdeltagare",
    signIn: () => {
      setSignedIn(true);
      location.reload();
    },
  };
})();
