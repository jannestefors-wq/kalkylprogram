# Rollback

## Prototypen som den ligger nu

Prototypen är en egen mapp på en egen branch. Den körs inte någonstans automatiskt. LUF-produktionen, Sites-projektet och kalkylprogrammets Render-tjänst berörs inte.

- Ta bort prototypen helt: radera branchen `claude/ledarskap-vecka-1-prototype-7sy98p`, eller ta bort mappen `luf-academy-prototype/`.
- Nollställ testdata: `npm run seed`. Raderar `data/prototype.db` och skapar nya testkonton och nya länkar.
- Stäng en inloggningslänk: sätt `revoked_at` i `lr_prototype_login`, eller kör `npm run seed` igen.

## Om schemat senare körs mot D1

Migrationen är enbart tillägg. Den skapar tabeller med prefixet `lr_` och rör inga befintliga tabeller. Den tas bort i omvänd ordning:

```sql
DROP TABLE IF EXISTS lr_admin_audit;
DROP TABLE IF EXISTS lr_event;
DROP TABLE IF EXISTS lr_prototype_login;
DROP TABLE IF EXISTS lr_auth_session;
DROP TABLE IF EXISTS lr_one_on_one;
DROP TABLE IF EXISTS lr_share;
DROP TABLE IF EXISTS lr_self_assessment;
DROP TABLE IF EXISTS lr_entry_history;
DROP TABLE IF EXISTS lr_entry;
DROP TRIGGER IF EXISTS lr_enrollment_capacity_update;
DROP TRIGGER IF EXISTS lr_enrollment_capacity_insert;
DROP TABLE IF EXISTS lr_enrollment;
DROP TABLE IF EXISTS lr_role_grant;
DROP TABLE IF EXISTS lr_user;
DROP TABLE IF EXISTS lr_live_session;
DROP TABLE IF EXISTS lr_cohort;
DROP TABLE IF EXISTS lr_program;
DROP TABLE IF EXISTS lr_migration;
```

Det raderar deltagardata. Gör det aldrig mot riktiga deltagare utan export först och ett separat beslut.
