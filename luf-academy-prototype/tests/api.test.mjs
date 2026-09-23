import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { openDb } from "../server/db.mjs";
import { createApp, WRITING_SESSION_GAP_MS } from "../server/app.mjs";
import { seed } from "../scripts/seed.mjs";

let server;
let base;
let db;
let links;
let clock = new Date("2026-09-23T08:00:00Z");
const SECRET = "HEMLIG-REFLEKTION-7Q2";

before(async () => {
  db = openDb(":memory:");
  links = seed(db, { today: clock });
  const app = createApp(db, { now: () => clock });
  server = createServer((req, res) => app.handle(req, res));
  await new Promise((r) => server.listen(0, "127.0.0.1", r));
  base = `http://127.0.0.1:${server.address().port}`;
});
after(() => server.close());

async function signIn(key) {
  const res = await fetch(`${base}/login?t=${links[key].token}`, { redirect: "manual" });
  assert.equal(res.status, 302);
  const cookie = res.headers.get("set-cookie").split(";")[0];
  assert.match(cookie, /^lr_session=.+/);
  return cookie;
}

function client(cookie) {
  const call = async (method, path, body, extraHeaders = {}) => {
    const headers = { "X-LUF-Academy": "1", ...(cookie ? { Cookie: cookie } : {}), ...extraHeaders };
    if (body !== undefined) headers["Content-Type"] = "application/json";
    const res = await fetch(base + path, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
    return { status: res.status, body: await res.json().catch(() => null) };
  };
  return {
    get: (p) => call("GET", p),
    put: (p, b) => call("PUT", p, b),
    post: (p, b) => call("POST", p, b),
    raw: call,
  };
}

async function participant(key) {
  const c = client(await signIn(key));
  const me = await c.get("/api/me");
  assert.equal(me.status, 200);
  return { c, me: me.body, enr: me.body.enrollments[0].id };
}

test("utloggad användare får inget", async () => {
  const c = client(null);
  assert.equal((await c.get("/api/me")).status, 401);
  assert.equal((await c.get("/api/journey/x")).status, 401);
});

test("ogiltig eller utgången länk loggar inte in", async () => {
  const res = await fetch(`${base}/login?t=fel`, { redirect: "manual" });
  assert.equal(res.status, 302);
  assert.equal(res.headers.get("location"), "/#/inloggning-misslyckades");
  assert.equal(res.headers.get("set-cookie"), null);
});

test("1. rätt deltagare når rätt program och grupp", async () => {
  const { me } = await participant("testdeltagare");
  assert.equal(me.program.title, "Ledarskap med hjärta och mod");
  assert.equal(me.enrollments.length, 1);
  assert.equal(me.enrollments[0].cohort.name, "Grupp A");
  assert.ok(me.enrollments[0].nextLiveSession, "nästa live-träff visas");
  const lena = await participant("deltagare-b1");
  assert.equal(lena.me.enrollments[0].cohort.name, "Grupp B");
});

test("2. en deltagare kan inte nå en annan deltagares resa", async () => {
  const jan = await participant("testdeltagare");
  const anna = await participant("deltagare-a2");
  await jan.c.put(`/api/journey/${jan.enr}/entry`, { step: "w1", field: "situation.tolkning", value: SECRET });

  assert.equal((await anna.c.get(`/api/journey/${jan.enr}`)).status, 404);
  assert.equal((await anna.c.get(`/api/journey/${jan.enr}/history?step=w1&field=situation.tolkning`)).status, 404);
  assert.equal(
    (await anna.c.put(`/api/journey/${jan.enr}/entry`, { step: "w1", field: "situation.tolkning", value: "x" })).status,
    404,
  );
  assert.equal(
    (await anna.c.put(`/api/journey/${jan.enr}/share`, { step: "w1", section: "situation", kind: "share_with_facilitator", active: true })).status,
    404,
  );
  const own = await anna.c.get(`/api/journey/${anna.enr}`);
  assert.ok(!JSON.stringify(own.body).includes(SECRET));
  // Texten är orörd.
  const mine = await jan.c.get(`/api/journey/${jan.enr}`);
  assert.equal(mine.body.entries["w1:situation.tolkning"].value, SECRET);
});

test("adminrollen ger ingen läsrätt till privat fritext", async () => {
  const admin = client(await signIn("programadmin"));
  const jan = await participant("testdeltagare");
  assert.equal((await admin.get(`/api/journey/${jan.enr}`)).status, 404);
  const overview = await admin.get("/api/admin/overview");
  assert.equal(overview.status, 200);
  assert.ok(!JSON.stringify(overview.body).includes(SECRET), "adminöversikten innehåller ingen fritext");
  assert.equal((await admin.get("/api/facilitator/shared")).status, 403);
});

test("delning är en aktiv handling och gäller bara det valda avsnittet", async () => {
  const jan = await participant("testdeltagare");
  const handledare = client(await signIn("jan-handledare"));
  const before = await handledare.get("/api/facilitator/shared");
  assert.equal(before.status, 200);
  assert.ok(!JSON.stringify(before.body).includes(SECRET), "inget delat som standard");

  // Ta med till nästa träff delar ingenting.
  await jan.c.put(`/api/journey/${jan.enr}/share`, { step: "w1", section: "situation", kind: "bring_to_session", active: true });
  assert.ok(!JSON.stringify((await handledare.get("/api/facilitator/shared")).body).includes(SECRET));

  await jan.c.put(`/api/journey/${jan.enr}/entry`, { step: "w1", field: "narvaro.missade", value: "PRIVAT-NARVARO" });
  const share = await jan.c.put(`/api/journey/${jan.enr}/share`, {
    step: "w1", section: "situation", kind: "share_with_facilitator", active: true,
  });
  assert.equal(share.status, 200);
  const shared = JSON.stringify((await handledare.get("/api/facilitator/shared")).body);
  assert.ok(shared.includes(SECRET), "det delade avsnittet syns");
  assert.ok(!shared.includes("PRIVAT-NARVARO"), "andra avsnitt syns inte");

  // Andra deltagare ser aldrig delat material.
  const anna = await participant("deltagare-a2");
  assert.equal((await anna.c.get("/api/facilitator/shared")).status, 403);

  // Ej delbara avsnitt kan inte delas.
  assert.equal(
    (await jan.c.put(`/api/journey/${jan.enr}/share`, { step: "w1", section: "narvaro", kind: "share_with_facilitator", active: true })).status,
    400,
  );

  await jan.c.put(`/api/journey/${jan.enr}/share`, { step: "w1", section: "situation", kind: "share_with_facilitator", active: false });
  assert.ok(!JSON.stringify((await handledare.get("/api/facilitator/shared")).body).includes(SECRET), "återkallad delning syns inte");
});

test("handledare ser bara grupper hen är tilldelad", async () => {
  const { randomUUID } = await import("node:crypto");
  const id = randomUUID();
  db.prepare("INSERT INTO lr_user (id, email, display_name) VALUES (?, ?, ?)").run(id, "b-only@prototyp.luf", "Handledare B");
  db.prepare("INSERT INTO lr_role_grant (user_id, role, cohort_id) VALUES (?, 'facilitator', 'grupp-b')").run(id);
  const { hashToken } = await import("../server/app.mjs");
  db.prepare("INSERT INTO lr_prototype_login (token_hash, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)").run(
    hashToken("b-only-token"), id, clock.toISOString(), "2099-01-01T00:00:00Z",
  );
  const res = await fetch(`${base}/login?t=b-only-token`, { redirect: "manual" });
  const c = client(res.headers.get("set-cookie").split(";")[0]);
  const jan = await participant("testdeltagare");
  await jan.c.put(`/api/journey/${jan.enr}/share`, { step: "w1", section: "situation", kind: "share_with_facilitator", active: true });
  const out = await c.get("/api/facilitator/shared");
  assert.deepEqual(out.body.cohorts.map((x) => x.id), ["grupp-b"]);
  assert.ok(!JSON.stringify(out.body).includes(SECRET));
  await jan.c.put(`/api/journey/${jan.enr}/share`, { step: "w1", section: "situation", kind: "share_with_facilitator", active: false });
});

test("3. flera grupper samtidigt och högst sex deltagare per grupp", async () => {
  const cohorts = db.prepare("SELECT id, status FROM lr_cohort ORDER BY id").all();
  assert.deepEqual(cohorts.map((c) => c.id), ["grupp-a", "grupp-b"]);
  const { randomUUID } = await import("node:crypto");
  const add = (n) => {
    const id = randomUUID();
    db.prepare("INSERT INTO lr_user (id, email, display_name) VALUES (?, ?, ?)").run(id, `extra${n}@prototyp.luf`, `Extra ${n}`);
    db.prepare("INSERT INTO lr_enrollment (id, user_id, cohort_id) VALUES (?, ?, 'grupp-b')").run(randomUUID(), id);
  };
  for (let n = 1; n <= 4; n += 1) add(n); // Grupp B har 2 + 4 = 6
  assert.throws(() => add(5), /lr_cohort_full/);
  assert.throws(() => db.prepare("UPDATE lr_cohort SET max_participants = 7 WHERE id = 'grupp-b'").run(), /CHECK/);
});

test("4. autosparning: revisioner, konflikt mellan enheter och ingen tyst förlust", async () => {
  const desktop = await participant("testdeltagare");
  const mobile = await participant("testdeltagare"); // samma konto, ny session
  const path = `/api/journey/${desktop.enr}/entry`;
  const a = await desktop.c.put(path, { step: "w1", field: "forandring.mal_1", value: "Lyssna längre", baseRevision: 0 });
  assert.equal(a.status, 200);
  assert.equal(a.body.revision, 1);
  const b = await desktop.c.put(path, { step: "w1", field: "forandring.mal_1", value: "Lyssna längre innan jag svarar", baseRevision: 1 });
  assert.equal(b.body.revision, 2);

  // Mobilen har fortfarande revision 1. Servern vägrar skriva över tyst.
  const stale = await mobile.c.put(path, { step: "w1", field: "forandring.mal_1", value: "Något annat", baseRevision: 1 });
  assert.equal(stale.status, 409);
  assert.equal(stale.body.value, "Lyssna längre innan jag svarar");
  assert.equal(stale.body.revision, 2);

  // Deltagaren väljer medvetet sin version.
  const forced = await mobile.c.put(path, { step: "w1", field: "forandring.mal_1", value: "Något annat", baseRevision: 2 });
  assert.equal(forced.status, 200);
  assert.equal(forced.body.revision, 3);
});

test("5 och 6. svar finns kvar efter utloggning, ny inloggning och byte av enhet", async () => {
  const first = await participant("testdeltagare");
  await first.c.put(`/api/journey/${first.enr}/entry`, { step: "w1", field: "situation.vad_hande", value: "Mötet i måndags" });
  const logout = await first.c.post("/api/logout", {});
  assert.equal(logout.status, 200);
  assert.equal((await first.c.get("/api/me")).status, 401, "sessionen är död efter utloggning");

  const second = await participant("testdeltagare");
  const journey = await second.c.get(`/api/journey/${second.enr}`);
  assert.equal(journey.body.entries["w1:situation.vad_hande"].value, "Mötet i måndags");
});

test("historik sparas per skrivpass", async () => {
  const p = await participant("deltagare-a3");
  const put = (value) => p.c.put(`/api/journey/${p.enr}/entry`, { step: "w1", field: "forandring.mal_2", value });
  await put("Version ett");
  await put("Version ett, lite längre");
  clock = new Date(clock.getTime() + WRITING_SESSION_GAP_MS + 60000);
  await put("Version två");
  const h = await p.c.get(`/api/journey/${p.enr}/history?step=w1&field=forandring.mal_2`);
  assert.equal(h.status, 200);
  assert.equal(h.body.current.value, "Version två");
  assert.deepEqual(h.body.versions.map((v) => v.value), ["Version ett, lite längre"]);
});

test("7 till 15. hela Vecka 1-kedjan på servern", async () => {
  const p = await participant("deltagare-a2");
  const put = (field, value) => p.c.put(`/api/journey/${p.enr}/entry`, { step: "w1", field, value });

  // 9. Ledarskapskartan
  for (const [dimension, value] of [["narvaro", 3], ["mod", 4], ["lyssnande", 2], ["tydlighet", 5], ["relation", 4], ["ansvar", 6]]) {
    assert.equal((await p.c.put(`/api/journey/${p.enr}/assessment`, { point: "start", dimension, value })).status, 200);
  }
  assert.equal((await p.c.put(`/api/journey/${p.enr}/assessment`, { point: "start", dimension: "mod", value: 7 })).status, 400);
  assert.equal((await p.c.put(`/api/journey/${p.enr}/assessment`, { point: "end", dimension: "mod", value: 3 })).status, 403);
  let j = (await p.c.get(`/api/journey/${p.enr}`)).body;
  assert.deepEqual(j.assessments.start, { narvaro: 3, mod: 4, lyssnande: 2, tydlighet: 5, relation: 4, ansvar: 6 });
  assert.equal(j.status["w1:karta"], "done");
  const stored = db.prepare("SELECT measure_point, assessed_at FROM lr_self_assessment WHERE enrollment_id = ?").all(p.enr);
  assert.ok(stored.every((r) => r.measure_point === "start" && r.assessed_at));

  // 10. Tre förändringsmål
  await put("forandring.mal_1", "Ett");
  await put("forandring.mal_2", "Två");
  await put("forandring.mal_3", "Tre");
  // 11 och 12. Situation, observation och tolkning i skilda fält
  await put("situation.vad_hande", "Hon lämnade mötet tidigt.");
  await put("situation.sag_horde", "Hon tittade på klockan två gånger.");
  await put("situation.tolkning", "Jag tror att hon var missnöjd.");
  await put("situation.gjorde", "Jag fortsatte dagordningen.");
  // 13. Veckans handling
  await put("handling.prova", "Fråga innan jag svarar.");
  await put("handling.situation", "Veckomötet.");
  assert.equal((await put("handling.nar", "i morgon")).status, 400);
  await put("handling.nar", "2026-09-25");
  j = (await p.c.get(`/api/journey/${p.enr}`)).body;
  assert.equal(j.status["w1:handling"], "done");
  // 14. Återvisning: handlingen finns kvar och kan läsas tillbaka
  assert.equal(j.entries["w1:handling.prova"].value, "Fråga innan jag svarar.");
  // 15. Vad hände? Planen låses som historiskt faktum.
  await put("vad-hande.gjorde_faktiskt", "Jag frågade först.");
  const locked = await put("handling.prova", "Ändrad plan");
  assert.equal(locked.status, 423);
  j = (await p.c.get(`/api/journey/${p.enr}`)).body;
  assert.equal(j.entries["w1:handling.prova"].value, "Fråga innan jag svarar.");
  assert.equal(j.locked["w1:handling"], "return_started");
  await put("vad-hande.hande", "Det blev tyst. Sedan svarade hon.");
  await put("vad-hande.upptackte", "Jag fyller tystnad för snabbt.");
  j = (await p.c.get(`/api/journey/${p.enr}`)).body;
  assert.equal(j.status["w1:vad-hande"], "done");
});

test("21. vecka 2 till 6 och 30 dagar är inte öppna", async () => {
  const p = await participant("testdeltagare");
  for (const step of ["w2", "w3", "w4", "w5", "w6", "d30"]) {
    const res = await p.c.put(`/api/journey/${p.enr}/entry`, { step, field: "x.y", value: "test" });
    assert.equal(res.status, 403, step);
  }
  assert.ok(p.me.program.steps.filter((s) => s.key !== "w1").every((s) => !s.built && s.sections.length === 0));
  assert.equal((await p.c.put(`/api/journey/${p.enr}/entry`, { step: "w1", field: "situation.hittepa", value: "x" })).status, 400);
});

test("16. mätning innehåller aldrig fritext", async () => {
  const p = await participant("testdeltagare");
  assert.equal((await p.c.post("/api/events", { name: "action_revisited", step: "w1", section: "vad-hande", enrollmentId: p.enr })).status, 200);
  assert.equal((await p.c.post("/api/events", { name: "action_revisited", text: SECRET })).status, 400);
  assert.equal((await p.c.post("/api/events", { name: SECRET })).status, 400);
  assert.equal((await p.c.post("/api/events", { name: "client_error", step: SECRET })).status, 400);

  const events = db.prepare("SELECT * FROM lr_event").all();
  const names = new Set(events.map((e) => e.event_name));
  for (const expected of ["week_started", "section_completed", "action_chosen", "what_happened_completed", "action_revisited"]) {
    assert.ok(names.has(expected), `saknar ${expected}`);
  }
  const allowedColumns = ["id", "enrollment_id", "event_name", "step_key", "section_key", "created_at"];
  assert.deepEqual(Object.keys(events[0]).sort(), [...allowedColumns].sort());
  const entryValues = db.prepare("SELECT value FROM lr_entry WHERE value <> ''").all().map((r) => r.value);
  const dump = JSON.stringify(events);
  for (const v of entryValues) assert.ok(!dump.includes(v), `fritext i mätning: ${v}`);
});

test("skrivande anrop kräver JSON och egen header", async () => {
  const p = await participant("testdeltagare");
  const noHeader = await p.c.raw("PUT", `/api/journey/${p.enr}/entry`, { step: "w1", field: "situation.gjorde", value: "x" }, { "X-LUF-Academy": "0" });
  assert.equal(noHeader.status, 403);
  const cookie = (await signIn("testdeltagare"));
  const form = await fetch(`${base}/api/journey/${p.enr}/entry`, {
    method: "PUT",
    headers: { Cookie: cookie, "Content-Type": "application/x-www-form-urlencoded", "X-LUF-Academy": "1" },
    body: "step=w1",
  });
  assert.equal(form.status, 415);
});

test("programadmin kan ändra Teamslänk, loggas, men deltagare kan inte", async () => {
  const admin = client(await signIn("programadmin"));
  const bad = await admin.put("/api/admin/live-sessions/grupp-a-w1", { teamsUrl: "javascript:alert(1)" });
  assert.equal(bad.status, 400);
  const ok = await admin.put("/api/admin/live-sessions/grupp-a-w1", { teamsUrl: "https://teams.microsoft.com/l/meetup-join/test" });
  assert.equal(ok.status, 200);
  assert.equal(db.prepare("SELECT COUNT(*) AS n FROM lr_admin_audit WHERE target = 'grupp-a-w1'").get().n, 1);
  const p = await participant("testdeltagare");
  assert.equal((await p.c.put("/api/admin/live-sessions/grupp-a-w1", { teamsUrl: "https://x.se" })).status, 403);
  assert.equal(p.me.enrollments[0].nextLiveSession.teamsUrl, "https://teams.microsoft.com/l/meetup-join/test");
});

test("sites-header-läget följer produktionens identitetskontrakt", async () => {
  const app = createApp(db, { identityMode: "sites-header", now: () => clock });
  const s = createServer((req, res) => app.handle(req, res));
  await new Promise((r) => s.listen(0, "127.0.0.1", r));
  const url = `http://127.0.0.1:${s.address().port}/api/me`;
  const known = await fetch(url, { headers: { "oai-authenticated-user-email": "testdeltagare@prototyp.luf" } });
  assert.equal(known.status, 200);
  const unknown = await fetch(url, { headers: { "oai-authenticated-user-email": "okand@example.com" } });
  assert.equal(unknown.status, 401);
  const none = await fetch(url);
  assert.equal(none.status, 401);
  s.close();
});

test("startskattningen låses när gruppen gått vidare från vecka 1", async () => {
  const p = await participant("deltagare-b2");
  assert.equal((await p.c.put(`/api/journey/${p.enr}/assessment`, { point: "start", dimension: "mod", value: 2 })).status, 200);
  db.prepare("UPDATE lr_cohort SET current_step = 'w2' WHERE id = 'grupp-b'").run();
  assert.equal((await p.c.put(`/api/journey/${p.enr}/assessment`, { point: "start", dimension: "mod", value: 5 })).status, 423);
  db.prepare("UPDATE lr_cohort SET current_step = 'w1' WHERE id = 'grupp-b'").run();
});
