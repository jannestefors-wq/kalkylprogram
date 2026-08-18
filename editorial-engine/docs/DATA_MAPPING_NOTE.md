# C. Data Mapping Note — Canonical Data Integration V1

Kalla: `canonical_data/source/LUF_Canonical_Data_Pack_V1.json` (maskinlasbar,
sanningskalla for denna integration) och
`canonical_data/source/LUF_Canonical_Data_Pack_V1_Report.md`
(gransknings-/provenanceunderlag). Bada filerna ligger orort bevarade for
sparbarhet. Mappningskoden star i `canonical_data/series_registry.py` och
`canonical_data/thesis_family_registry.py`.

## Series: pack -> `Series` (schema/series.py)

| Pack-falt | Schema V1.1-falt | Mappning |
|---|---|---|
| `series_id` | `series_id` | 1:1, verbatim (t.ex. `"series-dear-001"`) |
| `canonical_name` | `name` | 1:1, verbatim |
| `description` | `description` | 1:1, verbatim |
| `status` (`"canonical"` / `"strongly_supported"`) | `provenance.certainty` | Se "Statusmappningen" nedan -- INTE 1:1 falt-till-falt, men samma betydelse bevarad |
| `known_language` (lista) | `provenance.notes` (del av) | Series har inget eget sprakfalt (medvetet, se nedan). Renderas som `"Sprak: sv, en."` i notes. |
| `evidence` (lista) | `provenance.notes` (del av) | Renderas som `"Evidence: <e1> \| <e2> ..."` i notes. Inget tappas. |
| `notes` (lista) | `provenance.notes` (del av) | Renderas som `"Notes: <n1> \| <n2> ..."` i notes. Inget tappas. |
| *(saknas i pack)* | `role` (`SeriesRole`, obligatoriskt) | Se "Role-faltet" nedan. |
| *(saknas i pack)* | `created_at` | Satt till pack-datumet `2026-08-18` (fran pack:ens eget `source_basis`-falt). |
| *(saknas i pack)* | `active` | `True` for samtliga 16 -- ingen post ar markerad avvecklad. |
| *(saknas i pack)* | `provenance.created_by` | `Actor.HUMAN` -- se motivering i `docs/PROVENANCE_STRATEGY.md`-tillagget nedan. |
| *(saknas i pack)* | `provenance.method` | `"work_canonical_data_pack_v1"` -- identifierar kallan. |

### Statusmappningen (INGEN schemaandring)

Schema V1.1:s `Series`-modell hade fran V1 bara `active: bool` -- ingen
canonical/strongly_supported-distinktion pa serienivan (registret antogs
bara vaxa, inte behova en konfidensgrad per rad). Pack:ens `status`-falt
kraver dock exakt den distinktionen. Losningen: `Provenance.certainty`
(`EvidenceCertainty`) hade redan bade `VERIFIED` och `STRONGLY_SUPPORTED`
som varden (infort i Beslut 23, V1). Mappningen:

- pack `status: "canonical"` -> `Series.provenance.certainty = EvidenceCertainty.VERIFIED`
- pack `status: "strongly_supported"` -> `Series.provenance.certainty = EvidenceCertainty.STRONGLY_SUPPORTED`

Detta ar INTE en schemaandring -- inget nytt falt, ingen ny enum-medlem.
Det ar ett medvetet val att aterandvanda ett befintligt falt vars
betydelse redan tackte exakt detta behov. Se
`docs/TECHNICAL_PROPOSALS.md` TP-10.

### Role-faltet (`SeriesRole`, obligatoriskt pa `Series`)

`SeriesRole` ar en Schema V1.1-intern klassificerare (V1 TECHNICAL
PROPOSAL) -- pack:en har inget motsvarande falt. For att INTE gora ny
redaktionell analys (forbjudet, ordern avsnitt 12) tilldelas ett specifikt
`role`-varde ENDAST de tva serier dar rollen redan var uttryckligen
faststalld i tidigare godkant material:

- `series-dear-001` (Kara ...): `FORM_BEARING_PILLAR` -- fran ursprungliga
  V1-uppdragets eget Beslut 17-exempel, bekraftat av pack:ens egen
  beskrivning ("formen ar brevet/pelaren").
- `series-long-game-001` (Det langa spelet): `TIME_PERSPECTIVE` -- samma
  Beslut 17-exempel ("serie med tidsperspektiv"), bekraftat av pack:ens
  beskrivning ("Val over tid ...").

Ovriga 14 serier far `SeriesRole.OTHER` -- enumens egna neutrala
"ej vidare klassificerad"-varde, inte ett specifikt pastaende. Ingen ny
enum-medlem skapades.

## Thesis Family: pack -> `ThesisFamily` (schema/series.py)

| Pack-falt | Schema V1.1-falt | Mappning |
|---|---|---|
| `thesis_family_id` | `thesis_family_id` | 1:1, verbatim |
| `canonical_name` | `name` | 1:1, verbatim |
| `definition` | `core_statement` | 1:1, verbatim (kärntesens familje-nivaformulering) |
| `status` (samtliga `"strongly_supported"`) | `provenance.certainty` | Samma mappning som for Series: `STRONGLY_SUPPORTED` for alla atta. |
| `evidence` (lista) | `provenance.notes` (del av) | Renderas som `"Evidence: ..."`. |
| `notes` (lista) | `provenance.notes` (del av) | Renderas som `"Notes: ..."`. |
| `related_topics` (lista) | `description` | ThesisFamily har inget eget "relaterade amnen"-falt, och pack:en har ingen separat `description` for thesis families. Renderas som `"Relaterade teman: symptom, orsak, ..."` i det annars oanvanda `description`-faltet. Inget tappas -- ren omformatering. |
| *(saknas i pack)* | `example_phrasings` | Lamnas som tom lista `[]`. Pack:en gav inga exempelformuleringar; att hitta pa sadana hade varit ny redaktionell text, inte teknisk mappning. |

## Varfor ingen schemaandring krävdes (ordern avsnitt 16)

Bada de tva potentiellt schema-paverkande behoven (canonical/
strongly_supported-status per rad; bevara sprak/evidence/notes-listor)
loste sig genom att aterandvanda BEFINTLIGA falt (`Provenance.certainty`,
`Provenance.notes`, `ThesisFamily.description`) pa nya men konsekventa
satt. Ingen ny modellklass, inget nytt falt, ingen ny enum-medlem lades
till i `schema/*.py`. JSON Schema (`schema/json/*.schema.json`) andrades
darfor INTE av denna integration -- filerna ar identiska fore och efter,
verifierat via om-generering (se `docs/FINAL_REPORT_DATA_INTEGRATION_V1.md`
punkt M).

## Vad som INTE mappades in

- `pack_id`, `source_basis`, `data_quality`, `schema_mapping_note`
  (pack-metadata pa toppniva) -- inga motsvarande falt i Schema V1.1 pa
  entitetsniva; `data_quality: "medium"` dokumenteras separat, se
  `docs/VALIDATION_REPORT_DATA_INTEGRATION_V1.md`.
- `possible_duplicates` (tom lista, 0 dubbletter) -- inget att mappa.
- `classification_issues` (5 poster) -- dessa AR exakt de fem
  projektledarbesluten A-E; se `docs/CLASSIFICATION_DECISION_NOTE.md`
  istallet for en separat teknisk mappning.
- `missing_source_material` -- dokumenterat i
  `docs/VALIDATION_REPORT_DATA_INTEGRATION_V1.md`, inte i sjalva
  registerposterna (det ar metadata om HELA pack:en, inte om enskilda
  serier/tesfamiljer).
