-- Separat migreringskatalog. V2:s automatiska migrerare läser aldrig denna.
-- Endast v3-tabeller. Körs enbart mot en märkt syntetisk Human Test-databas.
CREATE TABLE IF NOT EXISTS lr_v3_meta (id TEXT PRIMARY KEY CHECK(id = 'lmhm-v3-024-synthetic'));
CREATE TABLE IF NOT EXISTS lr_v3_state (
  user_id TEXT PRIMARY KEY,
  revision INTEGER NOT NULL DEFAULT 0 CHECK(revision >= 0),
  value TEXT NOT NULL CHECK(json_valid(value)),
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS lr_v3_history (
  user_id TEXT NOT NULL,
  revision INTEGER NOT NULL,
  value TEXT NOT NULL CHECK(json_valid(value)),
  created_at TEXT NOT NULL,
  PRIMARY KEY(user_id, revision)
);
-- Rollback: DROP TABLE lr_v3_history; DROP TABLE lr_v3_state; DROP TABLE lr_v3_meta;
-- Ingen v2-tabell läses, ändras eller raderas av denna migrering.
