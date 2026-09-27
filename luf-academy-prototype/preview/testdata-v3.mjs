// Enbart syntetiskt. Inga kontaktuppgifter, inbjudningar eller nätanrop.
export const FIXTURE_ID = "lmhm-v3-024-synthetic";
export const PEOPLE = [
  { id: "v3_alex", role: "participant", name: "Alex · syntetisk deltagare" },
  { id: "v3_sam", role: "participant", name: "Sam · syntetisk deltagare" },
  { id: "v3_jan", role: "facilitator", name: "Jan · testvy" },
  { id: "v3_admin", role: "program_admin", name: "Fredde · testvy" },
  { id: "v3_employer", role: "employer", name: "Arbetsgivare · spärrad testvy" }
];
export const MIRROR_FIXTURES = [1, 2].flatMap(round =>
  ["egen chef", "kollega", "medarbetare", "partner"].map((relation, i) => ({
    id: "mirror" + round + "-" + i, round, relation, synthetic: true,
    answers: round === 1 ? [
      "I vårt fiktiva planeringsmöte lyssnade personen klart innan den svarade.",
      "Ställa fler frågor. Jag hörde ett svar komma innan frågan var färdig.",
      "Avbryta mindre. Vid ett fiktivt samtal fick jag börja om.",
      "När tiden blev knapp började personen själv lösa uppgiften.",
      "Lämna mer utrymme för andras förslag. Jag skulle märka att fler talar till punkt.",
      i === 3 ? "Ge också dig själv tid att tänka." : ""
    ] : [
      i === 1 ? "Jag har inte märkt någon tydlig skillnad ännu." : "Vid det senaste fiktiva samtalet fick jag mer tid att tänka.",
      "Personen väntade efter sin fråga innan den gav ett eget förslag.",
      "När det blir bråttom kommer svaren fortfarande snabbt.",
      "Fortsätta fråga och ge tid för svaret."
    ]
  }))
);
export const ROUNDS = Array.from({ length: 7 }, (_, i) => ({
  id: "round-" + (i + 1),
  title: i < 6 ? "Runda bordet " + (i + 1) : "Runda bordet Återträff",
  day: i < 6 ? 7 * i + 3 : 72,
  startsAt: new Date(Date.UTC(2026, 9, 5 + (i < 6 ? 7 * i + 3 : 72), 15)).toISOString(),
  duration: i < 6 ? "cirka 90–120 minuter" : "cirka 60 minuter",
  preparation: "Vilken verklig situation vill du förstå bättre? Det räcker att ta med den i tanken.",
  testLink: "#round"
}));
