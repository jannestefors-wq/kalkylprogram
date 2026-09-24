import { createHash, randomBytes, randomUUID } from "node:crypto";
import { readFile } from "node:fs/promises";
import { extname, join, normalize } from "node:path";
import { fileURLToPath } from "node:url";
import { tx } from "./db.mjs";
import { MAP_DIMENSIONS, STEPS, findField, getSection, getStep, publicProgram } from "./content.mjs";
import * as rules from "./rules.mjs";

const PUBLIC_DIR = fileURLToPath(new URL("../public/", import.meta.url));
const SESSION_COOKIE = "lr_session";
const SESSION_DAYS = 30;
const MAX_BODY_BYTES = 64 * 1024;
// Ett nytt skrivpass börjar efter så här lång paus. Då sparas föregående
// version som historik innan den skrivs över.
export const WRITING_SESSION_GAP_MS = 30 * 60 * 1000;

// Händelser som klienten själv får rapportera. Allt annat härleds på servern.
const CLIENT_EVENTS = new Set(["action_revisited", "autosave_failed", "client_error", "session_ended"]);

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".svg": "image/svg+xml",
  ".webp": "image/webp",
  ".png": "image/png",
};

const SECURITY_HEADERS = {
  "Content-Security-Policy":
    "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'",
  "Referrer-Policy": "no-referrer",
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "DENY",
  "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
};

class HttpError extends Error {
  constructor(status, code, extra = {}) {
    super(code);
    this.status = status;
    this.code = code;
    this.extra = extra;
  }
}

export const hashToken = (token) => createHash("sha256").update(String(token)).digest("hex");

export function createApp(db, config = {}) {
  const cfg = {
    identityMode: "prototype-link",
    prototype: true,
    secureCookies: false,
    now: () => new Date(),
    ...config,
  };
  const nowIso = () => cfg.now().toISOString();

  const q = {
    userByEmail: db.prepare("SELECT * FROM lr_user WHERE email = ? AND status = 'active'"),
    sessionUser: db.prepare(
      `SELECT u.* FROM lr_auth_session s JOIN lr_user u ON u.id = s.user_id
       WHERE s.token_hash = ? AND s.expires_at > ? AND u.status = 'active'`,
    ),
    touchSession: db.prepare("UPDATE lr_auth_session SET last_seen_at = ? WHERE token_hash = ?"),
    roles: db.prepare("SELECT role, cohort_id FROM lr_role_grant WHERE user_id = ?"),
    ownEnrollment: db.prepare(
      `SELECT e.*, c.name AS cohort_name, c.start_date, c.end_date, c.current_step, c.status AS cohort_status, c.program_id
       FROM lr_enrollment e JOIN lr_cohort c ON c.id = e.cohort_id
       WHERE e.id = ? AND e.user_id = ? AND e.status IN ('active', 'paused', 'completed')`,
    ),
    ownEnrollments: db.prepare(
      `SELECT e.*, c.name AS cohort_name, c.start_date, c.end_date, c.current_step, c.status AS cohort_status, c.program_id
       FROM lr_enrollment e JOIN lr_cohort c ON c.id = e.cohort_id
       WHERE e.user_id = ? AND e.status IN ('active', 'paused', 'completed') ORDER BY c.start_date`,
    ),
    liveSessions: db.prepare("SELECT * FROM lr_live_session WHERE cohort_id = ? ORDER BY starts_at"),
    oneOnOnes: db.prepare(
      "SELECT id, scheduled_at, status FROM lr_one_on_one WHERE enrollment_id = ? AND status IN ('proposed', 'booked') ORDER BY scheduled_at",
    ),
    entries: db.prepare("SELECT step_key, field_key, value, revision, updated_at FROM lr_entry WHERE enrollment_id = ?"),
    entry: db.prepare("SELECT * FROM lr_entry WHERE enrollment_id = ? AND step_key = ? AND field_key = ?"),
    assessments: db.prepare(
      "SELECT measure_point, dimension, value, assessed_at, updated_at FROM lr_self_assessment WHERE enrollment_id = ?",
    ),
    shares: db.prepare(
      "SELECT step_key, section_key, kind, created_at FROM lr_share WHERE enrollment_id = ? AND revoked_at IS NULL",
    ),
    eventExists: db.prepare(
      "SELECT 1 FROM lr_event WHERE enrollment_id = ? AND event_name = ? AND IFNULL(step_key, '') = ? AND IFNULL(section_key, '') = ?",
    ),
    insertEvent: db.prepare(
      "INSERT INTO lr_event (enrollment_id, event_name, step_key, section_key, created_at) VALUES (?, ?, ?, ?, ?)",
    ),
    touchEnrollment: db.prepare("UPDATE lr_enrollment SET last_activity_at = ? WHERE id = ?"),
  };

  // ---------- Identitet ----------

  function currentUser(req) {
    if (cfg.identityMode === "sites-header") {
      // Samma kontrakt som produktionens Sites-inloggning. Headern sätts av
      // plattformen och får aldrig litas på utanför den miljön.
      const email = req.headers["oai-authenticated-user-email"];
      return email ? q.userByEmail.get(String(email).trim()) || null : null;
    }
    const token = parseCookies(req.headers.cookie)[SESSION_COOKIE];
    if (!token) return null;
    const hash = hashToken(token);
    const user = q.sessionUser.get(hash, nowIso());
    if (user) q.touchSession.run(nowIso(), hash);
    return user || null;
  }

  function requireUser(req) {
    const user = currentUser(req);
    if (!user) throw new HttpError(401, "not_signed_in");
    return user;
  }

  function rolesOf(user) {
    return q.roles.all(user.id);
  }

  function isProgramAdmin(user) {
    return rolesOf(user).some((r) => r.role === "program_admin" || r.role === "platform_admin");
  }

  function facilitatorCohorts(user) {
    return rolesOf(user).filter((r) => r.role === "facilitator" && r.cohort_id).map((r) => r.cohort_id);
  }

  // Deltagarens resa kan bara nås av deltagaren själv. Fel ägare ger 404,
  // så att det inte går att pröva sig fram till andras resor.
  function ownEnrollment(user, enrollmentId) {
    const enr = q.ownEnrollment.get(String(enrollmentId), user.id);
    if (!enr) throw new HttpError(404, "not_found");
    return enr;
  }

  // ---------- Resans tillstånd ----------

  function entryMap(enrollmentId) {
    const map = {};
    for (const row of q.entries.all(enrollmentId)) {
      map[`${row.step_key}:${row.field_key}`] = row;
    }
    return map;
  }

  function assessmentMap(enrollmentId) {
    const map = {};
    for (const row of q.assessments.all(enrollmentId)) {
      (map[row.measure_point] ||= {})[row.dimension] = row.value;
    }
    return map;
  }

  // Steget gruppen står i. I prototypen kan en testperson flyttas med testläget.
  function currentStepOf(enr) {
    return (cfg.prototype && enr.test_step) || enr.current_step;
  }

  function lockedFor(enr, entries) {
    return rules.lockedSections(STEPS, currentStepOf(enr), entries);
  }

  function journeyState(enr) {
    const entries = entryMap(enr.id);
    const assessments = assessmentMap(enr.id);
    return {
      enrollmentId: enr.id,
      currentStep: currentStepOf(enr),
      openSteps: rules.openStepKeys(STEPS, currentStepOf(enr)),
      entries: Object.fromEntries(
        Object.entries(entries).map(([k, r]) => [k, { value: r.value, revision: r.revision, updatedAt: r.updated_at }]),
      ),
      assessments,
      shares: q.shares.all(enr.id).map((s) => ({ step: s.step_key, section: s.section_key, kind: s.kind, since: s.created_at })),
      locked: lockedFor(enr, entries),
      status: rules.allStatuses(STEPS, entries, assessments, MAP_DIMENSIONS),
      lastActivityAt: enr.last_activity_at,
    };
  }

  // Mätning härleds av servern från vad som faktiskt hände. Ingen text följer med.
  function recordOnce(enrollmentId, name, stepKey = null, sectionKey = null) {
    if (q.eventExists.get(enrollmentId, name, stepKey || "", sectionKey || "")) return;
    q.insertEvent.run(enrollmentId, name, stepKey, sectionKey, nowIso());
  }

  function deriveEvents(enr, stepKey, section, before, after) {
    if (!before.anyInStep && after.anyInStep) recordOnce(enr.id, "week_started", stepKey);
    if (before.status !== "done" && after.status === "done") {
      recordOnce(enr.id, "section_completed", stepKey, section.key);
      if (section.kind === "action") recordOnce(enr.id, "action_chosen", stepKey, section.key);
      if (section.kind === "return") recordOnce(enr.id, "what_happened_completed", stepKey, section.key);
    }
  }

  function snapshot(enr, stepKey, section) {
    const entries = entryMap(enr.id);
    const assessments = assessmentMap(enr.id);
    return {
      anyInStep: rules.anyInStep(stepKey, entries, assessments, STEPS),
      status: rules.sectionStatus(stepKey, section, entries, assessments, MAP_DIMENSIONS),
    };
  }

  // ---------- Handlers ----------

  function me(req) {
    const user = requireUser(req);
    const roles = rolesOf(user);
    const now = nowIso();
    const enrollments = q.ownEnrollments.all(user.id).map((enr) => {
      const sessions = q.liveSessions.all(enr.cohort_id);
      const next = sessions.find((s) => endOf(s) > now) || null;
      return {
        id: enr.id,
        status: enr.status,
        lastActivityAt: enr.last_activity_at,
        cohort: {
          id: enr.cohort_id,
          name: enr.cohort_name,
          startDate: enr.start_date,
          endDate: enr.end_date,
          currentStep: currentStepOf(enr),
          groupStep: enr.current_step,
          status: enr.cohort_status,
        },
        nextLiveSession: next && liveSessionOut(next),
        oneOnOnes: q.oneOnOnes.all(enr.id).map((o) => ({ id: o.id, scheduledAt: o.scheduled_at, status: o.status })),
      };
    });
    return {
      user: { id: user.id, displayName: user.display_name, email: user.email },
      roles: {
        programAdmin: isProgramAdmin(user),
        facilitatorCohorts: facilitatorCohorts(user),
      },
      prototype: cfg.prototype,
      program: publicProgram({ internal: cfg.prototype }),
      enrollments,
    };
  }

  function getJourney(req, enrollmentId) {
    const user = requireUser(req);
    return journeyState(ownEnrollment(user, enrollmentId));
  }

  function putEntry(req, enrollmentId, body) {
    const user = requireUser(req);
    const enr = ownEnrollment(user, enrollmentId);
    const { step, field, value, baseRevision } = body || {};
    // baseRevision är den revision klienten utgår från. 0 betyder "inget sparat ännu".
    if (baseRevision != null && !(Number.isInteger(baseRevision) && baseRevision >= 0)) {
      throw new HttpError(400, "invalid_base_revision");
    }
    const base = baseRevision ?? null;
    const stepDef = getStep(step);
    if (!stepDef) throw new HttpError(400, "unknown_step");
    if (!rules.isStepOpen(STEPS, step, currentStepOf(enr))) throw new HttpError(403, "step_not_open");
    const found = findField(step, field);
    if (!found) throw new HttpError(400, "unknown_field");
    const { section, field: def } = found;
    const invalid = rules.validateValue(def, value);
    if (invalid) throw new HttpError(invalid === "too_long" ? 413 : 400, invalid);

    return tx(db, () => {
      const entriesBefore = entryMap(enr.id);
      const lock = lockedFor(enr, entriesBefore)[`${step}:${section.key}`];
      if (lock) throw new HttpError(423, "locked", { reason: lock });

      const before = snapshot(enr, step, section);
      const now = nowIso();
      const existing = q.entry.get(enr.id, step, field);
      const conflict = (row) =>
        new HttpError(409, "conflict", { revision: row?.revision ?? 0, value: row?.value ?? "", updatedAt: row?.updated_at ?? null });
      let result;
      if (!existing) {
        // Nytt svar. Klienten får inte tro att det finns en tidigare version.
        if (base > 0) throw conflict(null);
        if (value === "") return { revision: 0, savedAt: now };
        // Villkorlig insättning. Hann någon annan skapa svaret först blir det konflikt.
        const created = db
          .prepare(
            "INSERT INTO lr_entry (enrollment_id, step_key, field_key, value, revision, created_at, updated_at) VALUES (?, ?, ?, ?, 1, ?, ?) ON CONFLICT (enrollment_id, step_key, field_key) DO NOTHING",
          )
          .run(enr.id, step, field, value, now, now);
        if (created.changes !== 1) throw conflict(q.entry.get(enr.id, step, field));
        result = { revision: 1, savedAt: now };
      } else {
        // Ett befintligt svar får bara ändras av den som utgår från den senaste
        // revisionen. Saknas revisionen skrivs ingenting.
        if (base == null) throw new HttpError(428, "base_revision_required");
        if (base !== existing.revision) throw conflict(existing);
        if (existing.value === value) return { revision: existing.revision, savedAt: existing.updated_at };
        const gap = Date.parse(now) - Date.parse(existing.updated_at);
        if (gap > WRITING_SESSION_GAP_MS && existing.value.trim()) {
          const last = db
            .prepare("SELECT written_until FROM lr_entry_history WHERE entry_id = ? ORDER BY id DESC LIMIT 1")
            .get(existing.id);
          db.prepare(
            "INSERT INTO lr_entry_history (entry_id, value, written_from, written_until) VALUES (?, ?, ?, ?)",
          ).run(existing.id, existing.value, last?.written_until || existing.created_at, existing.updated_at);
        }
        // Villkorlig uppdatering. Jämförelsen och skrivningen är en och samma
        // sats, så två samtidiga anrop med samma revision kan inte båda lyckas.
        // Blir ingen rad uppdaterad rullas transaktionen tillbaka, även historiken.
        const updated = db
          .prepare("UPDATE lr_entry SET value = ?, revision = revision + 1, updated_at = ? WHERE id = ? AND revision = ?")
          .run(value, now, existing.id, base);
        if (updated.changes !== 1) throw conflict(q.entry.get(enr.id, step, field));
        result = { revision: base + 1, savedAt: now };
      }
      q.touchEnrollment.run(now, enr.id);
      deriveEvents(enr, step, section, before, snapshot(enr, step, section));
      return result;
    });
  }

  function putAssessment(req, enrollmentId, body) {
    const user = requireUser(req);
    const enr = ownEnrollment(user, enrollmentId);
    const { point, dimension, value } = body || {};
    // En skattning får bara göras i en karta som finns i ett öppet steg.
    const found = rules.mapSectionFor(STEPS, point, currentStepOf(enr));
    if (!found || found.closed) throw new HttpError(403, "measure_point_not_open");
    if (!MAP_DIMENSIONS.some((d) => d.key === dimension)) throw new HttpError(400, "unknown_dimension");
    if (!Number.isInteger(value) || value < 1 || value > 6) throw new HttpError(400, "invalid_value");
    const { step, section } = found;
    return tx(db, () => {
      if (lockedFor(enr, entryMap(enr.id))[`${step.key}:${section.key}`]) throw new HttpError(423, "locked");
      const before = snapshot(enr, step.key, section);
      const now = nowIso();
      db.prepare(
        `INSERT INTO lr_self_assessment (enrollment_id, measure_point, dimension, value, assessed_at, updated_at)
         VALUES (?, ?, ?, ?, ?, ?)
         ON CONFLICT (enrollment_id, measure_point, dimension) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at`,
      ).run(enr.id, point, dimension, value, now, now);
      q.touchEnrollment.run(now, enr.id);
      deriveEvents(enr, step.key, section, before, snapshot(enr, step.key, section));
      return { savedAt: now };
    });
  }

  function putShare(req, enrollmentId, body) {
    const user = requireUser(req);
    const enr = ownEnrollment(user, enrollmentId);
    const { step, section: sectionKey, kind, active } = body || {};
    const section = getSection(step, sectionKey);
    if (!section || !section.shareable) throw new HttpError(400, "not_shareable");
    if (!["share_with_facilitator", "bring_to_session"].includes(kind)) throw new HttpError(400, "unknown_kind");
    const now = nowIso();
    tx(db, () => {
      db.prepare(
        "UPDATE lr_share SET revoked_at = ? WHERE enrollment_id = ? AND step_key = ? AND section_key = ? AND kind = ? AND revoked_at IS NULL",
      ).run(now, enr.id, step, sectionKey, kind);
      if (active === true) {
        db.prepare(
          "INSERT INTO lr_share (enrollment_id, step_key, section_key, kind, created_at) VALUES (?, ?, ?, ?, ?)",
        ).run(enr.id, step, sectionKey, kind, now);
      }
    });
    return { shares: journeyState(enr).shares };
  }

  function getHistory(req, enrollmentId, url) {
    const user = requireUser(req);
    const enr = ownEnrollment(user, enrollmentId);
    const step = url.searchParams.get("step");
    const field = url.searchParams.get("field");
    if (!findField(step, field)) throw new HttpError(400, "unknown_field");
    const entry = q.entry.get(enr.id, step, field);
    if (!entry) return { current: null, versions: [] };
    const versions = db
      .prepare("SELECT value, written_from, written_until FROM lr_entry_history WHERE entry_id = ? ORDER BY id")
      .all(entry.id)
      .map((v) => ({ value: v.value, from: v.written_from, until: v.written_until }));
    return { current: { value: entry.value, since: entry.created_at, updatedAt: entry.updated_at }, versions };
  }

  function postEvent(req, body) {
    const user = requireUser(req);
    const keys = Object.keys(body || {});
    if (keys.some((k) => !["name", "enrollmentId", "step", "section"].includes(k))) throw new HttpError(400, "unknown_key");
    const { name, enrollmentId, step = null, section = null } = body;
    if (!CLIENT_EVENTS.has(name)) throw new HttpError(400, "unknown_event");
    if (step !== null && !getStep(step)) throw new HttpError(400, "unknown_step");
    if (section !== null && !getSection(step, section)) throw new HttpError(400, "unknown_section");
    const enr = enrollmentId ? ownEnrollment(user, enrollmentId) : null;
    q.insertEvent.run(enr?.id || null, name, step, section, nowIso());
    return { ok: true };
  }

  // Testläge. Flyttar en testperson genom resan utan att verklig tid går.
  // Finns bara när servern körs som prototyp. Aldrig för verkliga deltagare.
  function putTestStep(req, enrollmentId, body) {
    if (!cfg.prototype) throw new HttpError(404, "not_found");
    const user = requireUser(req);
    const enr = ownEnrollment(user, enrollmentId);
    // null rensar testläget. Då gäller gruppens verkliga steg igen.
    const step = body?.step ?? null;
    const def = step === null ? null : getStep(step);
    if (step !== null && (!def || def.aside)) throw new HttpError(400, "unknown_step");
    db.prepare("UPDATE lr_enrollment SET test_step = ? WHERE id = ?").run(step, enr.id);
    return journeyState({ ...enr, test_step: step });
  }

  // Jan som handledare ser endast det som en deltagare aktivt har delat.
  function facilitatorShared(req) {
    const user = requireUser(req);
    const cohorts = facilitatorCohorts(user);
    if (!cohorts.length) throw new HttpError(403, "forbidden");
    return {
      cohorts: cohorts.map((cohortId) => {
        const cohort = db.prepare("SELECT id, name, start_date, current_step FROM lr_cohort WHERE id = ?").get(cohortId);
        const participants = db
          .prepare(
            `SELECT e.id, u.display_name FROM lr_enrollment e JOIN lr_user u ON u.id = e.user_id
             WHERE e.cohort_id = ? AND e.status IN ('active', 'paused') ORDER BY u.display_name`,
          )
          .all(cohortId)
          .map((p) => {
            const shares = db
              .prepare(
                "SELECT step_key, section_key, created_at FROM lr_share WHERE enrollment_id = ? AND kind = 'share_with_facilitator' AND revoked_at IS NULL",
              )
              .all(p.id);
            return {
              name: p.display_name,
              shared: shares.map((s) => {
                const section = getSection(s.step_key, s.section_key);
                return {
                  step: s.step_key,
                  section: s.section_key,
                  title: section.title,
                  since: s.created_at,
                  fields: section.fields.map((f) => ({
                    label: f.label,
                    value: q.entry.get(p.id, s.step_key, `${section.key}.${f.key}`)?.value || "",
                  })),
                };
              }),
            };
          });
        return { id: cohort.id, name: cohort.name, startDate: cohort.start_date, participants };
      }),
    };
  }

  // Programadministration. Grupper, datum, länkar, status. Aldrig fritext.
  function adminOverview(req) {
    const user = requireUser(req);
    if (!isProgramAdmin(user)) throw new HttpError(403, "forbidden");
    const cohorts = db.prepare("SELECT * FROM lr_cohort ORDER BY start_date").all();
    return {
      cohorts: cohorts.map((c) => ({
        id: c.id,
        name: c.name,
        startDate: c.start_date,
        endDate: c.end_date,
        currentStep: c.current_step,
        status: c.status,
        maxParticipants: c.max_participants,
        liveSessions: q.liveSessions.all(c.id).map(liveSessionOut),
        participants: db
          .prepare(
            `SELECT e.id, e.status, e.last_activity_at, u.display_name, u.email FROM lr_enrollment e
             JOIN lr_user u ON u.id = e.user_id WHERE e.cohort_id = ? ORDER BY u.display_name`,
          )
          .all(c.id)
          .map((p) => ({
            name: p.display_name,
            email: p.email,
            status: p.status,
            lastActivityAt: p.last_activity_at,
            startedSteps: db
              .prepare("SELECT DISTINCT step_key FROM lr_event WHERE enrollment_id = ? AND event_name = 'week_started'")
              .all(p.id)
              .map((r) => r.step_key),
          })),
      })),
    };
  }

  function adminUpdateLiveSession(req, sessionId, body) {
    const user = requireUser(req);
    if (!isProgramAdmin(user)) throw new HttpError(403, "forbidden");
    const session = db.prepare("SELECT * FROM lr_live_session WHERE id = ?").get(String(sessionId));
    if (!session) throw new HttpError(404, "not_found");
    const next = { ...session };
    if (body.teamsUrl !== undefined) {
      if (typeof body.teamsUrl !== "string" || (body.teamsUrl && !/^https:\/\/[^\s]+$/.test(body.teamsUrl))) {
        throw new HttpError(400, "invalid_url");
      }
      next.teams_url = body.teamsUrl;
    }
    if (body.startsAt !== undefined) {
      if (Number.isNaN(Date.parse(body.startsAt))) throw new HttpError(400, "invalid_time");
      next.starts_at = new Date(body.startsAt).toISOString();
    }
    if (body.preparation !== undefined) {
      if (typeof body.preparation !== "string" || body.preparation.length > 1000) throw new HttpError(400, "invalid_text");
      next.preparation = body.preparation;
    }
    tx(db, () => {
      db.prepare("UPDATE lr_live_session SET teams_url = ?, starts_at = ?, preparation = ? WHERE id = ?").run(
        next.teams_url,
        next.starts_at,
        next.preparation,
        session.id,
      );
      db.prepare("INSERT INTO lr_admin_audit (actor_user_id, action, target, created_at) VALUES (?, ?, ?, ?)").run(
        user.id,
        "live_session.update",
        session.id,
        nowIso(),
      );
    });
    return liveSessionOut(next);
  }

  function login(req, res, url) {
    if (cfg.identityMode !== "prototype-link") return redirect(res, "/");
    const token = url.searchParams.get("t") || "";
    const row = db
      .prepare("SELECT * FROM lr_prototype_login WHERE token_hash = ? AND revoked_at IS NULL AND expires_at > ?")
      .get(hashToken(token), nowIso());
    if (!row) return redirect(res, "/#/inloggning-misslyckades");
    const sessionToken = randomBytes(32).toString("base64url");
    const now = cfg.now();
    const expires = new Date(now.getTime() + SESSION_DAYS * 86400000);
    db.prepare(
      "INSERT INTO lr_auth_session (token_hash, user_id, created_at, expires_at, last_seen_at) VALUES (?, ?, ?, ?, ?)",
    ).run(hashToken(sessionToken), row.user_id, now.toISOString(), expires.toISOString(), now.toISOString());
    res.setHeader("Set-Cookie", sessionCookie(sessionToken, SESSION_DAYS * 86400));
    return redirect(res, "/");
  }

  function logout(req, res) {
    const token = parseCookies(req.headers.cookie)[SESSION_COOKIE];
    if (token) db.prepare("DELETE FROM lr_auth_session WHERE token_hash = ?").run(hashToken(token));
    res.setHeader("Set-Cookie", sessionCookie("", 0));
    return { ok: true };
  }

  function sessionCookie(value, maxAge) {
    return `${SESSION_COOKIE}=${value}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${maxAge}${cfg.secureCookies ? "; Secure" : ""}`;
  }

  // ---------- Router ----------

  async function handle(req, res) {
    const url = new URL(req.url, "http://localhost");
    const path = url.pathname;
    try {
      if (path === "/login" && req.method === "GET") return login(req, res, url);
      if (path.startsWith("/api/")) {
        if (req.method !== "GET") assertJsonRequest(req);
        const body = req.method === "GET" ? null : await readJson(req);
        const out = await routeApi(req, res, path, url, body);
        return sendJson(res, 200, out);
      }
      return serveStatic(res, path);
    } catch (error) {
      if (error instanceof HttpError) return sendJson(res, error.status, { error: error.code, ...error.extra });
      if (String(error?.message).includes("lr_cohort_full")) return sendJson(res, 409, { error: "cohort_full" });
      console.error(error);
      return sendJson(res, 500, { error: "server_error" });
    }
  }

  function routeApi(req, res, path, url, body) {
    const m = (pattern) => path.match(pattern);
    let match;
    if (path === "/api/me" && req.method === "GET") return me(req);
    if (path === "/api/logout" && req.method === "POST") return logout(req, res);
    if (path === "/api/events" && req.method === "POST") return postEvent(req, body);
    if (path === "/api/facilitator/shared" && req.method === "GET") return facilitatorShared(req);
    if (path === "/api/admin/overview" && req.method === "GET") return adminOverview(req);
    if ((match = m(/^\/api\/admin\/live-sessions\/([\w-]+)$/)) && req.method === "PUT") {
      return adminUpdateLiveSession(req, match[1], body || {});
    }
    if ((match = m(/^\/api\/journey\/([\w-]+)$/)) && req.method === "GET") return getJourney(req, match[1]);
    if ((match = m(/^\/api\/journey\/([\w-]+)\/entry$/)) && req.method === "PUT") return putEntry(req, match[1], body);
    if ((match = m(/^\/api\/journey\/([\w-]+)\/assessment$/)) && req.method === "PUT") {
      return putAssessment(req, match[1], body);
    }
    if ((match = m(/^\/api\/journey\/([\w-]+)\/share$/)) && req.method === "PUT") return putShare(req, match[1], body);
    if ((match = m(/^\/api\/journey\/([\w-]+)\/test-step$/)) && req.method === "PUT") {
      return putTestStep(req, match[1], body);
    }
    if ((match = m(/^\/api\/journey\/([\w-]+)\/history$/)) && req.method === "GET") {
      return getHistory(req, match[1], url);
    }
    throw new HttpError(404, "not_found");
  }

  return { handle, config: cfg };
}

// ---------- Hjälpfunktioner ----------

function endOf(session) {
  return new Date(Date.parse(session.starts_at) + session.duration_minutes * 60000).toISOString();
}

function liveSessionOut(s) {
  return {
    id: s.id,
    step: s.step_key,
    startsAt: s.starts_at,
    durationMinutes: s.duration_minutes,
    teamsUrl: s.teams_url,
    preparation: s.preparation,
  };
}

function parseCookies(header = "") {
  const out = {};
  for (const part of String(header).split(";")) {
    const i = part.indexOf("=");
    if (i > 0) out[part.slice(0, i).trim()] = decodeURIComponent(part.slice(i + 1).trim());
  }
  return out;
}

// Skydd mot förfalskade anrop från andra webbplatser: skrivande anrop måste
// vara JSON och bära en egen header som en vanlig formulärpost inte kan sätta.
function assertJsonRequest(req) {
  if (!String(req.headers["content-type"] || "").startsWith("application/json")) {
    throw new HttpError(415, "json_required");
  }
  if (req.headers["x-luf-academy"] !== "1") throw new HttpError(403, "missing_header");
}

function readJson(req) {
  return new Promise((resolve, reject) => {
    let size = 0;
    const chunks = [];
    req.on("data", (chunk) => {
      size += chunk.length;
      if (size > MAX_BODY_BYTES) {
        reject(new HttpError(413, "too_large"));
        req.destroy();
        return;
      }
      chunks.push(chunk);
    });
    req.on("end", () => {
      if (!chunks.length) return resolve({});
      try {
        const parsed = JSON.parse(Buffer.concat(chunks).toString("utf8"));
        resolve(parsed && typeof parsed === "object" && !Array.isArray(parsed) ? parsed : {});
      } catch {
        reject(new HttpError(400, "invalid_json"));
      }
    });
    req.on("error", reject);
  });
}

function sendJson(res, status, data) {
  if (res.headersSent) return;
  res.writeHead(status, {
    ...SECURITY_HEADERS,
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store",
  });
  res.end(JSON.stringify(data));
}

function redirect(res, location) {
  res.writeHead(302, { ...SECURITY_HEADERS, Location: location, "Cache-Control": "no-store" });
  res.end();
}

async function serveStatic(res, path) {
  const rel = path === "/" ? "index.html" : normalize(path).replace(/^([/\\])+/, "");
  if (rel.includes("..")) return sendJson(res, 404, { error: "not_found" });
  const file = join(PUBLIC_DIR, rel);
  try {
    const data = await readFile(file);
    res.writeHead(200, {
      ...SECURITY_HEADERS,
      "Content-Type": MIME[extname(file)] || "application/octet-stream",
      "Cache-Control": "no-cache",
    });
    res.end(data);
  } catch {
    const index = await readFile(join(PUBLIC_DIR, "index.html"));
    res.writeHead(200, { ...SECURITY_HEADERS, "Content-Type": MIME[".html"], "Cache-Control": "no-cache" });
    res.end(index);
  }
}

export { randomUUID };
