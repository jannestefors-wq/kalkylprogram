// Förhandsvisningen för Human Test, körd mot en lokal modell av claude.ai-
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
  if (a === "shared" || a === "roster") return uid === OWNER || b === uid;
  return true;
}
function canWrite(path, uid) {
  const [a, b, c] = path.split("/");
  if (a === "data" && b === "users") return c === uid;
  if (a === "shared" || a === "roster") return b === uid || uid === OWNER;
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

before(async () => {
  execFileSync("node", ["--no-warnings", "scripts/build-preview.mjs"]);
  const page = readFileSync(new URL("../preview/dist/min-ledarskapsresa.html", import.meta.url), "utf8");
  // Samma skal som claude.ai lägger runt sidan.
  const html = `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"></head><body>${page}</body></html>`;
  server = createServer((req, res) => { res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" }); res.end(html); });
  await new Promise((r) => server.listen(0, "127.0.0.1", r));
  base = `http://127.0.0.1:${server.address().port}/`;
  browser = await chromium.launch();
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
const go = async (page, section, sel) => { await page.evaluate((s) => { location.hash = `#/vecka-1/${s}`; }, section); await page.waitForSelector(sel); };

test("desktop: inloggning, hela vecka 1, delning, utloggning och återkomst", async () => {
  const { ctx, page } = await open("desktop", OWNER);
  await page.waitForSelector(".signin");
  assert.ok((await page.textContent("#prototype-band")).includes("Testversion. Ej produktion."));
  assert.equal(await page.isVisible("#prototype-band"), false, "märkningen syns först efter inloggning");
  await signIn(page);
  assert.equal(await page.isVisible("#prototype-band"), true);
  const text = await page.textContent("main");
  for (const s of ["Testgrupp. Human Test", "23 september", "Nästa träff", "Fortsätt min ledarskapsresa"]) assert.ok(text.includes(s), s);
  assert.equal(await page.locator(".journey-step.is-locked").count(), 6);

  await page.click(".focus-card .button.primary");
  await page.waitForSelector(".section-intro");
  await page.click(".section-nav .primary");
  await page.waitForSelector(".section-reading");
  const reading = await page.textContent(".section-reading");
  assert.ok(reading.includes("Inför den här veckan") && reading.includes("Läs:"));
  assert.ok(reading.includes("Utan filter") && reading.includes("Sidor 7–15"));
  await page.screenshot({ path: new URL("../docs/skarmbilder/31-infor-veckan-desktop.png", import.meta.url).pathname, fullPage: true });
  await go(page, "karta", ".map");
  const rows = page.locator(".scale-row");
  const picks = [3, 4, 2, 5, 4, 3];
  // Snabba klick i följd. Inget får skrivas över.
  for (let i = 0; i < 6; i += 1) await rows.nth(i).locator(`.scale-dot[data-value="${picks[i]}"]`).click({ delay: 0 });
  await saved(page);
  await page.waitForTimeout(600);
  assert.deepEqual(store.get(`data/users/${OWNER}/assessments`).points.start, { narvaro: 3, mod: 4, lyssnande: 2, tydlighet: 5, relation: 4, ansvar: 3 });

  await go(page, "forandring", "#f-forandring-mal_1");
  await type(page, "#f-forandring-mal_1", "Lyssna klart innan jag svarar.");
  await type(page, "#f-forandring-mal_2", "Ta det svåra samtalet direkt.");
  await type(page, "#f-forandring-mal_3", "Säga vad jag tycker tidigt.");
  await saved(page);

  await go(page, "situation", ".situation");
  await type(page, "#f-situation-vad_hande", "Projektledaren lämnade mötet tidigt.");
  await type(page, "#f-situation-tolkning", "DELAD-TOLKNING. Jag tror att hon var missnöjd.");
  await saved(page);
  await page.click("button.toggle:has-text('Dela med Jan')");
  await page.waitForSelector("dialog[open]");
  await page.click("dialog button[value=share]");
  await page.waitForSelector("text=Delat med Jan sedan");
  // Levande delning: en ändring efter delning syns för Jan.
  await type(page, "#f-situation-gjorde", "Jag fortsatte dagordningen.");
  await saved(page);

  await go(page, "narvaro", "#f-narvaro-missade");
  await type(page, "#f-narvaro-missade", "PRIVAT-NARVARO. Jag missade hennes blick.");
  await saved(page);

  await go(page, "handling", "#f-handling-prova");
  await type(page, "#f-handling-prova", "Ställa en öppen fråga och vänta.");
  await type(page, "#f-handling-situation", "Torsdagens avstämning.");
  await page.fill("#f-handling-nar", "2026-09-25");
  await page.locator("#f-handling-nar").blur();
  await saved(page);

  // Handledarvyn: bara det delade
  await page.evaluate(() => { location.hash = "#/jan"; });
  await page.waitForSelector(".role-view");
  const shared = await page.textContent("main");
  assert.ok(shared.includes("DELAD-TOLKNING") && shared.includes("Jag fortsatte dagordningen."));
  assert.ok(!shared.includes("PRIVAT-NARVARO") && !shared.includes("Ställa en öppen fråga"));

  // Programadmin: ingen fritext
  await page.evaluate(() => { location.hash = "#/admin"; });
  await page.waitForSelector(".role-view .table");
  const admin = await page.textContent("main");
  for (const s of ["DELAD-TOLKNING", "PRIVAT-NARVARO", "Ställa en öppen fråga"]) assert.ok(!admin.includes(s));

  // Utloggning, ny inloggning
  await page.evaluate(() => { location.hash = "#/"; });
  await page.click(".account button");
  await page.waitForSelector("text=Du är utloggad");
  await page.reload();
  await page.waitForSelector(".signin");
  await signIn(page);
  await page.waitForSelector(".focus-card.is-recall");
  assert.ok((await page.textContent(".focus-card")).includes("Ställa en öppen fråga och vänta."));
  await go(page, "forandring", "#f-forandring-mal_2");
  assert.equal(await page.inputValue("#f-forandring-mal_2"), "Ta det svåra samtalet direkt.");
  assert.deepEqual(page.errors, []);
  await ctx.close();
});

test("sparproblem: fel syns, texten finns kvar och sparas när förbindelsen är tillbaka", async () => {
  const { ctx, page } = await open("desktop", OWNER);
  await signIn(page);
  await go(page, "narvaro", "#f-narvaro-stanna_kvar");
  offline = true;
  await type(page, "#f-narvaro-stanna_kvar", "Skrivet under avbrott.");
  await page.waitForSelector(".save-status.is-error", { timeout: 8000 });
  const dialogs = [];
  page.on("dialog", (d) => { dialogs.push(d.type()); d.accept(); });
  try {
    await page.reload();
    assert.deepEqual(dialogs, ["beforeunload"]);
    // Fortfarande ingen förbindelse: ett mänskligt besked, inget tekniskt fel.
    await page.waitForSelector("text=Vi når inte din resa just nu.");
    const kept = await page.evaluate(() => Object.entries(localStorage).find(([k]) => k.startsWith("lr-osparat:"))?.[1] || "");
    assert.ok(kept.includes("Skrivet under avbrott."));
  } finally {
    offline = false;
  }
  await page.click(".notice-page button");
  await page.waitForSelector("#f-narvaro-stanna_kvar");
  assert.equal(await page.inputValue("#f-narvaro-stanna_kvar"), "Skrivet under avbrott.");
  await saved(page);
  assert.equal(store.get(`data/users/${OWNER}/e:w1:narvaro.stanna_kvar`).value, "Skrivet under avbrott.");
  await ctx.close();
});

test("mobil: samma konto, återkomst, Vad hände? och låst plan", async () => {
  const { ctx, page } = await open("mobile", OWNER);
  await signIn(page);
  await noSideScroll(page, "översikt");
  await page.waitForSelector(".focus-card.is-recall");
  await go(page, "karta", ".map");
  await noSideScroll(page, "karta");
  assert.equal(await page.locator(".scale-row").nth(1).locator('[aria-checked="true"]').getAttribute("data-value"), "4");
  const smallest = Math.min(...(await page.$$eval(".scale-dot", (els) => els.map((e) => Math.min(e.getBoundingClientRect().width, e.getBoundingClientRect().height)))));
  assert.ok(smallest >= 40);
  await page.evaluate(() => { location.hash = "#/"; });
  await page.click(".focus-card .button.primary");
  await page.waitForSelector(".recall");
  assert.ok((await page.textContent(".recall")).includes("Ställa en öppen fråga och vänta."));
  await page.tap("#f-vad-hande-gjorde_faktiskt");
  await page.keyboard.type("Jag frågade och väntade.");
  await type(page, "#f-vad-hande-hande", "Hon berättade om tempot.");
  await type(page, "#f-vad-hande-upptackte", "Jag fyller tystnaden.");
  await page.locator("#f-vad-hande-upptackte").blur();
  await saved(page);
  await noSideScroll(page, "vad hände");
  await page.screenshot({ path: new URL("../docs/skarmbilder/30-forhandsvisning-mobil.png", import.meta.url).pathname, fullPage: true });
  await go(page, "handling", ".lock-note");
  assert.equal(await page.locator("#f-handling-prova").count(), 0);
  assert.deepEqual(page.errors, []);
  await ctx.close();
});

test("annan testperson ser inget av Jans resa och har ingen handledarvy", async () => {
  const { ctx, page } = await open("desktop", OTHER);
  await signIn(page);
  const text = await page.textContent("body");
  for (const s of ["Ställa en öppen fråga", "DELAD-TOLKNING", "PRIVAT-NARVARO"]) assert.ok(!text.includes(s));
  assert.equal(await page.locator(".account a[href='#/jan']").count(), 0);
  const res = await page.evaluate(async () => {
    try { await window.LR_TRANSPORT.request("GET", "/api/facilitator/shared"); return 200; } catch (e) { return e.status; }
  });
  assert.equal(res, 403);
  await ctx.close();
});

test("förhandsvisningen gör inga anrop utanför sidan", () => {
  assert.deepEqual(external, []);
});

// ---------- Hela programmet ----------

const FULL = "u_hela_resan";

async function sectionsOf(page) {
  return page.evaluate(() => window.LR_PROGRAM.steps.filter((s) => s.built).map((s) => ({ key: s.key, slug: s.slug, aside: Boolean(s.aside), sections: s.sections.map((x) => ({ key: x.key, kind: x.kind, model: x.model, reading: x.reading })) })));
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

async function fillSection(page, label) {
  const inputs = page.locator("textarea.input-text, input.input-short");
  const n = await inputs.count();
  for (let i = 0; i < n; i += 1) {
    const el = inputs.nth(i);
    if (!(await el.isVisible()) || (await el.inputValue())) continue;
    await el.fill(`${label} svar ${i + 1}`);
  }
  for (const d of await page.locator("input.input-date").all()) if (!(await d.inputValue())) await d.fill("2026-10-01");
  for (const group of await page.locator(".choices").all()) {
    if (!(await group.locator(".choice.is-on").count())) await group.locator(".choice").nth(1).click();
  }
  for (const row of await page.locator(".scale-row").all()) {
    const dot = row.locator('.scale-dot[data-value="4"]');
    if (!(await dot.isDisabled()) && (await row.locator('[aria-checked="true"]').count()) === 0) await dot.click();
  }
  await page.locator("body").click({ position: { x: 2, y: 2 } });
  await settle(page);
}

// Det som aldrig får synas för en deltagare. Källor och sidor för spårbarhet
// finns kvar internt i innehållsregistret.
const FORBIDDEN = [/Källa/, /arbetsbok/i, /köper du/i, /\bPDF\b/, /\bWord\b/, /HOLD/, /TODO|TBD/, /master/i, /crosswalk|provenance/i,
  /\bSource\b/, /\bPASS\b|\bFAIL\b|\bDEV\b|TEST DATA|SOURCE VERIFIED/, /\(s\. \d/, /Bokens övning|Boken \(/, /intern/i];
const assertClean = (text, where) => {
  for (const re of FORBIDDEN) assert.ok(!re.test(text), `${where}: ${re} syns för deltagaren (${text.match(new RegExp(".{0,40}" + re.source + ".{0,40}", re.flags))?.[0]})`);
};

test("hela programmet på desktop: sex veckor, 30 dagar och samtal. Resan minns.", async () => {
  const { ctx, page } = await open("desktop", FULL);
  await signIn(page);
  const steps = await sectionsOf(page);
  assert.deepEqual(steps.map((s) => s.key), ["w1", "w2", "w3", "w4", "w5", "w6", "d30", "samtal"]);

  for (const s of steps) {
    if (!s.aside) await moveTo(page, s.key);
    for (const sec of s.sections) {
      await page.evaluate(([slug, key]) => { location.hash = `#/${slug}/${key}`; }, [s.slug, sec.key]);
      await page.waitForSelector(`article[data-step="${s.key}"] #section-title`);
      await page.waitForFunction(([slug, key]) => location.hash === `#/${slug}/${key}`, [s.slug, sec.key]);

      if (sec.kind === "bridge") {
        const text = await page.textContent(".section-bridge");
        assert.ok(/svar 1/.test(text), `${s.key}: förra veckans handling visas tillbaka`);
        assert.ok(text.includes("Efteråt skrev du"), `${s.key}: vad som hände visas tillbaka`);
      }
      if (sec.kind === "halfway") assert.ok((await page.textContent(".recall")).includes("w1/forandring svar 1"), "halvvägs visar förändringsmålen");
      if (sec.model === "se-hora-kanna") {
        const x = async (c) => (await page.locator(`g[data-corner="${c}"]`).boundingBox()).x;
        const [se, hora, kanna] = [await x("se"), await x("hora"), await x("kanna")];
        assert.ok(se < hora && hora < kanna, "SE vänster, HÖRA mitten, KÄNNA höger");
        const order = await page.$$eval(".corner-field textarea", (els) => els.map((e) => e.id));
        assert.deepEqual(order, ["f-se-hora-kanna-se", "f-se-hora-kanna-hora", "f-se-hora-kanna-kanna"]);
        assert.ok((await page.textContent(".section-triangle")).includes("En signal, inte ett bevis."));
      }

      await fillSection(page, `${s.key}/${sec.key}`);
      if ((sec.kind === "triangle" || sec.kind === "situation") && sec.key !== "ny-eller-vaxa") {
        await page.waitForFunction((k) => document.querySelector(`.rail-item[data-section="${k}"] .dot`)?.classList.contains("is-done"), sec.key, { timeout: 5000 })
          .catch(async () => assert.fail(`${s.key}/${sec.key}: sidomenyn visar inte att momentet är skrivet (${await page.getAttribute(`.rail-item[data-section="${sec.key}"] .dot`, "class")})`));
      }

      if (s.key === "w6" && sec.kind === "map") {
        assert.equal(await page.locator(".compare .compare-line .marker.m0").count(), 6, "startbilden visas");
        assert.equal(await page.locator(".compare .compare-line .marker.m1").count(), 6, "slutbilden visas");
        assert.ok((await page.textContent(".compare")).includes("Självskattning"));
      }
      if (s.key === "w6" && sec.kind === "lookback") {
        const text = await page.textContent(".lookback");
        for (const w of ["Vecka 1", "Vecka 2", "Vecka 3", "Vecka 4", "Vecka 5"]) assert.ok(text.includes(w), `tillbakablicken visar ${w}`);
        assert.ok(text.includes("w1/karta svar 1"), "varför är jag här visas");
        assert.ok(!text.includes("[object"), "inga trasiga element");
      }
      if (s.key === "d30" && sec.key === "minns") {
        const text = await page.textContent(".lookback");
        assert.ok(text.includes("w1/forandring svar 1") && text.includes("w6/avslut") && text.includes("Du lovade dig själv att"));
      }
    }
    if (s.key === "w3") {
      await page.evaluate(() => { location.hash = "#/vecka-3/se-hora-kanna"; });
      await page.waitForSelector(".triangle-figure");
      await page.waitForFunction(() => document.querySelectorAll(".rail-item .dot.is-done").length >= 6, null, { timeout: 5000 });
      await page.screenshot({ path: new URL("../docs/skarmbilder/40-se-hora-kanna-desktop.png", import.meta.url).pathname, fullPage: true });
    }
    if (s.key === "w6") {
      await page.evaluate(() => { location.hash = "#/vecka-6/karta"; });
      await page.waitForSelector(".compare");
      await page.screenshot({ path: new URL("../docs/skarmbilder/41-forflyttning-desktop.png", import.meta.url).pathname, fullPage: true });
    }
  }

  // Allt finns i databasen, i personens eget privata område.
  const mine = [...store.keys()].filter((k) => k.startsWith(`data/users/${FULL}/e:`));
  for (const k of ["w1", "w2", "w3", "w4", "w5", "w6", "d30", "samtal"]) assert.ok(mine.some((p) => p.includes(`/e:${k}:`)), `${k} sparat`);
  const points = store.get(`data/users/${FULL}/assessments`).points;
  assert.deepEqual(Object.keys(points).sort(), ["d30", "end", "start"]);

  // Översikten visar framsteg för varje vecka, utan poäng.
  await page.evaluate(() => { location.hash = "#/"; });
  await page.waitForSelector(".journey");
  const journeyText = await page.textContent(".journey");
  assert.ok(!/poäng|badge|streak/i.test(journeyText));
  const overviewText = await page.$eval("main", (m) => { const c = m.cloneNode(true); c.querySelector(".test-mode")?.remove(); return c.textContent; });
  assertClean(overviewText, "översikten");
  assert.equal(await page.locator(".journey-step.is-locked").count(), 0);
  await page.screenshot({ path: new URL("../docs/skarmbilder/42-oversikt-hela-resan-desktop.png", import.meta.url).pathname, fullPage: true });
  assert.deepEqual(page.errors, []);
  await ctx.close();
});

test("hela programmet på mobil: varje moment går att läsa och skriva i, inget klipps", async () => {
  const { ctx, page } = await open("mobile", FULL);
  await signIn(page);
  const steps = await sectionsOf(page);
  let shots = 0;
  for (const s of steps) {
    for (const sec of s.sections) {
      await page.evaluate(([slug, key]) => { location.hash = `#/${slug}/${key}`; }, [s.slug, sec.key]);
      await page.waitForSelector(`article[data-step="${s.key}"] #section-title`);
      await noSideScroll(page, `${s.key}/${sec.key}`);
      const mainText = await page.textContent("main");
      assert.ok(!mainText.includes("[object") && !/\bnull\b|\bundefined\b/.test(mainText), `${s.key}/${sec.key}: inga trasiga element`);
      assertClean(mainText, `${s.key}/${sec.key}`);
      if (sec.kind === "reading") {
        assert.ok(mainText.includes("Inför den här veckan") && mainText.includes("Läs:"), `${s.key}: läsanvisningen visas`);
        for (const c of sec.reading.chapters) assert.ok(mainText.includes(c.title) && mainText.includes(`Sidor ${c.pages}`), `${s.key}: ${c.title} Sidor ${c.pages}`);
        if (s.key === "w6") await page.screenshot({ path: new URL("../docs/skarmbilder/32-infor-veckan-w6-mobil.png", import.meta.url).pathname, fullPage: true });
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
      if ((sec.model === "se-hora-kanna" || sec.kind === "map" || sec.kind === "lookback") && shots < 6) {
        await page.screenshot({ path: new URL(`../docs/skarmbilder/5${shots}-${s.key}-${sec.key}-mobil.png`, import.meta.url).pathname, fullPage: true });
        shots += 1;
      }
    }
  }
  // Skriv med tangentbordet i en vecka på mobilen.
  await page.evaluate(() => { location.hash = "#/vecka-4/privat"; });
  await page.waitForSelector("#f-privat-undviker");
  await page.fill("#f-privat-undviker", "");
  await page.tap("#f-privat-undviker");
  await page.keyboard.type("Skrivet på telefonen.");
  await page.locator("#f-privat-undviker").blur();
  await settle(page);
  assert.equal(store.get(`data/users/${FULL}/e:w4:privat.undviker`).value, "Skrivet på telefonen.");
  assert.deepEqual(page.errors, []);
  await ctx.close();
});

test("Jan ser delade avsnitt från alla veckor, programadmin ser bara status", async () => {
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
  assert.ok(!admin.includes("svar 1") && !admin.includes("Skrivet på telefonen."), "programadmin ser ingen fritext");
  assert.ok(admin.includes("Vecka 6"), "programadmin ser vilka veckor som påbörjats");
  await ctx.close();
});
