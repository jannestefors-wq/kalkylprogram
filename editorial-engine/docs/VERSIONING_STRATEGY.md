# E. Versioning Strategy (Beslut 22)

Kallfil: `schema/versioning.py` (fullstandig motivering finns i dess
docstring; detta ar sammanfattningen).

Tre saker versioneras separat, eftersom de andras av olika skal och pa
olika tidslinjer:

## 1. Schemat sjalvt — `SCHEMA_VERSION`

En enda semver-strang (`schema/__init__.py`, just nu `"1.0.0"`). Varje
kanoniskt toppobjekt har ett `schema_version`-falt som stamplas vid
skapandet. Svar pa: *"vilket kontrakt skapades/tolkades den har posten
under?"* — aven efter att schemat har gatt vidare.

Nar hojs den?
- **PATCH** (`1.0.x`): dokumentationsandring, ny valfri metadata som inte
  paverkar befintliga falt.
- **MINOR** (`1.x.0`): nytt valfritt falt, ny enum-medlem, ny valfri entitet.
- **MAJOR** (`x.0.0`): ett befintligt falts betydelse andras, ett falt tas
  bort, eller en relation mellan objekt andras pa ett satt som gor gamla
  poster otolkbara utan migrering.

## 2. Voice Core — `VoiceCoreSnapshot` (V1.1, OQ-1 -- ersatter den tidigare fria etiketten)

Voice Core andras av redaktionella skal, inte for att datamodellen andras.
Varje `VoicePrinciple` bar sin egen `version` + `valid_from` (Beslut 11).

**V1.1-beslut:** en fri etikett-strang visade sig otillrackligt langsiktigt
— vi maste kunna svara inte bara *"vilken version"* utan *"exakt vilka
principer"*. `ContentRecord` och `QualityAssessment` stamplar darfor nu
`voice_core_snapshot_id`, en riktig FK mot `VoiceCoreSnapshot.snapshot_id`
(`schema/voice.py`). En `VoiceCoreSnapshot` bar `version` (t.ex. `"1.0"`),
`created_at`, och `voice_principle_ids` — REFERENSER till existerande
`VoicePrinciple`-rader, inte kopior av deras text (se TP-9). Detta later
oss svara bade:

> "Vilken Voice Core-version anvandes vid analysen av detta content?"
(`ContentRecord.voice_core_snapshot_id -> VoiceCoreSnapshot.version`)

> "Vilka exakta principer ingick i den versionen?"
(`VoiceCoreSnapshot.voice_principle_ids -> VoicePrinciple` for var och en)

utan att skapa en andra sanningskalla for principernas text — bara for
VILKA av dem som var i kraft vid ett givet tillfalle, vilket ar
information `VoicePrinciple` sjalv inte bar (en princip vet inte vilka
andra principer den var gruppmedlem med).

Livscykel: `VoiceCoreSnapshot` aterandvander samma `active` +
`superseded_by`-monster som `VoicePrinciple` redan har, ingen ny
statusenum (se TP-8).

## 3. Register som bara vaxer — ingen global version

`Series`, `Territory`, `ThesisFamily`, `ReaderEffect`, `RepetitionSignal`,
`StyleAttribute` versioneras INTE som en mangd. Varje rad bar sin egen
`created_at` + `active` (och `superseded_by` dar det ar relevant for
`VoicePrinciple` och `VoiceCoreSnapshot`). Att en ny series eller ett nytt
territory lagts till ar inte en brytande andring; bara en andring av en
befintlig rads BETYDELSE ar det, och det flaggas i
`docs/OPEN_QUESTIONS.md`, inte genom att hoja en global siffra.

## Tumregel

> Versionera KONTRAKTET (schema) och den REDAKTIONELLA SANNINGEN (voice
> core) explicit, eftersom bada ar saker en gammal post maste kunna
> kontrolleras mot senare. Versionera inte saker som bara vaxer.
