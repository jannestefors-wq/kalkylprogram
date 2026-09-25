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

  await jan.c.put(`/api/journey/${jan.enr}/entry`, { step: "w1", field: "privat.vet_redan", value: "PRIVAT-NARVARO" });
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
    (await jan.c.put(`/api/journey/${jan.enr}/share`, { step: "w1", section: "privat", kind: "share_with_facilitator", active: true })).status,
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

// ---------- Order 010. Revisionskontroll för befintliga svar ----------
// Work fann i verifiering 009 att en uppdatering utan baseRevision kunde
// ersätta ett nyare svar utan konflikt. Testerna nedan täcker kontraktet.

// Version 2: Startsamtalet och Samtal med Jan är de alltid öppna stegen.
const entryRow = (enr, field, stepKey = "start") =>
  db.prepare("SELECT id, value, revision FROM lr_entry WHERE enrollment_id = ? AND step_key = ? AND field_key = ?").get(enr, stepKey, field);
const historyCount = (entryId) => db.prepare("SELECT COUNT(*) AS n FROM lr_entry_history WHERE entry_id = ?").get(entryId).n;

test("010 test 1. nytt svar skapas utan tidigare revision", async () => {
  const p = await participant("deltagare-b1");
  const put = (body) => p.c.put(`/api/journey/${p.enr}/entry`, { step: "start", field: "infor.forsta", ...body });
  const created = await put({ value: "Första texten" });
  assert.equal(created.status, 200, "baseRevision krävs inte när inget svar finns");
  assert.equal(created.body.revision, 1);
  assert.deepEqual({ ...entryRow(p.enr, "infor.forsta"), id: 0 }, { id: 0, value: "Första texten", revision: 1 });
  const other = await p.c.put(`/api/journey/${p.enr}/entry`, { step: "start", field: "infor.skaver", value: "Med noll", baseRevision: 0 });
  assert.equal(other.status, 200, "baseRevision 0 betyder att inget svar finns ännu");
  assert.equal(other.body.revision, 1);
});

test("010 test 2 och autosparning. rätt revision flyttar fram revisionen 1, 2, 3", async () => {
  const p = await participant("deltagare-b1");
  const put = (value, baseRevision) => p.c.put(`/api/journey/${p.enr}/entry`, { step: "start", field: "efter.tar_med", value, baseRevision });
  let rev = 0;
  for (const [i, text] of ["Ett", "Ett två", "Ett två tre"].entries()) {
    const out = await put(text, rev);
    assert.equal(out.status, 200);
    assert.equal(out.body.revision, rev + 1, `sparning ${i + 1} ger revision ${rev + 1}`);
    rev = out.body.revision;
  }
  assert.deepEqual({ ...entryRow(p.enr, "efter.tar_med"), id: 0 }, { id: 0, value: "Ett två tre", revision: 3 });
});

test("010 test 3. gammal revision ger konflikt och ingenting skrivs", async () => {
  const p = await participant("deltagare-b1");
  const put = (value, baseRevision) => p.c.put(`/api/journey/${p.enr}/entry`, { step: "samtal", field: "infor.monster", value, baseRevision });
  let rev = 0;
  for (const text of ["v1", "v2", "v3", "v4", "v5"]) rev = (await put(text, rev)).body.revision;
  assert.equal(rev, 5);
  const stale = await put("Från revision 4", 4);
  assert.equal(stale.status, 409);
  assert.equal(stale.body.error, "conflict");
  assert.equal(stale.body.revision, 5, "klienten får veta vilken revision som gäller");
  assert.deepEqual({ ...entryRow(p.enr, "infor.monster", "samtal"), id: 0 }, { id: 0, value: "v5", revision: 5 });
});

test("010 test 4. befintligt svar utan baseRevision avvisas. Works fynd i 009.", async () => {
  const p = await participant("deltagare-b1");
  const field = "efter.gora_nu";
  await p.c.put(`/api/journey/${p.enr}/entry`, { step: "start", field, value: "Nyare svar", baseRevision: 0 });
  const before = entryRow(p.enr, field);
  clock = new Date(clock.getTime() + WRITING_SESSION_GAP_MS + 60000);
  const missing = await p.c.put(`/api/journey/${p.enr}/entry`, { step: "start", field, value: "Äldre text utan revision" });
  assert.equal(missing.status, 428);
  assert.equal(missing.body.error, "base_revision_required");
  assert.equal(missing.body.value, undefined, "avvisningen skickar ingen text");
  const nullBase = await p.c.put(`/api/journey/${p.enr}/entry`, { step: "start", field, value: "Med null", baseRevision: null });
  assert.equal(nullBase.status, 428);
  const invalid = await p.c.put(`/api/journey/${p.enr}/entry`, { step: "start", field, value: "Med text", baseRevision: "1" });
  assert.equal(invalid.status, 400);
  assert.deepEqual(entryRow(p.enr, field), before, "text och revision är oförändrade");
  assert.equal(historyCount(before.id), 0, "ingen historik för en avvisad skrivning");
});

test("010 test 5 och 6. två enheter: en lyckas, en får konflikt, ingen tyst överskrivning", async () => {
  const device1 = await participant("deltagare-b1");
  const device2 = await participant("deltagare-b1"); // samma konto, annan enhet
  const path = `/api/journey/${device1.enr}/entry`;
  const field = "infor.inte_gruppen";
  // Start: revision 7, text A.
  let rev = 0;
  for (let i = 1; i <= 7; i += 1) rev = (await device1.c.put(path, { step: "start", field, value: i === 7 ? "A" : `A${i}`, baseRevision: rev })).body.revision;
  assert.equal(rev, 7);
  // Båda enheterna har läst revision 7.
  const b = await device1.c.put(path, { step: "start", field, value: "B", baseRevision: 7 });
  assert.equal(b.status, 200);
  assert.equal(b.body.revision, 8);
  const c = await device2.c.put(path, { step: "start", field, value: "C", baseRevision: 7 });
  assert.equal(c.status, 409);
  assert.equal(c.body.value, "B");
  assert.equal(c.body.revision, 8);
  assert.deepEqual({ ...entryRow(device1.enr, field), id: 0 }, { id: 0, value: "B", revision: 8 }, "B ligger kvar. C skrev inte över.");
});

test("010. samtidiga anrop med samma revision: exakt ett lyckas", async () => {
  const p = await participant("deltagare-b1");
  const path = `/api/journey/${p.enr}/entry`;
  const field = "infor.tanka_kring";
  await p.c.put(path, { step: "samtal", field, value: "Start", baseRevision: 0 });
  const results = await Promise.all(
    [1, 2, 3, 4, 5].map((n) => p.c.put(path, { step: "samtal", field, value: `Enhet ${n}`, baseRevision: 1 })),
  );
  const ok = results.filter((r) => r.status === 200);
  assert.equal(ok.length, 1, "exakt en skrivning lyckas");
  assert.equal(results.filter((r) => r.status === 409).length, 4);
  const row = entryRow(p.enr, field, "samtal");
  assert.equal(row.revision, 2);
  assert.equal(row.value, `Enhet ${results.indexOf(ok[0]) + 1}`, "det som ligger kvar är det som lyckades");
  // Samtidigt skapande av ett nytt svar: exakt ett lyckas, resten får konflikt.
  const created = await Promise.all(
    [1, 2, 3].map((n) => p.c.put(path, { step: "samtal", field: "efter.gora_nu", value: `Ny ${n}`, baseRevision: 0 })),
  );
  assert.equal(created.filter((r) => r.status === 200).length, 1);
  assert.equal(created.filter((r) => r.status === 409).length, 2);
});

test("010 test 8. en avvisad konflikt skapar ingen historikrad", async () => {
  const p = await participant("deltagare-b1");
  const path = `/api/journey/${p.enr}/entry`;
  const field = "infor.forsta";
  const row = entryRow(p.enr, field);
  const before = historyCount(row.id);
  // Skrivpasset är slut. En lyckad skrivning hade sparat en historikrad.
  clock = new Date(clock.getTime() + WRITING_SESSION_GAP_MS + 60000);
  const stale = await p.c.put(path, { step: "start", field, value: "Gammal enhet", baseRevision: row.revision - 1 });
  assert.equal(stale.status, 409);
  assert.equal(historyCount(row.id), before, "konflikten lämnar historiken orörd");
  const ok = await p.c.put(path, { step: "start", field, value: "Nytt skrivpass", baseRevision: row.revision });
  assert.equal(ok.status, 200);
  assert.equal(historyCount(row.id), before + 1, "en verklig skrivning sparar det gamla i historiken");
  const h = await p.c.get(`/api/journey/${p.enr}/history?step=start&field=${field}`);
  assert.deepEqual(h.body.versions.map((v) => v.value), ["Första texten"]);
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
  // Order 010: en uppdatering av ett befintligt svar måste bära sin revision.
  // Testet skickade tidigare ingen revision och byggde därmed på felet.
  const put = (value, baseRevision) => p.c.put(`/api/journey/${p.enr}/entry`, { step: "w1", field: "forandring.mal_2", value, baseRevision });
  assert.equal((await put("Version ett", 0)).body.revision, 1);
  assert.equal((await put("Version ett, lite längre", 1)).body.revision, 2);
  clock = new Date(clock.getTime() + WRITING_SESSION_GAP_MS + 60000);
  assert.equal((await put("Version två", 2)).body.revision, 3);
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

  // 10. Tre förändringsområden, med hur det skulle märkas. Version 2.
  for (const n of [1, 2, 3]) {
    await put(`forandring.mal_${n}`, `Område ${n}`);
    await put(`forandring.mal_${n}_hur`, `Märks ${n}`);
  }
  // 11 och 12. Situation, observation och tolkning i skilda fält
  await put("situation.vad_hande", "Hon lämnade mötet tidigt.");
  await put("situation.tolkning", "Jag tror att hon var missnöjd.");
  await put("situation.gjorde_lat", "Jag fortsatte dagordningen.");
  // 13. Veckans handling. Den gemensamma motorn.
  assert.equal((await put("handling.omrade", "4")).status, 400, "bara område 1, 2, 3 eller Något nytt");
  await put("handling.omrade", "1");
  await put("handling.gora", "Fråga innan jag svarar, på veckomötet.");
  await put("handling.marks", "Att fler pratar. Teamet.");
  assert.equal((await put("handling.nar", "i morgon")).status, 400);
  await put("handling.nar", "2026-09-25");
  let jj = (await p.c.get(`/api/journey/${p.enr}`)).body;
  assert.equal(jj.status["w1:handling"], "done");
  // 14. Återvisning: handlingen finns kvar och kan läsas tillbaka
  assert.equal(jj.entries["w1:handling.gora"].value, "Fråga innan jag svarar, på veckomötet.");
  // 15. Vad hände? Planen låses som historiskt faktum.
  await put("vad-hande.blev", "Ja");
  const locked = await put("handling.gora", "Ändrad plan");
  assert.equal(locked.status, 423);
  jj = (await p.c.get(`/api/journey/${p.enr}`)).body;
  assert.equal(jj.entries["w1:handling.gora"].value, "Fråga innan jag svarar, på veckomötet.");
  assert.equal(jj.locked["w1:handling"], "return_started");
  await put("vad-hande.gjorde_faktiskt", "Jag frågade först.");
  await put("vad-hande.hande", "Det blev tyst. Sedan svarade hon.");
  await put("vad-hande.markte", "Jag vet inte");
  await put("vad-hande.nasta", "Behåller det.");
  jj = (await p.c.get(`/api/journey/${p.enr}`)).body;
  assert.equal(jj.status["w1:vad-hande"], "done");
  assert.equal(j.status["w1:karta"], "done");
});

test("steg öppnas i ordning. Testläget flyttar bara testpersonen.", async () => {
  const p = await participant("deltagare-a3");
  const put = (step, field, value = "test") => p.c.put(`/api/journey/${p.enr}/entry`, { step, field, value });
  assert.deepEqual(p.me.program.steps.filter((s) => s.built).map((s) => s.key), ["w1", "w2", "w3", "w4", "w5", "w6", "d30", "start", "samtal"]);
  assert.equal((await put("w2", "stanna.skjutit_upp_beslut")).status, 403, "vecka 2 är stängd när gruppen är i vecka 1");
  assert.equal((await put("d30", "kvar.fortfarande")).status, 403);
  assert.equal((await put("samtal", "infor.tanka_kring")).status, 200, "samtal med Jan är alltid öppet");
  assert.equal((await put("start", "infor.forsta")).status, 200, "startsamtalet är öppet från inskrivningen");
  assert.equal((await put("w1", "situation.hittepa")).status, 400);

  const moved = await p.c.put(`/api/journey/${p.enr}/test-step`, { step: "w3" });
  assert.equal(moved.status, 200);
  assert.deepEqual(moved.body.openSteps, ["w1", "w2", "w3", "start", "samtal"]);
  assert.equal((await put("w2", "stanna.skjutit_upp_beslut")).status, 200);
  assert.equal((await put("w3", "se-hora-kanna.se")).status, 200);
  assert.equal((await put("w4", "stanna.for_tidigt")).status, 403);
  // Startskattningen låses när testpersonen har gått vidare från vecka 1.
  assert.equal((await p.c.put(`/api/journey/${p.enr}/assessment`, { point: "start", dimension: "mod", value: 3 })).status, 423);

  // Andra i samma grupp påverkas inte.
  const anna = await participant("deltagare-a2");
  assert.equal(anna.me.enrollments[0].cohort.currentStep, "w1");
  assert.equal((await p.c.put(`/api/journey/${anna.enr}/test-step`, { step: "w6" })).status, 404, "kan inte flytta någon annan");
  await p.c.put(`/api/journey/${p.enr}/test-step`, { step: null });
});

test("testläget finns inte utanför prototypen", async () => {
  const app = createApp(db, { prototype: false, now: () => clock });
  const s = createServer((req, res) => app.handle(req, res));
  await new Promise((r) => s.listen(0, "127.0.0.1", r));
  const res = await fetch(`http://127.0.0.1:${s.address().port}/login?t=${links["deltagare-b1"].token}`, { redirect: "manual" });
  const cookie = res.headers.get("set-cookie").split(";")[0];
  const headers = { Cookie: cookie, "X-LUF-Academy": "1", "Content-Type": "application/json" };
  const me = await (await fetch(`http://127.0.0.1:${s.address().port}/api/me`, { headers })).json();
  const out = await fetch(`http://127.0.0.1:${s.address().port}/api/journey/${me.enrollments[0].id}/test-step`, {
    method: "PUT", headers, body: JSON.stringify({ step: "w6" }),
  });
  assert.equal(out.status, 404);
  assert.equal(me.program.diploma, null, "interna HOLD-noter syns inte utanför prototypen");
  s.close();
});

test("hela programmet: val, slutskattning, 30 dagar och lås per vecka", async () => {
  const p = await participant("deltagare-b2");
  const put = (step, field, value) => p.c.put(`/api/journey/${p.enr}/entry`, { step, field, value });
  await p.c.put(`/api/journey/${p.enr}/test-step`, { step: "w6" });
  assert.equal((await put("w6", "principer.vald", "Mod före bekvämlighet")).status, 200);
  assert.equal((await put("w6", "principer.vald", "Något påhittat")).status, 400, "val måste finnas bland alternativen");
  assert.equal((await put("w5", "niva.tror", "Team")).status, 200);
  assert.equal((await p.c.put(`/api/journey/${p.enr}/assessment`, { point: "end", dimension: "mod", value: 5 })).status, 200);
  assert.equal((await p.c.put(`/api/journey/${p.enr}/assessment`, { point: "d30", dimension: "mod", value: 5 })).status, 403);
  // Planen i vecka 4 låses när Vad hände? i vecka 4 börjar skrivas.
  await put("w4", "handling.gora", "Ta samtalet med platschefen.");
  await put("w4", "vad-hande.blev", "Ja");
  assert.equal((await put("w4", "handling.gora", "Ändrad")).status, 423);
  assert.equal((await put("w5", "handling.marks", "Hen vet vad som gäller.")).status, 200, "andra veckors planer är inte låsta");

  await p.c.put(`/api/journey/${p.enr}/test-step`, { step: "d30" });
  assert.equal((await p.c.put(`/api/journey/${p.enr}/assessment`, { point: "d30", dimension: "mod", value: 4 })).status, 200);
  assert.equal((await put("d30", "kvar.fortfarande", "Jag frågar först.")).status, 200);
  const j = (await p.c.get(`/api/journey/${p.enr}`)).body;
  assert.equal(j.assessments.end.mod, 5);
  assert.equal(j.assessments.d30.mod, 4);
  assert.equal(j.locked["w4:handling"], "return_started");
  await p.c.put(`/api/journey/${p.enr}/test-step`, { step: null });
});

test("nycklar i registret krockar aldrig", async () => {
  const { STEPS } = await import("../server/content.mjs");
  for (const step of STEPS.filter((s) => s.built)) {
    const keys = step.sections.map((s) => s.key);
    assert.deepEqual(keys, [...new Set(keys)], `${step.key}: momentnycklar är unika`);
    for (const section of step.sections) {
      const f = section.fields.map((x) => x.key);
      assert.deepEqual(f, [...new Set(f)], `${step.key}/${section.key}: fältnycklar är unika`);
      if (section.kind === "triangle") assert.equal(section.corners.length, 3);
    }
  }
  const slugs = STEPS.map((s) => s.slug);
  assert.deepEqual(slugs, [...new Set(slugs)]);
});

test("Se. Höra. Känna. har fast ordning i registret", async () => {
  const { STEPS } = await import("../server/content.mjs");
  const shk = STEPS.flatMap((s) => s.sections || []).filter((s) => s.model === "se-hora-kanna");
  assert.equal(shk.length, 1);
  assert.deepEqual(shk[0].corners.map((c) => c.label), ["Se", "Höra", "Känna"]);
  const text = JSON.stringify(STEPS);
  assert.ok(!/katalys/i.test(text), "inget Katalysatormaterial i utbildningen");
});

test("order 006: inget Katalysatorspråk i deltagarens utbildning", async () => {
  const { STEPS, publicProgram } = await import("../server/content.mjs");
  const { readFileSync } = await import("node:fs");
  const client = readFileSync(new URL("../public/app.js", import.meta.url), "utf8");
  for (const [where, text] of [["registret", JSON.stringify(STEPS)], ["programmet", JSON.stringify(publicProgram({ internal: true }))], ["klienten", client]]) {
    assert.ok(!/kataly/i.test(text), `${where}: katalys, katalytisk eller Katalysator förekommer`);
  }
});

test("order 006: Känna är en signal att undersöka, aldrig en slutsats om en annan människa", async () => {
  const { STEPS, publicProgram } = await import("../server/content.mjs");
  const text = JSON.stringify(publicProgram({ internal: true }));
  assert.ok(!/(jag|du) känner att (han|hon|hen|personen|den andra|de|medarbetaren)/i.test(text));
  const shk = STEPS.find((s) => s.key === "w3").sections.find((s) => s.model === "se-hora-kanna");
  const kanna = shk.fields.find((f) => f.corner === "kanna");
  assert.ok(kanna.label.includes("medveten om men inte låta styra") && kanna.hint.includes("En signal, inte ett bevis."));
  // Version 2: Trygghetsfrågan frågar efter det deltagaren har sett eller hört. Order 011.
  const trygg = STEPS.find((s) => s.key === "w4").sections.find((s) => s.key === "trygghet").fields.find((f) => f.corner === "trygghet_sett");
  assert.equal(trygg.label, "Trygghet. Vad har du sett eller hört som tyder på att personen vågar säga vad den tänker, fråga, göra fel eller säga emot?");
  const room = publicProgram().liveSupport.roomRules.join(" ");
  assert.ok(room.includes("Observera före tolkning. Tystnad, blick, tempo och ordval kan ge oss frågor. De är aldrig facit på vad någon känner."));
});

test("order 006: hörnfrågor. Källans fråga först, digitala märks internt för Jan", async () => {
  const { STEPS, publicProgram, JAN_REVIEW } = await import("../server/content.mjs");
  const corners = STEPS.flatMap((s) => (s.sections || []).filter((x) => x.kind === "triangle").flatMap((x) => x.fields.filter((f) => f.corner).map((f) => ({ step: s.key, section: x.key, f }))));
  // Version 2: 18 hörnfrågor. Individ · Team · Organisation och Tryck · Val · Riktning har bara hörnord.
  assert.equal(corners.length, 18);
  for (const { step, section, f } of corners) {
    assert.ok(["book", "digital"].includes(f.origin), `${step}/${section}.${f.key} saknar ursprung`);
    if (f.origin === "book") assert.ok(f.refs?.length, `${step}/${section}.${f.key} saknar sida`);
    if (f.origin === "digital") assert.ok(f.review === JAN_REVIEW && f.support, `${step}/${section}.${f.key} saknar märkning eller stöd`);
  }
  assert.equal(corners.filter((c) => c.f.origin === "book").length, 10);
  assert.equal(corners.filter((c) => c.f.origin === "digital").length, 8);
  const text = JSON.stringify(publicProgram({ internal: true }));
  assert.ok(!text.includes(JAN_REVIEW) && !text.includes("JAN REVIEW") && !/"origin"|"review"|"refs"/.test(text));
});

test("order 006 och version 2: vecka 6 utan dubbleringar och utan löfte", async () => {
  const { STEPS } = await import("../server/content.mjs");
  const w6 = STEPS.find((s) => s.key === "w6");
  const fields = w6.sections.flatMap((s) => s.fields.map((f) => ({ path: `${s.key}.${f.key}`, label: f.label })));
  const paths = fields.map((f) => f.path);
  for (const gone of ["stanna.inte_ledaren", "tillbaka.idag", "tillbaka.fortfarande", "avslut.lofte", "avslut.annorlunda_nu", "avslut.fortsatta_3", "trycket.tryck"]) {
    assert.ok(!paths.includes(gone), `${gone} finns kvar`);
  }
  for (const kept of ["misstaget.se_m", "avslut.fortsatta_1", "avslut.fortsatta_2", "trycket.nar_trycket"]) assert.ok(paths.includes(kept), `${kept} saknas`);
  assert.equal(fields.filter((f) => /inte (var )?den ledare du vill vara|inte var den ledare jag vill vara/i.test(f.label)).length, 0, "misstaget efterfrågas bara i triangeln");
  assert.deepEqual(fields.filter((f) => /träna på/i.test(f.label)).map((f) => f.path), ["avslut.fortsatta_1", "avslut.fortsatta_2"]);
});

test("order 006: ingen totalsiffra för trianglar i deltagarens text", async () => {
  const { publicProgram } = await import("../server/content.mjs");
  const { readFileSync } = await import("node:fs");
  const text = JSON.stringify(publicProgram({ internal: true })) + readFileSync(new URL("../public/app.js", import.meta.url), "utf8");
  assert.ok(!/\b(åtta|nio|tio|\d+) trianglar/i.test(text));
});

test("källor finns kvar internt men når aldrig deltagaren", async () => {
  const { STEPS, publicProgram } = await import("../server/content.mjs");
  const sections = STEPS.flatMap((s) => s.sections || []);
  assert.ok(sections.filter((s) => s.source).length >= 20, "källa finns per moment internt");
  assert.ok(sections.some((s) => s.refs?.length), "sidreferenser finns internt");
  assert.ok(sections.flatMap((s) => s.reading?.chapters || []).every((c) => c.pdfPages), "PDF-sidor finns internt");
  for (const internal of [true, false]) {
    const text = JSON.stringify(publicProgram({ internal }));
    for (const re of [/"source"/, /"refs"/, /pdfPages/, /Källa/, /Arbetsbok/i, /köper du/i, /HOLD/, /\(s\. \d/]) {
      assert.ok(!re.test(text), `${re} når deltagaren`);
    }
    const program = JSON.parse(text);
    assert.equal(program.diploma, null);
    const readings = program.steps.flatMap((s) => s.sections || []).filter((s) => s.reading);
    assert.ok(readings.length >= 6 && readings.every((r) => r.reading.chapters.every((c) => c.title && /^\d+–\d+$/.test(c.pages))));
  }
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
  // Fritext. Korta val som "1" eller "Ja" är inga texter och kan förekomma i id:n.
  const entryValues = db.prepare("SELECT value FROM lr_entry WHERE length(value) > 3").all().map((r) => r.value);
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
