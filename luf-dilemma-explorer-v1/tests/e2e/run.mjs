// LUF Dilemma Explorer V1 — end-to-end journey verification (RESA A/B/C).
// Runs against a real Chromium instance via Playwright, serving the app
// from a throwaway static server (no build step, no network).
//
// Run with: NODE_PATH=<global node_modules> node tests/e2e/run.mjs
// (see package.json "test:e2e" / docs/INSTALL.md)

import path from "node:path";
import { mkdir } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";
import { startServer } from "./static-server.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(here, "../..");
const screenshotDir = path.join(here, "screenshots");

let passCount = 0;
let failCount = 0;
const failures = [];

function check(label, condition) {
  if (condition) {
    passCount++;
    console.log(`  PASS  ${label}`);
  } else {
    failCount++;
    failures.push(label);
    console.log(`  FAIL  ${label}`);
  }
}

// Must run before the app's own script does, so the very first
// dilemma_explorer_opened event (fired on load) is not missed.
async function captureHouseEvents(page) {
  await page.addInitScript(() => {
    window.__capturedEvents = [];
    const names = [
      "dilemma_explorer_opened", "theme_selected", "dilemma_discovered",
      "dilemma_opened", "thinking_chair_requested",
    ];
    for (const name of names) {
      window.addEventListener(`luf:${name}`, (e) => window.__capturedEvents.push(e.detail));
    }
  });
}

async function eventNames(page) {
  return page.evaluate(() => (window.__capturedEvents || []).map((e) => e.name));
}

async function noHorizontalScroll(page) {
  return page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1);
}

async function run() {
  await mkdir(screenshotDir, { recursive: true });
  const { url, close } = await startServer(projectRoot, 0);
  const entry = `${url}/src/ui/index.html`;

  const browser = await chromium.launch();
  try {
    // ---- RESA A: Öppna -> Ge mig ett dilemma -> dilemma -> Tänk vidare (sv) ----
    {
      console.log("\nRESA A (random, sv)");
      const page = await browser.newPage();
      await captureHouseEvents(page);
      await page.goto(entry);
      await page.waitForSelector(".home__question");

      check("home question visible", await page.getByText("Vad vill du utforska?").isVisible());
      await page.getByRole("button", { name: "Ge mig ett dilemma" }).click();
      await page.waitForSelector(".dilemma-card__title");
      check("dilemma title visible", await page.locator(".dilemma-card__title").isVisible());
      check("'Vad hade du gjort?' prompt visible", await page.getByText("Vad hade du gjort?").isVisible());

      await page.getByRole("button", { name: "Tänk vidare" }).click();
      check("thinking chair status note appears", await page.getByText("Tänkarstolen är inte ansluten").isVisible());

      const names = await eventNames(page);
      check("dilemma_explorer_opened fired", names.includes("dilemma_explorer_opened"));
      check("dilemma_discovered fired", names.includes("dilemma_discovered"));
      check("dilemma_opened fired", names.includes("dilemma_opened"));
      check("thinking_chair_requested fired", names.includes("thinking_chair_requested"));

      await page.screenshot({ path: path.join(screenshotDir, "resa-a-sv.png") });
      await page.close();
    }

    // ---- RESA B: Öppna -> Välj ämne -> välj dilemma -> Tänk vidare (sv) ----
    {
      console.log("\nRESA B (theme, sv)");
      const page = await browser.newPage();
      await page.goto(entry);

      await page.getByRole("button", { name: "Välj ett ämne" }).click();
      check("theme grid shows 'Tystnad'", await page.getByText("Tystnad", { exact: true }).isVisible());

      await page.getByText("Tystnad", { exact: true }).click();
      check("theme results show a relevant dilemma", await page.getByText("Tystnaden i rummet").isVisible());

      await page.getByText("Tystnaden i rummet").click();
      await page.waitForSelector(".dilemma-card__title");
      check("opened the selected dilemma", (await page.locator(".dilemma-card__title").innerText()) === "Tystnaden i rummet");

      await page.getByRole("button", { name: "Tänk vidare" }).click();
      check("thinking chair status note appears (theme path)", await page.getByText("Tänkarstolen är inte ansluten").isVisible());

      await page.screenshot({ path: path.join(screenshotDir, "resa-b-sv.png") });
      await page.close();
    }

    // ---- RESA C: Öppna -> sök fritext -> relevanta resultat -> välj -> Tänk vidare (sv) ----
    {
      console.log("\nRESA C (search, sv)");
      const page = await browser.newPage();
      await page.goto(entry);

      await page.getByRole("button", { name: "Sök bland dilemman" }).click();
      await page.locator(".search-input").fill("chef som inte lyssnar");
      await page.locator(".search-submit").click();
      check("search returns the expected dilemma", await page.getByText("Chefen som inte lyssnar").isVisible());

      await page.getByText("Chefen som inte lyssnar").click();
      await page.waitForSelector(".dilemma-card__title");
      check("opened the searched dilemma", (await page.locator(".dilemma-card__title").innerText()) === "Chefen som inte lyssnar");

      await page.getByRole("button", { name: "Tänk vidare" }).click();
      check("thinking chair status note appears (search path)", await page.getByText("Tänkarstolen är inte ansluten").isVisible());

      // treasure-hunt discovery elements present but collapsed by default
      const discoveryOpen = await page.locator(".discovery details[open]").count();
      check("discovery sections exist but are collapsed by default", (await page.locator(".discovery details").count()) > 0 && discoveryOpen === 0);

      await page.screenshot({ path: path.join(screenshotDir, "resa-c-sv.png") });
      await page.close();
    }

    // ---- English locale: RESA A end-to-end in en ----
    {
      console.log("\nRESA A (random, en)");
      const page = await browser.newPage();
      await page.goto(entry);
      await page.getByRole("button", { name: "English" }).click();
      check("home question switched to English", await page.getByText("What would you like to explore?").isVisible());

      await page.getByRole("button", { name: "Give me a dilemma" }).click();
      await page.waitForSelector(".dilemma-card__title");
      check("en dilemma prompt visible", await page.getByText("What would you have done?").isVisible());

      await page.getByRole("button", { name: "Think further" }).click();
      check("en thinking chair status note appears", await page.getByText("not connected in this version").isVisible());

      await page.screenshot({ path: path.join(screenshotDir, "resa-a-en.png") });
      await page.close();
    }

    // ---- Language switch mid-journey stays on the same dilemma ----
    {
      console.log("\nLocale switch mid-dilemma");
      const page = await browser.newPage();
      await page.goto(entry);
      await page.getByRole("button", { name: "Sök bland dilemman" }).click();
      await page.locator(".search-input").fill("resultat före människor");
      await page.locator(".search-submit").click();
      await page.getByText("Resultat före människor").click();
      await page.waitForSelector(".dilemma-card__title");

      await page.getByRole("button", { name: "English" }).click();
      check("same dilemma, now in English", (await page.locator(".dilemma-card__title").innerText()) === "Results before people");

      await page.screenshot({ path: path.join(screenshotDir, "locale-switch-mid-dilemma.png") });
      await page.close();
    }

    // ---- Mobile viewport 375px: full RESA A + no horizontal scroll ----
    {
      console.log("\nMobile 375px (RESA A)");
      const page = await browser.newPage({ viewport: { width: 375, height: 812 } });
      await page.goto(entry);
      await page.waitForSelector(".home__question");
      check("no horizontal scroll on home", await noHorizontalScroll(page));

      await page.getByRole("button", { name: "Ge mig ett dilemma" }).click();
      await page.waitForSelector(".dilemma-card__title");
      check("no horizontal scroll on dilemma view", await noHorizontalScroll(page));

      const chairBtn = page.getByRole("button", { name: "Tänk vidare" });
      const box = await chairBtn.boundingBox();
      check("'Tänk vidare' is a large touch target (>= 44px tall)", box && box.height >= 44);

      await page.getByRole("button", { name: "Tänk vidare" }).click();
      await page.waitForSelector(".status-note");
      check("thinking chair note visible on mobile", await page.getByText("Tänkarstolen är inte ansluten").isVisible());

      await page.screenshot({ path: path.join(screenshotDir, "mobile-375-resa-a.png"), fullPage: true });
      await page.close();
    }

    // ---- Mobile 375px: theme + search paths, no horizontal scroll ----
    {
      console.log("\nMobile 375px (theme + search)");
      const page = await browser.newPage({ viewport: { width: 375, height: 812 } });
      await page.goto(entry);

      await page.getByRole("button", { name: "Välj ett ämne" }).click();
      check("no horizontal scroll on theme grid (375px)", await noHorizontalScroll(page));
      await page.screenshot({ path: path.join(screenshotDir, "mobile-375-themes.png") });

      await page.getByRole("button", { name: "Till start" }).click();
      await page.getByRole("button", { name: "Sök bland dilemman" }).click();
      await page.locator(".search-input").fill("medarbetare som gjort fel");
      await page.locator(".search-submit").click();
      check("search results readable on 375px, no horizontal scroll", await noHorizontalScroll(page));
      await page.screenshot({ path: path.join(screenshotDir, "mobile-375-search.png") });

      await page.close();
    }
  } finally {
    await browser.close();
    await close();
  }

  console.log(`\n${passCount} passed, ${failCount} failed`);
  if (failCount > 0) {
    console.error("FAILED:", failures);
    process.exitCode = 1;
  }
}

run().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
