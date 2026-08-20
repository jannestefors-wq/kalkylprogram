import { FixtureDilemmaSource } from "../core/DilemmaSource.js";
import { HOUSE_EVENTS, emitHouseEvent } from "../core/events.js";
import { openInThinkingChair, setThinkingChairHandler } from "../core/integrationBridge.js";
import { DEFAULT_LOCALE, resolveInitialLocale, createTranslator } from "../core/locale.js";

const DATA_BASE = new URL("../data/", import.meta.url);

async function loadJSON(name) {
  const res = await fetch(new URL(name, DATA_BASE));
  if (!res.ok) throw new Error(`Failed to load ${name}: ${res.status}`);
  return res.json();
}

function escapeHtml(str) {
  return String(str ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

// Work: this is the one place a real Dilemma Bank source would be swapped
// in. Everything downstream only talks to the DilemmaSource interface.
function createSource({ dilemmasByLocale, themesByLocale }) {
  return new FixtureDilemmaSource({ dilemmasByLocale, themesByLocale });
}

const SCREEN = Object.freeze({
  HOME: "HOME",
  RANDOM: "RANDOM",
  THEME_LIST: "THEME_LIST",
  THEME_RESULTS: "THEME_RESULTS",
  SEARCH: "SEARCH",
  DILEMMA: "DILEMMA",
});

async function main() {
  const root = document.getElementById("app");

  const [dilemmasSv, dilemmasEn, themesSv, themesEn, stringsSv, stringsEn] = await Promise.all([
    loadJSON("dilemmas.sv.json"), loadJSON("dilemmas.en.json"),
    loadJSON("themes.sv.json"), loadJSON("themes.en.json"),
    loadJSON("strings.sv.json"), loadJSON("strings.en.json"),
  ]);

  const source = createSource({
    dilemmasByLocale: { sv: dilemmasSv, en: dilemmasEn },
    themesByLocale: { sv: themesSv, en: themesEn },
  });
  const stringsByLocale = { sv: stringsSv, en: stringsEn };

  // No real Thinking Chair yet — V1 fails soft and reports it visibly.
  setThinkingChairHandler(null);

  // The Explorer runs on a fixed kiosk computer in Runda bordet, so it
  // always rests on Swedish (DEFAULT_LOCALE) rather than sniffing the
  // browser's language — a kiosk's OS/browser locale says nothing about
  // the visitor standing in front of it. An explicit "?lang=en" override
  // (or a Work-set window.__LUF_LOCALE__) still switches it, e.g. for a
  // future non-kiosk embedding of this same component.
  const langOverride = new URLSearchParams(window.location.search).get("lang") || window.__LUF_LOCALE__;
  const state = {
    locale: resolveInitialLocale({ override: langOverride }),
    screen: SCREEN.HOME,
    themeId: null,
    searchQuery: "",
    searchResults: [],
    themeResults: [],
    currentDilemma: null,
    currentSource: null,
    history: [],
    chairStatus: null,
  };

  emitHouseEvent(HOUSE_EVENTS.EXPLORER_OPENED, { locale: state.locale });

  function t(key, vars) {
    return createTranslator(stringsByLocale[state.locale])(key, vars);
  }

  function snapshot() {
    return {
      screen: state.screen, themeId: state.themeId, searchQuery: state.searchQuery,
      searchResults: state.searchResults, themeResults: state.themeResults,
      currentDilemma: state.currentDilemma, currentSource: state.currentSource,
    };
  }

  function navigate(screen, patch = {}) {
    state.history.push(snapshot());
    Object.assign(state, { screen, ...patch });
    render();
  }

  function back() {
    const prev = state.history.pop();
    if (prev) Object.assign(state, prev);
    else state.screen = SCREEN.HOME;
    render();
  }

  function goHome() {
    state.history = [];
    Object.assign(state, {
      screen: SCREEN.HOME, themeId: null, searchQuery: "", searchResults: [],
      themeResults: [], currentDilemma: null, currentSource: null, chairStatus: null,
    });
    render();
  }

  async function openRandom() {
    const dilemma = await source.getRandom(state.locale);
    const related = await source.getRelated(dilemma.id, state.locale);
    emitHouseEvent(HOUSE_EVENTS.DILEMMA_DISCOVERED, { dilemma_id: dilemma.id, source: "random" });
    navigate(SCREEN.DILEMMA, { currentDilemma: { ...dilemma, related }, currentSource: "random" });
    emitHouseEvent(HOUSE_EVENTS.DILEMMA_OPENED, { dilemma_id: dilemma.id, source: "random" });
  }

  async function openThemeList() {
    const themes = await source.listThemes(state.locale);
    navigate(SCREEN.THEME_LIST, { themes });
  }

  async function selectTheme(themeId) {
    emitHouseEvent(HOUSE_EVENTS.THEME_SELECTED, { theme: themeId });
    const results = await source.getByTheme(themeId, state.locale);
    emitHouseEvent(HOUSE_EVENTS.DILEMMA_DISCOVERED, {
      dilemma_ids: results.map((d) => d.id), source: "theme", theme: themeId,
    });
    navigate(SCREEN.THEME_RESULTS, { themeId, themeResults: results });
  }

  async function runSearch(query) {
    const results = await source.search(query, state.locale);
    emitHouseEvent(HOUSE_EVENTS.DILEMMA_DISCOVERED, {
      dilemma_ids: results.map((d) => d.id), source: "search", query,
    });
    Object.assign(state, { searchQuery: query, searchResults: results });
    render();
  }

  async function openDilemma(id, fromSource) {
    const dilemma = await source.getById(id, state.locale);
    const related = await source.getRelated(id, state.locale);
    navigate(SCREEN.DILEMMA, { currentDilemma: { ...dilemma, related }, currentSource: fromSource });
    emitHouseEvent(HOUSE_EVENTS.DILEMMA_OPENED, { dilemma_id: id, source: fromSource });
  }

  function requestThinkingChair() {
    const d = state.currentDilemma;
    const result = openInThinkingChair(d.id, {
      theme: d.themes, source: state.currentSource, language: state.locale,
      context: { title: d.title },
    });
    state.chairStatus = result.delivered ? "pending" : "unavailable";
    render();
  }

  async function toggleLocale() {
    state.locale = state.locale === "sv" ? "en" : "sv";
    await refreshForLocale();
    render();
  }

  // Re-derive whatever the current screen shows in the newly selected
  // locale, so switching language mid-journey never leaves stale text on
  // screen (theme labels, search results, and the open dilemma itself all
  // carry locale-specific fields).
  async function refreshForLocale() {
    switch (state.screen) {
      case SCREEN.THEME_LIST:
        state.themes = await source.listThemes(state.locale);
        break;
      case SCREEN.THEME_RESULTS:
        state.themeResults = await source.getByTheme(state.themeId, state.locale);
        break;
      case SCREEN.SEARCH:
        if (state.searchQuery.trim()) {
          state.searchResults = await source.search(state.searchQuery, state.locale);
        }
        break;
      case SCREEN.DILEMMA:
        if (state.currentDilemma) {
          const dilemma = await source.getById(state.currentDilemma.id, state.locale);
          const related = await source.getRelated(state.currentDilemma.id, state.locale);
          state.currentDilemma = { ...dilemma, related };
        }
        break;
    }
  }

  // ---- rendering ----

  function topbar(showBack) {
    return `
      <div class="topbar">
        <div class="topbar__nav">
          ${showBack ? `<button class="iconbtn" data-action="back">${t("nav.back")}</button>` : ""}
          ${state.screen !== SCREEN.HOME ? `<button class="iconbtn" data-action="home">${t("nav.home")}</button>` : ""}
        </div>
        <button class="lang-toggle" data-action="toggle-lang">${t("language.toggle")}</button>
      </div>`;
  }

  function renderHome() {
    return `
      ${topbar(false)}
      <div class="home">
        <h1 class="home__question">${escapeHtml(t("home.question"))}</h1>
        <div class="home__paths">
          <button class="path-card" data-action="go-random"><span class="path-card__mark">✦</span>${escapeHtml(t("home.path.random"))}</button>
          <button class="path-card" data-action="go-theme"><span class="path-card__mark">✦</span>${escapeHtml(t("home.path.theme"))}</button>
          <button class="path-card" data-action="go-search"><span class="path-card__mark">✦</span>${escapeHtml(t("home.path.search"))}</button>
        </div>
      </div>`;
  }

  function renderThemeList() {
    const items = state.themes.map((theme) => {
      const count = dilemmasByLocaleCount(theme.id);
      return `
        <button class="theme-chip" data-action="select-theme" data-theme-id="${escapeHtml(theme.id)}">
          <span class="theme-chip__label">${escapeHtml(theme.label)}</span>
          <span class="theme-chip__count">${escapeHtml(t("theme.count", { count }))}</span>
        </button>`;
    }).join("");
    return `
      ${topbar(true)}
      <h2 class="section-title">${escapeHtml(t("theme.title"))}</h2>
      <div class="theme-grid">${items}</div>`;
  }

  function dilemmasByLocaleCount(themeId) {
    const list = state.locale === "sv" ? dilemmasSv : dilemmasEn;
    return list.filter((d) => d.themes.includes(themeId)).length;
  }

  function resultCard(d, action) {
    return `
      <li>
        <button class="result-card" data-action="${action}" data-id="${escapeHtml(d.id)}">
          <p class="result-card__title">${escapeHtml(d.title)}</p>
          <p class="result-card__meta">${escapeHtml(d.conflict)}</p>
        </button>
      </li>`;
  }

  function renderThemeResults() {
    const list = state.themeResults.map((d) => resultCard(d, "open-theme-result")).join("");
    return `
      ${topbar(true)}
      <h2 class="section-title">${escapeHtml(t("theme.title"))}</h2>
      <ul class="result-list">${list}</ul>`;
  }

  function renderSearch() {
    const hasQuery = state.searchQuery.trim().length > 0;
    const results = hasQuery
      ? (state.searchResults.length
          ? `<p class="section-title" style="font-size:1rem;">${escapeHtml(t("search.resultCount", { count: state.searchResults.length }))}</p>
             <ul class="result-list">${state.searchResults.map((d) => resultCard(d, "open-search-result")).join("")}</ul>`
          : `<p class="empty-state">${escapeHtml(t("search.empty"))}</p>`)
      : "";
    return `
      ${topbar(true)}
      <h2 class="section-title">${escapeHtml(t("home.path.search"))}</h2>
      <form class="search-form" data-role="search-form">
        <input class="search-input" type="search" name="q" placeholder="${escapeHtml(t("search.placeholder"))}" value="${escapeHtml(state.searchQuery)}" autofocus />
        <button class="search-submit" type="submit">${escapeHtml(t("search.button"))}</button>
      </form>
      ${results}`;
  }

  function renderDilemma() {
    const d = state.currentDilemma;
    const related = d.related || [];
    const perspectives = (d.perspectives || []).map((p) => `
      <div class="perspective">
        <span class="perspective__label">${escapeHtml(p.label)}</span>
        <span>${escapeHtml(p.text)}</span>
      </div>`).join("");
    const relatedItems = related.map((r) => `
      <li><button class="result-card" data-action="open-related" data-id="${escapeHtml(r.id)}">
        <p class="result-card__title">${escapeHtml(r.title)}</p>
      </button></li>`).join("");

    const chairNote = state.chairStatus === "pending" ? `<p class="status-note">${escapeHtml(t("chair.pending"))}</p>`
      : state.chairStatus === "unavailable" ? `<p class="status-note">${escapeHtml(t("chair.unavailable"))}</p>` : "";

    const againBtn = state.currentSource === "random"
      ? `<button class="iconbtn" data-action="go-random" style="margin-top:1rem;">${escapeHtml(t("random.again"))}</button>` : "";

    return `
      ${topbar(true)}
      <article class="dilemma-card">
        <h2 class="dilemma-card__title">${escapeHtml(d.title)}</h2>
        <p class="dilemma-card__body">${escapeHtml(d.dilemma)}</p>
        <p class="dilemma-card__prompt">${escapeHtml(t("dilemma.prompt"))}</p>
        <button class="think-further" data-action="think-further">${escapeHtml(t("dilemma.thinkFurther"))}</button>
        ${chairNote}
      </article>
      ${(perspectives || relatedItems) ? `
      <div class="discovery">
        ${perspectives ? `<details><summary>${escapeHtml(t("dilemma.perspectives"))}</summary>${perspectives}</details>` : ""}
        ${relatedItems ? `<details><summary>${escapeHtml(t("dilemma.related"))}</summary><ul class="related-list">${relatedItems}</ul></details>` : ""}
      </div>` : ""}
      ${againBtn}`;
  }

  function render() {
    let html;
    switch (state.screen) {
      case SCREEN.HOME: html = renderHome(); break;
      case SCREEN.THEME_LIST: html = renderThemeList(); break;
      case SCREEN.THEME_RESULTS: html = renderThemeResults(); break;
      case SCREEN.SEARCH: html = renderSearch(); break;
      case SCREEN.DILEMMA: html = renderDilemma(); break;
      default: html = renderHome();
    }
    root.innerHTML = html;
    document.documentElement.lang = state.locale;
  }

  // ---- event delegation ----

  root.addEventListener("click", (e) => {
    const el = e.target.closest("[data-action]");
    if (!el) return;
    const action = el.dataset.action;
    if (action === "back") return back();
    if (action === "home") return goHome();
    if (action === "toggle-lang") return void toggleLocale();
    if (action === "go-random") return void openRandom();
    if (action === "go-theme") return void openThemeList();
    if (action === "go-search") return navigate(SCREEN.SEARCH, { searchQuery: "", searchResults: [] });
    if (action === "select-theme") return void selectTheme(el.dataset.themeId);
    if (action === "open-theme-result") return void openDilemma(el.dataset.id, "theme");
    if (action === "open-search-result") return void openDilemma(el.dataset.id, "search");
    if (action === "open-related") return void openDilemma(el.dataset.id, state.currentSource);
    if (action === "think-further") return requestThinkingChair();
  });

  root.addEventListener("submit", (e) => {
    const form = e.target.closest('[data-role="search-form"]');
    if (!form) return;
    e.preventDefault();
    const query = new FormData(form).get("q") || "";
    void runSearch(String(query));
  });

  render();
}

main().catch((err) => {
  console.error("LUF Dilemma Explorer failed to start:", err);
  const root = document.getElementById("app");
  if (root) root.innerHTML = `<p class="empty-state">Something went wrong loading the Explorer.</p>`;
});
