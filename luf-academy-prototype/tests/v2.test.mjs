// Ledarskap med hjärta och mod, version 2. Order 014.
// Flöden, villkor, privat vägledning efter två Nej och integritet per roll.
import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { openDb } from "../server/db.mjs";
import { createApp } from "../server/app.mjs";
import { seed } from "../scripts/seed.mjs";
import { STEPS, AREA_NEW, PRIVACY_TEXT, SUPPORT_PROMPT, publicProgram, getSection } from "../server/content.mjs";
import * as rules from "../server/rules.mjs";

let server;
let base;
let db;
let links;
const clock = new Date("2026-09-23T08:00:00Z");
const PRIVATE = "PRIVAT-STOPP-9X";
const AREA_TEXT = "OMRADESTEXT-LYSSNA-4K";

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
  return res.headers.get("set-cookie").split(";")[0];
}
function client(cookie) {
  const call = async (method, path, body) => {
    const headers = { "X-LUF-Academy": "1", Cookie: cookie };
    if (body !== undefined) headers["Content-Type"] = "application/json";
    const res = await fetch(base + path, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
    return { status: res.status, body: await res.json().catch(() => null) };
  };
  return { get: (p) => call("GET", p), put: (p, b) => call("PUT", p, b) };
}
async function participant(key) {
  const c = client(await signIn(key));
  const me = (await c.get("/api/me")).body;
  const enr = me.enrollments[0].id;
  const put = async (step, field, value) => {
    const cur = (await c.get(`/api/journey/${enr}`)).body.entries[`${step}:${field}`];
    return c.put(`/api/journey/${enr}/entry`, { step, field, value, baseRevision: cur?.revision ?? 0 });
  };
  const journey = async () => (await c.get(`/api/journey/${enr}`)).body;
  const moveTo = (step) => c.put(`/api/journey/${enr}/test-step`, { step });
  return { c, me, enr, put, journey, moveTo };
}
const countRows = (table, where = "1=1", ...args) => db.prepare(`SELECT COUNT(*) AS n FROM ${table} WHERE ${where}`).get(...args).n;

// ---------- Registret ----------

test("v2: resans steg och ordning enligt specifikationen", () => {
  assert.deepEqual(STEPS.map((s) => s.key), ["w1", "w2", "w3", "w4", "w5", "w6", "d30", "start", "samtal"]);
  const order = (k) => STEPS.find((s) => s.key === k).sections.map((s) => s.key);
  assert.deepEqual(order("w1"), ["intro", "lasning", "stanna", "karta", "forandring", "manniskor", "situation", "triangel", "handling", "vad-hande", "privat", "traffen"]);
  assert.deepEqual(order("w2"), ["forra-veckan", "intro", "lasning", "stanna", "triangel", "handling", "vad-hande", "privat", "traffen"]);
  assert.deepEqual(order("w3"), ["forra-veckan", "intro", "lasning", "stanna", "se-hora-kanna", "aterkoppling", "handling", "vad-hande", "privat", "traffen"]);
  assert.deepEqual(order("w4"), ["forra-veckan", "halvvags", "spegel", "intro", "lasning", "stanna", "trygghet", "samtalet", "handling", "vad-hande", "privat", "traffen"]);
  assert.deepEqual(order("w5"), ["forra-veckan", "intro", "lasning", "stanna", "niva", "handling", "vad-hande", "privat", "traffen"]);
  assert.deepEqual(order("w6"), ["forra-veckan", "intro", "lasning", "stanna", "trycket", "tillbaka", "spegel", "misstaget", "principer", "karta", "avslut", "handling", "privat", "traffen"]);
  assert.deepEqual(order("d30"), ["intro", "minns", "karta", "kvar", "atertraff"]);
  assert.deepEqual(order("start"), ["infor", "efter"]);
  assert.deepEqual(order("samtal"), ["behov", "infor", "efter"]);
  assert.ok(!order("w6").includes("vad-hande"), "vecka 6 följs upp vid 30 dagar");
});

test("v2: integritetstexten och den privata frågan finns ordagrant", () => {
  const p = publicProgram();
  assert.deepEqual(p.privacyText, PRIVACY_TEXT);
  assert.deepEqual(PRIVACY_TEXT, [
    "Det här är din resa.",
    "Det du skriver här delas inte automatiskt med din arbetsgivare.",
    "Inte heller med Jan.",
    "Du väljer själv vad du delar, och du kan ta tillbaka det.",
    "Den som administrerar kursen ser vilka veckor du har börjat på. Aldrig det du skriver.",
  ]);
  // Order 015: en tredje rad som säger att rutan är privat. Samma knappar.
  assert.deepEqual(SUPPORT_PROMPT.lines, ["Två veckor i rad blev det inte som du hade tänkt.", "Vill du prata med Jan om vad som stoppar dig?", "Den här rutan ser bara du."]);
  assert.equal(SUPPORT_PROMPT.request, "Be om ett samtal");
  assert.equal(SUPPORT_PROMPT.notNow, "Inte nu");
  assert.equal(getSection("start", "infor").privacy, true);
});

test("v2: bara momenten i spec avsnitt 21 kan delas med Jan", () => {
  const shareable = STEPS.flatMap((s) => s.sections.filter((x) => x.shareable).map((x) => `${s.key}:${x.key}`)).sort();
  const expected = [
    "start:infor", "w1:situation",
    ...["w1", "w2", "w3", "w4", "w5", "w6"].map((w) => `${w}:handling`),
    ...["w1", "w2", "w3", "w4", "w5"].map((w) => `${w}:vad-hande`),
    "w2:triangel", "w3:se-hora-kanna", "w3:aterkoppling", "w4:samtalet", "w4:spegel", "w6:spegel", "w5:niva",
    "w6:tillbaka", "w6:avslut", "d30:kvar", "samtal:infor",
  ].sort();
  assert.deepEqual(shareable, expected);
  for (const k of ["privat", "stanna", "karta", "manniskor", "halvvags", "trycket", "misstaget", "principer", "traffen", "efter"]) {
    for (const s of STEPS) {
      const sec = s.sections.find((x) => x.key === k);
      if (sec && !(s.key === "w1" && k === "triangel")) assert.ok(!sec.shareable, `${s.key}:${k} är privat`);
    }
  }
  assert.ok(!getSection("w1", "triangel").shareable && !getSection("w4", "trygghet").shareable);
});

test("v2: SE vänster, HÖRA mitten, KÄNNA höger och Känna är egen signal", () => {
  const shk = getSection("w3", "se-hora-kanna");
  assert.deepEqual(shk.corners.map((c) => c.label), ["Se", "Höra", "Känna"]);
  assert.deepEqual(shk.fields.filter((f) => f.corner).map((f) => f.corner), ["se", "hora", "kanna"]);
  assert.equal(shk.fields.find((f) => f.corner === "kanna").hint, "Något förändrades. Vad behöver jag förstå mer om? En signal, inte ett bevis.");
});

test("v2: vecka 5 och vecka 6 har bara hörnord där specifikationen säger det", () => {
  const niva = getSection("w5", "niva");
  assert.ok(niva.displayOnly && niva.corners.every((c) => c.key === null));
  assert.deepEqual(niva.corners.map((c) => c.label), ["Individ", "Team", "Organisation"]);
  assert.equal(niva.fields.find((f) => f.key === "byggt").label, "Vad har jag själv byggt runt problemet? Eller låtit bli att bygga?");
  const trycket = getSection("w6", "trycket");
  assert.ok(trycket.displayOnly);
  assert.deepEqual(trycket.fields.map((f) => f.key), ["nar_trycket"], "ett gemensamt skrivfält");
});

// ---------- Regler ----------

const entriesOf = (obj) => Object.fromEntries(Object.entries(obj).map(([k, v]) => [k, { value: v }]));

test("v2 regel: klarstatus räknar bara synliga och obligatoriska fält", () => {
  const vh = getSection("w1", "vad-hande");
  const st = (vals) => rules.sectionStatus("w1", vh, entriesOf(Object.fromEntries(Object.entries(vals).map(([k, v]) => [`w1:vad-hande.${k}`, v]))), {}, []);
  assert.equal(st({ blev: "Nej", stoppade: "Tid", nasta: "Gör något mindre" }), "done", "Nej räcker med Vad stoppade dig? och Vad gör du nu?");
  assert.equal(st({ blev: "Nej", nasta: "x" }), "started");
  assert.equal(st({ blev: "Ja", gjorde_faktiskt: "a", hande: "b", markte: "Nej", nasta: "c" }), "done");
  assert.equal(st({ blev: "Delvis", gjorde_faktiskt: "a", hande: "b", markte: "Ja", nasta: "c" }), "started", "Ja på Märkte någon något? kräver Vad bygger du det på?");
  assert.equal(st({ blev: "Delvis", gjorde_faktiskt: "a", hande: "b", markte: "Ja", bygger: "d", nasta: "c" }), "done");
  assert.equal(st({ blev: "Ja", gjorde_faktiskt: "a", nasta: "c" }), "started");
  const vis = rules.visibleFields("w1", vh, entriesOf({ "w1:vad-hande.blev": "Nej" })).map((f) => f.key);
  assert.deepEqual(vis, ["blev", "stoppade", "kostar", "nasta"]);
  assert.ok(vh.fields.find((f) => f.key === "kostar").optional, "Vad kostar det att vänta? är frivillig");
});

test("v2 regel: två Nej i rad, uteblivet svar är inget Nej", () => {
  const seq = (vals, handled = []) =>
    rules.supportPromptFor(STEPS, entriesOf(Object.fromEntries(Object.entries(vals).map(([w, v]) => [w === "w6" ? "d30:kvar.blev" : `${w}:vad-hande.blev`, v]))), handled);
  assert.equal(seq({ w1: "Nej" }), null);
  assert.equal(seq({ w1: "Nej", w2: "Nej" }), "w2");
  assert.equal(seq({ w1: "Nej", w3: "Nej" }), null, "ett uteblivet svar emellan bryter följden");
  assert.equal(seq({ w1: "Nej", w2: "Delvis", w3: "Nej" }), null);
  assert.equal(seq({ w1: "Nej", w2: "Nej" }, ["w2"]), null, "Inte nu stänger rutan");
  assert.equal(seq({ w1: "Nej", w2: "Nej", w3: "Nej" }, ["w2"]), null, "en ny följd kräver två nya Nej");
  assert.equal(seq({ w1: "Nej", w2: "Nej", w3: "Nej", w4: "Nej" }, ["w2"]), "w4");
  assert.equal(seq({ w5: "Nej", w6: "Nej" }), "d30", "vecka 6 räknas vid 30 dagar");
  assert.equal(seq({ w1: "Nej", w2: "Nej", w3: "Ja" }), null, "ett senare Ja gör frågan inaktuell");
});

test("v2 regel: validering av område, flerval och kryssruta", () => {
  const omrade = getSection("w1", "handling").fields.find((f) => f.key === "omrade");
  assert.equal(rules.validateValue(omrade, "1"), null);
  assert.equal(rules.validateValue(omrade, AREA_NEW), null);
  assert.equal(rules.validateValue(omrade, AREA_TEXT), "invalid_choice", "områdets text sparas aldrig i valet");
  const fatt = getSection("w5", "niva").fields.find((f) => f.key === "fatt");
  assert.equal(rules.validateValue(fatt, `${fatt.options[0]}\n${fatt.options[2]}`), null);
  assert.equal(rules.validateValue(fatt, `${fatt.options[0]}\n${fatt.options[0]}`), "invalid_choice");
  assert.equal(rules.validateValue(fatt, "Påhittat"), "invalid_choice");
  const pagatt = getSection("w4", "samtalet").fields.find((f) => f.key === "pagatt");
  assert.equal(rules.validateValue(pagatt, "ja"), null);
  assert.equal(rules.validateValue(pagatt, "kanske"), "invalid_choice");
});

// ---------- Flöden på servern ----------

test("v2: startsamtalet är öppet från inskrivningen och ger ingen händelse", async () => {
  const p = await participant("deltagare-a3");
  const events = countRows("lr_event", "enrollment_id = ?", p.enr);
  assert.equal((await p.put("start", "infor.skaver", "Samtalet jag skjuter upp.")).status, 200);
  assert.equal((await p.put("start", "efter.tar_med", "Att börja smått.")).status, 200);
  const j = await p.journey();
  assert.equal(j.status["start:infor"], "done");
  assert.equal(j.status["start:efter"], "done");
  assert.equal(countRows("lr_event", "enrollment_id = ?", p.enr), events, "startsamtalet mäts aldrig");
  assert.equal((await p.c.put(`/api/journey/${p.enr}/share`, { step: "start", section: "efter", kind: "share_with_facilitator", active: true })).status, 400, "Efter startsamtalet är privat");
});

test("v2: tre förändringsområden och Något nytt i den gemensamma motorn", async () => {
  const p = await participant("deltagare-a2");
  await p.put("w1", "forandring.mal_1", AREA_TEXT);
  assert.equal((await p.put("w1", "handling.omrade", "1")).status, 200);
  await p.put("w1", "handling.gora", "Fråga först på måndagsmötet.");
  await p.put("w1", "handling.marks", "Fler pratar.");
  await p.put("w1", "handling.nar", "2026-09-28");
  let j = await p.journey();
  assert.equal(j.status["w1:handling"], "done", "Något nytt krävs inte när ett av de tre är valt");
  assert.equal(j.entries["w1:handling.omrade"].value, "1", "valet sparas som nummer");
  // Något nytt
  await p.moveTo("w2");
  await p.put("w2", "handling.omrade", AREA_NEW);
  await p.put("w2", "handling.gora", "Säga nej till extrauppdraget.");
  await p.put("w2", "handling.marks", "Chefen märker.");
  await p.put("w2", "handling.nar", "2026-10-02");
  j = await p.journey();
  assert.equal(j.status["w2:handling"], "started", "vid Något nytt krävs Vad är det, och varför passar inte de tre?");
  await p.put("w2", "handling.nytt", "Det handlar om min egen chef.");
  j = await p.journey();
  assert.equal(j.status["w2:handling"], "done");
  assert.equal(j.entries["w1:forandring.mal_1"].value, AREA_TEXT, "Något nytt ändrar inte de tre områdena");
  await p.moveTo(null);
});

test("v2: Ja, Delvis och Nej. Nej kan räknas som klart utan att något gjordes", async () => {
  const p = await participant("deltagare-b1");
  await p.put("w1", "handling.omrade", "2");
  assert.equal((await p.put("w1", "vad-hande.blev", "Nej")).status, 200);
  await p.put("w1", "vad-hande.stoppade", PRIVATE);
  await p.put("w1", "vad-hande.nasta", "Gör något mindre.");
  let j = await p.journey();
  assert.equal(j.status["w1:vad-hande"], "done");
  assert.ok(!j.entries["w1:vad-hande.gjorde_faktiskt"], "inget krav på att skriva att något gjordes");
  // Byte till Ja: nu krävs vad som gjordes. Nej-texten ligger kvar men räknas inte.
  await p.put("w1", "vad-hande.blev", "Ja");
  j = await p.journey();
  assert.equal(j.status["w1:vad-hande"], "started");
  await p.put("w1", "vad-hande.gjorde_faktiskt", "Jag frågade.");
  await p.put("w1", "vad-hande.hande", "Hon svarade.");
  await p.put("w1", "vad-hande.markte", "Ja");
  j = await p.journey();
  assert.equal(j.status["w1:vad-hande"], "started", "Vad bygger du det på? krävs vid Ja");
  await p.put("w1", "vad-hande.bygger", "Hon sa det.");
  j = await p.journey();
  assert.equal(j.status["w1:vad-hande"], "done");
  assert.equal(j.entries["w1:vad-hande.stoppade"].value, PRIVATE, "ingen data skrivs över");
  await p.put("w1", "vad-hande.blev", "Delvis");
  assert.equal((await p.journey()).status["w1:vad-hande"], "done");
  await p.put("w1", "vad-hande.blev", "Nej");
});

test("v2: två Nej i rad visar privat fråga. Inget går till Jan eller admin. Inte nu stänger.", async () => {
  const p = await participant("deltagare-b1"); // vecka 1 är Nej sedan förra testet
  const jan = client(await signIn("jan-handledare"));
  const admin = client(await signIn("programadmin"));
  await p.moveTo("w3");
  const eventsBefore = countRows("lr_event");
  const talkBefore = countRows("lr_talk_request");
  assert.equal((await p.journey()).support.promptFor, null, "ett Nej räcker inte");
  // Uteblivet svar i vecka 2 är inget Nej.
  await p.put("w3", "vad-hande.blev", "Nej");
  assert.equal((await p.journey()).support.promptFor, null, "vecka 2 saknar svar, följden är bruten");
  await p.put("w2", "vad-hande.blev", "Nej");
  await p.put("w2", "vad-hande.stoppade", PRIVATE);
  const j = await p.journey();
  assert.equal(j.support.promptFor, "w3");
  // Att rutan visas registreras inte och når ingen.
  for (let i = 0; i < 3; i += 1) await p.journey();
  assert.equal(countRows("lr_support_prompt"), 0, "att rutan visas sparas aldrig");
  assert.equal(countRows("lr_talk_request"), talkBefore);
  const janView = JSON.stringify((await jan.get("/api/facilitator/shared")).body);
  assert.ok(!janView.includes(PRIVATE) && !/support|prompt|promptFor|Nej/.test(janView), "Jan ser ingen privat signal");
  const lena = JSON.parse(janView).cohorts.find((c) => c.id === "grupp-b").participants.find((x) => x.name.startsWith("Lena"));
  assert.equal(lena.talkRequestedAt, null);
  const adminView = JSON.stringify((await admin.get("/api/admin/overview")).body);
  assert.ok(!adminView.includes(PRIVATE) && !/support|prompt|talk|Nej/.test(adminView), "admin ser ingen privat signal");
  // Order 015: rutans text når varken Jan eller administratören.
  for (const line of SUPPORT_PROMPT.lines) {
    assert.ok(!janView.includes(line), `Jans vy innehåller rutans text: ${line}`);
    assert.ok(!adminView.includes(line), `administratörens vy innehåller rutans text: ${line}`);
  }
  const newEvents = db.prepare("SELECT event_name FROM lr_event WHERE id > (SELECT IFNULL(MAX(id), 0) - ? FROM lr_event)").all(countRows("lr_event") - eventsBefore);
  assert.ok(newEvents.every((e) => ["week_started", "section_completed", "action_chosen", "what_happened_completed"].includes(e.event_name)), "inga händelser om vägledningen");
  // Fel följd kan inte besvaras.
  assert.equal((await p.c.put(`/api/journey/${p.enr}/support`, { action: "not_now", step: "w1" })).status, 409);
  assert.equal((await p.c.put(`/api/journey/${p.enr}/support`, { action: "maybe", step: "w3" })).status, 400);
  // Inte nu
  const notNow = await p.c.put(`/api/journey/${p.enr}/support`, { action: "not_now", step: "w3" });
  assert.equal(notNow.status, 200);
  assert.equal(notNow.body.support.promptFor, null);
  assert.equal(countRows("lr_talk_request"), talkBefore, "Inte nu skickar ingenting");
  assert.equal(JSON.parse(JSON.stringify((await jan.get("/api/facilitator/shared")).body)).cohorts.find((c) => c.id === "grupp-b").participants.find((x) => x.name.startsWith("Lena")).talkRequestedAt, null);
  // Tredje Nej: ingen ny ruta förrän en ny följd av två.
  await p.moveTo("w4");
  await p.put("w4", "vad-hande.blev", "Nej");
  assert.equal((await p.journey()).support.promptFor, null);
  await p.moveTo("w5");
  await p.put("w5", "vad-hande.blev", "Nej");
  assert.equal((await p.journey()).support.promptFor, "w5", "en ny följd av två Nej visar rutan igen");
});

test("v2: Be om ett samtal. Jan får bara namn, grupp och önskemål", async () => {
  const p = await participant("deltagare-b1");
  const jan = client(await signIn("jan-handledare"));
  const admin = client(await signIn("programadmin"));
  const out = await p.c.put(`/api/journey/${p.enr}/support`, { action: "request", step: "w5" });
  assert.equal(out.status, 200);
  assert.equal(out.body.support.promptFor, null);
  assert.ok(out.body.support.talkRequestedAt);
  const rows = db.prepare("SELECT * FROM lr_talk_request WHERE enrollment_id = ?").all(p.enr);
  assert.equal(rows.length, 1);
  assert.deepEqual(Object.keys(rows[0]).sort(), ["created_at", "enrollment_id", "id"], "förfrågan bär ingen text och ingen källa");
  const view = (await jan.get("/api/facilitator/shared")).body;
  const cohort = view.cohorts.find((c) => c.id === "grupp-b");
  const lena = cohort.participants.find((x) => x.name.startsWith("Lena"));
  assert.equal(cohort.name, "Grupp B");
  assert.ok(lena.talkRequestedAt, "Jan ser att Lena vill boka ett samtal");
  assert.deepEqual(Object.keys(lena).sort(), ["name", "shared", "talkRequestedAt"]);
  const text = JSON.stringify(view);
  assert.ok(!text.includes(PRIVATE) && !text.includes("Gör något mindre."), "ingen fritext följer med");
  assert.ok(!/"blev"|Nej/.test(text), "inget svar på Blev det av? följer med");
  assert.ok(!/talk|samtal/i.test(JSON.stringify((await admin.get("/api/admin/overview")).body)), "admin ser inga samtalsförfrågningar");
  await p.moveTo(null);
});

test("v2: Be om ett samtal från sidan Samtal med Jan. Flera grupper hålls isär", async () => {
  const p = await participant("deltagare-a3"); // Grupp A
  const out = await p.c.put(`/api/journey/${p.enr}/talk-request`, {});
  assert.equal(out.status, 200);
  assert.ok(out.body.support.talkRequestedAt);
  assert.equal((await p.c.put(`/api/journey/${p.enr}/talk-request`, { text: PRIVATE })).status, 400, "ingen fritext kan skickas med");
  // En handledare för bara Grupp B ser inte förfrågan från Grupp A.
  const { randomUUID } = await import("node:crypto");
  const { hashToken } = await import("../server/app.mjs");
  const id = randomUUID();
  db.prepare("INSERT INTO lr_user (id, email, display_name) VALUES (?, ?, ?)").run(id, "hb@prototyp.luf", "Handledare B");
  db.prepare("INSERT INTO lr_role_grant (user_id, role, cohort_id) VALUES (?, 'facilitator', 'grupp-b')").run(id);
  db.prepare("INSERT INTO lr_prototype_login (token_hash, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)").run(hashToken("hb-token"), id, clock.toISOString(), "2099-01-01T00:00:00Z");
  const res = await fetch(`${base}/login?t=hb-token`, { redirect: "manual" });
  const hb = client(res.headers.get("set-cookie").split(";")[0]);
  const view = (await hb.get("/api/facilitator/shared")).body;
  assert.deepEqual(view.cohorts.map((c) => c.id), ["grupp-b"]);
  assert.ok(!JSON.stringify(view).includes("Karim"));
  // En annan deltagare kan inte be om samtal i någon annans namn.
  const anna = await participant("deltagare-a2");
  assert.equal((await anna.c.put(`/api/journey/${p.enr}/talk-request`, {})).status, 404);
  assert.equal((await anna.c.put(`/api/journey/${p.enr}/support`, { action: "request", step: "w2" })).status, 404);
});

test("v2: dela, läs som Jan, återkalla, Jan saknar åtkomst efteråt. Området visas som nummer.", async () => {
  const p = await participant("deltagare-a2");
  const jan = client(await signIn("jan-handledare"));
  await p.put("w1", "handling.gora", "DELAD-PLAN-51");
  const shared = await p.c.put(`/api/journey/${p.enr}/share`, { step: "w1", section: "handling", kind: "share_with_facilitator", active: true });
  assert.equal(shared.status, 200);
  let view = JSON.stringify((await jan.get("/api/facilitator/shared")).body);
  assert.ok(view.includes("DELAD-PLAN-51"), "Jan läser det delade");
  assert.ok(view.includes("Förändringsområde 1"), "området visas som nummer");
  assert.ok(!view.includes(AREA_TEXT), "områdets egen text står i ett privat moment och delas inte");
  await p.c.put(`/api/journey/${p.enr}/share`, { step: "w1", section: "handling", kind: "share_with_facilitator", active: false });
  view = JSON.stringify((await jan.get("/api/facilitator/shared")).body);
  assert.ok(!view.includes("DELAD-PLAN-51"), "efter återkallelse saknar Jan åtkomst");
  // Ta med till nästa träff är privat.
  await p.c.put(`/api/journey/${p.enr}/share`, { step: "w1", section: "handling", kind: "bring_to_session", active: true });
  assert.ok(!JSON.stringify((await jan.get("/api/facilitator/shared")).body).includes("DELAD-PLAN-51"));
  // Privata moment går inte att dela.
  for (const [step, section] of [["w1", "privat"], ["w1", "manniskor"], ["w1", "triangel"], ["w4", "halvvags"], ["w4", "trygghet"], ["start", "efter"], ["samtal", "efter"], ["d30", "karta"]]) {
    assert.equal((await p.c.put(`/api/journey/${p.enr}/share`, { step, section, kind: "share_with_facilitator", active: true })).status, 400, `${step}:${section}`);
  }
});

test("v2: Spegeln sparar bara roll och egen reflektion", async () => {
  for (const key of ["w4", "w6"]) {
    const sp = getSection(key, "spegel");
    assert.deepEqual(sp.fields.map((f) => [f.key, f.kind]), [["vem", "choice"], ["tog_med", "text"]]);
    assert.deepEqual(sp.fields[0].options, ["Medarbetare", "Kollega", "Egen chef", "Annan"]);
    assert.equal(sp.fields[1].label, "Vad tog du med dig från samtalet?");
  }
  assert.ok(getSection("w6", "spegel").lead.includes("Fråga samma person som förra gången. Eller någon ny."));
  const p = await participant("deltagare-a2");
  await p.moveTo("w4");
  assert.equal((await p.put("w4", "spegel.vem", "Anna Andersson")).status, 400, "inget namn kan sparas som vem");
  assert.equal((await p.put("w4", "spegel.vem", "A.A.")).status, 400, "ingen initial kan sparas som vem");
  assert.equal((await p.put("w4", "spegel.namn", "Anna")).status, 400, "det finns inget namnfält");
  assert.equal((await p.put("w4", "spegel.vem", "Kollega")).status, 200);
  await p.put("w4", "spegel.tog_med", "Att jag avbryter.");
  assert.equal((await p.journey()).status["w4:spegel"], "done");
  await p.moveTo(null);
});

test("v2: vecka 2 visar Hur står du kvar? bara för beslut, nej och besked. Frivillig.", async () => {
  const sec = getSection("w2", "triangel");
  const f = sec.fields.find((x) => x.key === "sta_kvar");
  assert.ok(f.optional);
  const vis = (galler) => rules.visibleFields("w2", sec, entriesOf({ "w2:triangel.galler": galler })).some((x) => x.key === "sta_kvar");
  assert.equal(vis("Ett samtal"), false);
  assert.equal(vis("Något annat jag behöver kliva fram i"), false);
  for (const g of ["Ett beslut", "Ett nej", "Ett besked"]) assert.equal(vis(g), true, g);
  const p = await participant("deltagare-a3");
  await p.moveTo("w2");
  for (const [k, v] of [["galler", "Ett beslut"], ["vad_det_ar", "Omorganisationen, tre veckor."], ["radsla", "a"], ["mod_t", "b"], ["ansvar_leder", "c"], ["obehag_risk", "d"]]) await p.put("w2", `triangel.${k}`, v);
  assert.equal((await p.journey()).status["w2:triangel"], "done", "G4 krävs inte");
  await p.moveTo(null);
});

test("v2: vecka 4 När stödet inte räcker. Kryssrutan gör båda fälten obligatoriska.", async () => {
  const sec = getSection("w4", "samtalet");
  const info = sec.fields.find((f) => f.key === "stod_racker");
  assert.equal(info.title, "När stödet inte räcker");
  assert.equal(info.lines[2], "Om det kan påverka anställningen, eller behöver hanteras formellt: ta stöd i organisationens rutiner och hos rätt kompetens innan du går vidare.");
  const p = await participant("deltagare-b2");
  await p.moveTo("w4");
  for (const [k, v] of [["med_vem", "Någon jag har ansvar för"], ["observerat", "Sen tre gånger."], ["konflikt", "a"], ["losning", "b"], ["ansvar_k", "c"]]) await p.put("w4", `samtalet.${k}`, v);
  assert.equal((await p.journey()).status["w4:samtalet"], "done");
  await p.put("w4", "samtalet.pagatt", "ja");
  assert.equal((await p.journey()).status["w4:samtalet"], "started");
  await p.put("w4", "samtalet.gjorts", "Två samtal.");
  await p.put("w4", "samtalet.sitter", "Otydliga förväntningar.");
  assert.equal((await p.journey()).status["w4:samtalet"], "done");
  const jam = rules.visibleFields("w4", sec, entriesOf({ "w4:samtalet.med_vem": "En jämbördig kollega" }));
  assert.ok(sec.fields.find((f) => f.key === "jambordig").showWhen.in.includes("En jämbördig kollega") && jam.length > 0);
  await p.moveTo(null);
});

test("v2: vecka 5 tre vägar som villkorade flöden, utan Katalysatorlogik", async () => {
  const sec = getSection("w5", "handling");
  assert.deepEqual(sec.fields.find((f) => f.key === "vag").options, ["Skapar det som saknas", "Lämnar över ett resultat", "Lyfter det uppåt"]);
  assert.ok(!sec.fields.some((f) => f.key === "gora"), "I2 används inte i vecka 5");
  const vis = (vag) => rules.visibleFields("w5", sec, entriesOf({ "w5:handling.vag": vag, "w5:handling.omrade": "1" })).map((f) => f.key);
  assert.deepEqual(vis("Skapar det som saknas"), ["omrade", "vag", "skapa", "marks", "nar"]);
  assert.deepEqual(vis("Lämnar över ett resultat"), ["omrade", "vag", "resultat", "ramar", "marks", "nar"]);
  assert.deepEqual(vis("Lyfter det uppåt"), ["omrade", "vag", "chef_veta", "hur_saga", "marks", "nar"]);
  const p = await participant("deltagare-b2");
  await p.moveTo("w5");
  for (const [k, v] of [["omrade", "3"], ["vag", "Lyfter det uppåt"], ["chef_veta", "Att resurserna saknas."], ["marks", "Chefen frågar."], ["nar", "2026-10-20"]]) await p.put("w5", `handling.${k}`, v);
  assert.equal((await p.journey()).status["w5:handling"], "started");
  await p.put("w5", "handling.hur_saga", "Som ett bidrag.");
  assert.equal((await p.journey()).status["w5:handling"], "done");
  const text = JSON.stringify(STEPS.find((s) => s.key === "w5"));
  assert.ok(!/kataly|systemkonsekvens|Följ konsekvensen|Vad har vi själva skapat/i.test(text));
  await p.moveTo(null);
});

test("v2: vecka 6 följs upp vid 30 dagar och planen låses där", async () => {
  const p = await participant("deltagare-b2");
  await p.moveTo("w6");
  assert.equal((await p.put("w6", "stanna.tog_hand", "Länge sedan.")).status, 200);
  assert.equal((await p.put("w6", "vad-hande.blev", "Ja")).status, 400, "vecka 6 har ingen egen Vad hände?");
  assert.equal((await p.put("w6", "avslut.lofte", "Jag lovar")).status, 400, "inget ledarskapslöfte");
  await p.put("w6", "trycket.nar_trycket", "När tidplanen spricker.");
  for (const [k, v] of [["omrade", "1"], ["gora", "Fortsätta fråga först."], ["marks", "Teamet."], ["nar", "2026-11-01"]]) await p.put("w6", `handling.${k}`, v);
  let j = await p.journey();
  assert.equal(j.status["w6:trycket"], "done");
  assert.equal(j.status["w6:handling"], "done");
  assert.equal(j.locked["w6:handling"], undefined);
  await p.moveTo("d30");
  assert.equal((await p.put("d30", "kvar.blev", "Delvis")).status, 200);
  assert.equal((await p.put("w6", "handling.gora", "Ändrad")).status, 423, "planen låses när 30 dagar har besvarats");
  await p.put("d30", "kvar.hande_markte", "Två frågade tillbaka.");
  await p.put("d30", "kvar.fortfarande", "Jag frågar först.");
  await p.put("d30", "kvar.nasta_steg", "Boka samtalet.");
  j = await p.journey();
  assert.equal(j.status["d30:kvar"], "done", "frivilliga frågor krävs inte");
  await p.put("d30", "kvar.blev", "Nej");
  assert.equal((await p.journey()).status["d30:kvar"], "started", "vid Nej krävs Vad stoppade dig?");
  await p.put("d30", "kvar.stoppade", "Tid.");
  assert.equal((await p.journey()).status["d30:kvar"], "done");
  const me = (await p.c.get("/api/me")).body;
  assert.equal(me.enrollments[0].reunion.durationMinutes, 60, "återträffen är 60 minuter");
  await p.moveTo(null);
});

// ---------- Integritet per roll ----------

test("v2 integritet: admin ser grupper, datum, deltagare, status, påbörjade veckor och träffar. Aldrig text.", async () => {
  const admin = client(await signIn("programadmin"));
  const out = (await admin.get("/api/admin/overview")).body;
  const a = out.cohorts.find((c) => c.id === "grupp-a");
  assert.ok(a.startDate && a.endDate && a.status && a.liveSessions.length === 7);
  assert.deepEqual(Object.keys(a.participants[0]).sort(), ["email", "lastActivityAt", "name", "startedSteps", "status"]);
  const text = JSON.stringify(out);
  // Fritext. Datum är inga texter och kan sammanfalla med träffarnas datum.
  const values = db.prepare("SELECT value FROM lr_entry WHERE length(value) > 3").all().map((r) => r.value).filter((v) => !/^\d{4}-\d{2}-\d{2}$/.test(v));
  for (const v of values) assert.ok(!text.includes(v), `admin ser text: ${v}`);
  for (const forbidden of ['"Kollega"', '"Nej"', '"Delvis"', '"Ja"', "talk", "support", "prompt"]) {
    assert.ok(!text.includes(forbidden), `admin ser ${forbidden}`);
  }
  const started = out.cohorts.flatMap((c) => c.participants.flatMap((p) => p.startedSteps));
  assert.ok(started.every((s) => /^w[1-6]$|^d30$/.test(s)), "bara veckor, aldrig startsamtal eller samtal");
});

test("v2 integritet: arbetsgivaren har ingen roll och ingen läsväg. Ingen dold journal.", () => {
  const roleCheck = db.prepare("SELECT sql FROM sqlite_master WHERE name = 'lr_role_grant'").get().sql;
  assert.match(roleCheck, /role IN \('platform_admin', 'program_admin', 'facilitator'\)/);
  const tables = db.prepare("SELECT name FROM sqlite_master WHERE type = 'table'").all().map((t) => t.name);
  assert.ok(!tables.some((t) => /note|journal|anteckning|employer|arbetsgivare|report/i.test(t)), `tabeller: ${tables.join(", ")}`);
  const cols = (t) => db.prepare(`PRAGMA table_info(${t})`).all().map((c) => c.name);
  assert.deepEqual(cols("lr_talk_request").sort(), ["created_at", "enrollment_id", "id"]);
  assert.deepEqual(cols("lr_support_prompt").sort(), ["choice", "created_at", "enrollment_id", "id", "streak_end_step"]);
});

test("v2 integritet: privat systemlogik exponeras bara för deltagaren själv", async () => {
  const lena = await participant("deltagare-b1");
  const oskar = await participant("deltagare-b2");
  assert.equal((await oskar.c.get(`/api/journey/${lena.enr}`)).status, 404);
  const own = await oskar.journey();
  assert.ok(!JSON.stringify(own).includes(PRIVATE));
  const jan = client(await signIn("jan-handledare"));
  assert.equal((await jan.get(`/api/journey/${lena.enr}`)).status, 404, "Jan når aldrig resan direkt");
});

test("v2: befintliga nycklar ändras aldrig. Gamla svar ligger kvar och visas inte.", async () => {
  const p = await participant("deltagare-a3");
  const { randomUUID } = await import("node:crypto");
  // Ett svar sparat i version 1 under en pensionerad nyckel.
  db.prepare("INSERT INTO lr_entry (enrollment_id, step_key, field_key, value, revision, created_at, updated_at) VALUES (?, 'w6', 'avslut.lofte', ?, 1, ?, ?)").run(
    p.enr, "GAMMALT-LOFTE", clock.toISOString(), clock.toISOString(),
  );
  const j = await p.journey();
  assert.equal(j.entries["w6:avslut.lofte"].value, "GAMMALT-LOFTE", "datan ligger kvar");
  await p.moveTo("w6");
  assert.equal((await p.put("w6", "avslut.lofte", "nytt")).status, 400, "pensionerade nycklar kan inte skrivas");
  assert.equal((await p.journey()).entries["w6:avslut.lofte"].value, "GAMMALT-LOFTE", "och skrivs aldrig över");
  await p.moveTo(null);
  assert.ok(!JSON.stringify(publicProgram()).includes('"lofte"'), "fältet finns inte i version 2");
  assert.ok(randomUUID());
});

test("v2: migrationen är additiv. En databas från version 1 behåller alla svar.", async () => {
  const { DatabaseSync } = await import("node:sqlite");
  const { readFileSync, mkdtempSync } = await import("node:fs");
  const { join } = await import("node:path");
  const { tmpdir } = await import("node:os");
  const path = join(mkdtempSync(join(tmpdir(), "lr-v1-")), "v1.db");
  const old = new DatabaseSync(path);
  old.exec("PRAGMA foreign_keys = ON; CREATE TABLE lr_migration (name TEXT PRIMARY KEY, applied_at TEXT NOT NULL)");
  for (const f of ["0001_ledarskapsresa.sql", "0002_testlage.sql"]) {
    old.exec(readFileSync(new URL(`../server/migrations/${f}`, import.meta.url), "utf8"));
    old.prepare("INSERT INTO lr_migration VALUES (?, ?)").run(f, "2026-09-01");
  }
  seed(old, { today: clock });
  const enr = old.prepare("SELECT id FROM lr_enrollment LIMIT 1").get().id;
  const ins = old.prepare("INSERT INTO lr_entry (enrollment_id, step_key, field_key, value, revision, created_at, updated_at) VALUES (?, ?, ?, ?, 3, 'x', 'x')");
  ins.run(enr, "w1", "handling.prova", "V1-PLAN");
  ins.run(enr, "w6", "avslut.lofte", "V1-LOFTE");
  const before = old.prepare("SELECT * FROM lr_entry ORDER BY id").all();
  old.close();
  const migrated = openDb(path);
  assert.deepEqual(migrated.prepare("SELECT * FROM lr_entry ORDER BY id").all(), before, "inga svar ändrade");
  assert.ok(migrated.prepare("SELECT 1 FROM lr_migration WHERE name = '0003_lmhm_v2.sql'").get());
  migrated.close();
});
