-- LUF Academy. Ledarskap med hjärta och mod, version 2. Order 014.
-- Endast additiv. Inga befintliga tabeller, kolumner eller rader ändras.
-- Befintliga svar under pensionerade fältnycklar ligger kvar i lr_entry.

-- Förfrågan om samtal med Jan. Skapas bara när deltagaren själv trycker
-- "Be om ett samtal". Innehåller ingen text och inget om varför.
-- Varken källan (rutan eller sidan) eller något svar sparas här.
CREATE TABLE lr_talk_request (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  enrollment_id TEXT NOT NULL REFERENCES lr_enrollment(id) ON DELETE CASCADE,
  created_at TEXT NOT NULL
);
CREATE INDEX lr_talk_request_enrollment ON lr_talk_request(enrollment_id);

-- Deltagarens eget svar på den privata vägledningen efter två Nej i rad.
-- Behövs bara för att rutan inte ska visas igen för samma följd.
-- Att rutan har visats sparas aldrig. Läses bara i deltagarens egen vy.
CREATE TABLE lr_support_prompt (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  enrollment_id TEXT NOT NULL REFERENCES lr_enrollment(id) ON DELETE CASCADE,
  streak_end_step TEXT NOT NULL,
  choice TEXT NOT NULL CHECK (choice IN ('not_now', 'requested')),
  created_at TEXT NOT NULL,
  UNIQUE (enrollment_id, streak_end_step)
);
