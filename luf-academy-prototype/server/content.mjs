// Innehållsregister för Ledarskap med hjärta och mod. Version 2.
//
// Enda innehållskällan för deltagarens resa. All deltagartext följer
// LMHM VERSION 2 FINAL CONTENT SPEC ordagrant. Order 008 till 013 är historik.
//
// Servern validerar varje skrivning mot registret. Ett fält som inte står
// här kan inte sparas. Ett steg som inte är öppet kan inte skrivas till.
//
// Fältnycklar är stabila. En befintlig nyckel ändras aldrig. En ny eller
// ändrad fråga får en ny nyckel. Svar under pensionerade nycklar ligger kvar
// i databasen men visas inte. Se docs/LMHM-V2-FIELD-MAP.md.
//
// Källor, se docs/LHM-SIX-WEEK-SOURCE-CROSSWALK-001.md och
// docs/LMHM-V2-CONTENT-CROSSWALK.md:
//   Boken: Ledarskap med hjärta och mod (ISBN 978-91-8134-261-1).
//     Sidor anges som tryckta sidor. Tryckt sida = PDF-sida minus 7.
//   Arbetsboken: Min ledarskapsresa MASTER v2 (Word och PDF).
//
// Citat ur boken anges med sida och kontrolleras mot bokens text med
// scripts/verify-book-references.mjs. Boktexten ligger aldrig i repot.
//
// Villkorade fält: showWhen { field, in } visar fältet bara när ett annat
// fält i samma moment har något av värdena. Dolda fält räknas aldrig i
// klarstatus och sparas inte som krav. Se server/rules.mjs.

export const PROGRAM_ID = "ledarskap-med-hjarta-och-mod";
export const PROGRAM_TITLE = "Ledarskap med hjärta och mod";
export const CONTENT_VERSION = "2";
export const MAX_PARTICIPANTS_PER_COHORT = 6;
export const HOLD_FOR_JAN = "HOLD FÖR JAN";
// Intern märkning av hörnfrågor utan egen fråga i källan. Visas aldrig för deltagaren.
export const JAN_REVIEW = "DIGITALT FORMULERAD. JAN REVIEW.";
// Hörnfrågans ursprung. Internt. Källfrågor kontrolleras ordagrant mot boken.
const fromBook = (...refs) => ({ origin: "book", refs });
const digital = (support) => ({ origin: "digital", review: JAN_REVIEW, support });

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

// Spec avsnitt 4. Överst i resan och på sidan Inför startsamtalet.
export const PRIVACY_TEXT = [
  "Det här är din resa.",
  "Det du skriver här delas inte automatiskt med din arbetsgivare.",
  "Inte heller med Jan.",
  "Du väljer själv vad du delar, och du kan ta tillbaka det.",
  "Den som administrerar kursen ser vilka veckor du har börjat på. Aldrig det du skriver.",
];

// Spec avsnitt 16. Privat vägledning efter två Nej i rad. Visas bara för deltagaren.
export const SUPPORT_PROMPT = {
  lines: ["Två veckor i rad blev det inte som du hade tänkt.", "Vill du prata med Jan om vad som stoppar dig?", "Den här rutan ser bara du."],
  request: "Be om ett samtal",
  notNow: "Inte nu",
};

// Stöd under träffen. Spec avsnitt 6. Oförändrat från arbetsboken.
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
    "Observera före tolkning. Tystnad, blick, tempo och ordval kan ge oss frågor. De är aldrig facit på vad någon känner.",
    "Beslutet och handlingen är din egen.",
  ],
};

const t = (key, label, extra = {}) => ({ key, label, kind: "text", ...extra });
const short = (key, label, extra = {}) => ({ key, label, kind: "short", ...extra });
const choice = (key, label, options, extra = {}) => ({ key, label, kind: "choice", options, ...extra });
const multi = (key, label, options, extra = {}) => ({ key, label, kind: "multi", options, ...extra });
const check = (key, label, extra = {}) => ({ key, label, kind: "check", options: ["ja"], ...extra });
// Ett textblock utan svar. Sparas aldrig.
const info = (key, lines, extra = {}) => ({ key, label: "", kind: "info", lines, ...extra });
const when = (field, values) => ({ showWhen: { field, in: values } });

// Val av förändringsområde. Alternativen är deltagarens egna tre områden från
// vecka 1, med egna ord. Värdet som sparas är områdets nummer, aldrig texten.
export const AREA_NEW = "nytt";
const area = (key, label, extra = {}) => ({ key, label, kind: "area", options: ["1", "2", "3", AREA_NEW], newLabel: "Något nytt", ...extra });

const YES_PARTLY = ["Ja", "Delvis"];

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

// Spec 7.6.
function stanna(questions) {
  return {
    key: "stanna",
    kind: "reflection",
    title: "Stanna upp",
    lead: ["Svara inte snabbt. Det du först skriver är ofta det du redan vet. Stanna lite längre."],
    note: "Svara på de frågor som biter. Du behöver inte svara på alla.",
    doneWhen: { atLeast: 1 },
    source: "Arbetsboken, Läs och landa",
    fields: questions.map(([key, label]) => t(key, label)),
  };
}

// Spec 7.1.
function bridge(fromStep) {
  return { key: "forra-veckan", kind: "bridge", title: "Förra veckan", fromStep, fields: [] };
}

// Spec 7.2. Det här ska jag prova. Vecka 5 har egen variant.
const PLAN_FIELDS = [
  area("omrade", "Vilket av mina förändringsområden arbetar jag med nu?"),
  t("nytt", "Vad är det, och varför passar inte de tre?", { rows: 2, hint: "Du får byta. Ibland var första gissningen fel.", ...when("omrade", [AREA_NEW]) }),
  t("gora", "Vad ska jag göra, och i vilken situation?", { rows: 3 }),
  t("marks", "Hur skulle det märkas, och vem skulle kunna märka det?", { rows: 2, hint: "Något en annan människa skulle kunna se eller höra." }),
  { key: "nar", label: "När tänker jag göra det?", kind: "date" },
];

function action(lead, { hint, refs, fields = PLAN_FIELDS, doneWhen, returnAt } = {}) {
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
    returnAt,
    doneWhen: doneWhen || { all: ["omrade", "nytt", "gora", "marks", "nar"] },
    fields,
  };
}

// Spec 7.3. Vad hände? Nej är ett giltigt utfall.
function whatHappened() {
  return {
    key: "vad-hande",
    kind: "return",
    title: "Vad hände?",
    lead: ["Fyll i efter veckan. Oavsett hur det gick."],
    recallFrom: "handling",
    outcomeField: "blev",
    shareable: true,
    doneWhen: { all: ["blev", "gjorde_faktiskt", "hande", "markte", "bygger", "stoppade", "nasta"] },
    fields: [
      choice("blev", "Blev det av?", ["Ja", "Delvis", "Nej"]),
      t("gjorde_faktiskt", "Vad gjorde du faktiskt?", { hint: "Inte vad du tänkte göra.", ...when("blev", YES_PARTLY) }),
      t("hande", "Vad hände?", { hint: "Ord, reaktioner och beteenden du kunde se och höra. Blev något annorlunda än du trodde?", ...when("blev", YES_PARTLY) }),
      choice("markte", "Märkte någon något?", ["Ja", "Nej", "Jag vet inte"], when("blev", YES_PARTLY)),
      t("bygger", "Vad bygger du det på?", {
        hint: "Något någon sa. Något du såg. Något någon gjorde annorlunda. Skriv det du vet. Inte det du tror att någon kände.",
        ...when("markte", ["Ja"]),
      }),
      info("inte_blev", ["Det händer. Ofta finns mer att hämta här än i det som gick som planerat."], when("blev", ["Nej"])),
      t("stoppade", "Vad stoppade dig?", {
        hint: "Tid, rädsla, osäkerhet, att det inte kändes rätt. Skriv det som faktiskt stoppade dig. Inte det som låter bäst.",
        ...when("blev", ["Nej"]),
      }),
      t("kostar", "Vad kostar det att vänta?", { optional: true, ...when("blev", ["Nej"]) }),
      t("nasta", "Vad gör du nu?", {
        hint: "Behåll, ändra eller släpp något.",
        hintWhen: [{ field: "blev", in: ["Nej"], text: "Gör det nu. Gör något mindre. Eller välj något annat. Alla tre är ärliga svar." }],
      }),
    ],
  };
}

// Spec 7.4.
function privat(key, label) {
  return {
    key: "privat",
    kind: "reflection",
    title: "Min privata reflektion",
    lead: ["Det här är ditt. Skriv det du behöver se själv, även om du inte vill säga det högt ännu."],
    note: "Det här kan inte delas. Det finns ingen delningsknapp här.",
    doneWhen: { atLeast: 1 },
    source: "Arbetsboken, Min privata reflektion",
    fields: [t(key, label)],
  };
}

// Spec 7.5.
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

// Spec 15. Spegeln. Inga namn, ingen initial, inget referat.
function spegel(extraLine) {
  return {
    key: "spegel",
    kind: "mirror",
    title: "Spegeln",
    lead: [
      "Fråga någon som arbetar nära dig:",
      "\"Jag försöker förändra det här. Har du märkt någon skillnad?\"",
      "Säg att det är frivilligt att svara.",
      "Fråga gärna någon som inte automatiskt håller med dig.",
      "Lyssna klart. Försvara inget. Tacka.",
      ...(extraLine ? [extraLine] : []),
    ],
    shareable: true,
    doneWhen: { all: ["vem", "tog_med"] },
    source: "Order 010 och 011. Boken s. 81.",
    fields: [
      choice("vem", "Vem frågade du?", ["Medarbetare", "Kollega", "Egen chef", "Annan"]),
      t("tog_med", "Vad tog du med dig från samtalet?", { rows: 3, hint: "Det du tog med dig. Inte vad hen sa, ord för ord." }),
    ],
  };
}

// Triangel. Hörnen placeras i läsordning: vänster, mitten, höger.
// Hörn: [nyckel, ord, fråga, hjälptext, ursprung]. Ursprunget är internt.
// För Se · Höra · Känna är det den fasta regeln: SE vänster, HÖRA mitten, KÄNNA höger.
// displayOnly: triangeln visas med hörnorden men utan hörnfält.
function triangle({ key, title, corners, prompt, source, lead, figureLead, pre = [], post = [], model, doneWhen, shareable, note, refs, displayOnly }) {
  return {
    key,
    refs,
    kind: "triangle",
    title,
    model: model || "triangle",
    displayOnly: Boolean(displayOnly),
    corners: corners.map(([k, label]) => ({ key: displayOnly ? null : k, label })),
    prompt,
    source,
    lead,
    figureLead,
    note,
    shareable: Boolean(shareable),
    doneWhen: doneWhen || { all: corners.map(([k]) => k) },
    fields: [
      ...pre.map((f) => ({ ...f, place: "pre" })),
      ...(displayOnly ? [] : corners.map(([k, label, question, hint, meta = {}]) => t(k, question || label, { corner: k, hint, rows: 3, ...meta }))),
      ...post.map((f) => ({ ...f, place: "post" })),
    ],
  };
}

// ---------- Vecka 1. Jag som ledare ----------

const WEEK_1_SECTIONS = [
  {
    key: "intro",
    kind: "intro",
    title: "Människan först",
    lead: [
      "Ledarskap börjar inte med modellen.",
      "Det börjar med vad du faktiskt gör när du möter andra människor.",
      "Den här veckan väljer du vad som behöver förändras.",
      "Inte det som låter bra.",
      "Det som människorna runt dig skulle märka.",
    ],
    fields: [],
  },
  reading(
    [
      { title: "Utan filter", pages: "7–15", pdfPages: "14–22" },
      { title: "Människan först", pages: "17–27", pdfPages: "24–34" },
    ],
    { note: "Läs under första veckan. Du behöver inte vara klar innan första träffen. Stanna där något skaver." },
  ),
  stanna([
    ["filter", "Vilket filter känner du igen mest hos dig själv: corporatespråk, prestige, rädsla eller fasad?"],
    ["pratar_for_lite", "Vem i din närhet pratar du mycket om arbete med, men för lite om hur personen faktiskt har det?"],
  ]),
  {
    key: "karta",
    kind: "map",
    title: "Var är jag nu?",
    lead: ["Markera var du upplever att du befinner dig idag.", "Det här är ingen bedömning. Det är en startpunkt."],
    note: "Självskattning. Ditt eget perspektiv just nu. Inget test och ingen poäng.",
    measurePoint: "start",
    doneWhen: { allDimensions: true },
    fields: [],
  },
  {
    key: "forandring",
    kind: "goals",
    title: "Tre saker jag vill förändra",
    lead: ["Om sex veckor. Vad skulle du vilja att människorna runt dig märkte var annorlunda?"],
    noteLines: ["Skriv det du själv vill förändra. Inte det du borde.", "Välj något du kan påverka, och som någon skulle kunna märka.", "Du får ändra dem senare."],
    source: "Boken s. 198. Arbetsboken, Tre saker. Order 013 A1.",
    doneWhen: { all: ["mal_1", "mal_1_hur", "mal_2", "mal_2_hur", "mal_3", "mal_3_hur"] },
    fields: [1, 2, 3].flatMap((n) => [
      t(`mal_${n}`, `${n}. Jag vill förändra`, { rows: 2, group: n }),
      t(`mal_${n}_hur`, "Hur skulle det märkas, och vem skulle kunna märka det?", { rows: 2, group: n, secondary: true }),
    ]),
  },
  {
    key: "manniskor",
    kind: "people",
    title: "Människorna runt mig",
    lead: ["Vilka påverkas faktiskt av ditt ledarskap just nu?", "Välj två till fyra. Roll eller initial räcker."],
    note: "Skriv roll eller initial i stället för namn. \"En projektledare i mitt team\" räcker ofta.",
    doneWhen: { atLeast: 2 },
    fields: [1, 2, 3, 4].map((n) => t(`vem_${n}`, "Vem, och vad behöver jag förstå bättre om hen?", { rows: 2, group: n, nameCheck: true })),
  },
  {
    key: "situation",
    kind: "situation",
    title: "En situation från min verklighet",
    lead: ["Välj något som faktiskt har hänt med någon du leder. Börja med det som hände. Vänta med tolkningen."],
    shareable: true,
    doneWhen: { all: ["vad_hande", "tolkning", "gjorde_lat"] },
    groups: [
      { key: "observation", title: "Det som hände", hint: "Det en kamera hade kunnat fånga.", tone: "observe" },
      { key: "tolkning", title: "Min tolkning", hint: "Här får du gissa. Det är din bild, inte fakta.", tone: "interpret" },
      { key: "agerande", title: "Mitt agerande", hint: "" },
    ],
    fields: [
      t("vad_hande", "Vad hände?", { group: "observation", rows: 4 }),
      t("tolkning", "Vad är din egen tolkning?", { group: "tolkning", rows: 3 }),
      t("gjorde_lat", "Vad gjorde du, och vad lät du bli att göra?", { group: "agerande", rows: 3 }),
    ],
  },
  triangle({
    key: "triangel",
    title: "Veckans triangel",
    corners: [
      ["filter", "Filter", "Filter. Vad lägger sig mellan dig och den andra?", "Språket, prestigen, rädslan eller fasaden.", digital("Boken s. 7: det som står mellan dig och människorna du leder. De fyra filtren s. 8–11 och 198.")],
      ["manniska", "Människa", "Människa. Vem står framför dig, bortom rollen?", undefined, digital("Boken s. 20–27: ser du dina människor, inte om arbetet, om dem.")],
      ["narvaro_t", "Närvaro", "Närvaro. Var är du själv när ni pratar?", undefined, digital("Boken s. 15: din fulla uppmärksamhet. Jans definition av närvaro, order 001 §20.")],
    ],
    prompt: "Se vad som står mellan dig och ett ärligare möte.",
    source: "Arbetsboken, vecka 1",
    lead: ["Utgå från situationen du just beskrev. Skriv vid varje hörn."],
  }),
  action(["Välj en verklig situation den här veckan. Litet nog för att bli gjort. Tydligt nog för att gå att följa upp."], {
    hint: "Ett förslag: välj en person. Sitt ner. Fråga hur de mår. Lyssna utan att lösa.",
    refs: [27],
  }),
  whatHappened(),
  privat("vet_redan", "Vad vet jag egentligen redan?"),
  live(),
];

// ---------- Vecka 2. Mod, ansvar och beslut ----------

const W2_DECISION_KINDS = ["Ett beslut", "Ett nej", "Ett besked"];

const WEEK_2_SECTIONS = [
  bridge("w1"),
  {
    key: "intro",
    kind: "intro",
    title: "Mod, ansvar och beslut",
    lead: [
      "Den här veckan handlar inte om hur andra borde kliva fram.",
      "Den handlar om dig.",
      "Samtalet du skjuter upp. Beslutet du inte fattar. Nejet du inte säger.",
    ],
    quote: { text: "Modet ligger i att vara rädd och ändå kliva fram.", page: 38 },
    fields: [],
  },
  reading(
    [
      { title: "Modet att kliva fram", pages: "28–39", pdfPages: "35–46" },
      { title: "Vad som formar en ledare", pages: "40–44", pdfPages: "47–51" },
    ],
    {
      optional: [
        { title: "När det kostar att göra rätt", pages: "131–137", pdfPages: "138–144" },
        { title: "Att säga nej utan att skapa drama", pages: "106–107", pdfPages: "113–114", inChapter: "Individ — Team — Organisation" },
      ],
    },
  ),
  stanna([
    ["skjutit_upp_beslut", "Vilket samtal, beslut eller besked har du skjutit upp?"],
    ["kostar_vanta", "Vad kostar det att fortsätta vänta?"],
  ]),
  triangle({
    key: "triangel",
    title: "Det jag skjuter upp",
    lead: ["Välj något som ligger och väntar just nu."],
    figureLead: "Utgå från det du skjuter upp.",
    corners: [
      ["radsla", "Rädsla", "Rädsla. Vad är du rädd för här?", undefined, digital("Boken s. 9 och 36: rädslan, mod är inte avsaknad av rädsla.")],
      ["mod_t", "Mod", "Mod. Vad vore det modiga steget?", undefined, digital("Boken s. 31–36: beslutet att kliva fram.")],
      ["ansvar_leder", "Ansvar", "Ansvar. Vad är ditt ansvar här, eftersom du leder? Och vad är inte ditt?", undefined, digital("Order 009 och 010. Boken s. 31 och 92.")],
    ],
    prompt: "Se skillnaden mellan obehag och verklig risk.",
    source: "Arbetsboken, vecka 2. Boken s. 36, 131–132. Order 009 och 010.",
    shareable: true,
    pre: [
      choice("galler", "Vad gäller det?", ["Ett samtal", ...W2_DECISION_KINDS, "Något annat jag behöver kliva fram i"]),
      t("vad_det_ar", "Vad är det, och hur länge har det legat?", { rows: 2 }),
    ],
    post: [
      t("obehag_risk", "Vad är obehag, och vad är verklig risk?", { rows: 2 }),
      t("sta_kvar", "Hur står du kvar i det när någon ifrågasätter?", {
        rows: 2,
        optional: true,
        hint: "Du kan ändra dig när du får veta något nytt. Inte för att det blåser. Är beslutet fattat ovanför dig? Bär det ändå. Skyll inte på ledningen.",
        refs: [36, 131, 132],
        ...when("galler", W2_DECISION_KINDS),
      }),
    ],
    doneWhen: { all: ["galler", "vad_det_ar", "radsla", "mod_t", "ansvar_leder", "obehag_risk"] },
  }),
  action(["Välj något du faktiskt ska göra före nästa träff. Ett samtal, ett beslut, en fråga eller en förändring."], {
    hint: [
      "Ett förslag: boka samtalet du har skjutit upp. Förbered dig med nyfikenhet, inte med argument. Gå in med frågan ”Hur ser det ut från din sida?”",
      "Är det ett beslut, ett nej eller ett besked? Bestäm ett datum. Säg det till den det gäller. Säg varför.",
    ],
    refs: [39, 107, 199],
  }),
  whatHappened(),
  privat("undviker", "Vad undviker jag just nu?"),
  live(),
];

// ---------- Vecka 3. Se. Höra. Känna. ----------

const WEEK_3_SECTIONS = [
  bridge("w2"),
  {
    key: "intro",
    kind: "intro",
    title: "Se. Höra. Känna.",
    lead: [
      "Det du ser. Det du hör. Det du känner.",
      "Tre olika saker.",
      "När du leder blir din tolkning lätt en bedömning av en annan människa.",
      "Den här veckan håller du isär dem innan du säger något.",
      "Känna är din egen signal. Inte ett bevis på vad någon annan känner.",
    ],
    quote: { text: "Tre helt olika saker. Blanda dem, och du fattar fel beslut.", page: 66 },
    fields: [],
  },
  reading([
    { title: "Triangelmetodiken", pages: "54–59", pdfPages: "61–66", note: "Till och med avsnittet Triangulering — att mäta det omätbara." },
    { title: "Se — Höra — Känna", pages: "66–74", pdfPages: "73–81" },
    { title: "Konsten att ge och ta emot feedback", pages: "79–81", pdfPages: "86–88", inChapter: "Trygghet — Relation — Utveckling" },
  ]),
  stanna([
    ["for_snabbt", "Vilket problem försöker du lösa för snabbt?"],
    ["kansla_tolkning", "Vilken del är din egen känsla eller tolkning?"],
  ]),
  triangle({
    key: "se-hora-kanna",
    model: "se-hora-kanna",
    title: "Se. Höra. Känna.",
    corners: [
      ["se", "Se", "Se. Vad har du faktiskt observerat?", "Det konkreta. Beteenden, resultat. Inga tolkningar.", fromBook(61)],
      ["hora", "Höra", "Höra. Vad har du hört från personen själv?", "Orden, tonfallet, pauserna. Och det som inte sades.", fromBook(61)],
      ["kanna", "Känna", "Känna. Vad är din känsla, som du behöver vara medveten om men inte låta styra?", "Något förändrades. Vad behöver jag förstå mer om? En signal, inte ett bevis.", fromBook(61)],
    ],
    prompt: "Skriv bara sådant du faktiskt kan placera i respektive hörn.",
    source: "Boken s. 66–74. Hörnfrågorna: boken s. 61. Arbetsboken, vecka 3.",
    lead: ["Tänk på någon du leder, där något skaver just nu. Fyll i de tre innan du säger något."],
    shareable: true,
    pre: [t("vem", "Vilken situation gäller det?", { rows: 2, hint: "Roll eller initial räcker." })],
    post: [t("tolkning_vet_inte", "Vad är min tolkning, och vad vet jag inte?", { rows: 2, tone: "interpret" })],
    doneWhen: { all: ["se", "hora", "kanna", "tolkning_vet_inte"] },
  }),
  {
    key: "aterkoppling",
    kind: "reflection",
    title: "Min återkoppling",
    lead: ["Återkoppling som landar börjar i det du har sett.", "Inte i vem du tycker att personen är."],
    shareable: true,
    source: "Boken s. 72, 80–81. Order 009 och 010.",
    doneWhen: { all: ["sett_hort", "fraga"] },
    fields: [
      t("sett_hort", "Det jag har sett eller hört. Så konkret att en kamera kunde bekräfta det.", { rows: 3 }),
      t("fraga", "Vilken fråga kan jag ställa som öppnar utan att styra svaret?", { rows: 2, hint: "Till exempel: Hur upplevde du själv situationen?" }),
      t("signal", "Min egen signal, om jag vill säga den.", { rows: 2, optional: true, hint: "Säg vad du märker i dig själv. Aldrig vad den andra känner." }),
    ],
  },
  action(["Ge återkopplingen. Så nära det som hände som möjligt."], {
    hint: "Börja med det du har sett. Ställ din fråga. Lyssna klart.",
    refs: [80, 81],
  }),
  whatHappened(),
  privat("forsvarar", "Vad försvarar jag hos mig själv?"),
  live(),
];

// ---------- Vecka 4. Relation, trygghet och det svåra samtalet ----------

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
      t("inte_gjort", "Vad har jag fortfarande inte gjort?", { hint: "Vad krävs för att det ska bli av?" }),
    ],
  },
  spegel(),
  {
    key: "intro",
    kind: "intro",
    title: "Relation, trygghet och det svåra samtalet",
    lead: [
      "Trygghet först. Sedan relation. Sedan utveckling.",
      "Och det svåra samtalet blir inte lättare av att vänta.",
      "Den här veckan handlar om samtalet som är ditt att ta.",
      "Inte för att det är ditt fel.",
      "För att du har ansvaret.",
    ],
    quote: { text: "Ingen utvecklas i otrygghet.", page: 75 },
    fields: [],
  },
  reading(
    [
      { title: "Trygghet — Relation — Utveckling", pages: "75–84", pdfPages: "82–91" },
      { title: "Konflikt — Lösning — Ansvar", pages: "85–93", pdfPages: "92–100" },
    ],
    {
      optional: [
        { title: "Kommunikation — företagets livsnerv", pages: "114–116", pdfPages: "121–123", note: "Avsnitten ”Svåra samtal — så gör du” och ”Att våga vara ärlig”." },
        { title: "Varför vi alltid börjar i fel ände", pages: "98", pdfPages: "105", inChapter: "Person — Process — Produkt" },
        { title: "Avrekrytering med värdighet", pages: "145", pdfPages: "152", inChapter: "Att välkomna, rekrytera och introducera" },
      ],
    },
  ),
  stanna([["for_tidigt", "Vem försöker du utveckla innan grunden är på plats?"]]),
  triangle({
    key: "trygghet",
    title: "Trygghet. Relation. Utveckling.",
    corners: [
      ["trygghet_sett", "Trygghet", "Trygghet. Vad har du sett eller hört som tyder på att personen vågar säga vad den tänker, fråga, göra fel eller säga emot?", undefined, digital("Order 011 beslut 1. Ersätter bokens fråga s. 60, som ber deltagaren bedöma en annan människas inre tillstånd.")],
      ["relation_t", "Relation", "Relation. Finns det en relation där feedback kan landa?", undefined, fromBook(60)],
      ["utveckling_t", "Utveckling", "Utveckling. Är utvecklingsmålen realistiska?", undefined, fromBook(60)],
    ],
    prompt: "Använd triangeln för en person eller ett helt team.",
    source: "Boken s. 75–84. Hörnfrågorna Relation och Utveckling: boken s. 60. Trygghet: order 011.",
    pre: [short("vem", "Vem eller vilka gäller det?", { placeholder: "Roll, initial eller teamet" })],
  }),
  triangle({
    key: "samtalet",
    title: "Samtalet som är mitt att ta",
    corners: [
      ["konflikt", "Konflikt", "Konflikt. Vad är konflikten?", undefined, fromBook(93)],
      ["losning", "Lösning", "Lösning. Vilken lösning är möjlig?", undefined, fromBook(93)],
      ["ansvar_k", "Ansvar", "Ansvar. Vem tar ansvar för vad?", "Om du leder kommer ditt ansvar först. Inte för att det är ditt fel. För att du kan förändra.", fromBook(93)],
    ],
    prompt: "Börja inte med att vinna. Börja med att tydliggöra vad som faktiskt behöver lösas.",
    source: "Bokens övning s. 93. Boken s. 91–92 och 145. Order 009, 010 och 011.",
    shareable: true,
    pre: [
      choice("med_vem", "Vem är samtalet med?", ["Någon jag har ansvar för", "Två jag leder, som inte kommer överens", "En jämbördig kollega"]),
      info("jambordig", ["Då har du inget mandat. Då är frågan din del av det. Inte deras."], when("med_vem", ["En jämbördig kollega"])),
      t("observerat", "Vad har du observerat?", { rows: 2, hint: "Börja med observation. Inte tolkning.", tone: "observe" }),
    ],
    post: [
      check("pagatt", "Det här har pågått länge, och stöd har redan getts."),
      info("stod_racker", [
        "Ibland fungerar det inte. Trots stöd.",
        "Då måste du agera. Med värdighet, och i tid.",
        "Om det kan påverka anställningen, eller behöver hanteras formellt: ta stöd i organisationens rutiner och hos rätt kompetens innan du går vidare.",
      ], { title: "När stödet inte räcker", ...when("pagatt", ["ja"]) }),
      t("gjorts", "Vad har redan gjorts, och vad hände?", { rows: 2, ...when("pagatt", ["ja"]) }),
      t("sitter", "Sitter det hos personen, eller i det runt personen?", { rows: 2, hint: "Otydliga förväntningar. Brist på stöd. Fel plats. Är du säker? Hur vet du?", ...when("pagatt", ["ja"]) }),
    ],
    doneWhen: { all: ["med_vem", "observerat", "konflikt", "losning", "ansvar_k", "gjorts", "sitter"] },
  }),
  action(["Välj det samtal eller den handling som behöver hända i en relation."], {
    hint: "Boka samtalet inom fem dagar. Stäng dörren. Börja med det du har sett. Beskriv följden. Fråga, och lyssna på svaret. Kom överens om ett nästa steg och när ni följer upp.",
    refs: [91, 92, 93],
  }),
  whatHappened(),
  privat("hjalp_samtal", "Vad behöver jag hjälp med i ett enskilt samtal?"),
  live(),
];

// ---------- Vecka 5. Teamet och förutsättningarna ----------

const W5_PATHS = ["Skapar det som saknas", "Lämnar över ett resultat", "Lyfter det uppåt"];

const WEEK_5_SECTIONS = [
  bridge("w4"),
  {
    key: "intro",
    kind: "intro",
    title: "Teamet och förutsättningarna",
    lead: [
      "Allt är inte en fråga om en person.",
      "Ibland sitter det i det du har byggt runt dem.",
      "Eller i det du inte har byggt.",
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
        { title: "När chefen inte lyssnar", pages: "97", pdfPages: "104", inChapter: "Person — Process — Produkt" },
        { title: "Delegering som utvecklingsverktyg", pages: "164", pdfPages: "171", inChapter: "Att utveckla andra ledare" },
        { title: "Att leda uppåt och När din chef är problemet", pages: "174–176", pdfPages: "181–183", inChapter: "Ledarskapet framåt", headings: ["Att leda uppåt", "När din chef är problemet"] },
      ],
    },
  ),
  stanna([
    ["grupp_team_saknas", "Har ni en grupp eller ett riktigt team? Vad saknas?"],
    ["tolererar", "Vad tolererar ni idag som försvagar laget?"],
  ]),
  triangle({
    key: "niva",
    title: "Problemet jag har lagt hos en person",
    displayOnly: true,
    corners: [["individ", "Individ"], ["team", "Team"], ["organisation", "Organisation"]],
    prompt: "Placera problemet där du tror att det sitter. Fråga sedan vad som talar för att det sitter på en annan nivå.",
    source: "Boken s. 101–110, 128–129. Arbetsboken, vecka 6. Order 009, 010 och 013.",
    lead: ["Välj ett problem du har tänkt på som en persons problem. Något som faktiskt pågår."],
    shareable: true,
    pre: [
      t("problem_hos", "Vilket problem, och hos vem?", { rows: 2, hint: "Roll eller initial räcker." }),
      t("sett_hort", "Vad har du faktiskt sett och hört?", { rows: 2, tone: "observe" }),
    ],
    post: [
      choice("tror", "Var tror du att det sitter?", ["Individ", "Team", "Organisation"]),
      t("annan_niva", "Vad talar för att det sitter på en annan nivå?", { rows: 2, hint: "Är du säker? Hur vet du?" }),
      multi("fatt", "Vilka av de här har personen fått av mig?", [
        "Trygghet. Hen frågar, säger emot och berättar när något blivit fel.",
        "Tydlighet. Hen vet varför, vart och vad som förväntas.",
        "Roller. Hen vet vem som gör vad och vem som beslutar.",
        "Feedback. Hen får höra vad som fungerar och vad som inte gör det.",
        "Firande. Hen får höra när något blev bra.",
      ], { optional: true }),
      t("byggt", "Vad har jag själv byggt runt problemet? Eller låtit bli att bygga?", { rows: 2, hint: "Det här är ditt ansvar, oavsett var problemet sitter." }),
    ],
    doneWhen: { all: ["problem_hos", "sett_hort", "tror", "annan_niva", "byggt"] },
  }),
  action(["Välj något du gör själv. Även när problemet sitter i systemet."], {
    refs: [106, 161, 164, 174, 175],
    fields: [
      PLAN_FIELDS[0],
      PLAN_FIELDS[1],
      choice("vag", "Vad gör jag?", W5_PATHS),
      t("skapa", "Vad skapar jag, och hur vet personen att det finns nu?", { rows: 2, ...when("vag", [W5_PATHS[0]]) }),
      t("resultat", "Vilket resultat lämnar jag över? Inte uppgiften. Resultatet.", { rows: 2, ...when("vag", [W5_PATHS[1]]) }),
      t("ramar", "Vilka ramar gäller, och när följer vi upp?", { rows: 2, ...when("vag", [W5_PATHS[1]]) }),
      info("lamnar_over", ["Säg vad. Inte hur. Och ta inte tillbaka det när det görs annorlunda än du hade gjort."], when("vag", [W5_PATHS[1]])),
      t("chef_veta", "Vad behöver min chef veta som hen inte vet idag?", { rows: 2, ...when("vag", [W5_PATHS[2]]) }),
      t("hur_saga", "Hur säger jag det så att det går att ta emot?", { rows: 2, ...when("vag", [W5_PATHS[2]]) }),
      info("lyfter", ["Som ett bidrag. Inte som en attack."], when("vag", [W5_PATHS[2]])),
      PLAN_FIELDS[3],
      PLAN_FIELDS[4],
    ],
    doneWhen: { all: ["omrade", "nytt", "vag", "skapa", "resultat", "ramar", "chef_veta", "hur_saga", "marks", "nar"] },
  }),
  whatHappened(),
  privat("slappa", "Vad behöver jag släppa för att någon annan ska kunna växa?"),
  live(),
];

// ---------- Vecka 6. Ledarskap under press ----------

const WEEK_6_SECTIONS = [
  bridge("w5"),
  {
    key: "intro",
    kind: "intro",
    title: "Ledarskap under press",
    lead: [
      "Sista veckan handlar om vad som håller när trycket ökar.",
      "Du kommer att möta dina egna ord från början.",
      "Titta på vad som hände. Och på vad som inte hände.",
      "Det är inte perfektion som räknas. Det är riktningen.",
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
    ["tog_hand", "När tog du senast hand om dig själv på riktigt? Inte för att prestera bättre. Bara för att du behövde det."],
  ]),
  triangle({
    key: "trycket",
    title: "Trycket och valet",
    displayOnly: true,
    corners: [["tryck", "Tryck"], ["val", "Val"], ["riktning", "Riktning"]],
    prompt: "Se vad som händer mellan trycket du känner och valet du faktiskt gör.",
    source: "Arbetsboken, vecka 9. Boken s. 148–157. Order 011 beslut 3.",
    note: "”Om jag är i obalans, tillför jag inte mer obalans.”",
    refs: [149],
    post: [t("nar_trycket", "När trycket kommer: vad pressar dig, vad brukar du välja och vilken riktning vill du hålla?", { rows: 3, hint: "Och vad gör du då, som andra kan se?" })],
    doneWhen: { all: ["nar_trycket"] },
  }),
  {
    key: "tillbaka",
    kind: "lookback",
    title: "Hela resan",
    lead: ["Läs dina första ord innan du skriver här. Försök inte låta klok. Beskriv vad som faktiskt har förändrats."],
    source: "Arbetsboken, Tillbaka till början. Order 010.",
    shareable: true,
    doneWhen: { all: ["forandrats", "inte_forandrats"] },
    fields: [
      t("forandrats", "Vad har faktiskt förändrats?", { hint: "Något som syns i handling eller i hur andra reagerar." }),
      t("inte_forandrats", "Vad har inte förändrats?", { hint: "Skriv det utan att förklara bort det." }),
    ],
  },
  spegel("Fråga samma person som förra gången. Eller någon ny."),
  triangle({
    key: "misstaget",
    title: "Det jag föll tillbaka i",
    corners: [
      ["se_m", "Se", "Se. Vad var situationen? Vad valde du?", "Beskriv det. Utan att försköna. Utan att döma.", fromBook(187)],
      ["lara", "Lära", "Lära. Vad hade du gjort annorlunda om du inte var rädd?", undefined, fromBook(187)],
      ["vanda", "Vända", "Vända. Vad gör du nu?", undefined, digital("Boken s. 187: nästa gång välja lite modigare. Arbetsbokens instruktion v10: riktningen avgör vad du gör med det.")],
    ],
    prompt: "Misstaget är material. Riktningen avgör vad du gör med det.",
    source: "Arbetsboken, vecka 10. Bokens övning s. 187 och 203.",
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
    fields: [choice("vald", "Den som skaver mest", FIVE_PRINCIPLES)],
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
  {
    key: "avslut",
    kind: "closing",
    title: "Det som fortsätter",
    lead: ["Inte vad du tyckte om kursen. Vad du gör. Och vad som kommer att testa dig."],
    source: "Arbetsboken: Min riktning för 90 dagar. Order 010, 012 och 013 B5.",
    shareable: true,
    doneWhen: { all: ["fortsatta_1", "folja_upp_1", "testar", "gor_da"] },
    fields: [
      ...[1, 2].flatMap((n) => [
        t(`fortsatta_${n}`, `${n}. Det här ska jag fortsätta träna på`, { rows: 2, group: n, optional: n === 2 }),
        t(`folja_upp_${n}`, "Så följer jag upp att det händer", { rows: 2, group: n, secondary: true, optional: n === 2, hint: "Vem kan säga till dig om du glider tillbaka?" }),
      ]),
      t("testar", "Vilken situation vet du redan kommer att testa dig?", { rows: 2 }),
      t("gor_da", "Vad gör du när den kommer?", { rows: 2 }),
    ],
  },
  // Vecka 6:s handling följs upp vid 30 dagar. Planen låses när deltagaren
  // har svarat på Blev det av? där.
  action(["Veckans handling är den första i det som kommer efter utbildningen."], {
    hint: "Välj något du vill kunna säga att du fortfarande gör om 30 dagar.",
    returnAt: { step: "d30", section: "kvar", field: "blev" },
  }),
  privat("vet_redan", "Vad vet jag egentligen redan?"),
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
    recallStep: "w6",
    outcomeField: "blev",
    shareable: true,
    doneWhen: { all: ["blev", "hande_markte", "stoppade", "fortfarande", "nasta_steg"] },
    fields: [
      choice("blev", "Handlingen du valde i vecka 6. Blev det av?", ["Ja", "Delvis", "Nej"]),
      t("hande_markte", "Vad hände? Märkte någon något? Vad bygger du det på?", when("blev", YES_PARTLY)),
      t("stoppade", "Vad stoppade dig?", when("blev", ["Nej"])),
      t("fortfarande", "Vad gör du fortfarande?"),
      t("foll_bort_stoppade", "Vad föll bort, och vad stoppade det?", { optional: true }),
      t("reagerat_bygger", "Har någon reagerat på något? Vad bygger du det på?", { optional: true }),
      t("testade", "Situationen du visste skulle testa dig. Kom den? Vad gjorde du?", { optional: true }),
      t("undvikit", "Vad har du undvikit sedan kursen slutade?", { optional: true }),
      t("nasta_steg", "Vad är ditt nästa konkreta steg?"),
    ],
  },
  {
    key: "atertraff",
    kind: "reunion",
    title: "Återträffen",
    lead: ["Vi ses en gång till.", "Ingen ny kurs. Bara det som hände.", "Fyll i din uppföljning innan vi ses. Ta med det du vill säga högt."],
    source: "Order 010 och 011. Spec avsnitt 18.",
    fields: [],
  },
];

// ---------- Startsamtalet ----------

const START_SECTIONS = [
  {
    key: "infor",
    kind: "reflection",
    title: "Inför startsamtalet",
    privacy: true,
    lead: ["Du behöver inte ta med ett färdigt svar. Ta med det du faktiskt funderar på."],
    source: "Arbetsboken, Enskilt samtal. Order 010.",
    shareable: true,
    doneWhen: { atLeast: 1 },
    fields: [
      t("forsta", "Vad vill jag att Jan ska förstå om min situation?"),
      t("skaver", "Vad skaver mest i mitt ledarskap just nu?", { hint: "Vilken situation, relation eller del av ditt ledarskap tar mest energi?" }),
      t("inte_gruppen", "Vad vill jag inte ta i gruppen just nu?"),
    ],
  },
  {
    key: "efter",
    kind: "reflection",
    title: "Efter startsamtalet",
    lead: ["Skriv medan det är färskt."],
    source: "Order 010 beslut 7.",
    doneWhen: { atLeast: 1 },
    fields: [t("tar_med", "Vad tar jag med mig från samtalet?"), t("gora_nu", "Vad ska jag göra nu?")],
  },
];

// ---------- Samtal med Jan vid behov ----------

const TALK_SECTIONS = [
  {
    key: "behov",
    kind: "talk",
    title: "Samtal med Jan",
    lead: [
      "Sitter du fast? Kommer samma sak tillbaka vecka efter vecka?",
      "Be om ett samtal.",
      "Jan kan också höra av sig, om han ser något i det du har delat med honom.",
    ],
    button: "Be om ett samtal med Jan",
    source: "Order 013. Spec avsnitt 16.",
    fields: [],
  },
  {
    key: "infor",
    kind: "reflection",
    title: "Inför samtalet",
    lead: ["Du behöver inte ta med ett färdigt svar. Ta med det du faktiskt funderar på."],
    source: "Arbetsboken, Enskilt samtal.",
    shareable: true,
    doneWhen: { atLeast: 1 },
    fields: [t("tanka_kring", "Vad vill jag få hjälp att tänka kring?"), t("monster", "Vilket mönster ser jag hos mig själv?")],
  },
  {
    key: "efter",
    kind: "reflection",
    title: "Efter samtalet",
    lead: ["Skriv medan det är färskt."],
    source: "Order 010 beslut 7.",
    doneWhen: { atLeast: 1 },
    fields: [t("tar_med", "Vad tar jag med mig från samtalet?"), t("gora_nu", "Vad ska jag göra nu?")],
  },
];

// ---------- Programmet ----------

export const STEPS = [
  { key: "w1", slug: "vecka-1", order: 1, label: "Vecka 1", title: "Jag som ledare", subtitle: "Vad behöver faktiskt förändras i mitt ledarskap?", built: true, sections: WEEK_1_SECTIONS },
  { key: "w2", slug: "vecka-2", order: 2, label: "Vecka 2", title: "Mod, ansvar och beslut", subtitle: "Vad skjuter jag upp trots att det är mitt ansvar?", built: true, sections: WEEK_2_SECTIONS },
  // Se · Höra · Känna. Fast regel: SE vänster, HÖRA mitten, KÄNNA höger.
  // KÄNNA är en signal att undersöka, aldrig ett påstående om vad någon annan känner.
  { key: "w3", slug: "vecka-3", order: 3, label: "Vecka 3", title: "Se. Höra. Känna.", subtitle: "Vad vet jag faktiskt innan jag bedömer en annan människa?", built: true, sections: WEEK_3_SECTIONS },
  { key: "w4", slug: "vecka-4", order: 4, label: "Vecka 4", title: "Relation, trygghet och det svåra samtalet", subtitle: "Vad behöver jag göra eftersom jag har ansvaret?", built: true, sections: WEEK_4_SECTIONS },
  { key: "w5", slug: "vecka-5", order: 5, label: "Vecka 5", title: "Teamet och förutsättningarna", subtitle: "Vad sitter hos personen, vad sitter i gruppen och vad har jag själv byggt runt dem?", built: true, sections: WEEK_5_SECTIONS },
  { key: "w6", slug: "vecka-6", order: 6, label: "Vecka 6", title: "Ledarskap under press", subtitle: "Vem blir jag när det blir svårt, och vad fortsätter jag göra?", built: true, sections: WEEK_6_SECTIONS },
  { key: "d30", slug: "30-dagar", order: 7, label: "30 dagar", title: "Vad blev faktiskt kvar?", subtitle: "Uppföljning efter utbildningen", built: true, sections: DAY_30_SECTIONS },
  { key: "start", slug: "startsamtal", order: 0, aside: true, alwaysOpen: true, label: "Startsamtalet", title: "Startsamtalet", subtitle: "Inför och efter startsamtalet med Jan", built: true, sections: START_SECTIONS },
  { key: "samtal", slug: "samtal", order: 0, aside: true, alwaysOpen: true, label: "Samtal med Jan", title: "Samtal med Jan", subtitle: "Samtal vid behov", built: true, sections: TALK_SECTIONS },
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
// Textblock (info) är inga fält och kan inte sparas.
export function findField(stepKey, fieldPath) {
  const [sectionKey, fieldKey] = String(fieldPath).split(".");
  const section = getSection(stepKey, sectionKey);
  if (!section) return null;
  const field = section.fields.find((f) => f.key === fieldKey && f.kind !== "info");
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
    fields: fields.map(({ refs: _refs, origin: _origin, review: _review, support: _support, ...f }) => f),
  };
}

// eslint-disable-next-line no-unused-vars
export function publicProgram({ internal = false } = {}) {
  return {
    id: PROGRAM_ID,
    title: PROGRAM_TITLE,
    contentVersion: CONTENT_VERSION,
    mapDimensions: MAP_DIMENSIONS,
    mapScaleSteps: MAP_SCALE_STEPS,
    measurePointLabels: MEASURE_POINT_LABELS,
    liveSupport: LIVE_SUPPORT,
    privacyText: PRIVACY_TEXT,
    supportPrompt: SUPPORT_PROMPT,
    // Intern spårbarhet (källor, sidor, diplomstatus) stannar på servern.
    // Deltagarens sida får bara det som ska synas eller behövs för att fungera.
    diploma: null,
    steps: STEPS.map((s) => ({ ...s, sections: s.built ? s.sections.map(participantSection) : [] })),
  };
}
