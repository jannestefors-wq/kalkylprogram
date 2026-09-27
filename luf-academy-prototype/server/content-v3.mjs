// Deltagartext för 024. Källan 023 är låst. Inga veckomoduler.
import { STEPS } from "./content.mjs";
export const SURFACES = [
  ["direction", "Min riktning", "Välj det som skulle göra störst skillnad just nu. Du får ompröva när du ser tydligare."],
  ["action", "Det jag provar nu", "Förändring får ta plats i en verklig situation. Ett litet försök räcker att börja med."],
  ["outcome", "Vad hände?", "Stanna upp och undersök vad som faktiskt hände. Nej är också ett giltigt utfall."],
  ["reflection", "Det jag börjar se", "Här kan du tänka fritt. Du behöver inte ha svaret. Allt är privat tills du själv väljer att dela."],
  ["round", "Runda bordet", "Ta med en verklig situation. Lyssna och hjälp varandra att förstå före råd."],
  ["talk", "Mina samtal med Jan", "Mötet får följa det du behöver förstå. Anteckna bara det som hjälper dig."],
  ["journey", "Min resa", "Se tillbaka på ditt fokus, dina handlingar och det du börjat märka."]
];
export const TALKS = [
  { id: "start", title: "Start 1:1", minutes: 60 },
  { id: "middle", title: "Mitt 1:1", minutes: 45 },
  { id: "end", title: "Avslutande 1:1", minutes: 45 },
  { id: "three", title: "3-månaders 1:1", minutes: 30 }
];
export const COMPASS = ["Verklig situation", "Övriga lyssnar", "Vad vet vi?", "Vad tror vi?", "Vad saknas?", "Varför?", "Är detta rätt problem?", "Ta saken", "Dela upp", "Prioritera", "Deltagaren väljer nästa steg"];
export const COMPASS_NOTE = "Kompass, inte manus. Stanna, byt ordning och följ människan. Fråga före råd. Hjärta: förstå innan bedömning. Mod: våga undersöka det svåra. Jag vet inte ännu är ett giltigt svar.";
export const CORNERS = ["SE", "HÖRA", "KÄNNA"];
export const FEELING = "KÄNNA är din egen signal att undersöka – aldrig kunskap om vad en annan människa känner.";
export const COTRAINER = "Vad såg eller hörde du idag som förändrade hur du själv tänker?";
export const MIRROR = {
  1: [
    "När fungerar personen som bäst i mötet med andra? Beskriv gärna en konkret situation du själv har sett eller hört.",
    "Vad skulle personen vinna mest på att göra mer av? Vad bygger du det på?",
    "Vad skulle personen vinna mest på att göra mindre av? Vad bygger du det på?",
    "Finns det något i personens sätt att agera som personen själv kanske inte alltid ser? Beskriv gärna en konkret situation.",
    "Om en enda sak förändrades under de kommande månaderna, vad tror du skulle göra störst positiv skillnad? Hur skulle du märka det?",
    "Är det något annat du vill skicka med som kan hjälpa personen att utvecklas?"
  ],
  2: [
    "Vad, om något, har du märkt är annorlunda i hur personen leder eller möter andra?",
    "Beskriv ett konkret exempel.",
    "Vad verkar oförändrat?",
    "Vad tycker du personen bör fortsätta träna på?"
  ]
};
export const FIELDS = {
  focus: [["title","Mitt primära fokus"],["why","Varför detta?"],["notice","Hur skulle någon kunna märka skillnad?"],["reason","Varför behåller eller byter jag fokus?"]],
  action: [["what","Vad ska jag göra?"],["situation","I vilken verklig situation?"],["when","När?"]],
  outcome: [["result","Blev det av?"],["happened","Vad hände?"],["evidence","Vad bygger du det på?"],["blocked","Vad stoppade dig?"],["next","Vad gör du nu?"]],
  reflection: [["text","Det jag också ser"]],
  talk: [["preparation","Vad vill jag förstå eller ta med till samtalet?"],["takeaway","Vad tar jag med mig?"],["next","Nästa steg"]],
  d30: [["still","Vad gör du fortfarande?"],["lost","Vad föll bort?"],["blocked","Vad stoppade det?"],["noticed","Vad märks?"],["evidence","Vad bygger du det på?"],["next","Vad gör du nu?"]],
  three: [["noticed","Vad ser du när du jämför då och nu?"],["evidence","Vad bygger du det på?"],["next","Vad vill du fortsätta träna på?"]],
  summary: [["text","Min egen sammanfattning av Spegeln"]],
  cotrainer: [["text", COTRAINER]]
};
// Endast källhänvisningar hämtas från v2. Ingen veckostyrning följer med.
const source = STEPS.flatMap(s => s.sections.flatMap(x => x.reading ? [...x.reading.chapters, ...(x.reading.optional || [])] : []));
const find = title => {
  const r = source.find(x => x.title === title);
  if (!r) throw new Error("Saknad bokkälla: " + title);
  return { ...r };
};
export const BOOK = {
  foundation: ["Människan först", "Utan filter", "Modet att kliva fram", "Triangelmetodiken", "Se — Höra — Känna"].map(title => {
    const ref=find(title), start=Number(ref.pages.split("–")[0]);
    return { ...ref, pages: start+"–"+(start+1), pdfPages: (start+7)+"–"+(start+8), note: "Kort inledande urval. Stanna där det hjälper dig förstå." };
  }),
  cases: ["Konflikt — Lösning — Ansvar", "Varför vi alltid börjar i fel ände", "Individ — Team — Organisation", "Stress, press och den inre kompassen", "Konsten att ge och ta emot feedback"].map(find),
  optional: [...new Map(source.map(r => [r.title, { ...r }])).values()]
};
const coaching = { title: "Det coachande ledarskapet", pages: "163–164", pdfPages: "170–171", inChapter: "Att utveckla andra ledare" };
BOOK.cases.push(coaching);
BOOK.optional.push(coaching);
export const BOOK_NOTE = "Gemensam grund ger oss ett språk tidigt i resan. Välj ett kort stycke och stanna där det hjälper dig förstå. Sidintervallen visar var du hittar materialet, inte en läsläxa. Du behöver inte läsa allt eller bli klar före ett möte.";
export const RESULT_NOTE = "Observerad förändring och upplevd förändring: flera datapunkter som tillsammans ger en starkare bild. De visar inte i sig vad som orsakade en förändring.";
