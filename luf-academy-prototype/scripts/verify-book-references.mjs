// Kontrollerar varje bokhänvisning i innehållsregistret mot bokens text.
//
//   LHM_BOOK_TXT=/sökväg/bok.txt node scripts/verify-book-references.mjs
//
// Boktexten ska vara uttagen sida för sida med markeringen
// "=====PDFPAGE <n>=====" före varje PDF-sida. Den läggs aldrig i repot.
// Tryckt sida = PDF-sida minus 7.
//
// Kontrolleras:
//  1. Varje läsanvisnings kapitelrubrik finns i innehållsförteckningen och
//     börjar på den tryckta sida som förteckningen anger.
//  2. Anvisningens sidintervall ligger inom kapitlet.
//  3. Varje citat (quote) finns ordagrant på angiven sida.
//  4. Varje text inom ”citattecken” i en hjälptext eller not finns på någon
//     av sidorna i momentets eller fältets interna refs. Refs visas aldrig
//     för deltagaren.
//  5. De fem principerna finns ordagrant på s. 14–15.
//  6. Varje fält märkt som bokens egen fråga (origin "book") finns ordagrant
//     på sina sidor. Hörnets ord före första punkten räknas inte.
import { readFileSync } from "node:fs";
import { STEPS, FIVE_PRINCIPLES } from "../server/content.mjs";

const OFFSET = 7;
const path = process.env.LHM_BOOK_TXT;
if (!path) {
  console.log("LHM_BOOK_TXT saknas. Ingen kontroll gjord.");
  process.exit(2);
}
const raw = readFileSync(path, "utf8");
const parts = raw.split(/\n=====PDFPAGE (\d+)=====\n/).slice(1);
const pdf = {};
for (let i = 0; i < parts.length; i += 2) pdf[Number(parts[i])] = parts[i + 1];
const norm = (s) => s.replace(/[”“"]/g, '"').replace(/\s+/g, " ").replace(/- /g, "-").trim();
const printed = (p) => norm(pdf[p + OFFSET] || "");
const span = (from, to = from) => {
  let out = "";
  for (let p = from; p <= to; p += 1) out += " " + printed(p).replace(/^\d+ /, "");
  return norm(out);
};

// Innehållsförteckningen, PDF-sida 5.
const toc = [];
for (const line of pdf[5].split("\n")) {
  const m = line.match(/^(.+?)\s*\.{3,}\s*(\d+)\s*$/);
  if (m) toc.push({ title: norm(m[1]), page: Number(m[2]) });
}
const lastPrinted = Math.max(...Object.keys(pdf).map(Number)) - OFFSET;

const failures = [];
const passes = [];
const check = (ok, what) => (ok ? passes : failures).push(what);

for (const step of STEPS.filter((s) => s.built)) {
  for (const section of step.sections) {
    const r = section.reading;
    if (r) {
      for (const ch of [...r.chapters, ...(r.optional || [])]) {
        const idx = toc.findIndex((e) => e.title === norm(ch.title));
        check(idx >= 0, `${step.key} läsning: rubriken "${ch.title}" finns i innehållsförteckningen`);
        if (idx < 0) continue;
        const [from, to] = ch.pages.split("–").map(Number);
        const start = toc[idx].page;
        const end = (toc[idx + 1]?.page || lastPrinted + 1) - 1;
        check(from >= start && to <= end && from <= to, `${step.key} läsning: ${ch.title} s. ${ch.pages} ligger inom kapitlet (s. ${start}–${end})`);
        const head = printed(start).split(" ").slice(1).join(" ");
        check(head.startsWith(norm(ch.title)), `${step.key} läsning: ${ch.title} börjar på tryckt s. ${start}`);
        const [pf, pt] = ch.pdfPages.split("–").map(Number);
        check(pf === from + OFFSET && pt === to + OFFSET, `${step.key} läsning: PDF-sidor ${ch.pdfPages} motsvarar s. ${ch.pages}`);
      }
    }
    if (section.quote) {
      const q = norm(section.quote.text);
      check(span(section.quote.page, section.quote.page + 1).includes(q), `${step.key} citat s. ${section.quote.page}: "${section.quote.text}"`);
    }
    for (const page of new Set([...(section.refs || []), ...(section.fields || []).flatMap((f) => f.refs || [])])) {
      check(page >= 1 && page <= lastPrinted && printed(page).length > 0, `${step.key}/${section.key} intern sidreferens s. ${page} finns i boken`);
    }
    for (const f of (section.fields || []).filter((x) => x.origin === "book")) {
      const q = norm(f.label.replace(/^[A-ZÅÄÖ][a-zåäö]+\. (?=[A-ZÅÄÖ])/, "")).toLowerCase();
      const found = f.refs.some((page) => span(page, page + 1).toLowerCase().includes(q));
      check(found, `${step.key}/${section.key}.${f.key} källfråga s. ${f.refs.join(", ")}: "${f.label}"`);
    }
    const refTexts = [
      { text: section.hint, refs: section.refs },
      { text: section.note, refs: section.refs },
      ...(section.fields || []).map((f) => ({ text: f.hint, refs: f.refs })),
    ].filter((t) => t.text);
    for (const { text, refs } of refTexts) {
      const quotes = [...text.matchAll(/”([^”]+)”/g)].map((m) => m[1]);
      if (!refs?.length) continue;
      for (const q of quotes) {
        const found = refs.some((page) => span(page, page + 1).includes(norm(q)));
        check(found, `${step.key}/${section.key} citat s. ${refs.join(", ")}: "${q}"`);
      }
    }
  }
}
for (const principle of FIVE_PRINCIPLES) check(span(14, 15).includes(norm(principle)), `princip s. 14–15: "${principle}"`);

console.log(`Kontrollerade bokhänvisningar: ${passes.length} godkända, ${failures.length} fel.`);
for (const f of failures) console.log(`FEL  ${f}`);
if (process.argv.includes("--verbose")) for (const p of passes) console.log(`OK   ${p}`);
process.exit(failures.length ? 1 : 0);
