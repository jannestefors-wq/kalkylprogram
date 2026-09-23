# Datagränser, behörighet och GDPR

## Grundprincip

Privat som standard. En rad i `lr_share` är det enda som kan göra något synligt för någon annan än deltagaren. Utan en sådan rad finns ingen väg i systemet till deltagarens text.

## Vem ser vad

| Roll | Ser | Ser aldrig |
| --- | --- | --- |
| Deltagare | Sin egen resa. Sin grupps namn, datum, träffar och Teamslänk. | Andra deltagares resor. Andras delningar. |
| Handledare (Jan) | Grupper hen är tilldelad. Deltagarnas namn. **Endast** avsnitt som deltagaren aktivt delat med Jan, så länge delningen gäller. | Privata avsnitt. Markeringen "Ta med till nästa träff". Grupper hen inte är tilldelad. |
| Programadmin (t.ex. Fredde) | Grupper, datum, platser, Teamslänkar, deltagarnas namn, e-post, status, senaste aktivitet och vilka veckor som påbörjats. | Någon fritext. Någon självskattning. Något delat material. |
| Plattformsadmin | Samma som programadmin i gränssnittet. | Samma som programadmin. |
| Arbetsgivare eller sponsor | Ingenting. Rollen finns inte. | Allt. |

Deltagare är inte en roll. Det är en inskrivning i en grupp. Ingen roll i `lr_role_grant` ger läsrätt till fritext. Det finns inget API som lämnar ut en annan persons privata text.

Den som har teknisk åtkomst till databasen kan läsa allt. Den gränsen går inte att skriva bort i kod. Den kräver ett beslut om vem som har den åtkomsten och att sådan åtkomst loggas (se öppna frågor).

## Hur behörighet kontrolleras

- Varje anrop mot en resa slår upp inskrivningen med både `enrollment_id` och den inloggade användarens `user_id`. Stämmer inte ägaren blir svaret 404. Det går inte att pröva sig fram.
- Handledarens vy filtreras på `cohort_id` från rollen och på `kind = 'share_with_facilitator' AND revoked_at IS NULL`.
- Skrivande anrop kräver JSON och en egen header. En vanlig formulärpost från en annan webbplats kan inte skriva.
- Sessioner lagras som SHA256 av en slumpad token. Kakan är HttpOnly och SameSite=Lax, och Secure i drift.
- Gruppstorleken skyddas i databasen med en trigger. Den sjunde deltagaren kan inte skrivas in, oavsett vilken kod som försöker.

## Var data lagras

| Data | Tabell | Varför |
| --- | --- | --- |
| Namn, e-post | `lr_user` | Konto och tilltal. |
| Grupp, status | `lr_enrollment` | Rätt deltagare till rätt grupp. |
| Fritext | `lr_entry` | Deltagarens arbete. |
| Tidigare versioner | `lr_entry_history` | En version per skrivpass. En ny ögonblicksbild sparas när deltagaren kommer tillbaka efter mer än 30 minuter. Varje tangenttryckning sparas inte. |
| Självskattning | `lr_self_assessment` | Start, slut, 30 dagar. |
| Delning | `lr_share` | Vad som är delat, med vem, sedan när, och när det togs tillbaka. |
| Mätning | `lr_event` | Namngivna händelser. Inga texter. |
| Adminändringar | `lr_admin_audit` | Vem ändrade vilken träff och när. |

I webbläsaren lagras bara text som ännu inte bekräftats av servern, och bara tills den är sparad. Vid utloggning rensas den.

## Mätning

Tillåtna händelser: `week_started`, `section_completed`, `action_chosen`, `action_revisited`, `what_happened_completed`, `autosave_failed`, `client_error`, `session_ended`.

De flesta härleds på servern från vad som faktiskt hände. Klienten får bara rapportera fyra av dem och bara med nycklarna `name`, `enrollmentId`, `step` och `section`, där step och section måste finnas i innehållsregistret. Allt annat avvisas. Tabellen har en CHECK på händelsenamnet. Ingen tredjepartsanalys laddas.

Att en session avbryts utan utloggning mäts inte. Det kräver en tolkning av beteende som inte behövs för att förbättra utbildningen.

## Tredje person

Momentet "Människorna runt mig" ber om roll eller initial. Om deltagaren skriver något som ser ut som för- och efternamn visas en stilla fråga: "Räcker en roll eller initial?". Inget blockeras. Deltagaren bestämmer.

## Öppna frågor. Blockerande före riktiga deltagare

Dessa är inte beslutade i någon källa jag läst. De är inte gissade.

1. **Inloggning för deltagare.** Ska deltagare logga in med ChatGPT-kontot, som Sites erbjuder idag, eller behövs en annan identitetsleverantör? Påverkar tillgänglighet för deltagare utan ChatGPT.
2. **Rättslig grund** för att behandla reflektionstext. Avtal med deltagaren är det troliga, men beslut saknas.
3. **Lagringstid** per datatyp. KVALITET GDPR punkt 10 kräver beslut före lansering. Särskilt: hur länge efter 30-dagarsuppföljningen ligger resan kvar?
4. **Vad som händer när programmet avslutas.** Export till deltagaren, därefter radering? Eller behåller deltagaren tillgång?
5. **Export och radering.** Datamodellen stödjer det (`ON DELETE CASCADE` från inskrivningen), men varken flöde eller gränssnitt är byggt.
6. **Teknisk åtkomst till databasen.** Vem på LUF och vilka personuppgiftsbiträden (OpenAI Sites, Cloudflare) kan tekniskt läsa D1? Kräver personuppgiftsbiträdesavtal och beslut.
7. **Företagsbetalda platser.** Principen är klar och byggd: arbetsgivaren ser ingenting. Vad arbetsgivaren ska få veta, till exempel att en person har genomfört utbildningen, är inte beslutat.
8. **Integritetstext för deltagare.** Saknas.
9. **Google Analytics** måste undantas från deltagarsidorna vid en framtida integration i produktion.
