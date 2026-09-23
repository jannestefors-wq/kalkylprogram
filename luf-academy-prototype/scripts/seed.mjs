// Testdata för prototypen. Två parallella grupper, fiktiva deltagare,
// Jan som handledare och en programadministratör.
// Skriver personliga inloggningslänkar till data/inloggningslankar.txt.
import { randomBytes, randomUUID } from "node:crypto";
import { mkdirSync, rmSync, writeFileSync } from "node:fs";
import { openDb } from "../server/db.mjs";
import { hashToken } from "../server/app.mjs";
import { PROGRAM_ID, PROGRAM_TITLE } from "../server/content.mjs";

export function seed(db, { baseUrl = "http://127.0.0.1:4310", linkDays = 21, today = new Date() } = {}) {
  const now = today.toISOString();
  const day = (offset) => new Date(Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate() + offset));
  const isoDate = (d) => d.toISOString().slice(0, 10);
  const at = (d, hourUtc) => new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate(), hourUtc, 0)).toISOString();

  db.prepare("INSERT INTO lr_program (id, title, status) VALUES (?, ?, 'prototype')").run(PROGRAM_ID, PROGRAM_TITLE);

  const cohorts = [
    { id: "grupp-a", name: "Grupp A", start: day(-2), status: "running" },
    { id: "grupp-b", name: "Grupp B", start: day(12), status: "planned" },
  ];
  for (const c of cohorts) {
    db.prepare(
      "INSERT INTO lr_cohort (id, program_id, name, start_date, end_date, current_step, status) VALUES (?, ?, ?, ?, ?, 'w1', ?)",
    ).run(c.id, PROGRAM_ID, c.name, isoDate(c.start), isoDate(new Date(c.start.getTime() + 41 * 86400000)), c.status);
    ["w1", "w2", "w3", "w4", "w5", "w6"].forEach((step, i) => {
      const d = new Date(c.start.getTime() + (i * 7 + 3) * 86400000);
      db.prepare(
        "INSERT INTO lr_live_session (id, cohort_id, step_key, starts_at, duration_minutes, teams_url, preparation) VALUES (?, ?, ?, ?, 90, '', ?)",
      ).run(`${c.id}-${step}`, c.id, step, at(d, 14), step === "w1" ? "Ta med situationen du har beskrivit och det du har valt att prova." : "");
    });
  }

  const users = [
    { key: "testdeltagare", name: "Testdeltagare Jan", email: "testdeltagare@prototyp.luf", cohort: "grupp-a" },
    { key: "deltagare-a2", name: "Anna (fiktiv)", email: "anna@prototyp.luf", cohort: "grupp-a" },
    { key: "deltagare-a3", name: "Karim (fiktiv)", email: "karim@prototyp.luf", cohort: "grupp-a" },
    { key: "deltagare-b1", name: "Lena (fiktiv)", email: "lena@prototyp.luf", cohort: "grupp-b" },
    { key: "deltagare-b2", name: "Oskar (fiktiv)", email: "oskar@prototyp.luf", cohort: "grupp-b" },
    { key: "jan-handledare", name: "Jan Stefors", email: "jan@prototyp.luf", roles: [["facilitator", "grupp-a"], ["facilitator", "grupp-b"]] },
    { key: "programadmin", name: "Programadministratör", email: "admin@prototyp.luf", roles: [["program_admin", null]] },
  ];
  const links = {};
  for (const u of users) {
    const id = randomUUID();
    db.prepare("INSERT INTO lr_user (id, email, display_name) VALUES (?, ?, ?)").run(id, u.email, u.name);
    if (u.cohort) db.prepare("INSERT INTO lr_enrollment (id, user_id, cohort_id) VALUES (?, ?, ?)").run(randomUUID(), id, u.cohort);
    for (const [role, cohortId] of u.roles || []) {
      db.prepare("INSERT INTO lr_role_grant (user_id, role, cohort_id) VALUES (?, ?, ?)").run(id, role, cohortId);
    }
    const token = randomBytes(24).toString("base64url");
    const expires = new Date(today.getTime() + linkDays * 86400000).toISOString();
    db.prepare("INSERT INTO lr_prototype_login (token_hash, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)").run(
      hashToken(token), id, now, expires,
    );
    links[u.key] = { name: u.name, url: `${baseUrl}/login?t=${token}`, token };
  }
  return links;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const path = process.env.LR_DB || "data/prototype.db";
  mkdirSync("data", { recursive: true });
  for (const suffix of ["", "-wal", "-shm"]) rmSync(path + suffix, { force: true });
  const links = seed(openDb(path), { baseUrl: process.env.LR_BASE_URL || "http://127.0.0.1:4310" });
  const text = Object.values(links).map((l) => `${l.name}\n${l.url}\n`).join("\n");
  writeFileSync("data/inloggningslankar.txt", text);
  console.log(text);
}
