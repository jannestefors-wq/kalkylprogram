// Innehållsregister för Ledarskap med hjärta och mod.
//
// Detta är den enda källan för vilka steg, avsnitt och fält som finns.
// Servern validerar varje skrivning mot registret. Ett fält som inte står
// här kan inte sparas. Ett steg som inte är byggt kan inte öppnas.
//
// Källa för Vecka 1: arbetsordern DIGITAL LEDARSKAPSRESA 001 och
// Min ledarskapsresa MASTER v2 (Word). Arbetsbokens sidor är
// omsatta till funktion, inte kopierade som papper.

export const PROGRAM_ID = "ledarskap-med-hjarta-och-mod";
export const PROGRAM_TITLE = "Ledarskap med hjärta och mod";
export const MAX_PARTICIPANTS_PER_COHORT = 6;

// Läsanvisning. Får inte fabriceras.
// Arbetsboken (tio veckor) anger "Utan filter + Människan först" för sin
// vecka 1. Den uppgiften är inte kontrollerad mot den tryckta boken och
// arbetsboken är byggd för tio veckor, inte sex. Därför HOLD.
export const READING_HOLD = "HOLD FÖR JAN";

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

const t = (key, label, extra = {}) => ({ key, label, kind: "text", ...extra });

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
  {
    key: "lasning",
    kind: "reading",
    title: "Inför veckan",
    reading: {
      status: READING_HOLD,
      participantText: "Jan anger veckans läsning i boken före första träffen.",
      internalNote:
        "Arbetsboken MASTER v2 anger för sin vecka 1 av 10: Utan filter + Människan först. Ej kontrollerat mot den tryckta boken. Inga kapitelnummer eller sidor anges.",
    },
    fields: [],
  },
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
    fields: [],
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
      t(`person_${n}`, "Vem", { kind: "short", group: n, placeholder: "Roll eller initial" }),
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
      { key: "observation", title: "Det som hände", hint: "Det en kamera hade kunnat fånga." },
      { key: "tolkning", title: "Min tolkning", hint: "Här får du gissa. Det är din bild, inte fakta." },
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
  {
    key: "handling",
    kind: "action",
    doneWhen: { all: ["prova", "situation", "nar"] },
    title: "Det här ska jag prova",
    lead: ["Välj en verklig situation den här veckan. Litet nog för att bli gjort. Tydligt nog för att gå att följa upp."],
    note: "Det finns inget facit. Det är du som väljer.",
    shareable: true,
    lockedWhen: "returnStarted",
    fields: [
      t("prova", "Den här veckan ska jag prova", { rows: 3 }),
      t("situation", "I vilken situation?", { rows: 2 }),
      t("annorlunda", "Vad vill jag själv göra annorlunda?", { rows: 2 }),
      t("lagga_marke", "Vad vill jag försöka lägga märke till?", { rows: 2 }),
      t("nar", "När tänker jag göra det?", { kind: "date" }),
    ],
  },
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
];

export const STEPS = [
  { key: "w1", label: "Vecka 1", title: "Människan först", subtitle: "Mitt eget ledarskap och min närvaro", built: true, sections: WEEK_1_SECTIONS },
  { key: "w2", label: "Vecka 2", title: "Mod, ansvar och det jag undviker", built: false },
  // Vecka 3 kommer att använda Se. Höra. Känna. Permanent regel för modellen:
  // SE vänster, HÖRA mitten, KÄNNA höger. KÄNNA är en signal att undersöka,
  // aldrig ett påstående om vad någon annan känner.
  { key: "w3", label: "Vecka 3", title: "Se. Höra. Känna.", subtitle: "Att förstå innan jag agerar", built: false },
  { key: "w4", label: "Vecka 4", title: "Relationer, trygghet, konflikter och svåra samtal", built: false },
  { key: "w5", label: "Vecka 5", title: "Individ, team, organisation", subtitle: "Systemet runt människan", built: false },
  { key: "w6", label: "Vecka 6", title: "Stress, inre kompass och vad jag förändrar från och med nu", built: false },
  { key: "d30", label: "30 dagar", title: "Vad blev faktiskt kvar?", built: false },
];

export function getStep(stepKey) {
  return STEPS.find((s) => s.key === stepKey) || null;
}

export function getSection(stepKey, sectionKey) {
  const step = getStep(stepKey);
  return step?.sections?.find((s) => s.key === sectionKey) || null;
}

// Fältnyckel i databasen: "<avsnitt>.<fält>". Stabil över språk och versioner.
export function findField(stepKey, fieldPath) {
  const [sectionKey, fieldKey] = String(fieldPath).split(".");
  const section = getSection(stepKey, sectionKey);
  if (!section) return null;
  const field = section.fields.find((f) => f.key === fieldKey);
  return field ? { section, field } : null;
}

export function publicProgram({ internal = false } = {}) {
  return {
    id: PROGRAM_ID,
    title: PROGRAM_TITLE,
    mapDimensions: MAP_DIMENSIONS,
    mapScaleSteps: MAP_SCALE_STEPS,
    steps: STEPS.map((s) => ({
      key: s.key,
      label: s.label,
      title: s.title,
      subtitle: s.subtitle || "",
      built: s.built,
      sections: s.built
        ? s.sections.map((sec) => ({
            ...sec,
            reading: sec.reading
              ? {
                  status: sec.reading.status,
                  participantText: sec.reading.participantText,
                  ...(internal ? { internalNote: sec.reading.internalNote } : {}),
                }
              : undefined,
          }))
        : [],
    })),
  };
}
