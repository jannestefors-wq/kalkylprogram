-- LUF Academy. Min ledarskapsresa. Prototyp 001.
--
-- Endast additiv. Varje tabell har prefixet lr_ och ingen befintlig
-- LUF-tabell (messages, reviews, silence_wall_entries, round_table_dilemmas,
-- site_settings, editorial_notes, content_cases, house_content) berörs.
-- SQLite-dialekt, kompatibel med Cloudflare D1.
--
-- Rollback: DROP av lr_-tabellerna i omvänd ordning, se docs/ROLLBACK.md.

CREATE TABLE lr_program (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'prototype' CHECK (status IN ('prototype', 'active', 'closed')),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- En grupp. Aldrig fler än sex deltagare.
CREATE TABLE lr_cohort (
  id TEXT PRIMARY KEY,
  program_id TEXT NOT NULL REFERENCES lr_program(id),
  name TEXT NOT NULL,
  start_date TEXT NOT NULL,
  end_date TEXT NOT NULL,
  current_step TEXT NOT NULL DEFAULT 'w1',
  max_participants INTEGER NOT NULL DEFAULT 6 CHECK (max_participants BETWEEN 1 AND 6),
  status TEXT NOT NULL DEFAULT 'planned' CHECK (status IN ('planned', 'running', 'completed', 'closed')),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE lr_live_session (
  id TEXT PRIMARY KEY,
  cohort_id TEXT NOT NULL REFERENCES lr_cohort(id),
  step_key TEXT NOT NULL,
  starts_at TEXT NOT NULL,
  duration_minutes INTEGER NOT NULL DEFAULT 90,
  teams_url TEXT NOT NULL DEFAULT '',
  preparation TEXT NOT NULL DEFAULT ''
);
CREATE INDEX lr_live_session_cohort ON lr_live_session(cohort_id, starts_at);

-- Identitet. E-post kommer från inloggningslagret. Inga lösenord lagras.
CREATE TABLE lr_user (
  id TEXT PRIMARY KEY,
  email TEXT NOT NULL UNIQUE COLLATE NOCASE,
  display_name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'paused', 'closed')),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Arbetsroller. Deltagare är inte en roll här utan en inskrivning.
-- Ingen roll ger läsrätt till privat fritext.
CREATE TABLE lr_role_grant (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL REFERENCES lr_user(id),
  role TEXT NOT NULL CHECK (role IN ('platform_admin', 'program_admin', 'facilitator')),
  cohort_id TEXT REFERENCES lr_cohort(id),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (user_id, role, cohort_id)
);

CREATE TABLE lr_enrollment (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES lr_user(id),
  cohort_id TEXT NOT NULL REFERENCES lr_cohort(id),
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'paused', 'withdrawn', 'completed')),
  enrolled_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_activity_at TEXT,
  UNIQUE (user_id, cohort_id)
);

CREATE TRIGGER lr_enrollment_capacity_insert
BEFORE INSERT ON lr_enrollment
WHEN NEW.status IN ('active', 'paused')
  AND (SELECT COUNT(*) FROM lr_enrollment WHERE cohort_id = NEW.cohort_id AND status IN ('active', 'paused'))
      >= (SELECT max_participants FROM lr_cohort WHERE id = NEW.cohort_id)
BEGIN
  SELECT RAISE(ABORT, 'lr_cohort_full');
END;

CREATE TRIGGER lr_enrollment_capacity_update
BEFORE UPDATE OF status ON lr_enrollment
WHEN NEW.status IN ('active', 'paused') AND OLD.status NOT IN ('active', 'paused')
  AND (SELECT COUNT(*) FROM lr_enrollment WHERE cohort_id = NEW.cohort_id AND status IN ('active', 'paused'))
      >= (SELECT max_participants FROM lr_cohort WHERE id = NEW.cohort_id)
BEGIN
  SELECT RAISE(ABORT, 'lr_cohort_full');
END;

-- Deltagarens egen text. En rad per fält. Aktuellt värde.
CREATE TABLE lr_entry (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  enrollment_id TEXT NOT NULL REFERENCES lr_enrollment(id) ON DELETE CASCADE,
  step_key TEXT NOT NULL,
  field_key TEXT NOT NULL,
  value TEXT NOT NULL DEFAULT '',
  revision INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE (enrollment_id, step_key, field_key)
);

-- Tidigare versioner. En ögonblicksbild per skrivpass, så att
-- utvecklingen går att följa utan att varje tangenttryckning sparas.
CREATE TABLE lr_entry_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  entry_id INTEGER NOT NULL REFERENCES lr_entry(id) ON DELETE CASCADE,
  value TEXT NOT NULL,
  written_from TEXT NOT NULL,
  written_until TEXT NOT NULL
);
CREATE INDEX lr_entry_history_entry ON lr_entry_history(entry_id);

-- Självskattning. Start, slut och 30 dagar. Aldrig ett test eller en diagnos.
CREATE TABLE lr_self_assessment (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  enrollment_id TEXT NOT NULL REFERENCES lr_enrollment(id) ON DELETE CASCADE,
  measure_point TEXT NOT NULL CHECK (measure_point IN ('start', 'end', 'd30')),
  dimension TEXT NOT NULL CHECK (dimension IN ('narvaro', 'mod', 'lyssnande', 'tydlighet', 'relation', 'ansvar')),
  value INTEGER NOT NULL CHECK (value BETWEEN 1 AND 6),
  assessed_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE (enrollment_id, measure_point, dimension)
);

-- Aktiv delning. Finns ingen rad är innehållet privat.
-- share_with_facilitator: Jan kan läsa just det avsnittet.
-- bring_to_session: deltagarens egen markering. Delar ingenting.
CREATE TABLE lr_share (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  enrollment_id TEXT NOT NULL REFERENCES lr_enrollment(id) ON DELETE CASCADE,
  step_key TEXT NOT NULL,
  section_key TEXT NOT NULL,
  kind TEXT NOT NULL CHECK (kind IN ('share_with_facilitator', 'bring_to_session')),
  created_at TEXT NOT NULL,
  revoked_at TEXT
);
CREATE UNIQUE INDEX lr_share_active ON lr_share(enrollment_id, step_key, section_key, kind) WHERE revoked_at IS NULL;

-- Individuella samtal. Inget hårdkodat antal.
CREATE TABLE lr_one_on_one (
  id TEXT PRIMARY KEY,
  enrollment_id TEXT NOT NULL REFERENCES lr_enrollment(id) ON DELETE CASCADE,
  facilitator_user_id TEXT NOT NULL REFERENCES lr_user(id),
  scheduled_at TEXT,
  status TEXT NOT NULL DEFAULT 'proposed' CHECK (status IN ('proposed', 'booked', 'done', 'cancelled')),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE lr_auth_session (
  token_hash TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES lr_user(id),
  created_at TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  last_seen_at TEXT NOT NULL
);

-- Endast prototyp. Personliga inloggningslänkar för testanvändare.
-- Ersätts av Sites-identiteten i produktion.
CREATE TABLE lr_prototype_login (
  token_hash TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES lr_user(id),
  created_at TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  revoked_at TEXT
);

-- Produktmätning. Endast namngivna händelser och kända nycklar. Aldrig fritext.
CREATE TABLE lr_event (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  enrollment_id TEXT,
  event_name TEXT NOT NULL CHECK (event_name IN (
    'week_started', 'section_completed', 'action_chosen', 'action_revisited',
    'what_happened_completed', 'autosave_failed', 'client_error', 'session_ended'
  )),
  step_key TEXT,
  section_key TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE lr_admin_audit (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  actor_user_id TEXT NOT NULL,
  action TEXT NOT NULL,
  target TEXT NOT NULL,
  created_at TEXT NOT NULL
);
