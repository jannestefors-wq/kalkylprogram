-- LUF Academy. Ledarskap med hjärta och mod, version 2. Order 019.
-- Tre månader. Då och nu. Endast additiv. Inga befintliga tabeller,
-- kolumner eller rader ändras.
--
-- Fritexten i tre månaders uppföljningen sparas i lr_entry med nya nycklar
-- under steget m3. Ingen schemaändring behövs för den.
--
-- Kartan efter tre månader. lr_self_assessment tillåter bara start, end och
-- d30 och ändras inte. Den nya mätpunkten får en egen tabell med samma form.
-- Självskattning. Privat. Kan aldrig delas.
CREATE TABLE lr_self_assessment_followup (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  enrollment_id TEXT NOT NULL REFERENCES lr_enrollment(id) ON DELETE CASCADE,
  measure_point TEXT NOT NULL CHECK (measure_point IN ('m3')),
  dimension TEXT NOT NULL CHECK (dimension IN ('narvaro', 'mod', 'lyssnande', 'tydlighet', 'relation', 'ansvar')),
  value INTEGER NOT NULL CHECK (value BETWEEN 1 AND 6),
  assessed_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE (enrollment_id, measure_point, dimension)
);
