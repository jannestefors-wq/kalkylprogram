// Regler för resan. Samma regler används av servern och av förhandsvisningen,
// så att de aldrig kan glida isär. Inga beroenden. Inga sidoeffekter.

export const MAX_TEXT = 8000;
export const MAX_SHORT = 200;
export const NO = "Nej";

export function stepByKey(steps, key) {
  return steps.find((s) => s.key === key) || null;
}

// Kalenderdatum (ÅÅÅÅ-MM-DD) i svensk tid. Används för datumstyrda steg.
export function todayYmd(now = new Date()) {
  return new Intl.DateTimeFormat("sv-SE", { timeZone: "Europe/Stockholm", year: "numeric", month: "2-digit", day: "2-digit" }).format(now);
}

// Lägg till hela kalendermånader. 31 januari plus en månad blir sista februari.
export function addMonths(ymd, months) {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(ymd || ""));
  if (!m) return null;
  const y = Number(m[1]);
  const mo = Number(m[2]) - 1 + months;
  const year = y + Math.floor(mo / 12);
  const month = ((mo % 12) + 12) % 12;
  const last = new Date(Date.UTC(year, month + 1, 0)).getUTCDate();
  const day = Math.min(Number(m[3]), last);
  return `${year}-${String(month + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
}

// Datumet då ett datumstyrt steg öppnas. Tre månader: gruppens slutdatum plus tre kalendermånader.
export function stepOpensAt(step, endDate) {
  if (!step?.opensAfterEnd || !endDate) return null;
  return addMonths(endDate, step.opensAfterEnd.months);
}

// Ett steg är öppet när det är byggt och gruppen (eller testläget) har nått dit.
// Startsamtalet och Samtal med Jan är alltid öppna.
// Ett datumstyrt steg (tre månader) öppnas av datumet, aldrig av att gruppen
// flyttas fram. Bara testläget i testversionen kan öppna det tidigare.
// ctx: { endDate, today, testMode }.
export function isStepOpen(steps, stepKey, currentStep, ctx = {}) {
  const step = stepByKey(steps, stepKey);
  if (!step || !step.built) return false;
  if (step.alwaysOpen) return true;
  const current = stepByKey(steps, currentStep);
  const reached = Boolean(current) && step.order <= current.order;
  if (step.opensAfterEnd) {
    const at = stepOpensAt(step, ctx.endDate);
    if (at && (ctx.today || todayYmd()) >= at) return true;
    return Boolean(ctx.testMode) && reached;
  }
  return reached;
}

export function openStepKeys(steps, currentStep, ctx = {}) {
  return steps.filter((s) => isStepOpen(steps, s.key, currentStep, ctx)).map((s) => s.key);
}

// Öppningsdatum för alla datumstyrda steg, för att kunna visa dem diskret.
export function opensAtMap(steps, endDate) {
  return Object.fromEntries(steps.filter((s) => s.opensAfterEnd).map((s) => [s.key, stepOpensAt(s, endDate)]));
}

const valueOf = (entries, stepKey, sectionKey, fieldKey) =>
  String(entries[`${stepKey}:${sectionKey}.${fieldKey}`]?.value || "");

// Ett fält syns när dess villkor är uppfyllt. Villkoret gäller ett annat fält
// i samma moment. Är det fältet självt dolt, är också det här fältet dolt.
export function fieldVisible(section, field, get, depth = 0) {
  if (!field.showWhen) return true;
  if (depth > 5) return false;
  const parent = section.fields.find((f) => f.key === field.showWhen.field);
  if (!parent || !fieldVisible(section, parent, get, depth + 1)) return false;
  const value = get(parent.key);
  if (parent.kind === "multi") return value.split("\n").some((v) => field.showWhen.in.includes(v));
  return field.showWhen.in.includes(value);
}

export function visibleFields(stepKey, section, entries) {
  const get = (k) => valueOf(entries, stepKey, section.key, k);
  return section.fields.filter((f) => f.kind !== "info" && fieldVisible(section, f, get));
}

// Klarstatus räknar bara fält som syns. Ett dolt fält krävs aldrig.
// Ett frivilligt fält krävs aldrig, men räknas som påbörjat.
export function sectionStatus(stepKey, section, entries, assessments, dimensions) {
  const rule = section.doneWhen;
  if (!rule) return null;
  if (section.kind === "map") {
    const values = assessments[section.measurePoint] || {};
    const n = dimensions.filter((d) => values[d.key]).length;
    return n === dimensions.length ? "done" : n > 0 ? "started" : "empty";
  }
  const visible = visibleFields(stepKey, section, entries);
  const filled = (k) => Boolean(valueOf(entries, stepKey, section.key, k).trim());
  const count = visible.filter((f) => filled(f.key)).length;
  let done;
  if (rule.all) {
    const required = visible.filter((f) => rule.all.includes(f.key) && !f.optional);
    done = required.length > 0 && required.every((f) => filled(f.key));
  } else {
    done = count >= (rule.atLeast || 1);
  }
  return done ? "done" : count > 0 ? "started" : "empty";
}

export function allStatuses(steps, entries, assessments, dimensions) {
  const status = {};
  for (const step of steps.filter((s) => s.built)) {
    for (const section of step.sections) {
      const st = sectionStatus(step.key, section, entries, assessments, dimensions);
      if (st) status[`${step.key}:${section.key}`] = st;
    }
  }
  return status;
}

// Lås:
//  - Planen i en vecka låses när Vad hände? har börjat skrivas. Beslutet står kvar.
//    Vecka 6:s plan låses när Blev det av? är besvarat vid 30 dagar.
//  - Startskattningen låses när gruppen har gått vidare från vecka 1.
export function lockedSections(steps, currentStep, entries) {
  const locked = {};
  for (const step of steps.filter((s) => s.built)) {
    for (const section of step.sections) {
      if (section.lockedWhen === "returnStarted") {
        let started = false;
        if (section.returnAt) {
          const { step: rs, section: rsec, field } = section.returnAt;
          started = Boolean(valueOf(entries, rs, rsec, field).trim());
        } else {
          const ret = step.sections.find((s) => s.recallFrom === section.key);
          started = Boolean(ret?.fields.some((f) => valueOf(entries, step.key, ret.key, f.key).trim()));
        }
        if (started) locked[`${step.key}:${section.key}`] = "return_started";
      }
      if (section.kind === "map" && section.measurePoint === "start" && currentStep !== "w1") {
        locked[`${step.key}:${section.key}`] = "week_passed";
      }
    }
  }
  return locked;
}

// Var en skattning får göras: i en öppen karta med den mätpunkten.
export function mapSectionFor(steps, point, currentStep, ctx = {}) {
  for (const step of steps.filter((s) => s.built)) {
    const section = step.sections.find((s) => s.kind === "map" && s.measurePoint === point);
    if (section) return isStepOpen(steps, step.key, currentStep, ctx) ? { step, section } : { step, section, closed: true };
  }
  return null;
}

// Validering av ett värde mot fältets typ. Returnerar felkod eller null.
export function validateValue(field, value) {
  if (typeof value !== "string") return "invalid_value";
  if (field.kind === "info") return "invalid_field";
  if (field.kind === "date" && value && !/^\d{4}-\d{2}-\d{2}$/.test(value)) return "invalid_date";
  if ((field.kind === "choice" || field.kind === "area") && value && !field.options.includes(value)) return "invalid_choice";
  if (field.kind === "check" && value && value !== "ja") return "invalid_choice";
  if (field.kind === "multi" && value) {
    const parts = value.split("\n");
    if (parts.some((p) => !field.options.includes(p)) || new Set(parts).size !== parts.length) return "invalid_choice";
  }
  if (value.length > (field.kind === "short" ? MAX_SHORT : MAX_TEXT)) return "too_long";
  return null;
}

export function anyInStep(stepKey, entries, assessments, steps) {
  const hasText = Object.keys(entries).some((k) => k.startsWith(`${stepKey}:`) && String(entries[k].value || "").trim());
  if (hasText) return true;
  const step = stepByKey(steps, stepKey);
  return Boolean(step?.sections.some((s) => s.kind === "map" && Object.keys(assessments[s.measurePoint] || {}).length));
}

// Svaren på Blev det av?, i resans ordning. Vecka 1 till 5 i Vad hände?,
// vecka 6 vid 30 dagar. Ett uteblivet svar är inget Nej.
export function outcomeSequence(steps, entries) {
  const seq = [];
  const ordered = steps.filter((s) => s.built && !s.aside).sort((a, b) => a.order - b.order);
  for (const step of ordered) {
    for (const section of step.sections.filter((s) => s.outcomeField)) {
      seq.push({ step: step.key, section: section.key, value: valueOf(entries, step.key, section.key, section.outcomeField) });
    }
  }
  return seq;
}

// Privat vägledning efter två Nej i rad (spec avsnitt 16).
// handled: de följder deltagaren redan har svarat på, nycklade på steget där
// följden nådde två. Efter ett svar krävs en ny följd av två Nej i rad.
// Returnerar steget där den aktuella följden nådde två, eller null.
// Funktionen läser bara deltagarens egna svar och används bara i deltagarens egen vy.
export function supportPromptFor(steps, entries, handled = []) {
  const done = new Set(handled);
  let streak = 0;
  let candidate = null;
  for (const item of outcomeSequence(steps, entries)) {
    if (item.value === NO) streak += 1;
    else if (!item.value) streak = 0; // Inget svar ännu. Bryter följden men är inget Nej.
    else {
      streak = 0;
      candidate = null; // Ett senare Ja eller Delvis gör frågan inaktuell.
    }
    if (streak >= 2) {
      candidate = item.step;
      if (done.has(item.step)) {
        streak = 0;
        candidate = null;
      }
    }
  }
  return candidate;
}
