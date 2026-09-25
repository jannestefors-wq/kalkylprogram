// Maskinell innehållskontroll mot LMHM VERSION 2 FINAL CONTENT SPEC. Order 014, punkt 17.
//
// 1. All deltagartext i specifikationen (citatblock och text inom "citattecken")
//    finns ordagrant i det deltagaren ser: registret som skickas till klienten
//    och klientens egen text. Text för Jan, bokningsvillkor och interna
//    källor hoppas över. De visas aldrig i appen.
// 2. Borttagna texter från nuvarande kurs finns inte kvar synligt.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { STEPS, publicProgram } from "../server/content.mjs";

const SPEC = readFileSync(new URL("../docs/LMHM-V2-FINAL-CONTENT-SPEC.md", import.meta.url), "utf8");
const CLIENT = readFileSync(new URL("../public/app.js", import.meta.url), "utf8");

// Allt deltagaren kan se. Listor av textpar slås också ihop, så att en rad i
// specifikationen kan motsvara två delar i registret.
function corpus() {
  const out = [];
  const walk = (v) => {
    if (typeof v === "string") out.push(v);
    else if (Array.isArray(v)) {
      if (v.every((x) => typeof x === "string")) out.push(v.join(" "));
      v.forEach(walk);
    } else if (v && typeof v === "object") Object.values(v).forEach(walk);
  };
  walk(publicProgram());
  return `${out.join("\n")}\n${CLIENT}`;
}
const norm = (s) => s.replace(/\\"/g, '"').replace(/\s+/g, " ").trim();

// Delar av specifikationen som inte är deltagartext i appen.
function participantLines() {
  const lines = SPEC.split("\n");
  const keep = [];
  let skip = false;
  let section = 0;
  for (const line of lines) {
    const h2 = line.match(/^## (\d+)\./);
    if (h2) section = Number(h2[1]);
    if (/^\*\*JAN/.test(line) || /^\*\*DELTAGARTEXT\. Bokningsvillkor/.test(line) || /^\*\*INTERN KÄLLA/.test(line)) skip = true;
    else if (/^\*\*(DELTAGARTEXT|SYSTEMLOGIK)/.test(line) || /^#{2,3} /.test(line) || /^\*\*[A-ZÅÄÖ][^*]*\*\*/.test(line)) skip = false;
    if (/^\*\*JAN[:.]/.test(line)) skip = true;
    // 1 till 3 beskriver produkten, 5 är regler, 24 och 25 är nycklar och antal.
    if ([0, 1, 2, 3, 5, 24, 25].includes(section)) continue;
    if (!skip) keep.push(line);
  }
  return keep;
}

function required() {
  const texts = new Set();
  for (const line of participantLines()) {
    if (line.startsWith("> ")) texts.add(norm(line.slice(2)));
    for (const m of line.matchAll(/"([^"]+)"/g)) texts.add(norm(m[1]));
  }
  // Korta ord som "Ja" eller "Nej" kontrolleras genom valen nedan.
  return [...texts].filter((t) => t.length >= 12);
}

test("innehåll: all deltagartext i FINAL CONTENT SPEC finns ordagrant i appen", () => {
  const text = norm(corpus());
  const list = required();
  assert.ok(list.length > 150, `för få texter hittades i specifikationen: ${list.length}`);
  const missing = list.filter((t) => !text.includes(t));
  assert.deepEqual(missing, [], `saknas i appen:\n${missing.join("\n")}`);
});

test("innehåll: rubriker, val och knappar enligt specifikationen", () => {
  const titles = (k) => STEPS.find((s) => s.key === k).sections.map((s) => s.title);
  const has = (k, t) => assert.ok(titles(k).includes(t), `${k}: ${t}`);
  for (const t of ["Människan först", "Stanna upp", "Var är jag nu?", "Tre saker jag vill förändra", "Människorna runt mig", "En situation från min verklighet", "Veckans triangel", "Det här ska jag prova", "Vad hände?", "Min privata reflektion", "Träffen"]) has("w1", t);
  for (const t of ["Förra veckan", "Mod, ansvar och beslut", "Det jag skjuter upp"]) has("w2", t);
  for (const t of ["Se. Höra. Känna.", "Min återkoppling"]) has("w3", t);
  for (const t of ["Halvvägs", "Spegeln", "Relation, trygghet och det svåra samtalet", "Trygghet. Relation. Utveckling.", "Samtalet som är mitt att ta"]) has("w4", t);
  for (const t of ["Teamet och förutsättningarna", "Problemet jag har lagt hos en person"]) has("w5", t);
  for (const t of ["Ledarskap under press", "Trycket och valet", "Hela resan", "Spegeln", "Det jag föll tillbaka i", "De fem principerna", "Det som fortsätter"]) has("w6", t);
  for (const t of ["Vad blev faktiskt kvar?", "Återträffen"]) has("d30", t);
  for (const t of ["Inför startsamtalet", "Efter startsamtalet"]) has("start", t);
  for (const t of ["Samtal med Jan", "Inför samtalet", "Efter samtalet"]) has("samtal", t);
  const weeks = STEPS.filter((s) => /^w\d$/.test(s.key)).map((s) => [s.title, s.subtitle]);
  assert.deepEqual(weeks, [
    ["Jag som ledare", "Vad behöver faktiskt förändras i mitt ledarskap?"],
    ["Mod, ansvar och beslut", "Vad skjuter jag upp trots att det är mitt ansvar?"],
    ["Se. Höra. Känna.", "Vad vet jag faktiskt innan jag bedömer en annan människa?"],
    ["Relation, trygghet och det svåra samtalet", "Vad behöver jag göra eftersom jag har ansvaret?"],
    ["Teamet och förutsättningarna", "Vad sitter hos personen, vad sitter i gruppen och vad har jag själv byggt runt dem?"],
    ["Ledarskap under press", "Vem blir jag när det blir svårt, och vad fortsätter jag göra?"],
  ]);
  const text = corpus();
  for (const t of ["Be om ett samtal", "Inte nu", "Be om ett samtal med Jan", "Berätta vad som hände", "Något nytt", "Dela med Jan"]) assert.ok(text.includes(t), t);
  const choice = (step, sec, key) => STEPS.find((s) => s.key === step).sections.find((s) => s.key === sec).fields.find((f) => f.key === key).options;
  assert.deepEqual(choice("w1", "vad-hande", "blev"), ["Ja", "Delvis", "Nej"]);
  assert.deepEqual(choice("w1", "vad-hande", "markte"), ["Ja", "Nej", "Jag vet inte"]);
  assert.deepEqual(choice("w2", "triangel", "galler"), ["Ett samtal", "Ett beslut", "Ett nej", "Ett besked", "Något annat jag behöver kliva fram i"]);
  assert.deepEqual(choice("w4", "samtalet", "med_vem"), ["Någon jag har ansvar för", "Två jag leder, som inte kommer överens", "En jämbördig kollega"]);
  assert.deepEqual(choice("w5", "niva", "tror"), ["Individ", "Team", "Organisation"]);
  assert.deepEqual(choice("d30", "kvar", "blev"), ["Ja", "Delvis", "Nej"]);
  assert.deepEqual(choice("w5", "niva", "fatt"), [
    "Trygghet. Hen frågar, säger emot och berättar när något blivit fel.",
    "Tydlighet. Hen vet varför, vart och vad som förväntas.",
    "Roller. Hen vet vem som gör vad och vem som beslutar.",
    "Feedback. Hen får höra vad som fungerar och vad som inte gör det.",
    "Firande. Hen får höra när något blev bra.",
  ]);
  assert.deepEqual(choice("w4", "spegel", "vem"), ["Medarbetare", "Kollega", "Egen chef", "Annan"]);
  assert.deepEqual(choice("w6", "principer", "vald"), ["Autenticitet före image", "Mod före bekvämlighet", "Relation före position", "Närvaro före produktivitet", "Långsiktighet före snabba poäng"]);
});

test("innehåll: läsanvisningarna följer specifikationens tabell", () => {
  const reading = (k) => STEPS.find((s) => s.key === k).sections.find((s) => s.kind === "reading").reading;
  const pairs = (k) => ({
    chapters: reading(k).chapters.map((c) => `${c.title} ${c.pages}`),
    optional: reading(k).optional.map((c) => `${c.title} ${c.pages}`),
  });
  assert.deepEqual(pairs("w1"), { chapters: ["Utan filter 7–15", "Människan först 17–27"], optional: [] });
  assert.deepEqual(pairs("w2"), { chapters: ["Modet att kliva fram 28–39", "Vad som formar en ledare 40–44"], optional: ["När det kostar att göra rätt 131–137", "Att säga nej utan att skapa drama 106–107"] });
  assert.deepEqual(pairs("w3"), { chapters: ["Triangelmetodiken 54–59", "Se — Höra — Känna 66–74", "Konsten att ge och ta emot feedback 79–81"], optional: [] });
  assert.deepEqual(pairs("w4"), { chapters: ["Trygghet — Relation — Utveckling 75–84", "Konflikt — Lösning — Ansvar 85–93"], optional: ["Kommunikation — företagets livsnerv 114–116", "Varför vi alltid börjar i fel ände 98", "Avrekrytering med värdighet 145"] });
  assert.deepEqual(pairs("w5"), { chapters: ["Individ — Team — Organisation 101–110", "Att bygga team som håller 123–130"], optional: ["När chefen inte lyssnar 97", "Delegering som utvecklingsverktyg 164", "Att leda uppåt och När din chef är problemet 174–176"] });
  assert.deepEqual(pairs("w6"), { chapters: ["Stress, press och den inre kompassen 148–157", "Den dag du gör allt fel 186–190"], optional: ["Epilog 191–193"] });
});

// Borttagna texter. Källa: nuvarande kurs (commit 0242434) och spec avsnitt 24.
const RETIRED = [
  ["gamla trygghetsfrågan", /Känner den här personen sig trygg\?/],
  ["gamla trygghetsledtexten", /inte något du kan veta säkert/],
  ["Mitt ledarskapslöfte", /ledarskapslöfte|Du lovade dig själv|lofte/i],
  ["gamla När jag inte klev fram", /När jag inte klev fram|inte klev fram\?/],
  ["gamla Teamet-triangeln", /Resultat\. Vad blir resultatet av det\?|"title":"Teamet"/],
  ["gamla Någon som är ny", /Någon som är ny eller kan växa/],
  ["gamla veckotitlar", /Relationer som håller|Jag, teamet och systemet|Min inre kompass|Mod och ansvar"/],
  ["gamla misstagsrubriken", /Den dag jag inte var den ledare jag vill vara/],
  ["gamla planfälten", /"prova"|"lagga_marke"|"forvantan"|"annorlunda"/],
  ["gamla varför du var här", /Varför du var här|varfor_har|skaver_mest/],
];
const KATALYSATOR = [/kataly/i, /Diagnos före lösning/i, /Struktur · Kultur · Mindset/i, /Kulturkartan/i, /Sägs · Görs · Tystas/i, /Följ konsekvensen/i, /GO eller NO GO/i, /Vad har vi själva skapat/i, /systemkonsekvens/i];

test("innehåll: gamla borttagna texter finns inte kvar synligt", () => {
  const program = JSON.stringify(publicProgram());
  for (const [what, re] of RETIRED) {
    assert.ok(!re.test(program), `${what} finns i registret`);
    assert.ok(!re.test(CLIENT), `${what} finns i klienten`);
  }
  // Närvaro i mötet: momentet är borttaget. Ordet lever bara kvar som kartans skala.
  const sections = STEPS.flatMap((s) => s.sections);
  assert.ok(!sections.some((s) => s.title === "Närvaro i mötet" || s.key === "narvaro"), "momentet Närvaro i mötet finns kvar");
  const withoutMap = JSON.stringify({ ...publicProgram(), mapDimensions: [] });
  assert.ok(!withoutMap.includes("Närvaro i mötet"), "Närvaro i mötet får bara finnas som skala i kartan");
  // Teamet: ingen triangel Relation · Ansvar · Resultat.
  const triangles = sections.filter((s) => s.kind === "triangle").map((s) => s.corners.map((c) => c.label).join(" · "));
  assert.ok(!triangles.includes("Relation · Ansvar · Resultat"));
  assert.deepEqual(triangles, [
    "Filter · Människa · Närvaro",
    "Rädsla · Mod · Ansvar",
    "Se · Höra · Känna",
    "Trygghet · Relation · Utveckling",
    "Konflikt · Lösning · Ansvar",
    "Individ · Team · Organisation",
    "Tryck · Val · Riktning",
    "Se · Lära · Vända",
  ]);
});

test("innehåll: inget Katalysatorspråk i registret, klienten eller förhandsvisningen", () => {
  const sources = [
    ["registret", JSON.stringify(STEPS)],
    ["programmet", JSON.stringify(publicProgram({ internal: true }))],
    ["klienten", CLIENT],
    ["förhandsvisningen", readFileSync(new URL("../preview/transport.js", import.meta.url), "utf8")],
  ];
  for (const [where, text] of sources) for (const re of KATALYSATOR) assert.ok(!re.test(text), `${where}: ${re}`);
});

test("innehåll: P4 i jag-form och ingen fråga om någon annans känslor", () => {
  const byggt = STEPS.find((s) => s.key === "w5").sections.find((s) => s.key === "niva").fields.find((f) => f.key === "byggt");
  assert.equal(byggt.label, "Vad har jag själv byggt runt problemet? Eller låtit bli att bygga?");
  assert.ok(!/\bvi\b/i.test(byggt.label));
  const labels = STEPS.flatMap((s) => s.sections.flatMap((x) => x.fields.map((f) => f.label || "")));
  assert.ok(!labels.some((l) => /Känner (den här personen|hen|han|hon)/.test(l)));
});
