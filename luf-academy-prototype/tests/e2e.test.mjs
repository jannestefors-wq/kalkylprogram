// Hela deltagarkedjan i riktig webbläsare. Desktop och mobil.
// Kräver Playwright med Chromium (förinstallerat i utvecklingsmiljön).
import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { createRequire } from "node:module";
import { mkdirSync } from "node:fs";
import { openDb } from "../server/db.mjs";
import { createApp } from "../server/app.mjs";
import { seed } from "../scripts/seed.mjs";

const require = createRequire(import.meta.url);
function loadPlaywright() {
  for (const p of ["playwright", "/opt/node22/lib/node_modules/playwright"]) {
    try {
      return require(p);
    } catch {
      /* nästa */
    }
  }
  throw new Error("Playwright saknas");
}
const { chromium, devices } = loadPlaywright();

const SHOTS = new URL("../docs/skarmbilder/", import.meta.url).pathname;
mkdirSync(SHOTS, { recursive: true });

let server, base, links, browser, db;
// Simulerat nätavbrott på serversidan. Gäller alla anrop, även de som
// webbläsaren skickar när fliken stängs.
let offline = false;
const external = [];

before(async () => {
  db = openDb(":memory:");
  const app = createApp(db, {});
  server = createServer((req, res) => {
    if (offline && req.url.includes("/entry")) return req.socket.destroy();
    return app.handle(req, res);
  });
  await new Promise((r) => server.listen(0, "127.0.0.1", r));
  base = `http://127.0.0.1:${server.address().port}`;
  links = seed(db, { baseUrl: base });
  browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined });
});
after(async () => {
  await browser?.close();
  server?.close();
});

async function newPage(kind) {
  const ctx =
    kind === "mobile"
      ? await browser.newContext({ ...devices["Pixel 7"], locale: "sv-SE", timezoneId: "Europe/Stockholm" })
      : await browser.newContext({ viewport: { width: 1366, height: 900 }, locale: "sv-SE", timezoneId: "Europe/Stockholm" });
  const page = await ctx.newPage();
  page.on("request", (r) => {
    const host = new URL(r.url()).host;
    if (!r.url().startsWith("data:") && host !== new URL(base).host) external.push(r.url());
  });
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.errors = errors;
  return { ctx, page };
}

async function login(page, key) {
  await page.goto(links[key].url);
  await page.waitForSelector(".overview, .role-view, .notice-page");
}

async function saved(page) {
  await page.waitForFunction(() => {
    const el = document.getElementById("save-status");
    return el && el.classList.contains("is-saved");
  }, null, { timeout: 8000 });
}

async function noHorizontalScroll(page, label) {
  const { sw, cw } = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth }));
  assert.ok(sw <= cw + 1, `${label}: sidan scrollar i sidled (${sw} > ${cw})`);
}

async function go(page, path, selector) {
  await page.evaluate((p) => { location.hash = `#/${p}`; }, path);
  await page.waitForSelector(selector);
}

async function type(page, selector, text) {
  await page.fill(selector, "");
  await page.type(selector, text, { delay: 2 });
}

test("desktop: hela vecka 1, autosparning, utloggning och återkomst", async () => {
  const { ctx, page } = await newPage("desktop");
  await login(page, "testdeltagare");

  // Översikt
  const overview = await page.textContent("main");
  for (const s of ["Ledarskap med hjärta och mod", "Testdeltagare Jan", "Grupp A", "Nästa träff", "Vecka 1", "Vecka 6", "30 dagar", "Fortsätt min ledarskapsresa"]) {
    assert.ok(overview.includes(s), `översikten saknar: ${s}`);
  }
  assert.ok(!/poäng|badge|streak/i.test(overview));
  assert.equal(await page.locator(".journey-step.is-locked").count(), 6, "vecka 2 till 6 och 30 dagar är låsta");
  await page.screenshot({ path: `${SHOTS}01-oversikt-desktop.png`, fullPage: true });

  await page.click(".focus-card .button.primary");
  await page.waitForSelector(".section-intro");
  assert.ok((await page.textContent(".intro")).includes("Ledarskap börjar inte med modellen."));
  await page.screenshot({ path: `${SHOTS}02-intro-desktop.png` });
  await page.click(".section-nav .primary");

  // Läsning: verifierad mot boken. Kapitelrubrik och tryckta sidor, inga kapitelnummer.
  await page.waitForSelector(".section-reading");
  const reading = await page.textContent(".section-reading");
  assert.ok(reading.includes("Utan filter") && reading.includes("Sidor 7–15") && reading.includes("Inför den här veckan") && reading.includes("Läs:"));
  assert.ok(reading.includes("Människan först") && reading.includes("Sidor 17–27"));
  assert.ok(!reading.includes("HOLD") && !/kapitel \d/i.test(reading), "inga påhittade kapitelnummer");
  assert.ok(!/Källa|arbetsbok|köper du|PDF/i.test(reading), "inga källetiketter eller köptext");
  await go(page, "vecka-1/karta", ".map");

  // Ledarskapskartan
  await page.waitForSelector(".map");
  const rows = page.locator(".scale-row");
  assert.equal(await rows.count(), 6);
  const choices = [3, 4, 2, 5, 4, 3];
  for (let i = 0; i < 6; i += 1) await rows.nth(i).locator(`.scale-dot[data-value="${choices[i]}"]`).click();
  // Tangentbord: flytta Ansvar ett steg höger
  await rows.nth(5).locator(".scale-dot.is-selected").focus();
  await page.keyboard.press("ArrowRight");
  await saved(page);
  assert.equal(await rows.nth(5).locator('[aria-checked="true"]').getAttribute("data-value"), "4");
  assert.ok((await page.textContent(".section-map")).includes("Självskattning"));
  await page.screenshot({ path: `${SHOTS}03-ledarskapskarta-desktop.png`, fullPage: true });
  // Tre saker
  await go(page, "vecka-1/forandring", "#f-forandring-mal_1");
  await type(page, "#f-forandring-mal_1", "Att jag lyssnar klart innan jag svarar.");
  await type(page, "#f-forandring-mal_2", "Att jag tar det svåra samtalet direkt.");
  await type(page, "#f-forandring-mal_3", "Att jag säger vad jag tycker tidigt.");
  await saved(page);
  // Människorna runt mig: fullständigt namn ger en mild påminnelse
  await go(page, "vecka-1/manniskor", "#f-manniskor-person_1");
  await type(page, "#f-manniskor-person_1", "Anna Svensson");
  await page.waitForSelector(".field-hint:not(:empty)");
  await type(page, "#f-manniskor-person_1", "En projektledare i mitt team");
  assert.equal((await page.textContent(".field-hint")).trim(), "");
  // En verklig situation. Observation före tolkning, visuellt åtskilda.
  await go(page, "vecka-1/situation", ".situation");
  const bands = await page.$$eval(".situation-band", (els) => els.map((e) => e.querySelector(".band-title").textContent));
  assert.deepEqual(bands, ["Det som hände", "Min tolkning", "Mitt agerande", "Efteråt"]);
  const [obsColor, tolkColor] = await page.$$eval(".band-observation, .band-tolkning", (els) => els.map((e) => getComputedStyle(e).borderLeftColor));
  assert.notEqual(obsColor, tolkColor);
  await type(page, "#f-situation-vad_hande", "Projektledaren lämnade avstämningen efter tio minuter.");
  await type(page, "#f-situation-sag_horde", "Hon stängde datorn och sa: jag har ett annat möte.");
  await type(page, "#f-situation-tolkning", "SITUATIONENS-TOLKNING. Jag tror att hon tycker mötena är meningslösa.");
  await type(page, "#f-situation-gjorde", "Jag fortsatte med dagordningen.");
  await type(page, "#f-situation-gjorde_inte", "Jag frågade inte.");
  await saved(page);
  // Ta med till nästa träff och Dela med Jan
  await page.click("button.toggle:has-text(\"Ta med till nästa träff\")");
  await page.waitForSelector("text=Markerat: ta med till nästa träff");
  await page.click("button.toggle:has-text('Dela med Jan')");
  await page.waitForSelector("dialog[open]");
  const dialogText = await page.textContent("dialog");
  assert.ok(dialogText.includes("Inget annat från din resa"));
  await page.screenshot({ path: `${SHOTS}04-dela-med-jan-desktop.png` });
  await page.click("dialog button[value=share]");
  await page.waitForSelector("text=Delat med Jan sedan");
  await page.screenshot({ path: `${SHOTS}05-situation-desktop.png`, fullPage: true });
  // Närvaro
  await go(page, "vecka-1/narvaro", "#f-narvaro-eget_svar");
  await type(page, "#f-narvaro-eget_svar", "NARVARO-PRIVAT. Efter första meningen.");
  await type(page, "#f-narvaro-stanna_kvar", "Då hade jag hört varför.");
  await saved(page);
  // Det här ska jag prova
  await go(page, "vecka-1/handling", "#f-handling-prova");
  await type(page, "#f-handling-prova", "Ställa en öppen fråga och vänta på svaret.");
  await type(page, "#f-handling-situation", "Torsdagens avstämning.");
  await type(page, "#f-handling-lagga_marke", "När jag vill fylla tystnaden.");
  await page.fill("#f-handling-nar", "2026-09-24");
  await page.locator("#f-handling-nar").blur();
  await saved(page);
  await page.screenshot({ path: `${SHOTS}06-handling-desktop.png`, fullPage: true });

  // Utloggning och ny inloggning
  await page.click(".account button");
  await page.waitForSelector("text=Du är utloggad");
  const leftovers = await page.evaluate(() => Object.keys(localStorage).filter((k) => k.startsWith("lr-")));
  assert.deepEqual(leftovers, [], "ingen reflektionstext ligger kvar i webbläsaren efter utloggning");
  await page.goto(`${base}/`);
  await page.waitForSelector(".signin");
  await login(page, "testdeltagare");
  await page.waitForSelector(".focus-card.is-recall");
  assert.ok((await page.textContent(".focus-card")).includes("Ställa en öppen fråga och vänta på svaret."));
  assert.ok((await page.textContent(".bring")).includes("En situation från min verklighet"));
  await page.screenshot({ path: `${SHOTS}07-aterkomst-oversikt-desktop.png`, fullPage: true });

  // Kartan och texterna finns kvar. En tillåten text kan ändras.
  await page.goto(`${base}/#/vecka-1/karta`);
  await page.waitForSelector(".map");
  assert.equal(await page.locator(".scale-row").nth(0).locator('[aria-checked="true"]').getAttribute("data-value"), "3");
  await page.goto(`${base}/#/vecka-1/forandring`);
  await page.waitForSelector("#f-forandring-mal_2");
  assert.equal(await page.inputValue("#f-forandring-mal_2"), "Att jag tar det svåra samtalet direkt.");
  await type(page, "#f-forandring-mal_2", "Att jag tar det svåra samtalet samma dag.");
  await saved(page);

  assert.deepEqual(page.errors, []);
  await ctx.close();
});

test("autosparning: fel syns, texten finns kvar och sparas när nätet är tillbaka", async () => {
  const { ctx, page } = await newPage("desktop");
  await login(page, "deltagare-a3");
  await page.goto(`${base}/#/vecka-1/narvaro`);
  await page.waitForSelector("#f-narvaro-missade");

  offline = true;
  await type(page, "#f-narvaro-missade", "Text skriven utan nät.");
  await page.waitForSelector(".save-status.is-error", { timeout: 8000 });
  assert.ok((await page.textContent(".save-status")).includes("Din text finns kvar här"));
  const pending = await page.evaluate(() => Object.entries(localStorage).find(([k]) => k.startsWith("lr-osparat:"))?.[1] || "");
  assert.ok(pending.includes("Text skriven utan nät."));
  await page.screenshot({ path: `${SHOTS}08-sparfel-desktop.png` });

  // Deltagaren lämnar sidan medan nätet är nere. Webbläsaren varnar först.
  // Deltagaren lämnar ändå. Texten återställs vid återkomst.
  const dialogs = [];
  page.on("dialog", (d) => {
    dialogs.push(d.type());
    d.accept();
  });
  await page.reload();
  assert.deepEqual(dialogs, ["beforeunload"], "varning innan osparad text lämnas");
  await page.waitForSelector("#f-narvaro-missade");
  assert.equal(await page.inputValue("#f-narvaro-missade"), "Text skriven utan nät.");

  await page.waitForSelector(".save-status.is-error");
  offline = false;
  await page.click(".save-status.is-error button");
  await saved(page);
  const stored = db.prepare("SELECT value FROM lr_entry WHERE field_key = 'narvaro.missade'").all().map((r) => r.value);
  assert.ok(stored.includes("Text skriven utan nät."));
  assert.equal(await page.evaluate(() => Object.keys(localStorage).filter((k) => k.startsWith("lr-osparat:")).length), 0);
  await ctx.close();
});

test("mobil: samma konto på ny enhet, återkomsten och Vad hände?", async () => {
  const { ctx, page } = await newPage("mobile");
  await login(page, "testdeltagare");
  await noHorizontalScroll(page, "översikt mobil");
  await page.screenshot({ path: `${SHOTS}10-oversikt-mobil.png`, fullPage: true });
  assert.ok((await page.textContent(".focus-card")).includes("Ställa en öppen fråga och vänta på svaret."));

  // Kartan på mobil: rätt ordning, inga för små mål, ingen sidscroll
  await page.goto(`${base}/#/vecka-1/karta`);
  await page.waitForSelector(".map");
  await noHorizontalScroll(page, "karta mobil");
  const sizes = await page.$$eval(".scale-dot", (els) => els.map((e) => e.getBoundingClientRect()).map((r) => Math.min(r.width, r.height)));
  assert.ok(sizes.every((s) => s >= 40), `för små tryckytor: ${Math.min(...sizes)}`);
  const ends = await page.locator(".scale-row").first().evaluate((row) => {
    const low = row.querySelector(".is-low").getBoundingClientRect();
    const high = row.querySelector(".is-high").getBoundingClientRect();
    const first = row.querySelector('.scale-dot[data-value="1"]').getBoundingClientRect();
    const last = row.querySelector('.scale-dot[data-value="6"]').getBoundingClientRect();
    return { low: low.left, high: high.right, first: first.left, last: last.right, vw: innerWidth };
  });
  assert.ok(ends.low < ends.high && ends.first < ends.last, "skalan behåller vänster till höger");
  assert.ok(ends.high <= ends.vw && ends.last <= ends.vw, "skalan klipps inte");
  assert.equal(await page.locator(".scale-row").nth(0).locator('[aria-checked="true"]').getAttribute("data-value"), "3");
  await page.screenshot({ path: `${SHOTS}11-karta-mobil.png`, fullPage: true });

  await page.goto(`${base}/#/vecka-1/situation`);
  await page.waitForSelector(".situation");
  await noHorizontalScroll(page, "situation mobil");
  await page.screenshot({ path: `${SHOTS}12-situation-mobil.png`, fullPage: true });

  // Återkomsten
  await page.goto(`${base}/#/`);
  await page.waitForSelector(".focus-card.is-recall");
  await page.click(".focus-card .button.primary");
  await page.waitForSelector(".recall");
  assert.ok((await page.textContent(".recall")).includes("Ställa en öppen fråga och vänta på svaret."));
  assert.ok((await page.textContent(".recall")).includes("När jag vill fylla tystnaden."));
  await page.tap("#f-vad-hande-gjorde_faktiskt");
  await page.keyboard.type("Jag ställde frågan och räknade tyst till fem.");
  await type(page, "#f-vad-hande-hande", "Hon sa att tempot i mötena är för högt.");
  await type(page, "#f-vad-hande-upptackte", "Att jag fyller tystnaden för att slippa obehaget.");
  await type(page, "#f-vad-hande-prova_annorlunda", "Fråga en gång till.");
  await page.locator("#f-vad-hande-prova_annorlunda").blur();
  await saved(page);
  await noHorizontalScroll(page, "vad hände mobil");
  const box = await page.locator("#f-vad-hande-hande").boundingBox();
  assert.ok(box.width > 280, "textfältet är brett nog att skriva i");
  await page.screenshot({ path: `${SHOTS}13-vad-hande-mobil.png`, fullPage: true });

  // Planen står kvar som skriven, nu låst
  await page.goto(`${base}/#/vecka-1/handling`);
  await page.waitForSelector(".lock-note");
  assert.equal(await page.locator("#f-handling-prova").count(), 0);
  assert.ok((await page.textContent(".section-action")).includes("Ställa en öppen fråga och vänta på svaret."));

  assert.deepEqual(page.errors, []);
  await ctx.close();
});

test("en annan deltagare ser inget av testdeltagarens resa, inte ens via direkt URL", async () => {
  const owner = db
    .prepare("SELECT e.id FROM lr_enrollment e JOIN lr_user u ON u.id = e.user_id WHERE u.email = 'testdeltagare@prototyp.luf'")
    .get().id;
  const { ctx, page } = await newPage("desktop");
  await login(page, "deltagare-a2");
  const body = await page.textContent("main");
  assert.ok(!body.includes("Ställa en öppen fråga"));
  const status = await page.evaluate(async (id) => (await fetch(`/api/journey/${id}`)).status, owner);
  assert.equal(status, 404);
  await page.goto(`${base}/#/jan`);
  await page.waitForSelector(".overview");
  await ctx.close();
});

test("Jan som handledare ser bara det som delats", async () => {
  const { ctx, page } = await newPage("desktop");
  await login(page, "jan-handledare");
  await page.waitForSelector(".role-view");
  const text = await page.textContent("main");
  assert.ok(text.includes("SITUATIONENS-TOLKNING"), "delad situation syns");
  assert.ok(!text.includes("NARVARO-PRIVAT"), "privat närvaroreflektion syns inte");
  assert.ok(!text.includes("Ställa en öppen fråga"), "ej delad handling syns inte");
  await page.screenshot({ path: `${SHOTS}20-delat-med-jan.png`, fullPage: true });
  await ctx.close();
});

test("programadministratören ser grupper och status men ingen fritext", async () => {
  const { ctx, page } = await newPage("desktop");
  await login(page, "programadmin");
  await page.waitForSelector(".role-view");
  const text = await page.textContent("main");
  assert.ok(text.includes("Grupp A") && text.includes("Grupp B"));
  for (const secret of ["SITUATIONENS-TOLKNING", "NARVARO-PRIVAT", "Ställa en öppen fråga"]) assert.ok(!text.includes(secret));
  await page.screenshot({ path: `${SHOTS}21-programadmin.png`, fullPage: true });
  await ctx.close();
});

test("inga anrop lämnar prototypen. Ingen extern analys.", () => {
  assert.deepEqual(external, []);
});
