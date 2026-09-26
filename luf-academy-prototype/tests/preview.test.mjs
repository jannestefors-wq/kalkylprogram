// Förhandsvisningen av LMHM version 2, körd mot en lokal modell av claude.ai-
// sidans databas med samma åtkomstregler som publiceringen deklarerar.
// Den verkliga plattformen kontrolleras separat efter publicering.
import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { TEST_COHORT } from "../preview/testdata.mjs";

const require = createRequire(import.meta.url);
const { chromium, devices } = (() => {
  for (const p of ["playwright", "/opt/node22/lib/node_modules/playwright"]) {
    try { return require(p); } catch { /* nästa */ }
  }
  throw new Error("Playwright saknas");
})();

const OWNER = "u_jan_owner";
const OTHER = "u_annan";
const store = new Map([["testdata/cohort", structuredClone(TEST_COHORT)]]);
let offline = false;
let server, base, browser;
const external = [];

// Samma regler som publiceringen deklarerar.
function canRead(path, uid) {
  const [a, b, c] = path.split("/");
  if (a === "data" && b === "users") return c === uid;
  if (a === "shared" || a === "roster" || a === "requests") return uid === OWNER || b === uid;
  return true;
}
function canWrite(path, uid) {
  const [a, b, c] = path.split("/");
  if (a === "data" && b === "users") return c === uid;
  if (a === "shared" || a === "roster" || a === "requests") return b === uid || uid === OWNER;
  return uid === OWNER;
}
function dbCall(uid, op, path, body) {
  if (offline) throw Object.assign(new Error("unavailable"), { code: "unavailable" });
  if (op === "get") return canRead(path, uid) && store.has(path) ? { exists: true, body: store.get(path) } : { exists: false };
  if (op === "list") {
    const depth = path.split("/").length + 1;
    return [...store.entries()]
      .filter(([p]) => p.startsWith(path + "/") && p.split("/").length === depth && canRead(p, uid))
      .map(([p, b]) => ({ id: p.split("/").pop(), body: b }));
  }
  if (!canWrite(path, uid)) throw Object.assign(new Error("invalid_argument"), { code: "invalid_argument" });
  if (op === "set") store.set(path, JSON.parse(JSON.stringify(body)));
  if (op === "delete") store.delete(path);
  return null;
}

const SHIM = ({ uid, owner }) => {
  const call = async (op, path, body) => {
    const r = await window.__db(uid, op, path, body);
    if (r && r.error) throw { code: r.error, message: r.error };
    return r.value;
  };
  const snap = (id, r) => ({ id, exists: r.exists, data: () => r.body, metadata: { fromCache: false, hasPendingWrites: false } });
  const doc = (path) => ({
    id: path.split("/").pop(), path,
    get: async () => snap(path.split("/").pop(), await call("get", path)),
    set: (b) => call("set", path, b),
    delete: () => call("delete", path),
    collection: (sub) => collection(`${path}/${sub}`),
  });
  const collection = (path) => ({
    path,
    doc: (id) => doc(`${path}/${id}`),
    get: async () => {
      const rows = await call("list", path);
      const docs = rows.map((r) => snap(r.id, { exists: true, body: r.body }));
      return { docs, size: docs.length, empty: !docs.length };
    },
  });
  const user = { id: async () => uid, isOwner: async () => owner, profiles: async (ids) => Object.fromEntries([].concat(ids).map((i) => [i, { id: i, name: i === "u_annan" ? "Annan testperson" : "Jan" }])) };
  window.claude = { use: async (n) => (n === "db" ? { doc, collection } : n === "user" ? user : null) };
};

const SHOTS = new URL("../docs/skarmbilder-v2/", import.meta.url).pathname;

before(async () => {
  execFileSync("node", ["--no-warnings", "scripts/build-preview.mjs"]);
  const page = readFileSync(new URL("../preview/dist/lmhm-v2-human-test.html", import.meta.url), "utf8");
  // Samma skal som claude.ai lägger runt sidan.
  const html = `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"></head><body>${page}</body></html>`;
  server = createServer((req, res) => { res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" }); res.end(html); });
  await new Promise((r) => server.listen(0, "127.0.0.1", r));
  base = `http://127.0.0.1:${server.address().port}/`;
  browser = await chromium.launch();
  execFileSync("mkdir", ["-p", SHOTS]);
});
after(async () => { await browser?.close(); server?.close(); });

async function open(kind, uid) {
  const ctx = kind === "mobile"
    ? await browser.newContext({ ...devices["Pixel 7"], locale: "sv-SE", timezoneId: "Europe/Stockholm" })
    : await browser.newContext({ viewport: { width: 1366, height: 900 }, locale: "sv-SE", timezoneId: "Europe/Stockholm" });
  await ctx.exposeFunction("__db", (u, op, path, body) => {
    try { return { value: dbCall(u, op, path, body) }; } catch (e) { return { error: e.code || "unavailable" }; }
  });
  await ctx.addInitScript(SHIM, { uid, owner: uid === OWNER });
  const page = await ctx.newPage();
  page.on("request", (r) => { if (!r.url().startsWith(base) && !r.url().startsWith("data:")) external.push(r.url()); });
  page.errors = [];
  page.on("pageerror", (e) => page.errors.push(e.message));
  await page.goto(base);
  return { ctx, page };
}
const signIn = async (page) => {
  await page.click(".signin button");
  await page.waitForSelector(".overview");
};
const saved = (page) => page.waitForFunction(() => document.getElementById("save-status").classList.contains("is-saved"), null, { timeout: 8000 });
const type = async (page, sel, text) => { await page.fill(sel, ""); await page.type(sel, text, { delay: 2 }); };
const noSideScroll = async (page, label) => {
  const { sw, cw } = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth }));
  assert.ok(sw <= cw + 1, `${label}: sidscroll ${sw} > ${cw}`);
};
const goTo = async (page, slug, section, sel) => { await page.evaluate(([a, b]) => { location.hash = `#/${a}/${b}`; }, [slug, section]); await page.waitForSelector(sel); };
const go = (page, section, sel) => goTo(page, "vecka-1", section, sel);
const pick = async (page, field, value) => {
  await page.click(`[data-field="${field}"] .choice[data-value="${value}"]`);
  await page.waitForSelector(`[data-field="${field}"] .choice.is-on[data-value="${value}"]`);
};
const shot = (page, name) => page.screenshot({ path: `${SHOTS}${name}.png`, fullPage: true });

test("desktop: inloggning, integritet, vecka 1 med motorn, delning, utloggning och återkomst", async () => {
  const { ctx, page } = await open("desktop", OWNER);
  await page.waitForSelector(".signin");
  assert.ok((await page.textContent("#prototype-band")).includes("Testversion. LMHM version 2. Ej produktion."));
  assert.equal(await page.isVisible("#prototype-band"), false, "märkningen syns först efter inloggning");
  await signIn(page);
  assert.equal(await page.isVisible("#prototype-band"), true);
  const text = await page.textContent("main");
  for (const s of ["Testgrupp. LMHM version 2", "23 september", "Nästa träff", "Fortsätt min ledarskapsresa", "Startsamtalet", "Samtal med Jan"]) assert.ok(text.includes(s), s);
  for (const line of ["Det här är din resa.", "Inte heller med Jan.", "Den som administrerar kursen ser vilka veckor du har börjat på. Aldrig det du skriver."]) assert.ok(text.includes(line), line);
  assert.equal(await page.locator(".journey-step.is-locked").count(), 6);

  // Startsamtalet
  await goTo(page, "startsamtal", "infor", "#f-infor-skaver");
  assert.ok((await page.textContent(".section")).includes("Det du skriver här delas inte automatiskt med din arbetsgivare."));
  await type(page, "#f-infor-skaver", "SKAVER-START. Samtalet med platschefen.");
  await saved(page);
  await shot(page, "01-startsamtal-desktop");

  await page.evaluate(() => { location.hash = "#/"; });
  await page.click(".focus-card .button.primary");
  await page.waitForSelector(".section-intro");
  await page.click(".section-nav .primary");
  await page.waitForSelector(".section-reading");
  const reading = await page.textContent(".section-reading");
  assert.ok(reading.includes("Utan filter") && reading.includes("Sidor 7–15"));
  await go(page, "karta", ".map");
  const rows = page.locator(".scale-row");
  const picks = [3, 4, 2, 5, 4, 3];
  for (let i = 0; i < 6; i += 1) await rows.nth(i).locator(`.scale-dot[data-value="${picks[i]}"]`).click({ delay: 0 });
  await saved(page);
  await page.waitForTimeout(600);
  assert.deepEqual(store.get(`data/users/${OWNER}/assessments`).points.start, { narvaro: 3, mod: 4, lyssnande: 2, tydlighet: 5, relation: 4, ansvar: 3 });

  await go(page, "forandring", "#f-forandring-mal_1");
  assert.ok((await page.textContent(".section")).includes("Skriv det du själv vill förändra. Inte det du borde."));
  await type(page, "#f-forandring-mal_1", "Lyssna klart innan jag svarar.");
  await type(page, "#f-forandring-mal_1_hur", "Teamet pratar mer på mötena.");
  await type(page, "#f-forandring-mal_2", "Ta det svåra samtalet direkt.");
  await type(page, "#f-forandring-mal_3", "Säga vad jag tycker tidigt.");
  await saved(page);

  // Människorna runt mig: två rader visas, högst fyra.
  await go(page, "manniskor", ".people");
  assert.equal(await page.locator(".person").count(), 2);
  await page.click("button:has-text('Lägg till en person')");
  await page.click("button:has-text('Lägg till en person')");
  assert.equal(await page.locator(".person").count(), 4);
  assert.equal(await page.isVisible("button:has-text('Lägg till en person')"), false, "högst fyra");

  await go(page, "situation", ".situation");
  await type(page, "#f-situation-vad_hande", "Projektledaren lämnade mötet tidigt.");
  await type(page, "#f-situation-tolkning", "DELAD-TOLKNING. Jag tror att hon var missnöjd.");
  await saved(page);
  await page.click("button.toggle:has-text('Dela med Jan')");
  await page.waitForSelector("dialog[open]");
  await page.click("dialog button[value=share]");
  await page.waitForSelector("text=Delat med Jan sedan");
  await type(page, "#f-situation-gjorde_lat", "Jag fortsatte dagordningen.");
  await saved(page);

  await go(page, "privat", "#f-privat-vet_redan");
  assert.equal(await page.locator("article button:has-text('Dela med Jan')").count(), 0, "privat moment har ingen delningsknapp");
  await type(page, "#f-privat-vet_redan", "PRIVAT-REFLEKTION. Jag vet redan.");
  await saved(page);

  // Den gemensamma motorn: områdena med egna ord, och Något nytt.
  await go(page, "handling", '[data-field="omrade"]');
  const options = await page.$$eval('[data-field="omrade"] .choice', (els) => els.map((e) => e.textContent));
  assert.deepEqual(options, ["1. Lyssna klart innan jag svarar.", "2. Ta det svåra samtalet direkt.", "3. Säga vad jag tycker tidigt.", "Något nytt"]);
  await pick(page, "omrade", "nytt");
  await page.waitForSelector("#f-handling-nytt");
  assert.ok((await page.textContent('[data-field="nytt"]')).includes("Du får byta. Ibland var första gissningen fel."));
  await pick(page, "omrade", "1");
  await page.waitForSelector("#f-handling-nytt", { state: "detached" });
  await type(page, "#f-handling-gora", "Ställa en öppen fråga och vänta, på torsdagens avstämning.");
  await type(page, "#f-handling-marks", "Att fler pratar. Teamet.");
  await page.fill("#f-handling-nar", "2026-09-25");
  await page.locator("#f-handling-nar").blur();
  await saved(page);
  assert.equal(store.get(`data/users/${OWNER}/e:w1:handling.omrade`).value, "1", "området sparas som nummer");
  await shot(page, "02-vecka-1-handling-desktop");

  // Handledarvyn: bara det delade
  await page.evaluate(() => { location.hash = "#/jan"; });
  await page.waitForSelector(".role-view");
  const shared = await page.textContent("main");
  assert.ok(shared.includes("DELAD-TOLKNING") && shared.includes("Jag fortsatte dagordningen."));
  assert.ok(!shared.includes("PRIVAT-REFLEKTION") && !shared.includes("Ställa en öppen fråga") && !shared.includes("SKAVER-START"));

  // Programadmin: ingen fritext
  await page.evaluate(() => { location.hash = "#/admin"; });
  await page.waitForSelector(".role-view .table");
  const admin = await page.textContent("main");
  for (const s of ["DELAD-TOLKNING", "PRIVAT-REFLEKTION", "Ställa en öppen fråga", "SKAVER-START", "Startsamtalet"]) assert.ok(!admin.includes(s), s);
  assert.ok(admin.includes("Vecka 1"));

  // Utloggning, ny inloggning
  await page.evaluate(() => { location.hash = "#/"; });
  await page.click(".account button");
  await page.waitForSelector("text=Du är utloggad");
  await page.reload();
  await page.waitForSelector(".signin");
  await signIn(page);
  await page.waitForSelector(".focus-card.is-recall");
  assert.ok((await page.textContent(".focus-card")).includes("Ställa en öppen fråga och vänta"));
  assert.ok((await page.textContent(".focus-card")).includes("1. Lyssna klart innan jag svarar."), "området visas med egna ord");
  await go(page, "forandring", "#f-forandring-mal_2");
  assert.equal(await page.inputValue("#f-forandring-mal_2"), "Ta det svåra samtalet direkt.");
  assert.deepEqual(page.errors, []);
  await ctx.close();
});

test("sparproblem: fel syns, texten finns kvar och sparas när förbindelsen är tillbaka", async () => {
  const { ctx, page } = await open("desktop", OWNER);
  await signIn(page);
  await go(page, "stanna", "#f-stanna-filter");
  offline = true;
  await type(page, "#f-stanna-filter", "Skrivet under avbrott.");
  await page.waitForSelector(".save-status.is-error", { timeout: 8000 });
  const dialogs = [];
  page.on("dialog", (d) => { dialogs.push(d.type()); d.accept(); });
  try {
    await page.reload();
    assert.deepEqual(dialogs, ["beforeunload"]);
    await page.waitForSelector("text=Vi når inte din resa just nu.");
    const kept = await page.evaluate(() => Object.entries(localStorage).find(([k]) => k.startsWith("lr-osparat:"))?.[1] || "");
    assert.ok(kept.includes("Skrivet under avbrott."));
  } finally {
    offline = false;
  }
  await page.click(".notice-page button");
  await page.waitForSelector("#f-stanna-filter");
  assert.equal(await page.inputValue("#f-stanna-filter"), "Skrivet under avbrott.");
  await saved(page);
  assert.equal(store.get(`data/users/${OWNER}/e:w1:stanna.filter`).value, "Skrivet under avbrott.");
  await ctx.close();
});

test("mobil: Nej-flödet går att slutföra utan att något gjordes, planen låses", async () => {
  const { ctx, page } = await open("mobile", OWNER);
  await signIn(page);
  await noSideScroll(page, "översikt");
  await page.waitForSelector(".focus-card.is-recall");
  await page.click(".focus-card .button.primary");
  await page.waitForSelector(".recall");
  assert.ok((await page.textContent(".recall")).includes("Ställa en öppen fråga och vänta"));
  assert.equal(await page.locator("#f-vad-hande-gjorde_faktiskt").count(), 0, "inget krav på vad som gjordes innan valet");
  await pick(page, "blev", "Nej");
  await page.waitForSelector("#f-vad-hande-stoppade");
  const text = await page.textContent(".section");
  assert.ok(text.includes("Det händer. Ofta finns mer att hämta här än i det som gick som planerat."));
  assert.ok(text.includes("Gör det nu. Gör något mindre. Eller välj något annat. Alla tre är ärliga svar."));
  assert.equal(await page.locator("#f-vad-hande-gjorde_faktiskt").count(), 0);
  assert.equal(await page.locator("#f-vad-hande-hande").count(), 0);
  assert.equal(await page.locator("#f-vad-hande-kostar").count(), 1, "Vad kostar det att vänta? visas");
  assert.ok((await page.textContent('[data-field="kostar"]')).includes("Frivilligt"));
  await page.tap("#f-vad-hande-stoppade");
  await page.keyboard.type("STOPP-PRIVAT. Tiden tog slut.");
  await type(page, "#f-vad-hande-nasta", "Gör något mindre.");
  await page.locator("#f-vad-hande-nasta").blur();
  await saved(page);
  await page.waitForFunction(() => document.querySelector('.rail-item[data-section="vad-hande"] .dot')?.classList.contains("is-done"), null, { timeout: 5000 });
  await noSideScroll(page, "vad hände");
  await shot(page, "03-nej-flodet-mobil");
  await go(page, "handling", ".lock-note");
  assert.equal(await page.locator("#f-handling-gora").count(), 0);
  assert.deepEqual(page.errors, []);
  await ctx.close();
});

test("annan testperson ser inget av Jans resa och har ingen handledarvy", async () => {
  const { ctx, page } = await open("desktop", OTHER);
  await signIn(page);
  const text = await page.textContent("body");
  for (const s of ["Ställa en öppen fråga", "DELAD-TOLKNING", "PRIVAT-REFLEKTION", "STOPP-PRIVAT", "SKAVER-START"]) assert.ok(!text.includes(s));
  assert.equal(await page.locator(".account a[href='#/jan']").count(), 0);
  const res = await page.evaluate(async () => {
    try { await window.LR_TRANSPORT.request("GET", "/api/facilitator/shared"); return 200; } catch (e) { return e.status; }
  });
  assert.equal(res, 403);
  await ctx.close();
});

test("två Nej i rad: privat ruta, Inte nu skickar inget, Be om ett samtal skickar bara önskemålet", async () => {
  const { ctx, page } = await open("desktop", OWNER);
  await signIn(page);
  assert.equal(await page.locator(".support-card").count(), 0, "ett Nej räcker inte");
  await moveTo(page, "w2");
  await goTo(page, "vecka-2", "handling", '[data-field="omrade"]');
  await pick(page, "omrade", "2");
  await type(page, "#f-handling-gora", "Säga nej till extrauppdraget.");
  await page.locator("#f-handling-gora").blur();
  await settle(page);
  await goTo(page, "vecka-2", "vad-hande", '[data-field="blev"]');
  await pick(page, "blev", "Nej");
  await type(page, "#f-vad-hande-stoppade", "STOPP-PRIVAT-2");
  await type(page, "#f-vad-hande-nasta", "Välj något annat.");
  await page.locator("#f-vad-hande-nasta").blur();
  await settle(page);
  // Förra veckan visar Nej-texten i vecka 3.
  await moveTo(page, "w3");
  await goTo(page, "vecka-3", "forra-veckan", ".section-bridge");
  const bridge = await page.textContent(".section-bridge");
  assert.ok(bridge.includes("Förra veckan blev det inte av.") && bridge.includes("Du skrev att det här stoppade dig:") && bridge.includes("STOPP-PRIVAT-2"));
  await page.evaluate(() => { location.hash = "#/"; });
  await page.waitForSelector(".support-card");
  const card = await page.textContent(".support-card");
  assert.ok(card.includes("Två veckor i rad blev det inte som du hade tänkt.") && card.includes("Vill du prata med Jan om vad som stoppar dig?"));
  assert.ok(card.includes("Den här rutan ser bara du."), "order 015: rutan säger att bara deltagaren ser den");
  assert.ok(card.includes("Be om ett samtal") && card.includes("Inte nu"));
  await shot(page, "04-privat-fraga-desktop");
  // Att rutan visas skrivs ingenstans.
  assert.ok(![...store.keys()].some((k) => k.startsWith("requests/")), "ingen förfrågan");
  assert.ok(!store.has(`data/users/${OWNER}/support`), "att rutan visades sparas inte");
  const rosterBefore = JSON.stringify(store.get(`roster/${OWNER}`));
  await page.click(".support-card button:has-text('Inte nu')");
  await page.waitForSelector(".support-card", { state: "detached" });
  assert.ok(![...store.keys()].some((k) => k.startsWith("requests/")), "Inte nu skickar inget till Jan");
  assert.deepEqual(store.get(`data/users/${OWNER}/support`).handled, ["w2"]);
  assert.equal(JSON.stringify(store.get(`roster/${OWNER}`)), rosterBefore, "inget i administratörens status");
  // Jans vy: ingen signal.
  await page.evaluate(() => { location.hash = "#/jan"; });
  await page.waitForSelector(".role-view .participant");
  assert.ok(!(await page.textContent("main")).includes("Vill boka ett samtal"));
  // Samtal med Jan. Knappen skickar bara önskemålet.
  await goTo(page, "samtal", "behov", ".talk-request button");
  await shot(page, "05-samtal-med-jan-desktop");
  await page.click(".talk-request button");
  await page.waitForSelector("text=Förfrågan skickad");
  const req = store.get(`requests/${OWNER}`);
  assert.deepEqual(Object.keys(req), ["requestedAt"], "förfrågan bär ingen text");
  await page.evaluate(() => { location.hash = "#/jan"; });
  await page.waitForSelector(".talk-flag");
  const jan = await page.textContent("main");
  assert.ok(jan.includes("Vill boka ett samtal"));
  assert.ok(!jan.includes("STOPP-PRIVAT"), "ingen privat text");
  await page.evaluate(() => { location.hash = "#/admin"; });
  await page.waitForSelector(".role-view .table");
  const admin = await page.textContent("main");
  assert.ok(!/samtal|STOPP|Nej/i.test(admin.replace(/Träffar/g, "")), "admin ser inga samtalssignaler");
  await moveTo(page, "w1");
  assert.deepEqual(page.errors, []);
  await ctx.close();
});

test("förhandsvisningen gör inga anrop utanför sidan", () => {
  assert.deepEqual(external, []);
});

// ---------- Hela programmet ----------

const FULL = "u_hela_resan";

async function sectionsOf(page) {
  const steps = await page.evaluate(() => window.LR_PROGRAM.steps.filter((s) => s.built).map((s) => ({ key: s.key, slug: s.slug, aside: Boolean(s.aside), sections: s.sections.map((x) => ({ key: x.key, kind: x.kind, model: x.model, reading: x.reading, displayOnly: x.displayOnly })) })));
  // Startsamtalet först, som i verkligheten.
  return [...steps.filter((s) => s.key === "start"), ...steps.filter((s) => s.key !== "start")];
}

async function moveTo(page, stepKey) {
  await page.evaluate(() => { location.hash = "#/"; });
  await page.waitForSelector("#test-step");
  await page.selectOption("#test-step", stepKey);
  await page.click(".test-mode button");
  await page.waitForFunction((k) => document.querySelector("#test-step")?.value === k && document.querySelector(".journey-step.is-current"), stepKey);
}

async function settle(page) {
  await page.waitForFunction(() => {
    const el = document.getElementById("save-status");
    let pending = false;
    try { pending = Object.keys(localStorage).some((k) => k.startsWith("lr-osparat:")); } catch { /* */ }
    return !pending && el && !el.classList.contains("is-saving") && !el.classList.contains("is-error");
  }, null, { timeout: 15000 });
}

// Fyller i ett moment. Ett val kan visa nya frågor, så varvet körs tills inget nytt dyker upp.
async function fillSection(page, label) {
  for (let pass = 0; pass < 8; pass += 1) {
    let changed = false;
    const inputs = page.locator("article textarea.input-text, article input.input-short");
    const n = await inputs.count();
    for (let i = 0; i < n; i += 1) {
      const el = inputs.nth(i);
      if (!(await el.isVisible()) || (await el.isDisabled()) || (await el.inputValue())) continue;
      const id = await el.getAttribute("id");
      await el.fill(`${label} svar ${id.split("-").pop()}`);
      changed = true;
    }
    for (const d of await page.locator("article input.input-date").all()) if (!(await d.inputValue())) { await d.fill("2026-10-01"); changed = true; }
    const groups = page.locator("article .choices");
    const g = await groups.count();
    for (let i = 0; i < g; i += 1) {
      const group = groups.nth(i);
      if (await group.locator(".choice.is-on").count()) continue;
      const count = await group.locator(".choice").count();
      await group.locator(".choice").nth(Math.min(1, count - 1)).click();
      await page.waitForTimeout(150);
      changed = true;
      break; // Sidan kan ha ritats om. Börja om.
    }
    for (const row of await page.locator(".scale-row").all()) {
      const dot = row.locator('.scale-dot[data-value="4"]');
      if (!(await dot.isDisabled()) && (await row.locator('[aria-checked="true"]').count()) === 0) { await dot.click(); changed = true; }
    }
    await page.locator("body").click({ position: { x: 2, y: 2 } });
    await settle(page);
    if (!changed) break;
  }
}

// Det som aldrig får synas för en deltagare. Källor och sidor för spårbarhet
// finns kvar internt i innehållsregistret.
const FORBIDDEN = [/Källa/, /arbetsbok/i, /köper du/i, /\bPDF\b/, /\bWord\b/, /HOLD/, /TODO|TBD/, /master/i, /crosswalk|provenance/i,
  /\bSource\b/, /\bPASS\b|\bFAIL\b|\bDEV\b|TEST DATA|SOURCE VERIFIED/, /\(s\. \d/, /Bokens övning|Boken \(/, /intern/i,
  /kataly/i, /Claude/, /\bAI\b/, /PDF-sida|Word-master/i, /JAN REVIEW|DIGITALT FORMULERAD/i, /\b(åtta|nio|tio|\d+) trianglar/i,
  /ledarskapslöfte|lovade dig själv/i, /Känner den här personen sig trygg/, /När jag inte klev fram/];
const assertClean = (text, where) => {
  for (const re of FORBIDDEN) assert.ok(!re.test(text), `${where}: ${re} syns för deltagaren (${text.match(new RegExp(".{0,40}" + re.source + ".{0,40}", re.flags))?.[0]})`);
};

const SHOTS_FOR = {
  "w3:se-hora-kanna": "06-vecka-3-se-hora-kanna-desktop",
  "w4:spegel": "07-spegeln-vecka-4-desktop",
  "w5:niva": "08-vecka-5-problemet-desktop",
  "w5:handling": "09-vecka-5-tre-vagar-desktop",
  "w6:trycket": "10-vecka-6-trycket-desktop",
  "w6:tillbaka": "11-vecka-6-hela-resan-desktop",
  "d30:minns": "12-30-dagar-det-har-skrev-du-desktop",
  "d30:kvar": "13-30-dagar-vad-blev-kvar-desktop",
};

test("hela programmet på desktop: startsamtal, sex veckor, 30 dagar och samtal. Resan minns.", async () => {
  const { ctx, page } = await open("desktop", FULL);
  await signIn(page);
  const steps = await sectionsOf(page);
  assert.deepEqual(steps.map((s) => s.key), ["start", "w1", "w2", "w3", "w4", "w5", "w6", "d30", "samtal"]);

  for (const s of steps) {
    if (!s.aside) await moveTo(page, s.key);
    for (const sec of s.sections) {
      await page.evaluate(([slug, key]) => { location.hash = `#/${slug}/${key}`; }, [s.slug, sec.key]);
      await page.waitForSelector(`article[data-step="${s.key}"][data-section="${sec.key}"] #section-title`);

      if (sec.kind === "bridge") {
        const text = await page.textContent(".section-bridge");
        assert.ok(/svar gora|svar skapa|svar resultat|svar chef_veta/.test(text), `${s.key}: förra veckans handling visas tillbaka`);
        assert.ok(text.includes("Efteråt skrev du"), `${s.key}: vad som hände visas tillbaka`);
      }
      if (sec.kind === "halfway") {
        const recall = await page.textContent(".recall");
        assert.ok(recall.includes("w1/forandring svar mal_1") && recall.includes("w1/forandring svar mal_1_hur"), "halvvägs visar områdena och hur de märks");
        for (const w of ["Vecka 1. Blev det av?", "Vecka 2. Blev det av?", "Vecka 3. Blev det av?"]) assert.ok(recall.includes(w), w);
      }
      if (sec.model === "se-hora-kanna") {
        const x = async (c) => (await page.locator(`g[data-corner="${c}"]`).boundingBox()).x;
        const [se, hora, kanna] = [await x("se"), await x("hora"), await x("kanna")];
        assert.ok(se < hora && hora < kanna, "SE vänster, HÖRA mitten, KÄNNA höger");
        const order = await page.$$eval(".corner-field textarea", (els) => els.map((e) => e.id));
        assert.deepEqual(order, ["f-se-hora-kanna-se", "f-se-hora-kanna-hora", "f-se-hora-kanna-kanna"]);
        assert.ok((await page.textContent(".section-triangle")).includes("En signal, inte ett bevis."));
      }
      if (sec.displayOnly) assert.equal(await page.locator(".corner-field").count(), 0, `${s.key}/${sec.key}: bara hörnord`);
      if (sec.kind === "action" && s.key !== "w5") {
        const opts = await page.$$eval('[data-field="omrade"] .choice', (els) => els.map((e) => e.textContent));
        if (s.key !== "w1") assert.ok(opts[0].startsWith("1. w1/forandring svar mal_1"), `${s.key}: områdena med egna ord`);
      }

      await fillSection(page, `${s.key}/${sec.key}`);
      if (["triangle", "situation", "mirror", "action", "return", "reflection", "goals", "people", "closing", "lookback"].includes(sec.kind) && !(s.key === "d30" && sec.key === "minns")) {
        const hasStatus = await page.locator(`.rail-item[data-section="${sec.key}"] .dot.is-info`).count() === 0;
        if (hasStatus) {
          await page.waitForFunction((k) => document.querySelector(`.rail-item[data-section="${k}"] .dot`)?.classList.contains("is-done"), sec.key, { timeout: 6000 })
            .catch(async () => assert.fail(`${s.key}/${sec.key}: momentet blir inte klart (${await page.getAttribute(`.rail-item[data-section="${sec.key}"] .dot`, "class")})`));
        }
      }
      if (SHOTS_FOR[`${s.key}:${sec.key}`]) await shot(page, SHOTS_FOR[`${s.key}:${sec.key}`]);

      if (s.key === "w6" && sec.kind === "map") {
        assert.equal(await page.locator(".compare .compare-line .marker.m0").count(), 6, "startbilden visas");
        assert.equal(await page.locator(".compare .compare-line .marker.m1").count(), 6, "slutbilden visas");
      }
      if (s.key === "w6" && sec.key === "tillbaka") {
        const text = await page.textContent(".lookback");
        for (const w of ["Vecka 1", "Vecka 2", "Vecka 3", "Vecka 4", "Vecka 5"]) assert.ok(text.includes(w), `Hela resan visar ${w}`);
        assert.ok(text.includes("start/infor svar skaver"), "det som skavde från startsamtalet visas");
        assert.ok(text.includes("w4/halvvags svar"), "halvvägs visas");
        assert.ok(text.includes("w4/spegel svar tog_med") && text.includes("Kollega"), "Spegeln från vecka 4 visas");
        assert.ok(!text.includes("[object"), "inga trasiga element");
      }
      if (s.key === "d30" && sec.key === "minns") {
        const text = await page.textContent("article");
        for (const t of ["start/infor svar skaver", "w1/forandring svar mal_1", "w6/tillbaka svar inte_forandrats", "w6/avslut svar fortsatta_1", "w6/avslut svar folja_upp_1", "w6/avslut svar testar", "w6/handling svar gora"]) assert.ok(text.includes(t), `30 dagar visar ${t}`);
        assert.ok(!/lovade/i.test(text));
      }
      if (s.key === "d30" && sec.key === "atertraff") assert.ok((await page.textContent("article")).includes("60 minuter"));
    }
  }

  const mine = [...store.keys()].filter((k) => k.startsWith(`data/users/${FULL}/e:`));
  for (const k of ["start", "w1", "w2", "w3", "w4", "w5", "w6", "d30", "samtal"]) assert.ok(mine.some((p) => p.includes(`/e:${k}:`)), `${k} sparat`);
  assert.deepEqual(Object.keys(store.get(`data/users/${FULL}/assessments`).points).sort(), ["d30", "end", "start"]);
  assert.deepEqual(store.get(`roster/${FULL}`).startedSteps, ["w1", "w2", "w3", "w4", "w5", "w6", "d30"], "admin ser bara veckor");

  await page.evaluate(() => { location.hash = "#/"; });
  await page.waitForSelector(".journey");
  const journeyText = await page.textContent(".journey");
  assert.ok(!/poäng|badge|streak/i.test(journeyText));
  const overviewText = await page.$eval("main", (m) => { const c = m.cloneNode(true); c.querySelector(".test-mode")?.remove(); return c.textContent; });
  assertClean(overviewText, "översikten");
  assert.equal(await page.locator(".journey-step.is-locked").count(), 0);
  await shot(page, "14-oversikt-hela-resan-desktop");
  assert.deepEqual(page.errors, []);
  await ctx.close();
});

test("hela programmet på mobil: varje moment går att läsa och skriva i, inget klipps", async () => {
  const { ctx, page } = await open("mobile", FULL);
  await signIn(page);
  const steps = await sectionsOf(page);
  const MOBILE_SHOTS = { "start:infor": "20-startsamtal-mobil", "w1:handling": "21-vecka-1-handling-mobil", "w3:se-hora-kanna": "22-vecka-3-mobil", "w4:spegel": "23-spegeln-mobil", "w5:handling": "24-vecka-5-mobil", "w6:tillbaka": "25-vecka-6-mobil", "d30:kvar": "26-30-dagar-mobil" };
  for (const s of steps) {
    for (const sec of s.sections) {
      await page.evaluate(([slug, key]) => { location.hash = `#/${slug}/${key}`; }, [s.slug, sec.key]);
      await page.waitForSelector(`article[data-step="${s.key}"][data-section="${sec.key}"] #section-title`);
      await noSideScroll(page, `${s.key}/${sec.key}`);
      const mainText = await page.textContent("main");
      assert.ok(!mainText.includes("[object") && !/\bnull\b|\bundefined\b/.test(mainText), `${s.key}/${sec.key}: inga trasiga element`);
      assertClean(mainText, `${s.key}/${sec.key}`);
      // Order 015. Nya ledtexter syns, de gamla gör det inte.
      assert.ok(!mainText.includes("Läs innan första träffen") && !mainText.includes("Vad väntar du på?"), `${s.key}/${sec.key}: gammal ledtext syns`);
      if (s.key === "w1" && sec.kind === "reading") assert.ok(mainText.includes("Läs under första veckan. Du behöver inte vara klar innan första träffen. Stanna där något skaver."));
      if (sec.key === "halvvags") assert.ok(mainText.includes("Vad har jag fortfarande inte gjort?") && mainText.includes("Vad krävs för att det ska bli av?"));
      if (sec.kind === "reading") {
        for (const c of sec.reading.chapters) assert.ok(mainText.includes(c.title) && mainText.includes(`Sidor ${c.pages}`), `${s.key}: ${c.title} Sidor ${c.pages}`);
      }
      const widths = await page.$$eval("textarea.input-text", (els) => els.filter((e) => e.offsetParent).map((e) => e.getBoundingClientRect().width));
      assert.ok(widths.every((w) => w > 250), `${s.key}/${sec.key}: textfälten är breda nog`);
      const buttons = await page.$$eval(".section button, .section .button, .choice, .scale-dot", (els) => els.filter((e) => e.offsetParent).map((e) => Math.min(e.getBoundingClientRect().height, e.getBoundingClientRect().width)));
      assert.ok(buttons.every((b) => b >= 40), `${s.key}/${sec.key}: knappar är stora nog (${Math.min(...buttons)})`);
      if (sec.kind === "triangle") {
        const pos = await page.$$eval("g[data-corner]", (gs) => gs.map((g) => ({ p: g.dataset.position, x: g.getBoundingClientRect().x, r: g.getBoundingClientRect().right })));
        assert.deepEqual(pos.map((p) => p.p), ["left", "middle", "right"]);
        assert.ok(pos[0].x < pos[1].x && pos[1].x < pos[2].x, `${s.key}/${sec.key}: hörnen i ordning vänster till höger`);
        assert.ok(pos.every((p) => p.r <= 412 && p.x >= 0), `${s.key}/${sec.key}: triangeln klipps inte`);
      }
      if (MOBILE_SHOTS[`${s.key}:${sec.key}`]) await shot(page, MOBILE_SHOTS[`${s.key}:${sec.key}`]);
    }
  }
  await page.evaluate(() => { location.hash = "#/vecka-4/privat"; });
  await page.waitForSelector("#f-privat-hjalp_samtal");
  await page.fill("#f-privat-hjalp_samtal", "");
  await page.tap("#f-privat-hjalp_samtal");
  await page.keyboard.type("Skrivet på telefonen.");
  await page.locator("#f-privat-hjalp_samtal").blur();
  await settle(page);
  assert.equal(store.get(`data/users/${FULL}/e:w4:privat.hjalp_samtal`).value, "Skrivet på telefonen.");
  assert.deepEqual(page.errors, []);
  await ctx.close();
});

// Fast regel: SE vänster, HÖRA mitten, KÄNNA höger. På alla brytpunkter.
for (const [kind, width] of [["desktop", null], ["mobile", null], ["smal", 320], ["platta", 820]]) {
  test(`Se · Höra · Känna ligger vänster, mitten, höger (${kind})`, async () => {
    const { ctx, page } = await open(kind === "mobile" ? "mobile" : "desktop", FULL);
    if (width) await page.setViewportSize({ width, height: 900 });
    await signIn(page);
    await page.evaluate(() => { location.hash = "#/vecka-3/se-hora-kanna"; });
    await page.waitForSelector("g[data-corner]");
    const corners = await page.$$eval("g[data-corner]", (gs) => gs.map((g) => ({ key: g.dataset.corner, pos: g.dataset.position, label: g.textContent, x: g.getBoundingClientRect().x })));
    assert.deepEqual(corners.map((c) => c.label), ["SE", "HÖRA", "KÄNNA"]);
    assert.deepEqual(corners.map((c) => c.pos), ["left", "middle", "right"]);
    assert.ok(corners[0].x < corners[1].x && corners[1].x < corners[2].x, "vänster till höger på skärmen");
    const fields = await page.$$eval(".corner-field", (els) => els.map((e) => ({ pos: e.dataset.position, x: e.getBoundingClientRect().x, y: e.getBoundingClientRect().y, label: e.querySelector("label")?.textContent || "" })));
    assert.deepEqual(fields.map((f) => f.pos), ["left", "middle", "right"]);
    assert.ok(fields[0].label.startsWith("Se.") && fields[1].label.startsWith("Höra.") && fields[2].label.startsWith("Känna."));
    const wide = await page.evaluate(() => window.matchMedia("(min-width: 900px)").matches);
    if (wide) assert.ok(fields[0].x < fields[1].x && fields[1].x < fields[2].x);
    else assert.ok(fields[0].y < fields[1].y && fields[1].y < fields[2].y);
    assert.ok(fields[2].label.includes("medveten om men inte låta styra"));
    await noSideScroll(page, kind);
    assert.deepEqual(page.errors, []);
    await ctx.close();
  });
}

test("Jan ser delade avsnitt och förfrågan, programadmin ser bara status", async () => {
  const other = await open("desktop", FULL);
  await signIn(other.page);
  await other.page.evaluate(() => { location.hash = "#/vecka-3/se-hora-kanna"; });
  await other.page.waitForSelector("button.toggle:has-text('Dela med Jan')");
  await other.page.click("button.toggle:has-text('Dela med Jan')");
  await other.page.click("dialog button[value=share]");
  await other.page.waitForSelector("text=Delat med Jan sedan");
  await other.ctx.close();

  const { ctx, page } = await open("desktop", OWNER);
  await signIn(page);
  await page.evaluate(() => { location.hash = "#/jan"; });
  await page.waitForSelector(".role-view .participant");
  const text = await page.textContent("main");
  assert.ok(text.includes("w3/se-hora-kanna svar"), "delad Se. Höra. Känna. syns för Jan");
  assert.ok(!text.includes("w4/privat") && !text.includes("Skrivet på telefonen."), "privat reflektion syns inte");
  assertClean(text, "Jans vy");
  await page.evaluate(() => { location.hash = "#/admin"; });
  await page.waitForSelector(".role-view .table");
  const admin = await page.textContent("main");
  assert.ok(!admin.includes("svar ") && !admin.includes("Skrivet på telefonen."), "programadmin ser ingen fritext");
  assert.ok(admin.includes("Vecka 6") && admin.includes("30 dagar"), "programadmin ser vilka veckor som påbörjats");
  assert.ok(admin.includes("60 minuter"), "återträffen syns som träff");
  await ctx.close();
});
