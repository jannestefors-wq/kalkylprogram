// Regler för resan. Samma regler används av servern och av förhandsvisningen,
// så att de aldrig kan glida isär. Inga beroenden. Inga sidoeffekter.

export const MAX_TEXT = 8000;
export const MAX_SHORT = 200;

export function stepByKey(steps, key) {
  return steps.find((s) => s.key === key) || null;
}

// Ett steg är öppet när det är byggt och gruppen (eller testläget) har nått dit.
// Samtal med Jan är alltid öppet.
export function isStepOpen(steps, stepKey, currentStep) {
  const step = stepByKey(steps, stepKey);
  if (!step || !step.built) return false;
  if (step.alwaysOpen) return true;
  const current = stepByKey(steps, currentStep);
  return Boolean(current) && step.order <= current.order;
}

export function openStepKeys(steps, currentStep) {
  return steps.filter((s) => isStepOpen(steps, s.key, currentStep)).map((s) => s.key);
}

export function sectionStatus(stepKey, section, entries, assessments, dimensions) {
  const rule = section.doneWhen;
  if (!rule) return null;
  if (section.kind === "map") {
    const values = assessments[section.measurePoint] || {};
    const n = dimensions.filter((d) => values[d.key]).length;
    return n === dimensions.length ? "done" : n > 0 ? "started" : "empty";
  }
  const filled = (k) => Boolean(String(entries[`${stepKey}:${section.key}.${k}`]?.value || "").trim());
  const count = section.fields.filter((f) => filled(f.key)).length;
  const done = rule.all ? rule.all.every(filled) : count >= (rule.atLeast || 1);
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
//  - Startskattningen låses när gruppen har gått vidare från vecka 1.
export function lockedSections(steps, currentStep, entries) {
  const locked = {};
  for (const step of steps.filter((s) => s.built)) {
    for (const section of step.sections) {
      if (section.lockedWhen === "returnStarted") {
        const ret = step.sections.find((s) => s.recallFrom === section.key);
        const started = ret?.fields.some((f) => String(entries[`${step.key}:${ret.key}.${f.key}`]?.value || "").trim());
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
export function mapSectionFor(steps, point, currentStep) {
  for (const step of steps.filter((s) => s.built)) {
    const section = step.sections.find((s) => s.kind === "map" && s.measurePoint === point);
    if (section) return isStepOpen(steps, step.key, currentStep) ? { step, section } : { step, section, closed: true };
  }
  return null;
}

// Validering av ett värde mot fältets typ. Returnerar felkod eller null.
export function validateValue(field, value) {
  if (typeof value !== "string") return "invalid_value";
  if (field.kind === "date" && value && !/^\d{4}-\d{2}-\d{2}$/.test(value)) return "invalid_date";
  if (field.kind === "choice" && value && !field.options.includes(value)) return "invalid_choice";
  if (value.length > (field.kind === "short" ? MAX_SHORT : MAX_TEXT)) return "too_long";
  return null;
}

export function anyInStep(stepKey, entries, assessments, steps) {
  const hasText = Object.keys(entries).some((k) => k.startsWith(`${stepKey}:`) && String(entries[k].value || "").trim());
  if (hasText) return true;
  const step = stepByKey(steps, stepKey);
  return Boolean(step?.sections.some((s) => s.kind === "map" && Object.keys(assessments[s.measurePoint] || {}).length));
}
