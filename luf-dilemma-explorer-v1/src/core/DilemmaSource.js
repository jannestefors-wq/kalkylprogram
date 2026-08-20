/**
 * DilemmaSource — the adapter contract between the Explorer UI and wherever
 * dilemma content actually lives.
 *
 * V1 ships exactly one implementation: FixtureDilemmaSource, backed by the
 * local JSON files in src/data/. It reads no network, no D1, no production
 * system of any kind.
 *
 * Work integrates the real Dilemma Bank later by writing a second class
 * that implements this same interface (e.g. D1DilemmaSource) and swapping
 * it in at the app's composition point (see src/ui/app.js, `createSource`).
 * The UI and every other core module only ever talk to this interface —
 * never to fixtures or a database directly. See docs/DILEMMA_SOURCE_CONTRACT.md.
 *
 * All methods are async so a future network/D1-backed implementation is a
 * drop-in replacement with no UI changes.
 */
import { searchDilemmas } from "./searchEngine.js";

export class DilemmaSource {
  /** @param {string} locale - "sv" | "en" */
  async getRandom(locale) {
    throw new Error("DilemmaSource.getRandom not implemented");
  }

  /** @param {string} themeId @param {string} locale */
  async getByTheme(themeId, locale) {
    throw new Error("DilemmaSource.getByTheme not implemented");
  }

  /** @param {string} query @param {string} locale */
  async search(query, locale) {
    throw new Error("DilemmaSource.search not implemented");
  }

  /** @param {string} id @param {string} locale */
  async getById(id, locale) {
    throw new Error("DilemmaSource.getById not implemented");
  }

  /** @param {string} locale @returns {Promise<Array<{id:string,label:string}>>} */
  async listThemes(locale) {
    throw new Error("DilemmaSource.listThemes not implemented");
  }

  /**
   * Subtle "treasure hunt" discovery: dilemmas related to a given one.
   * @param {string} id @param {string} locale
   */
  async getRelated(id, locale) {
    throw new Error("DilemmaSource.getRelated not implemented");
  }
}

/**
 * FixtureDilemmaSource — V1's only implementation. Loads locale-scoped
 * JSON given to it at construction time (no fetch/import inside the class,
 * so it runs identically in the browser and in Node tests).
 */
export class FixtureDilemmaSource extends DilemmaSource {
  /**
   * @param {object} data
   * @param {Record<string, Array>} data.dilemmasByLocale - {sv: [...], en: [...]}
   * @param {Record<string, Array>} data.themesByLocale - {sv: [...], en: [...]}
   */
  constructor({ dilemmasByLocale, themesByLocale }) {
    super();
    this._dilemmasByLocale = dilemmasByLocale;
    this._themesByLocale = themesByLocale;
  }

  _dilemmas(locale) {
    const list = this._dilemmasByLocale[locale];
    if (!list) throw new Error(`No fixture dilemmas for locale "${locale}"`);
    return list;
  }

  _themes(locale) {
    const list = this._themesByLocale[locale];
    if (!list) throw new Error(`No fixture themes for locale "${locale}"`);
    return list;
  }

  async getRandom(locale) {
    const list = this._dilemmas(locale);
    return list[Math.floor(Math.random() * list.length)];
  }

  async getByTheme(themeId, locale) {
    return this._dilemmas(locale).filter((d) => d.themes.includes(themeId));
  }

  async search(query, locale) {
    return searchDilemmas(this._dilemmas(locale), query, this._themes(locale));
  }

  async getById(id, locale) {
    return this._dilemmas(locale).find((d) => d.id === id) || null;
  }

  async listThemes(locale) {
    return this._themes(locale);
  }

  async getRelated(id, locale) {
    const list = this._dilemmas(locale);
    const current = list.find((d) => d.id === id);
    if (!current) return [];

    const explicit = (current.related_ids || [])
      .map((relId) => list.find((d) => d.id === relId))
      .filter(Boolean);

    if (explicit.length) return explicit;

    // Fallback discovery: other dilemmas sharing a theme.
    return list
      .filter((d) => d.id !== id && d.themes.some((t) => current.themes.includes(t)))
      .slice(0, 3);
  }
}
