// Testgruppen för Human Test. Endast testdata. Skrivs till förhandsvisningens
// egen databas som testdata/cohort.
// 16:00 svensk tid. Sommartiden slutar 25 oktober 2026.
const at = (ymd) => `${ymd}T${ymd < "2026-10-25" ? "14" : "15"}:00:00.000Z`;
export const TEST_COHORT = {
  id: "testgrupp-lmhm-v2",
  name: "Testgrupp. LMHM version 2",
  startDate: "2026-09-23",
  endDate: "2026-11-03",
  currentStep: "w1",
  status: "running",
  maxParticipants: 6,
  liveSessions: [
    ["w1", "2026-09-29"], ["w2", "2026-10-06"], ["w3", "2026-10-13"],
    ["w4", "2026-10-20"], ["w5", "2026-10-27"], ["w6", "2026-11-03"],
  ].map(([step, day]) => ({
    id: `testgrupp-${step}`,
    step,
    startsAt: at(day),
    durationMinutes: 90,
    teamsUrl: "",
    preparation: step === "w1" ? "Ta med situationen du har beskrivit och det du har valt att prova." : "",
  })).concat([
    // Återträffen, 60 minuter, cirka 30 dagar efter vecka 6.
    { id: "testgrupp-d30", step: "d30", startsAt: at("2026-12-03"), durationMinutes: 60, teamsUrl: "", preparation: "" },
  ]),
};
