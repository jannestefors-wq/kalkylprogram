// Innehållsregister för Ledarskap med hjärta och mod.
//
// Detta är den enda källan för vilka steg, moment och fält som finns.
// Servern validerar varje skrivning mot registret. Ett fält som inte står
// här kan inte sparas. Ett steg som inte är öppet kan inte skrivas till.
//
// Källor, se docs/LHM-SIX-WEEK-SOURCE-CROSSWALK-001.md:
//   Boken: Ledarskap med hjärta och mod (ISBN 978-91-8134-261-1).
//     Sidor anges som tryckta sidor. Tryckt sida = PDF-sida minus 7.
//   Arbetsboken: Min ledarskapsresa MASTER v2 (Word och PDF).
//     Trianglarnas hörnord finns i PDF-mastern.
//
// Citat ur boken anges med sida och kontrolleras mot bokens text med
// scripts/verify-book-references.mjs. Boktexten ligger aldrig i repot.
//
// Fältnycklar är stabila. Ändra aldrig en befintlig nyckel. Sparade svar
// ligger under "<moment>.<fält>".

export const PROGRAM_ID = "ledarskap-med-hjarta-och-mod";
export const PROGRAM_TITLE = "Ledarskap med hjärta och mod";
export const MAX_PARTICIPANTS_PER_COHORT = 6;
export const HOLD_FOR_JAN = "HOLD FÖR JAN";

export const MAP_DIMENSIONS = [
  { key: "narvaro", label: "Närvaro i mötet", low: "Splittrad", high: "Fullt närvarande" },
  { key: "mod", label: "Mod", low: "Undviker", high: "Kliver fram" },
  { key: "lyssnande", label: "Lyssnande", low: "Svarar", high: "Utforskar" },
  { key: "tydlighet", label: "Tydlighet", low: "Otydlig", high: "Tydlig" },
  { key: "relation", label: "Relation", low: "Distans", high: "Nära" },
  { key: "ansvar", label: "Ansvar", low: "Skjuter", high: "Agerar" },
];
export const MAP_SCALE_STEPS = 6;
export const MEASURE_POINTS = ["start", "end", "d30"];
export const MEASURE_POINT_LABELS = { start: "När du började", end: "Efter sex veckor", d30: "30 dagar senare" };

// De fem principerna. Boken s. 14–15, ordagrant.
export const FIVE_PRINCIPLES = [
  "Autenticitet före image",
  "Mod före bekvämlighet",
  "Relation före position",
  "Närvaro före produktivitet",
  "Långsiktighet före snabba poäng",
];

// Stöd under träffen. Arbetsboken: Medtränarens fem regler och Vårt gemensamma rum.
export const LIVE_SUPPORT = {
  coachRules: [
    ["Lyssna längre än du vill.", "Låt personen tala färdigt innan du börjar bygga din egen lösning."],
    ["Skilj observation från antagande.", "Säg hellre ”jag hörde...” än ”du är...”."],
    ["Ställ en fråga i taget.", "Den bästa frågan behöver ofta tystnad efter sig."],
    ["Diagnostisera inte.", "Vi tränar ledarskap och lyssnande. Vi sätter inte etiketter på människor."],
    ["Lämna tillbaka ansvaret.", "Hjälp personen att tänka. Ta inte över situationen."],
  ],
  coachQuestions: [
    "Vad hör jag? Ord, mönster eller motsägelser.",
    "Vad saknar jag innan jag bildar mig en uppfattning?",
    "Vilken enda fråga kan öppna situationen utan att styra svaret?",
  ],
  roomRules: [
    "Det som delas stannar i gruppen.",
    "Skydda tredje person. Använd initial eller alias.",
    "Fråga före råd.",
    "Observera före tolkning.",
    "Beslutet och handlingen är din egen.",
  ],
};

const t = (key, label, extra = {}) => ({ key, label, kind: "text", ...extra });
const short = (key, label, extra = {}) => ({ key, label, kind: "short", ...extra });
const choice = (key, label, options, extra = {}) => ({ key, label, kind: "choice", options, ...extra });

// ---------- Byggstenar som återkommer varje vecka ----------

function reading(chapters, { optional = [], note = "" } = {}) {
  return {
    key: "lasning",
    kind: "reading",
    title: "Inför den här veckan",
    reading: { chapters, optional, note },
    fields: [],
  };
}

function stanna(questions, lead) {
  return {
    key: "stanna",
    kind: "reflection",
    title: "Stanna upp",
    lead: lead || ["Svara inte snabbt. Det du först skriver är ofta det du redan vet. Stanna lite längre."],
    note: "Svara på de frågor som biter. Du behöver inte svara på alla.",
    doneWhen: { atLeast: 1 },
    source: "Arbetsboken, Läs och landa",
    fields: questions.map(([key, label]) => t(key, label)),
  };
}

function bridge(fromStep) {
  return { key: "forra-veckan", kind: "bridge", title: "Förra veckan", fromStep, fields: [] };
}

function action(lead, { hint = "", refs, withExpectation = true } = {}) {
  return {
    key: "handling",
    kind: "action",
    title: "Det här ska jag prova",
    lead,
    note: "Det finns inget facit. Det är du som väljer.",
    hint,
    refs,
    shareable: true,
    lockedWhen: "returnStarted",
    doneWhen: { all: ["prova", "situation", "nar"] },
    fields: [
      t("prova", "Den här veckan ska jag prova", { rows: 3 }),
      t("situation", "I vilken situation?", { rows: 2 }),
      t("annorlunda", "Vad vill jag själv göra annorlunda?", { rows: 2 }),
      t("lagga_marke", "Vad vill jag försöka lägga märke till?", { rows: 2 }),
      ...(withExpectation ? [t("forvantan", "Vad tror jag kommer att hända?", { rows: 2, hint: "Skriv din förväntan innan du agerar." })] : []),
      { key: "nar", label: "När tänker jag göra det?", kind: "date" },
    ],
  };
}

function whatHappened(lead) {
  return {
    key: "vad-hande",
    kind: "return",
    title: "Vad hände?",
    lead: lead || ["Fyll i efter att du har provat. Här finns ofta mer lärande än i själva planen."],
    recallFrom: "handling",
    shareable: true,
    doneWhen: { all: ["gjorde_faktiskt", "hande", "larde"] },
    fields: [
      t("gjorde_faktiskt", "Vad gjorde du faktiskt?", { hint: "Inte vad du tänkte göra." }),
      t("hande", "Vad hände?", { hint: "Ord, reaktioner och beteenden du kunde observera." }),
      t("missbedomde", "Vad bedömde du fel?"),
      t("battre", "Vad blev bättre?"),
      t("svarare", "Vad blev svårare?"),
      t("larde", "Vad lärde du dig om ditt sätt att leda?"),
      t("nasta", "Vad gör du nu?", { hint: "Behåll, ändra eller släpp något." }),
    ],
  };
}

function privat(questions) {
  return {
    key: "privat",
    kind: "reflection",
    title: "Min privata reflektion",
    lead: ["Det här är ditt. Skriv det du behöver se själv, även om du inte vill säga det högt ännu."],
    note: "Det här kan inte delas. Det finns ingen delningsknapp här.",
    doneWhen: { atLeast: 1 },
    source: "Arbetsboken, Min privata reflektion",
    fields: questions.map(([key, label]) => t(key, label)),
  };
}

function live() {
  return {
    key: "traffen",
    kind: "live",
    title: "Träffen",
    lead: ["När någon annan står i centrum är du medtränare. Ditt lärande fortsätter."],
    note: "Skriv inte ner någon annans case här. Det som delas i gruppen stannar i gruppen.",
    doneWhen: { atLeast: 1 },
    source: "Arbetsboken, Jag är medtränare och Vårt gemensamma rum",
    fields: [t("vackte", "Efter träffen. Vad väckte dagens samtal i mitt eget ledarskap?", { rows: 4 })],
  };
}

// Triangel. Hörnen placeras i rubrikens läsordning: vänster, mitten, höger.
// För Se · Höra · Känna är det den fasta regeln: SE vänster, HÖRA mitten, KÄNNA höger.
function triangle({ key, title, corners, prompt, source, lead, pre = [], post = [], model, doneWhen, shareable, note, optional, refs }) {
  return {
    key,
    refs,
    kind: "triangle",
    title,
    model: model || "triangle",
    corners: corners.map(([k, label]) => ({ key: k, label })),
    prompt,
    source,
    lead,
    note,
    optional: Boolean(optional),
    shareable: Boolean(shareable),
    doneWhen: optional ? undefined : doneWhen || { all: corners.map(([k]) => k) },
    fields: [
      ...pre.map((f) => ({ ...f, place: "pre" })),
      ...corners.map(([k, label, question, hint]) => t(k, question || label, { corner: k, hint, rows: 3 })),
      ...post.map((f) => ({ ...f, place: "post" })),
    ],
  };
}

// ---------- Vecka 1 ----------

const WEEK_1_SECTIONS = [
  {
    key: "intro",
    kind: "intro",
    title: "Människan först",
    lead: [
      "Ledarskap börjar inte med modellen.",
      "Det börjar med vad du faktiskt gör när du möter andra människor.",
      "Den här veckan handlar om att börja se ditt eget ledarskap tydligare.",
      "Inte hur du vill beskriva dig själv.",
      "Utan vad som faktiskt händer i mötet med andra.",
    ],
    fields: [],
  },
  reading(
    [
      { title: "Utan filter", pages: "7–15", pdfPages: "14–22" },
      { title: "Människan först", pages: "17–27", pdfPages: "24–34" },
    ],
    { note: "Läs innan första träffen. Stanna där något skaver." },
  ),
  stanna([
    ["filter", "Vilket filter känner du igen mest hos dig själv: corporatespråk, prestige, rädsla eller fasad?"],
    ["pratar_for_lite", "Vem i din närhet pratar du mycket om arbete med, men för lite om hur personen faktiskt har det?"],
    ["lyssna_utan_losa", "Vad skulle förändras om du lyssnade utan att lösa under en hel vecka?"],
  ]),
  {
    key: "karta",
    kind: "map",
    title: "Var är jag nu?",
    lead: [
      "Markera var du upplever att du befinner dig idag.",
      "Det här är ingen bedömning. Det är en startpunkt.",
    ],
    note: "Självskattning. Ditt eget perspektiv just nu. Inget test och ingen poäng.",
    measurePoint: "start",
    doneWhen: { allDimensions: true },
    fields: [
      t("varfor_har", "Varför är jag här?", { rows: 2, place: "after", hint: "Vad vill du få ut av de kommande sex veckorna?" }),
      t("skaver_mest", "Vad skaver mest i mitt ledarskap just nu?", { rows: 2, place: "after", hint: "Vilken situation, relation eller del av ditt ledarskap tar mest energi?" }),
    ],
  },
  {
    key: "forandring",
    kind: "goals",
    doneWhen: { all: ["mal_1", "mal_2", "mal_3"] },
    title: "Tre saker jag vill förändra",
    lead: ["Om sex veckor. Vad skulle du vilja att människorna runt dig märkte var annorlunda?"],
    fields: [1, 2, 3].flatMap((n) => [
      t(`mal_${n}`, `${n}. Jag vill förändra`, { rows: 2, group: n }),
      t(`mal_${n}_marks`, "Hur märker jag att något faktiskt har förändrats?", { rows: 2, group: n, secondary: true }),
    ]),
  },
  {
    key: "manniskor",
    kind: "people",
    doneWhen: { atLeast: 1 },
    title: "Människorna runt mig",
    lead: [
      "Vilka påverkas faktiskt av ditt ledarskap just nu?",
      "Välj upp till sex. Skriv bara det du behöver för att kunna följa din utveckling.",
    ],
    note: "Skriv roll eller initial i stället för namn. \"En projektledare i mitt team\" räcker ofta.",
    fields: [1, 2, 3, 4, 5, 6].flatMap((n) => [
      short(`person_${n}`, "Vem", { group: n, placeholder: "Roll eller initial" }),
      t(`person_${n}_note`, "Relation, ansvar, det jag behöver förstå bättre", { rows: 2, group: n }),
    ]),
  },
  {
    key: "situation",
    kind: "situation",
    doneWhen: { all: ["vad_hande", "sag_horde", "tolkning", "gjorde"] },
    title: "En situation från min verklighet",
    lead: ["Välj något som faktiskt har hänt. Börja med det som hände. Vänta med tolkningen."],
    shareable: true,
    groups: [
      { key: "observation", title: "Det som hände", hint: "Det en kamera hade kunnat fånga.", tone: "observe" },
      { key: "tolkning", title: "Min tolkning", hint: "Här får du gissa. Det är din bild, inte fakta.", tone: "interpret" },
      { key: "agerande", title: "Mitt agerande", hint: "" },
      { key: "efterat", title: "Efteråt", hint: "" },
    ],
    fields: [
      t("vad_hande", "Vad hände?", { group: "observation", rows: 4 }),
      t("sag_horde", "Vad såg eller hörde du faktiskt?", { group: "observation", rows: 3 }),
      t("tolkning", "Vad är din egen tolkning?", { group: "tolkning", rows: 3 }),
      t("gjorde", "Vad gjorde du?", { group: "agerande", rows: 3 }),
      t("gjorde_inte", "Vad gjorde du inte?", { group: "agerande", rows: 3 }),
      t("hande_sedan", "Vad hände sedan?", { group: "efterat", rows: 3 }),
      t("vet_inte", "Vad vet du fortfarande inte?", { group: "efterat", rows: 3 }),
    ],
  },
  {
    key: "narvaro",
    kind: "reflection",
    doneWhen: { atLeast: 2 },
    title: "Närvaro i mötet",
    lead: [
      "Närvaro betyder här att mentalt vara kvar med människan och situationen.",
      "Inte bara befinna sig i rummet.",
      "Tänk på situationen du just beskrev. Svara på de frågor som biter.",
    ],
    fields: [
      t("eget_svar", "När började jag tänka på mitt eget svar?"),
      t("slutade_lyssna", "När slutade jag egentligen lyssna?"),
      t("losa_for_tidigt", "Försökte jag lösa något innan jag förstått?"),
      t("missade", "Vad missade jag?"),
      t("splittrad", "Vad hände med samtalet när jag blev splittrad?"),
      t("stanna_kvar", "Vad skulle kunna hända om jag stannade kvar lite längre?"),
    ],
  },
  triangle({
    key: "triangel",
    title: "Veckans triangel",
    corners: [
      ["filter", "Filter", "Filter. Vad lägger sig mellan dig och den andra?", "Språket, prestigen, rädslan eller fasaden."],
      ["manniska", "Människa", "Människa. Vem står framför dig, bortom rollen?"],
      ["narvaro_t", "Närvaro", "Närvaro. Var är du själv när ni pratar?"],
    ],
    prompt: "Se vad som står mellan dig och ett ärligare möte.",
    source: "Arbetsboken, vecka 1",
    lead: ["Tänk på ett möte den här veckan. Skriv vid varje hörn."],
    post: [t("ser_nu", "Vad ser du nu, när du ser de tre tillsammans?", { rows: 2 })],
  }),
  action(["Välj en verklig situation den här veckan. Litet nog för att bli gjort. Tydligt nog för att gå att följa upp."], {
    hint: "Ett förslag: välj en person. Sitt ner. Fråga hur de mår. Lyssna utan att lösa.",
    refs: [27],
    withExpectation: false,
  }),
  {
    key: "vad-hande",
    kind: "return",
    doneWhen: { all: ["gjorde_faktiskt", "hande", "upptackte"] },
    title: "Vad hände?",
    lead: ["Fyll i efter att du har provat. Här finns ofta mer lärande än i själva planen."],
    recallFrom: "handling",
    shareable: true,
    fields: [
      t("gjorde_faktiskt", "Vad gjorde du faktiskt?"),
      t("hande", "Vad hände?"),
      t("annorlunda_an_tankt", "Vad blev annorlunda än du hade tänkt?"),
      t("upptackte", "Vad upptäckte du om ditt eget sätt att leda?"),
      t("fortsatta", "Vad vill du fortsätta göra?"),
      t("prova_annorlunda", "Vad behöver du prova annorlunda nästa gång?"),
    ],
  },
  privat([
    ["vet_redan", "Vad vet jag egentligen redan?"],
    ["hjalp_samtal", "Vad behöver jag hjälp med i ett enskilt samtal?"],
  ]),
  live(),
];

// ---------- Vecka 2 ----------

const WEEK_2_SECTIONS = [
  bridge("w1"),
  {
    key: "intro",
    kind: "intro",
    title: "Mod och ansvar",
    lead: [
      "Den här veckan handlar inte om hur andra borde kliva fram.",
      "Den handlar om dig.",
      "Vad du gör. Vad du undviker. Vad du behöver kliva fram i.",
    ],
    quote: { text: "Modet ligger i att vara rädd och ändå kliva fram.", page: 38 },
    fields: [],
  },
  reading(
    [
      { title: "Modet att kliva fram", pages: "28–39", pdfPages: "35–46" },
      { title: "Vad som formar en ledare", pages: "40–44", pdfPages: "47–51" },
    ],
    { optional: [{ title: "När det kostar att göra rätt", pages: "131–137", pdfPages: "138–144" }] },
  ),
  stanna([
    ["skjutit_upp", "Vilket samtal har du skjutit upp?"],
    ["kostar_vanta", "Vad kostar det att fortsätta vänta?"],
    ["soker_dig_till", "Vem söker du dig till när det verkligen skaver?"],
    ["obekvam_sanning", "Vilken obekväm sanning behöver sägas?"],
  ]),
  {
    key: "situation",
    kind: "situation",
    doneWhen: { all: ["vad_hande", "sag_horde", "radd", "kostade"] },
    title: "När jag inte klev fram",
    lead: ["Tänk på en situation nyligen där du valde att inte kliva fram. Börja med det som hände."],
    source: "Bokens reflektionsfråga, s. 39",
    shareable: true,
    groups: [
      { key: "observation", title: "Det som hände", hint: "Det en kamera hade kunnat fånga.", tone: "observe" },
      { key: "tolkning", title: "Det jag sa till mig själv", hint: "Tankarna och rädslan. Din bild, inte fakta.", tone: "interpret" },
      { key: "agerande", title: "Mitt agerande", hint: "" },
      { key: "priset", title: "Priset", hint: "" },
    ],
    fields: [
      t("vad_hande", "Vad hände?", { group: "observation", rows: 3 }),
      t("sag_horde", "Vad såg eller hörde du?", { group: "observation", rows: 3 }),
      t("radd", "Vad var du rädd skulle hända?", { group: "tolkning", rows: 2 }),
      t("trodde_om_andra", "Vad trodde du om de andra?", { group: "tolkning", rows: 2 }),
      t("gjorde", "Vad gjorde du?", { group: "agerande", rows: 2 }),
      t("gjorde_inte", "Vad gjorde du inte?", { group: "agerande", rows: 2 }),
      t("kostade", "Vad kostade det att du inte klev fram?", { group: "priset", rows: 2 }),
      t("om_klivit", "Vad hade hänt om du hade gjort det?", { group: "priset", rows: 2 }),
    ],
  },
  triangle({
    key: "triangel",
    title: "Veckans triangel",
    corners: [
      ["radsla", "Rädsla", "Rädsla. Vad är du rädd för här?"],
      ["mod_t", "Mod", "Mod. Vad vore det modiga steget?"],
      ["ansvar_t", "Ansvar", "Ansvar. Vad är ditt ansvar, och vad är inte ditt?"],
    ],
    prompt: "Se skillnaden mellan obehag och verklig risk.",
    source: "Arbetsboken, vecka 2",
    lead: ["Utgå från situationen du just beskrev, eller från samtalet du har skjutit upp."],
    post: [t("obehag_risk", "Vad är obehag, och vad är verklig risk?", { rows: 2 })],
  }),
  action(["Välj något du faktiskt ska göra före nästa träff. Ett samtal, ett beslut, en fråga eller en förändring."], {
    hint: "Ett förslag: boka samtalet du har skjutit upp. Förbered dig med nyfikenhet, inte med argument. Gå in med frågan ”Hur ser det ut från din sida?”",
    refs: [39],
  }),
  whatHappened(),
  privat([
    ["undviker", "Vad undviker jag just nu?"],
    ["vet_redan", "Vad vet jag egentligen redan?"],
  ]),
  live(),
];

// ---------- Vecka 3 ----------

const WEEK_3_SECTIONS = [
  bridge("w2"),
  {
    key: "intro",
    kind: "intro",
    title: "Se. Höra. Känna.",
    lead: [
      "Det du ser. Det du hör. Det du känner.",
      "Tre olika saker.",
      "Den här veckan tränar du på att hålla isär dem innan du agerar.",
      "Känna är din egen signal. Inte ett bevis på vad någon annan känner.",
    ],
    quote: { text: "Tre helt olika saker. Blanda dem, och du fattar fel beslut.", page: 66 },
    fields: [],
  },
  reading(
    [
      { title: "Triangelmetodiken", pages: "54–59", pdfPages: "61–66", note: "Fram till rubriken Katalytiskt ledarskap." },
      { title: "Se — Höra — Känna", pages: "66–74", pdfPages: "73–81" },
    ],
  ),
  stanna([
    ["for_snabbt", "Vilket problem försöker du lösa för snabbt?"],
    ["sett_hort", "Vad har du faktiskt sett och hört?"],
    ["kansla_tolkning", "Vilken del är din egen känsla eller tolkning?"],
  ]),
  triangle({
    key: "se-hora-kanna",
    model: "se-hora-kanna",
    title: "Se. Höra. Känna.",
    corners: [
      ["se", "Se", "Se. Vad har jag faktiskt observerat?", "Det konkreta. Beteenden, resultat. Inga tolkningar."],
      ["hora", "Höra", "Höra. Vad har jag hört?", "Orden, tonfallet, pauserna. Och det som inte sades."],
      ["kanna", "Känna", "Känna. Vad känner jag själv?", "Något förändrades. Vad behöver jag förstå mer om? En signal, inte ett bevis."],
    ],
    prompt: "Skriv bara sådant du faktiskt kan placera i respektive hörn.",
    source: "Boken s. 66–74 och bokens övning s. 74. Arbetsboken, vecka 3.",
    lead: ["Tänk på en person eller en situation som skaver just nu. Fyll i de tre innan du agerar."],
    shareable: true,
    pre: [t("vem", "Vilken situation gäller det?", { rows: 2, hint: "Roll eller initial räcker." })],
    post: [
      t("tolkning", "Vad är min tolkning?", { rows: 2, tone: "interpret" }),
      t("vet_inte", "Vad vet jag inte?", { rows: 2 }),
      t("fraga", "Vilken fråga kan jag ställa som öppnar utan att styra svaret?", { rows: 2 }),
    ],
    doneWhen: { all: ["se", "hora", "kanna", "fraga"] },
  }),
  action(["Prova i ett verkligt samtal. Börja med det du har sett. Vänta med det du tror."], {
    hint: "Beskriv situationen konkret. Utan värderingar. Utan tolkningar.",
    refs: [73],
  }),
  whatHappened(),
  privat([
    ["forsvarar", "Vad försvarar jag hos mig själv?"],
    ["vet_redan", "Vad vet jag egentligen redan?"],
  ]),
  live(),
];

// ---------- Vecka 4 ----------

const WEEK_4_SECTIONS = [
  bridge("w3"),
  {
    key: "halvvags",
    kind: "halfway",
    title: "Halvvägs",
    lead: ["Du är halvvägs. Läs dina tre saker utan att värdera dig själv. Titta efter rörelse."],
    source: "Arbetsboken, Tillbaka till starten",
    doneWhen: { atLeast: 1 },
    fields: [
      t("forandrats", "Vad har faktiskt förändrats?", { hint: "Något som syns i handling eller i hur andra reagerar." }),
      t("medveten", "Vad har jag bara blivit mer medveten om?", { hint: "Medvetenhet är början. Men den är inte samma sak som förändring." }),
      t("inte_gjort", "Vad har jag fortfarande inte gjort?", { hint: "Vad väntar du på?" }),
      t("fokus", "Vad vill jag fokusera på under andra halvan?", { hint: "Välj mindre. Gå djupare." }),
    ],
  },
  {
    key: "intro",
    kind: "intro",
    title: "Relationer som håller",
    lead: [
      "Trygghet först. Sedan relation. Sedan utveckling.",
      "Och det svåra samtalet blir inte lättare av att vänta.",
      "Den här veckan handlar om vad du själv gör i relationen.",
      "Inte vad den andra borde göra.",
    ],
    quote: { text: "Ingen utvecklas i otrygghet.", page: 75 },
    fields: [],
  },
  reading(
    [
      { title: "Trygghet — Relation — Utveckling", pages: "75–84", pdfPages: "82–91" },
      { title: "Konflikt — Lösning — Ansvar", pages: "85–93", pdfPages: "92–100" },
    ],
    { optional: [{ title: "Kommunikation — företagets livsnerv", pages: "114–116", pdfPages: "121–123", note: "Avsnitten om svåra samtal och att våga vara ärlig." }] },
  ),
  stanna([
    ["trygghet_team", "Var finns tryggheten i ditt team idag?"],
    ["relation_tid", "Vilken relation behöver mer tid innan du driver nästa förändring?"],
    ["for_tidigt", "Vem försöker du utveckla innan grunden är på plats?"],
    ["konflikt_irritation", "Vad är konflikt och vad är bara irritation?"],
  ]),
  triangle({
    key: "trygghet",
    title: "Trygghet. Relation. Utveckling.",
    corners: [
      ["trygghet_t", "Trygghet", "Trygghet. Vet personen var den står? Kan den säga ”jag vet inte”?"],
      ["relation_t", "Relation", "Relation. Finns det tillit där feedback kan landa?"],
      ["utveckling_t", "Utveckling", "Utveckling. Vad försöker du utveckla, och är grunden på plats?"],
    ],
    prompt: "Använd triangeln för en person eller ett helt team.",
    source: "Boken s. 75–84. Arbetsboken, vecka 4.",
    pre: [short("vem", "Vem eller vilka gäller det?", { placeholder: "Roll, initial eller teamet" })],
    post: [t("borja", "Var börjar du idag? Och var borde du börja?", { rows: 2 })],
  }),
  triangle({
    key: "samtalet",
    title: "Samtalet som behöver tas",
    corners: [
      ["konflikt", "Konflikt", "Konflikt. Vad är konflikten?"],
      ["losning", "Lösning", "Lösning. Vilken lösning är möjlig?"],
      ["ansvar_k", "Ansvar", "Ansvar. Vem tar ansvar för vad?"],
    ],
    prompt: "Börja inte med att vinna. Börja med att tydliggöra vad som faktiskt behöver lösas.",
    source: "Bokens övning s. 93. Arbetsboken, vecka 5.",
    shareable: true,
    pre: [
      t("observerat", "Vad har du observerat?", { rows: 2, hint: "Börja med observation. Inte tolkning.", tone: "observe" }),
      t("tolkning", "Vad är din tolkning?", { rows: 2, tone: "interpret" }),
    ],
    post: [t("deras_sida", "Vad vet du inte om hur det ser ut från den andras sida?", { rows: 2 })],
  }),
  action(["Välj det samtal eller den handling som behöver hända i en relation."], {
    hint: "Ett förslag: boka samtalet inom fem dagar.",
    refs: [93],
  }),
  whatHappened(),
  privat([
    ["undviker", "Vad undviker jag just nu?"],
    ["hjalp_samtal", "Vad behöver jag hjälp med i ett enskilt samtal?"],
  ]),
  live(),
];

// ---------- Vecka 5 ----------

const WEEK_5_SECTIONS = [
  bridge("w4"),
  {
    key: "intro",
    kind: "intro",
    title: "Jag, teamet och systemet",
    lead: [
      "Allt är inte en fråga om en person.",
      "Den här veckan lyfter du blicken.",
      "Men du står kvar i ditt eget ansvar.",
    ],
    quote: { text: "Om du bara ser individen missar du teamet.", page: 101 },
    fields: [],
  },
  reading(
    [
      { title: "Individ — Team — Organisation", pages: "101–110", pdfPages: "108–117" },
      { title: "Att bygga team som håller", pages: "123–130", pdfPages: "130–137" },
    ],
    {
      optional: [
        { title: "Person — Process — Produkt", pages: "94–100", pdfPages: "101–107" },
        { title: "Att välkomna, rekrytera och introducera", pages: "138–146", pdfPages: "145–153" },
        { title: "Att utveckla andra ledare", pages: "158–166", pdfPages: "165–173" },
      ],
    },
  ),
  stanna([
    ["individfraga", "Vilket problem har ni gjort till en individfråga?"],
    ["grupp_team", "Har ni en grupp eller ett team?"],
    ["tolererar", "Vad tolererar ni idag som försvagar laget?"],
    ["potential", "Vem har potential att leda men har ännu inte fått chansen?"],
    ["slappa", "Vad behöver du släppa för att någon annan ska kunna växa?"],
  ]),
  triangle({
    key: "niva",
    title: "Var sitter det?",
    corners: [
      ["individ", "Individ", "Vad talar för att det sitter hos individen?"],
      ["team", "Team", "Vad talar för att det sitter i teamet?"],
      ["organisation", "Organisation", "Vad talar för att det sitter i organisationen?"],
    ],
    prompt: "Placera problemet där du tror att det sitter. Fråga sedan vad som talar för att det sitter på en annan nivå.",
    source: "Boken s. 101–110. Arbetsboken, vecka 6.",
    shareable: true,
    pre: [
      t("problem", "Vilket problem gäller det?", { rows: 2 }),
      t("sett_hort", "Vad har du faktiskt sett och hört?", { rows: 2, tone: "observe" }),
      choice("tror", "Var tror du att det sitter?", ["Individ", "Team", "Organisation"]),
    ],
    post: [t("eget_ansvar", "Vad är ditt eget ansvar här, oavsett nivå?", { rows: 2 })],
    doneWhen: { all: ["problem", "tror", "eget_ansvar"] },
  }),
  triangle({
    key: "teamet",
    title: "Teamet",
    corners: [
      ["relation_r", "Relation", "Relation. Hur är det mellan er?"],
      ["ansvar_r", "Ansvar", "Ansvar. Tar ni ansvar för varandra, eller bara för er egen del?"],
      ["resultat_r", "Resultat", "Resultat. Vad blir resultatet av det?"],
    ],
    prompt: "Se hur relation och ansvar tillsammans påverkar resultatet.",
    source: "Arbetsboken, vecka 7. Boken s. 123–130.",
    post: [t("saknas", "Grupp eller team? Vad saknas?", { rows: 2 })],
  }),
  triangle({
    key: "ny-eller-vaxa",
    title: "Någon som är ny eller kan växa",
    corners: [
      ["valkomna", "Välkomna", "Välkomna. Hur tas personen emot?"],
      ["fortroende", "Förtroende", "Förtroende. Vad behöver finnas för att personen ska våga?"],
      ["utveckla", "Utveckla", "Utveckla. Vilket ansvar kan du lämna över?"],
    ],
    prompt: "Titta på upplevelsen från den andra personens sida.",
    source: "Arbetsboken, vecka 8. Boken s. 138–146 och 158–166.",
    note: "Valfritt. För dig som har någon ny, eller någon som är redo för mer.",
    optional: true,
  }),
  action(["Välj något du gör själv. Även när problemet sitter i systemet."], {
    hint: "Ett förslag: fråga två kollegor, oberoende av varandra, var de tror att problemet sitter. Eller stå tyst i fikarummet i fem minuter och lyssna.",
    refs: [110, 122],
  }),
  whatHappened(),
  privat([
    ["forsvarar", "Vad försvarar jag hos mig själv?"],
    ["vet_redan", "Vad vet jag egentligen redan?"],
  ]),
  live(),
];

// ---------- Vecka 6 ----------

const WEEK_6_SECTIONS = [
  bridge("w5"),
  {
    key: "intro",
    kind: "intro",
    title: "Min inre kompass",
    lead: [
      "Sista veckan handlar om vad som håller när trycket ökar.",
      "Och om vad du tar med dig härifrån.",
      "Du kommer att möta dina egna ord från början.",
    ],
    quote: { text: "Alla blir stressade. Det är ingen svaghet. Det är biologi.", page: 148 },
    fields: [],
  },
  reading(
    [
      { title: "Stress, press och den inre kompassen", pages: "148–157", pdfPages: "155–164" },
      { title: "Den dag du gör allt fel", pages: "186–190", pdfPages: "193–197" },
    ],
    { optional: [{ title: "Epilog", pages: "191–193", pdfPages: "198–200" }] },
  ),
  stanna([
    ["stress_gor", "Vad gör stress med ditt sätt att leda?"],
    ["stannade", "När stannade du senast utan att försöka prestera bättre?"],
    ["inte_ledaren", "När var du senast inte den ledare du vill vara?"],
  ]),
  triangle({
    key: "trycket",
    title: "Trycket och valet",
    corners: [
      ["tryck", "Tryck", "Tryck. Vad pressar dig just nu?"],
      ["val", "Val", "Val. Vad väljer du när trycket kommer?"],
      ["riktning", "Riktning", "Riktning. Vart vill du egentligen?"],
    ],
    prompt: "Se vad som händer mellan trycket du känner och valet du faktiskt gör.",
    source: "Arbetsboken, vecka 9. Boken s. 148–157.",
    note: "”Om jag är i obalans, tillför jag inte mer obalans.”",
    refs: [149],
    post: [t("mellanrum", "Vad händer i mellanrummet mellan trycket och valet?", { rows: 2 })],
  }),
  triangle({
    key: "misstaget",
    title: "Den dag jag inte var den ledare jag vill vara",
    corners: [
      ["se_m", "Se", "Se. Vad hände? Vad valde du?", "Beskriv det. Utan att försköna. Utan att döma."],
      ["lara", "Lära", "Lära. Vad hade du gjort om du inte var rädd?"],
      ["vanda", "Vända", "Vända. Vad gör du nu?"],
    ],
    prompt: "Misstaget är material. Riktningen avgör vad du gör med det.",
    source: "Arbetsboken, vecka 10. Bokens övning s. 187 och 203.",
    pre: [t("radd_for", "Vad var du rädd för?", { rows: 2 })],
  }),
  {
    key: "principer",
    kind: "reflection",
    title: "De fem principerna",
    lead: [
      "Autenticitet före image. Mod före bekvämlighet. Relation före position. Närvaro före produktivitet. Långsiktighet före snabba poäng.",
      "Vilken av dem har du tappat? Börja där. Inte med alla. Med en.",
    ],
    source: "Boken s. 14–15 och s. 188.",
    doneWhen: { all: ["vald"] },
    fields: [choice("vald", "Den som skaver mest", FIVE_PRINCIPLES), t("marks", "Hur märks det i din vardag?", { rows: 2 })],
  },
  {
    key: "tillbaka",
    kind: "lookback",
    title: "Tillbaka till början",
    lead: ["Läs dina första ord innan du skriver här. Försök inte låta klok. Beskriv vad som faktiskt har förändrats."],
    source: "Arbetsboken, Tillbaka till början",
    doneWhen: { all: ["idag"] },
    fields: [
      t("nar_jag_borjade", "När jag började. Vad gjorde du, undvek du eller fastnade du i?"),
      t("idag", "Idag. Vad gör du annorlunda i verkliga situationer?"),
      t("manniskorna", "Människorna omkring mig. Vad tror du att de har märkt? Vad har någon faktiskt sagt?"),
      t("fortfarande", "Jag behöver fortfarande träna på"),
    ],
  },
  {
    key: "karta",
    kind: "map",
    title: "Min ledarskapskarta. Nu",
    lead: ["Markera var du upplever att du befinner dig idag. Sedan ser du den bredvid din första karta."],
    note: "Din egen bild av din förflyttning. Självskattning. Inte ett resultat, inte en poäng.",
    measurePoint: "end",
    compareWith: ["start"],
    doneWhen: { allDimensions: true },
    fields: [],
  },
  action(["Veckans handling är den första i det som kommer efter utbildningen."], {
    hint: "Välj något du vill kunna säga att du fortfarande gör om 30 dagar.",
  }),
  whatHappened(),
  {
    key: "avslut",
    kind: "closing",
    title: "Det här gör jag annorlunda nu",
    lead: ["Inte vad du tyckte om kursen. Vad du gör."],
    source: "Order 003. Arbetsboken: Min riktning för 90 dagar och Mitt ledarskapslöfte. Boken s. 174.",
    shareable: true,
    doneWhen: { all: ["annorlunda_nu", "marka_framover", "fortsatta_1"] },
    fields: [
      t("annorlunda_nu", "Vad gör du annorlunda nu?", { rows: 3 }),
      t("marka_framover", "Vad vill du att människorna runt dig ska märka framöver?", { rows: 3 }),
      ...[1, 2, 3].flatMap((n) => [
        t(`fortsatta_${n}`, `${n}. Det här ska jag fortsätta träna på`, { rows: 2, group: n }),
        t(`folja_upp_${n}`, "Så följer jag upp att det händer", { rows: 2, group: n, secondary: true }),
      ]),
      t("lofte", "Jag lovar mig själv att", { rows: 3, hint: "Vilken ledare vill du vara om fem år? Inte vilken titel. Vilken människa.", refs: [174] }),
    ],
  },
  privat([
    ["vet_redan", "Vad vet jag egentligen redan?"],
    ["hjalp_samtal", "Vad behöver jag hjälp med i ett enskilt samtal?"],
  ]),
  live(),
];

// ---------- 30 dagar ----------

const DAY_30_SECTIONS = [
  {
    key: "intro",
    kind: "intro",
    title: "Vad blev faktiskt kvar?",
    lead: ["Trettio dagar har gått.", "Här är det du skrev.", "Svara kort. Svara ärligt."],
    fields: [],
  },
  {
    key: "minns",
    kind: "lookback",
    title: "Det här skrev du",
    lead: ["Dina tre saker, din början, ditt slut och din riktning."],
    fields: [],
  },
  {
    key: "karta",
    kind: "map",
    title: "Kartan en gång till",
    lead: ["Frivilligt. Markera var du upplever att du är idag."],
    note: "Självskattning. Din egen bild. Inte en poäng.",
    measurePoint: "d30",
    compareWith: ["start", "end"],
    fields: [],
  },
  {
    key: "kvar",
    kind: "reflection",
    title: "Vad blev kvar?",
    lead: ["Håll det kort. Det som räknas är det som faktiskt händer."],
    shareable: true,
    doneWhen: { all: ["fortfarande", "nasta_steg"] },
    fields: [
      t("fortfarande", "Vad gör du fortfarande?"),
      t("foll_bort", "Vad föll bort?"),
      t("svarare", "Vad blev svårare än du trodde?"),
      t("reagerat", "Vad har människorna runt dig reagerat på?"),
      t("borja_igen", "Vad behöver du börja med igen?"),
      t("nasta_steg", "Vad är ditt nästa konkreta steg?"),
    ],
  },
];

// ---------- Samtal med Jan ----------

const TALK_SECTIONS = [
  {
    key: "infor",
    kind: "reflection",
    title: "Inför samtalet",
    lead: ["Du behöver inte ta med ett färdigt svar. Ta med det du faktiskt funderar på."],
    source: "Arbetsboken, Enskilt samtal",
    shareable: true,
    doneWhen: { atLeast: 1 },
    fields: [
      t("forsta", "Vad vill jag att Jan ska förstå om min situation?"),
      t("tanka_kring", "Vad vill jag få hjälp att tänka kring?"),
      t("inte_gruppen", "Vad vill jag inte ta i gruppen just nu?"),
      t("forsta_steg", "Vilket första steg vill jag lämna samtalet med?"),
    ],
  },
  {
    key: "efter",
    kind: "reflection",
    title: "Efter samtalet",
    lead: ["Skriv medan det är färskt."],
    source: "Arbetsboken, Enskilt samtal",
    doneWhen: { atLeast: 1 },
    fields: [
      t("sag", "Vad såg jag som jag inte såg innan?"),
      t("tydligare", "Vad blev tydligare?"),
      t("gora_nu", "Vad ska jag göra nu?"),
      t("folja_upp", "Vad vill jag att Jan följer upp med mig senare?"),
    ],
  },
];

// ---------- Programmet ----------

export const STEPS = [
  { key: "w1", slug: "vecka-1", order: 1, label: "Vecka 1", title: "Människan först", subtitle: "Mitt eget ledarskap och min närvaro", built: true, sections: WEEK_1_SECTIONS },
  { key: "w2", slug: "vecka-2", order: 2, label: "Vecka 2", title: "Mod och ansvar", subtitle: "Det jag gör. Det jag undviker. Det jag behöver kliva fram i.", built: true, sections: WEEK_2_SECTIONS },
  // Se · Höra · Känna. Fast regel: SE vänster, HÖRA mitten, KÄNNA höger.
  // KÄNNA är en signal att undersöka, aldrig ett påstående om vad någon annan känner.
  { key: "w3", slug: "vecka-3", order: 3, label: "Vecka 3", title: "Se. Höra. Känna.", subtitle: "Att förstå mer innan jag agerar", built: true, sections: WEEK_3_SECTIONS },
  { key: "w4", slug: "vecka-4", order: 4, label: "Vecka 4", title: "Relationer som håller", subtitle: "Trygghet, konflikt och svåra samtal", built: true, sections: WEEK_4_SECTIONS },
  { key: "w5", slug: "vecka-5", order: 5, label: "Vecka 5", title: "Jag, teamet och systemet", subtitle: "När ledarskap inte bara handlar om personen", built: true, sections: WEEK_5_SECTIONS },
  { key: "w6", slug: "vecka-6", order: 6, label: "Vecka 6", title: "Min inre kompass", subtitle: "Stress, riktning och vad jag faktiskt ska fortsätta göra", built: true, sections: WEEK_6_SECTIONS },
  { key: "d30", slug: "30-dagar", order: 7, label: "30 dagar", title: "Vad blev faktiskt kvar?", subtitle: "Uppföljning efter utbildningen", built: true, sections: DAY_30_SECTIONS },
  { key: "samtal", slug: "samtal", order: 0, aside: true, alwaysOpen: true, label: "Samtal med Jan", title: "Samtal med Jan", subtitle: "Inför och efter ett enskilt samtal", built: true, sections: TALK_SECTIONS },
];

// Diplom. Inga kriterier är beslutade för den här produkten.
export const DIPLOMA = { status: HOLD_FOR_JAN, note: "Kriterier för digitalt diplom fastställs av Jan. Inget diplom ges automatiskt." };

export function getStep(stepKey) {
  return STEPS.find((s) => s.key === stepKey) || null;
}

export function getSection(stepKey, sectionKey) {
  const step = getStep(stepKey);
  return step?.sections?.find((s) => s.key === sectionKey) || null;
}

// Fältnyckel i databasen: "<moment>.<fält>". Stabil över språk och versioner.
export function findField(stepKey, fieldPath) {
  const [sectionKey, fieldKey] = String(fieldPath).split(".");
  const section = getSection(stepKey, sectionKey);
  if (!section) return null;
  const field = section.fields.find((f) => f.key === fieldKey);
  return field ? { section, field } : null;
}

function participantSection({ source, refs, quote, reading, fields, ...rest }) {
  return {
    ...rest,
    ...(quote ? { quote: { text: quote.text } } : {}),
    ...(reading
      ? {
          reading: {
            note: reading.note,
            chapters: reading.chapters.map(({ title, pages, note }) => ({ title, pages, note })),
            optional: reading.optional.map(({ title, pages, note }) => ({ title, pages, note })),
          },
        }
      : {}),
    fields: fields.map(({ refs: _refs, ...f }) => f),
  };
}

// eslint-disable-next-line no-unused-vars
export function publicProgram({ internal = false } = {}) {
  return {
    id: PROGRAM_ID,
    title: PROGRAM_TITLE,
    mapDimensions: MAP_DIMENSIONS,
    mapScaleSteps: MAP_SCALE_STEPS,
    measurePointLabels: MEASURE_POINT_LABELS,
    liveSupport: LIVE_SUPPORT,
    // Intern spårbarhet (källor, sidor, diplomstatus) stannar på servern.
    // Deltagarens sida får bara det som ska synas eller behövs för att fungera.
    diploma: null,
    steps: STEPS.map((s) => ({ ...s, sections: s.built ? s.sections.map(participantSection) : [] })),
  };
}
