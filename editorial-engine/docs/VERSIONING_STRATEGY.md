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

## 2. Voice Core — `voice_core_version_ref`

Voice Core andras av redaktionella skal, inte for att datamodellen andras.
Varje `VoicePrinciple` bar sin egen `version` + `valid_from`
(Beslut 11). `ContentRecord` och `QualityAssessment` stamplar dessutom
`voice_core_version_ref` — en fri etikett som `"voice-core-1.0"` — sa att
vi alltid kan svara *"den har texten bedomdes mot Voice Core 1.0"*, aven
efter att enskilda principer redigerats eller lagts till senare.

Detta ar en **etikettkonvention**, inte en ny kanonisk entitet med egen
tabell. En separat `VoiceCoreSnapshot`-entitet overvagdes och avvisades for
V1 (se `docs/OPEN_QUESTIONS.md` OQ-1) eftersom den hade blivit en andra
sanningskalla for exakt samma information som redan finns i
`VoicePrinciple.version` — precis den typ av divergensrisk Beslut 27
varnar for.

## 3. Register som bara vaxer — ingen global version

`Series`, `ThesisFamily`, `ReaderEffect`, `RepetitionSignal`,
`StyleAttribute` versioneras INTE som en mangd. Varje rad bar sin egen
`created_at` + `active` (och `superseded_by` dar det ar relevant for
`VoicePrinciple`). Att en ny series lagts till ar inte en brytande
andring; bara en andring av en befintlig rads BETYDELSE ar det, och det
flaggas i `docs/OPEN_QUESTIONS.md`, inte genom att hoja en global siffra.

## Tumregel

> Versionera KONTRAKTET (schema) och den REDAKTIONELLA SANNINGEN (voice
> core) explicit, eftersom bada ar saker en gammal post maste kunna
> kontrolleras mot senare. Versionera inte saker som bara vaxer.
