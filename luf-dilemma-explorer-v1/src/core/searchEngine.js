/**
 * Free-text search over dilemma fixtures.
 * Pure function, no I/O — kept separate from DilemmaSource so it can be
 * reused verbatim by a future non-fixture DilemmaSource implementation.
 */

function normalize(text) {
  return (text || "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, ""); // strip diacritics so accented and unaccented spellings both match
}

const FIELD_WEIGHTS = {
  title: 5,
  tags: 4,
  conflict: 3,
  dilemma: 2,
  themeLabels: 1,
};

/**
 * @param {Array} dilemmas - dilemma records (already locale-resolved)
 * @param {string} query - free text query
 * @param {Array} [themeLabels] - locale theme label list, [{id,label}]
 * @returns {Array} dilemmas ranked by relevance, highest first
 */
export function searchDilemmas(dilemmas, query, themeLabels = []) {
  const q = normalize(query).trim();
  if (!q) return [];

  const terms = q.split(/\s+/).filter(Boolean);
  const labelById = new Map(themeLabels.map((t) => [t.id, t.label]));

  const scored = dilemmas.map((d) => {
    const themeLabelText = (d.themes || []).map((id) => labelById.get(id) || id).join(" ");
    const haystacks = {
      title: normalize(d.title),
      tags: normalize((d.tags || []).join(" ")),
      conflict: normalize(d.conflict),
      dilemma: normalize(d.dilemma),
      themeLabels: normalize(themeLabelText),
    };

    let score = 0;
    for (const term of terms) {
      for (const [field, weight] of Object.entries(FIELD_WEIGHTS)) {
        if (haystacks[field].includes(term)) score += weight;
      }
    }
    return { d, score };
  });

  return scored
    .filter((r) => r.score > 0)
    .sort((a, b) => b.score - a.score)
    .map((r) => r.d);
}
