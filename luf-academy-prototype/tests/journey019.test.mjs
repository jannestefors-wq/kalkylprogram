// Ledarskap med hjärta och mod, version 2. Order 019: pedagogisk resa och tre månader.
// Vägledningen är information. Inga nya fält i vecka 1 till 6. Tre månader öppnas
// efter datum, är privat som standard och kan delas aktivt med Jan. Kartan aldrig.
import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { readFileSync } from "node:fs";
import { openDb } from "../server/db.mjs";
import { createApp } from "../server/app.mjs";
import { seed } from "../scripts/seed.mjs";
import { STEPS, publicProgram, getSection, JOURNEY_STORY } from "../server/content.mjs";
import * as rules from "../server/rules.mjs";

const CLIENT = readFileSync(new URL("../public/app.js", import.meta.url), "utf8");
const BASELINE = JSON.parse(readFileSync(new URL("./fixtures/lmhm-v2-fields-015.json", import.meta.url), "utf8"));
const WEEKS = ["w1", "w2", "w3", "w4", "w5", "w6"];
const step = (k) => STEPS.find((s) => s.key === k);
const sectionsOf = (kind) => STEPS.flatMap((s) => s.sections.filter((x) => x.kind === kind).map((x) => ({ step: s.key, section: x })));
const guide = (sec, heading) => (sec.guides || []).find((g) => g.heading === heading);
const text = (g) => JSON.stringify(g);

// ---------- Innehåll ----------

test("019: Din förändringsresa står på översikten och hela tidslinjen finns", () => {
  const p = publicProgram();
  assert.equal(p.journeyStory.title, "Din förändringsresa");
  const all = JOURNEY_STORY.paragraphs.flat();
  assert.equal(all[0], "Du börjar inte här för att lära dig fler modeller.");
  assert.ok(all.includes("Efter tre månader jämför du då och nu."));
  assert.equal(all.at(-1), "Målet är att du ska börja leda annorlunda. Och att människorna omkring dig ska kunna märka skillnaden.");
  assert.deepEqual(STEPS.filter((s) => !s.aside).map((s) => s.label), ["Vecka 1", "Vecka 2", "Vecka 3", "Vecka 4", "Vecka 5", "Vecka 6", "30 dagar", "3 månader"]);
  assert.equal(step("w1").phase, "Förstå nuläget");
  for (const s of STEPS) assert.ok(s.phase, `${s.key} har en fas`);
  // Startraden och öppningsdatumet ritas av klienten.
  assert.ok(CLIENT.includes('"Start"') && CLIENT.includes("Öppnas ${fmtOpensDate(opensAt[s.key])}"));
});

test("019: momenträknaren är sekundär. Fasen står först.", () => {
  assert.ok(CLIENT.includes("`${s.label} · ${s.phase}`"), "Vecka 1 · Förstå nuläget");
  assert.ok(CLIENT.includes('h("span", { class: "rail-count" }, `${index + 1} av ${s.sections.length}`)'), "4 av 12, mindre");
  assert.ok(!CLIENT.includes("h(\"summary\", {}, `Moment ${index + 1}"), "Moment X av Y är inte längre det första ögat möter");
});

test("019: vecka 1 är nuläget", () => {
  const intro = getSection("w1", "intro");
  assert.equal(intro.title, "Människan först");
  assert.equal(intro.lead[0], "Den här veckan börjar vi inte med att förändra dig.");
  assert.ok(intro.lead.includes("Det här är inte en diagnos."));
  assert.equal(intro.lead.at(-1), "Först när du ser nuläget kan du välja vad du faktiskt vill förändra.");
  assert.ok(!intro.lead.includes("Ledarskap börjar inte med modellen."));
});

test("019: alla sex lässidor har ett tydligt syfte", () => {
  const first = {
    w1: "De här sidorna hjälper dig att börja känna igen ditt eget ledarskap.",
    w2: "Den här veckan tittar vi på det du redan vet behöver hända men ändå skjuter upp.",
    w3: "Vi tränar på att skilja det du faktiskt vet från det du tolkar.",
    w4: "Ett svårt samtal fungerar sällan bättre för att vi väntar.",
    w5: "När något inte fungerar är det lätt att börja med personen.",
    w6: "Det är lättare att leda som man vill när allt fungerar.",
  };
  for (const w of WEEKS) {
    const g = guide(getSection(w, "lasning"), "Varför läser du det här?");
    assert.ok(g, `${w}: lässyfte`);
    assert.equal(g.lines[0], first[w]);
    assert.ok(getSection(w, "lasning").reading.chapters.length > 0, `${w}: kapitlen finns kvar`);
  }
});

test("019: pedagogiska introduktioner i den gemensamma motorn", () => {
  const every = (kind, heading, must, weeks = 6) => {
    const list = sectionsOf(kind).filter((x) => WEEKS.includes(x.step));
    assert.equal(list.length, weeks, kind);
    for (const { step: s, section } of list) {
      const g = guide(section, heading);
      assert.ok(g, `${s}:${section.key} saknar ${heading}`);
      for (const m of must) assert.ok(text(g).includes(m), `${s}:${section.key}: ${m}`);
    }
  };
  // Stanna upp
  for (const w of WEEKS) assert.ok(text(guide(getSection(w, "stanna"), "Varför stannar vi här?")).includes("De finns för att sakta ner det automatiska svaret."), w);
  // Handlingen
  every("action", "Här lämnar utbildningen skärmen", ["Det här är inte en skrivövning.", "Det är först då vi vet något.", "och när du ska göra det."]);
  // Vad hände? Vecka 6 fylls i vid 30 dagar.
  every("return", "Här finns lärandet", ["Nu jämför vi inte med vad du ville göra.", "Skriv verkligheten. Inte den snyggaste versionen av den."], 5);
  // Träffen
  every("live", "Vad händer på träffen?", ["Du träffar Jan och din grupp online.", "Gruppen består av högst sex deltagare.", "Det som delas i gruppen stannar i gruppen."]);
  // Spegeln
  for (const w of ["w4", "w6"]) assert.ok(text(guide(getSection(w, "spegel"), "Varför gör vi det här?")).includes("Du ber om en spegel."), w);
  // Kartan, tre saker, människorna, situationen
  assert.ok(guide(getSection("w1", "karta"), "Varför gör du kartan?"));
  assert.ok(guide(getSection("w1", "forandring"), "Vad letar vi efter?"));
  assert.ok(guide(getSection("w1", "manniskor"), "Varför tittar vi på människorna runt dig?"));
  assert.ok(guide(getSection("w1", "situation"), "Varför delar vi upp situationen?") && guide(getSection("w1", "situation"), "Så gör du"));
  // Vecka 4, 5 och 6
  assert.ok(text(guide(getSection("w4", "intro"), "Vad är målet den här veckan?")).includes("Målet är inte att bli bekväm med svåra samtal."));
  assert.ok(guide(getSection("w5", "intro"), "Vad är målet den här veckan?"));
  assert.equal(getSection("w6", "intro").lead[0], "Sista veckan handlar om vad som håller när pressen kommer tillbaka.");
  assert.ok(text(guide(getSection("w6", "tillbaka"), "Nu jämför du med dig själv")).includes("och vad som fortfarande testar dig."));
});

test("019: startsamtalet, Samtal med Jan och 30 dagar", () => {
  const infor = getSection("start", "infor");
  assert.ok(text(guide(infor, "Vad är startsamtalet?")).includes("Det du säger förs inte vidare till din arbetsgivare inom utbildningen."));
  assert.ok(guide(infor, "Inför frågorna"));
  assert.ok(text(infor.guides.find((g) => g.example)).includes("Jag leder fem personer."));
  const efter = getSection("start", "efter");
  assert.ok(guide(efter, "Varför skriver du efter samtalet?"));
  assert.ok(text(efter.guides.find((g) => g.example)).includes("Jag bokar samtalet före fredag."));
  const talk = getSection("samtal", "behov");
  const g = guide(talk, "Vad är Samtal med Jan?");
  assert.ok(text(g).includes("Samtalet är inte terapi och inte en bedömning."));
  assert.ok(text(g).includes("Jan tar inte över problemet."));
  const d30 = getSection("d30", "intro");
  assert.equal(d30.title, "Vad blev faktiskt kvar?");
  assert.ok(d30.lead.includes("Nu tittar vi på vad som överlevde vardagen."));
  assert.equal(d30.lead.at(-1), "Inte med det du hade hoppats skulle hända.");
});

test("019: varje triangel har en exempelruta. Alla exempel märks Exempel, inte facit.", () => {
  const triangles = sectionsOf("triangle");
  assert.equal(triangles.length, 8);
  for (const { step: s, section } of triangles) {
    const ex = (section.guides || []).find((g) => g.example);
    assert.ok(ex, `${s}:${section.key} saknar exempel`);
    assert.ok(ex.sub, `${s}:${section.key}: hörnorden står i exemplet`);
  }
  assert.ok(text(getSection("w3", "se-hora-kanna").guides).includes("De tre första är material. Den sista är din slutsats."));
  for (const s of STEPS) for (const sec of s.sections) for (const g of sec.guides || []) {
    if (g.example) assert.equal(g.label, "Exempel, inte facit", `${s.key}:${sec.key}`);
    else assert.ok(g.heading, `${s.key}:${sec.key}: vägledning har rubrik`);
    assert.ok(!("key" in g) && !("fields" in g), `${s.key}:${sec.key}: vägledning har inga fält`);
  }
});

test("019: inga nya fält i vecka 1 till 6. Befintliga nycklar och klarregler är oförändrade.", () => {
  const now = {};
  for (const s of STEPS) for (const sec of s.sections) {
    for (const f of sec.fields || []) if (f.kind !== "info") now[`${s.key}:${sec.key}.${f.key}`] = { kind: f.kind, optional: Boolean(f.optional), showWhen: f.showWhen ? JSON.stringify(f.showWhen) : null };
    if (sec.doneWhen) now[`${s.key}:${sec.key}#doneWhen`] = JSON.stringify(sec.doneWhen);
    if (sec.shareable) now[`${s.key}:${sec.key}#shareable`] = true;
  }
  for (const [k, v] of Object.entries(BASELINE)) assert.deepEqual(now[k], v, `ändrad: ${k}`);
  const added = Object.keys(now).filter((k) => !(k in BASELINE));
  assert.ok(added.length > 0 && added.every((k) => k.startsWith("m3:")), `nya nycklar utanför tre månader: ${added.filter((k) => !k.startsWith("m3:"))}`);
});

test("019: tre månader. Titel, texter och fält enligt ordern.", () => {
  const m3 = step("m3");
  assert.equal(m3.title, "Tre månader. Då och nu.");
  assert.deepEqual(m3.opensAfterEnd, { months: 3 });
  assert.deepEqual(m3.sections.map((s) => s.key), ["intro", "minns", "da-och-nu", "karta"]);
  assert.equal(getSection("m3", "intro").lead[0], "Tre månader har gått sedan utbildningen.");
  const r = getSection("m3", "da-och-nu");
  const f = Object.fromEntries(r.fields.map((x) => [x.key, x]));
  assert.equal(f.gor_annorlunda.label, "Vad gör du annorlunda idag än när utbildningen började?");
  assert.equal(f.gor_annorlunda.hint, "Beskriv något du faktiskt gör annorlunda.");
  assert.equal(f.samma_satt.optional, true);
  assert.equal(f.lattare.hint, "Något som börjar kännas mer naturligt i vardagen.");
  assert.deepEqual(f.markt.options, ["Ja", "Nej", "Jag vet inte"]);
  assert.deepEqual(f.markt_bygger.showWhen, { field: "markt", in: ["Ja"] });
  assert.equal(f.faller_tillbaka.optional, true);
  assert.equal(f.fortsatta_3m.hint, "En sak. Konkret nog för att kunna märkas.");
  assert.equal(r.shareable, true);
  const map = getSection("m3", "karta");
  assert.equal(map.title, "Min ledarskapskarta. Tre månader.");
  assert.equal(map.measurePoint, "m3");
  assert.ok(!map.shareable, "kartan kan aldrig delas");
  assert.ok(!map.doneWhen, "kartan är frivillig");
  assert.equal(map.compareAfterDone, true);
  assert.deepEqual(map.compareWith, ["start", "end", "d30"]);
});

test("019: tre månaders låsdatum räknas i kalendermånader", () => {
  assert.equal(rules.addMonths("2026-11-03", 3), "2027-02-03");
  assert.equal(rules.addMonths("2026-11-30", 3), "2027-02-28");
  assert.equal(rules.addMonths("2026-10-31", 3), "2027-01-31");
  assert.equal(rules.addMonths("2027-11-30", 3), "2028-02-29");
  const ctx = (today, testMode = false) => ({ endDate: "2026-11-03", today, testMode });
  assert.equal(rules.isStepOpen(STEPS, "m3", "d30", ctx("2027-02-02")), false, "dagen före");
  assert.equal(rules.isStepOpen(STEPS, "m3", "d30", ctx("2027-02-03")), true, "på dagen");
  assert.equal(rules.isStepOpen(STEPS, "m3", "m3", ctx("2026-12-01")), false, "gruppens steg öppnar inte");
  assert.equal(rules.isStepOpen(STEPS, "m3", "m3", ctx("2026-12-01", true)), true, "testläget i testversionen");
  assert.equal(rules.isStepOpen(STEPS, "m3", "d30", ctx("2026-12-01", true)), false, "testläget måste ha nått steget");
});

// ---------- Server ----------

let server;
let base;
let db;
let links;
const clock = new Date("2026-09-23T08:00:00Z");
const TODAY = "2026-09-23";
// Klockan står still. Gruppens slutdatum flyttas så att öppningsdatumet hamnar före, på eller efter idag.
const setEnd = (ymd) => db.prepare("UPDATE lr_cohort SET end_date = ? WHERE id = 'grupp-b'").run(ymd);

before(async () => {
  db = openDb(":memory:");
  links = seed(db, { today: new Date(clock) });
  const app = createApp(db, { now: () => new Date(clock) });
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
  const put = async (stepKey, field, value) => {
    const cur = (await c.get(`/api/journey/${enr}`)).body.entries[`${stepKey}:${field}`];
    return c.put(`/api/journey/${enr}/entry`, { step: stepKey, field, value, baseRevision: cur?.revision ?? 0 });
  };
  const journey = async () => (await c.get(`/api/journey/${enr}`)).body;
  const assess = (point, dimension, value) => c.put(`/api/journey/${enr}/assessment`, { point, dimension, value });
  const share = (section, active) => c.put(`/api/journey/${enr}/share`, { step: "m3", section, kind: "share_with_facilitator", active });
  return { c, me, enr, put, journey, assess, share };
}
const adminRow = async (name) => {
  const admin = client(await signIn("programadmin"));
  const out = (await admin.get("/api/admin/overview")).body;
  return { out, row: out.cohorts.flatMap((c) => c.participants).find((p) => p.name === name) };
};

test("019 server: tre månader är låst före datumet, också när gruppen flyttas fram", async () => {
  const p = await participant("deltagare-b1");
  const end = db.prepare("SELECT c.end_date AS e FROM lr_cohort c JOIN lr_enrollment n ON n.cohort_id = c.id WHERE n.id = ?").get(p.enr).e;
  const opens = rules.addMonths(end, 3);
  const j = await p.journey();
  assert.equal(j.opensAt.m3, opens, "översikten får öppningsdatumet");
  assert.ok(!j.openSteps.includes("m3"));
  // Administratören flyttar gruppen till 30 dagar. Tre månader är fortfarande låst.
  db.prepare("UPDATE lr_cohort SET current_step = 'd30' WHERE id = 'grupp-b'").run();
  assert.ok(!(await p.journey()).openSteps.includes("m3"));
  assert.equal((await p.put("m3", "da-och-nu.gor_annorlunda", "för tidigt")).status, 403);
  assert.equal((await p.assess("m3", "narvaro", 3)).status, 403);
  // Öppningsdatumet är i morgon.
  setEnd("2026-06-24");
  assert.equal((await p.journey()).opensAt.m3, "2026-09-24");
  assert.ok(!(await p.journey()).openSteps.includes("m3"));
  assert.equal((await adminRow("Lena (fiktiv)")).row.followUp3m.status, "not_open");
  // Öppningsdatumet är idag.
  setEnd("2026-06-23");
  assert.equal((await p.journey()).opensAt.m3, TODAY);
  assert.ok((await p.journey()).openSteps.includes("m3"));
  assert.equal((await adminRow("Lena (fiktiv)")).row.followUp3m.status, "open");
});

test("019 server: klar när M1, M3, M4 och M6 är ifyllda. M4b krävs bara vid Ja.", async () => {
  const p = await participant("deltagare-b1");
  const status = async () => (await p.journey()).status["m3:da-och-nu"];
  assert.equal(await status(), "empty");
  await p.put("m3", "da-och-nu.gor_annorlunda", "M1-TEXT-3MAN");
  assert.equal((await adminRow("Lena (fiktiv)")).row.followUp3m.status, "started");
  await p.put("m3", "da-och-nu.lattare", "M3-TEXT");
  await p.put("m3", "da-och-nu.markt", "Ja");
  await p.put("m3", "da-och-nu.fortsatta_3m", "M6-TEXT");
  assert.equal(await status(), "started", "M4b krävs vid Ja");
  await p.put("m3", "da-och-nu.markt", "Nej");
  assert.equal(await status(), "done", "M4b krävs inte vid Nej. M2 och M5 är frivilliga.");
  await p.put("m3", "da-och-nu.markt", "Ja");
  await p.put("m3", "da-och-nu.markt_bygger", "M4B-TEXT");
  assert.equal(await status(), "done");
  assert.equal((await adminRow("Lena (fiktiv)")).row.followUp3m.status, "completed");
});

test("019 server: kartan efter tre månader sparas additivt och är alltid privat", async () => {
  const p = await participant("deltagare-b1");
  const before = db.prepare("SELECT * FROM lr_self_assessment ORDER BY enrollment_id, measure_point, dimension").all();
  for (const d of ["narvaro", "mod", "lyssnande", "tydlighet", "relation", "ansvar"]) assert.equal((await p.assess("m3", d, 4)).status, 200, d);
  assert.deepEqual(db.prepare("SELECT * FROM lr_self_assessment ORDER BY enrollment_id, measure_point, dimension").all(), before, "befintliga kartor orörda");
  assert.equal(db.prepare("SELECT COUNT(*) AS n FROM lr_self_assessment_followup WHERE enrollment_id = ?").get(p.enr).n, 6);
  assert.equal(Object.keys((await p.journey()).assessments.m3).length, 6, "deltagaren ser sin egen karta");
  assert.equal((await p.share("karta", true)).status, 400, "kartan kan aldrig delas");
  assert.equal((await p.share("minns", true)).status, 400);
  const jan = client(await signIn("jan-handledare"));
  assert.ok(!JSON.stringify((await jan.get("/api/facilitator/shared")).body).includes('"m3"'), "Jan ser ingen karta");
});

test("019 server: dela och återkalla Då och nu. Admin ser bara status. Ingen fritext i mätningen.", async () => {
  const p = await participant("deltagare-b1");
  const jan = client(await signIn("jan-handledare"));
  const janView = async () => JSON.stringify((await jan.get("/api/facilitator/shared")).body);
  assert.ok(!(await janView()).includes("M1-TEXT-3MAN"), "privat som standard");
  assert.equal((await p.share("da-och-nu", true)).status, 200);
  assert.ok((await janView()).includes("M1-TEXT-3MAN"), "Jan läser det som delats");
  assert.equal((await p.share("da-och-nu", false)).status, 200);
  assert.ok(!(await janView()).includes("M1-TEXT-3MAN"), "efter återkallelse saknar Jan åtkomst");

  const { out, row } = await adminRow("Lena (fiktiv)");
  assert.deepEqual(Object.keys(row.followUp3m).sort(), ["opensAt", "status"]);
  const all = JSON.stringify(out);
  for (const t of ["M1-TEXT-3MAN", "M3-TEXT", "M4B-TEXT", "M6-TEXT"]) assert.ok(!all.includes(t), `admin ser inte ${t}`);
  const events = JSON.stringify(db.prepare("SELECT * FROM lr_event").all());
  for (const t of ["M1-TEXT-3MAN", "M4B-TEXT", "M6-TEXT"]) assert.ok(!events.includes(t), "ingen fritext i mätningen");
});

test("019 server: arbetsgivaren har ingen läsväg. Uppföljningen har inga textkolumner.", () => {
  const cols = db.prepare("PRAGMA table_info(lr_self_assessment_followup)").all().map((c) => c.name).sort();
  assert.deepEqual(cols, ["assessed_at", "dimension", "enrollment_id", "id", "measure_point", "updated_at", "value"]);
  const tables = db.prepare("SELECT name FROM sqlite_master WHERE type = 'table'").all().map((t) => t.name);
  assert.ok(!tables.some((t) => /employer|arbetsgivare|report|journal/i.test(t)));
  const roleCheck = db.prepare("SELECT sql FROM sqlite_master WHERE name = 'lr_role_grant'").get().sql;
  assert.match(roleCheck, /role IN \('platform_admin', 'program_admin', 'facilitator'\)/);
});

test("019 server: i produktionsläge finns inget testläge som kan öppna tre månader", async () => {
  const prod = createApp(db, { now: () => new Date("2026-10-01T10:00:00Z"), prototype: false });
  const srv = createServer((req, res) => prod.handle(req, res));
  await new Promise((r) => srv.listen(0, "127.0.0.1", r));
  const url = `http://127.0.0.1:${srv.address().port}`;
  setEnd("2026-11-03");
  try {
    const res = await fetch(`${url}/login?t=${links["deltagare-b2"].token}`, { redirect: "manual" });
    const cookie = res.headers.get("set-cookie").split(";")[0];
    const h = { "X-LUF-Academy": "1", Cookie: cookie, "Content-Type": "application/json" };
    const me = await (await fetch(`${url}/api/me`, { headers: h })).json();
    const enr = me.enrollments[0].id;
    assert.equal((await fetch(`${url}/api/journey/${enr}/test-step`, { method: "PUT", headers: h, body: JSON.stringify({ step: "m3" }) })).status, 404);
    const j = await (await fetch(`${url}/api/journey/${enr}`, { headers: h })).json();
    assert.ok(!j.openSteps.includes("m3"), "öppnas först 2027-02-03");
    assert.equal(j.opensAt.m3, "2027-02-03");
  } finally {
    setEnd("2026-06-23");
    srv.close();
  }
});

// ---------- Order 019A ----------

test("019A: integritetstexten säger progression och status på uppföljningarna", () => {
  const text = publicProgram().privacyText;
  assert.equal(text.at(-1), "Den som administrerar utbildningen ser bara din progression, till exempel vilka veckor du har börjat och status på uppföljningarna. Aldrig det du skriver.");
  assert.ok(!JSON.stringify(publicProgram()).includes("Den som administrerar kursen"));
});

test("019A: adminstatus för tre månader heter Väntar, Tillgänglig, Påbörjad och Slutförd", () => {
  const fn = CLIENT.slice(CLIENT.indexOf("function followUpLabel"), CLIENT.indexOf("function liveSessionEditor"));
  for (const s of ['not_open: "Väntar"', 'open: "Tillgänglig"', 'started: "Påbörjad"', 'completed: "Slutförd"']) assert.ok(fn.includes(s), s);
  assert.ok(!fn.includes("Öppnad"), "inget som antyder att deltagaren har öppnat sidan");
});
