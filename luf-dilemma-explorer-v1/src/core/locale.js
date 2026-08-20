/**
 * Locale support. The Explorer supports "sv" and "en" from one codebase —
 * there is no separate component per language. Content (dilemmas, themes)
 * and UI strings are both keyed by locale and swapped at runtime.
 */

export const SUPPORTED_LOCALES = Object.freeze(["sv", "en"]);
export const DEFAULT_LOCALE = "sv";

export function isSupportedLocale(locale) {
  return SUPPORTED_LOCALES.includes(locale);
}

/**
 * Resolve the initial locale: explicit override > browser language > default.
 * Kept as a pure function (navigator passed in) so it is testable in Node.
 */
export function resolveInitialLocale({ override, navigatorLanguage } = {}) {
  if (isSupportedLocale(override)) return override;
  const short = (navigatorLanguage || "").slice(0, 2).toLowerCase();
  if (isSupportedLocale(short)) return short;
  return DEFAULT_LOCALE;
}

/**
 * Tiny string lookup with {placeholder} interpolation and a
 * singular/plural ".one"/".many" convention for counts.
 */
export function createTranslator(strings) {
  return function t(key, vars = {}) {
    let resolvedKey = key;
    if (typeof vars.count === "number") {
      resolvedKey = `${key}.${vars.count === 1 ? "one" : "many"}`;
      if (!(resolvedKey in strings)) resolvedKey = key;
    }
    const template = strings[resolvedKey] ?? key;
    return template.replace(/\{(\w+)\}/g, (_, name) => (name in vars ? String(vars[name]) : `{${name}}`));
  };
}
