# E. Validation Report — Canonical Data Integration V1

Korning: `cd editorial-engine && python3 -m pytest -q` (fran repo-roten,
`PYTHONPATH` satt av `pytest.ini`).

## Resultat

**60 passed, 0 failed** (37 tester fran V1/V1.1 + 23 nya for Canonical Data
Integration V1). Se `tests/test_canonical_data_integration.py`.

## Krav fran ordern avsnitt 14, med resultat

| Krav | Resultat | Verifierat av |
|---|---|---|
| Exakt 16 Series/Tracks | **JA** | `test_series_registry_contains_exactly_16` |
| Exakt 8 Thesis Families | **JA** | `test_thesis_family_registry_contains_exactly_8` |
| Alla ID:n unika | **JA** | `test_series_ids_are_unique`, `test_thesis_family_ids_are_unique`, `test_series_and_thesis_family_id_namespaces_do_not_collide` |
| Alla poster validerar mot Schema V1.1 | **JA** | Konstruktionen sjalv (Pydantic) + explicit JSON-rundtur i `test_all_24_records_validate_against_schema_v1_1` |
| Statusvarden ar giltiga | **JA** | Alla `provenance.certainty`-varden ar `EvidenceCertainty.VERIFIED`/`STRONGLY_SUPPORTED`, inga andra forekommer (se `test_no_series_was_upgraded_to_canonical_beyond_the_pack`) |
| Provenance kan lasas | **JA** | Varje post har en fullstandig `Provenance` med `certainty`, `method`, `notes` (evidence/notes/sprak konsoliderat), `created_by=HUMAN` |
| Sprakfalt validerar | **JA** (indirekt) | `known_language` bevarat i `provenance.notes` som `"Sprak: ..."`; testat i `test_series_provenance_preserves_language_and_evidence_information` for bade enkel- och flersprakiga poster (t.ex. Ubuntu: "sv, en") |
| Inga Series-placeholderposter kvar som canonical | **JA** | `test_no_series_placeholder_ids_remain`, `test_fixture_dataset_no_longer_carries_placeholder_series_or_thesis_names` |
| Inga ThesisFamily-placeholderposter kvar som canonical | **JA** | `test_no_thesis_family_placeholder_ids_remain` |
| Alla fem projektledarbeslut korrekt representerade | **JA** | `test_decision_a_...` t.o.m. `test_decision_e_...` (5 dedikerade tester), se ocksa `docs/CLASSIFICATION_DECISION_NOTE.md` |
| Samtliga atta Thesis Families ar strongly_supported | **JA** | `test_all_eight_thesis_families_are_strongly_supported` |

## Relationsintegritet

`schema.integrity.check_relations()` korde bade over hela fixture-datasetet
(som nu innehaller den riktiga 16+8-registret plus test-illustrationerna)
och over registret ENSAMT (utan fixture-data). Bada gav **0 violations**.

## Reproducerbarhet

- Registerladdningen (`load_series_registry()` / `load_thesis_family_registry()`)
  ar deterministisk: tva korningar fran samma kallfil ger identisk data
  (`test_registry_loading_is_reproducible`).
- JSON Schema-generering: `schema/json/*.schema.json` ar BYTE-IDENTISKA
  fore och efter denna integration (md5-jamforelse pa alla 17 filer). Detta
  bekraftar konkret att ingen schemaandring skedde -- se ordern avsnitt 16
  och `docs/DATA_MAPPING_NOTE.md`.

## Data quality (ordern avsnitt 10)

`data_quality: "medium"` fran pack:ens metadata (`pack_id`,
`source_basis`, `data_quality`-falt i
`canonical_data/source/LUF_Canonical_Data_Pack_V1.json`) dokumenteras har,
inte pa enskilda registerposter (det ar en egenskap hos hela pack:en, inte
hos en enskild serie/tesfamilj). Innebord, oforandrad fran pack-rapporten:

Godkanda poster ar INTE opalitliga -- MEDEL syftar pa att datasetet annu
inte ar en komplett karta over allt publicerat LUF-material. Saknat
underlag, oforsokt lost av detta uppdrag (per uttrycklig instruktion,
ordern avsnitt 10):

- Komplett export av publicerade LinkedIn-inlagg med datum, sprak, marknad
  och fulltext.
- Saker status for publicerat, utkast, vilande och avvecklat.
- Komplett engelskt innehallscorpus.

## Possible duplicates

**0** (fran pack:ens egen `possible_duplicates: []`). Ingen sammanslagning
gjordes eller behovdes. "Alla vet. Ingen sager det." och "Det tysta priset"
forblir tva separata serier, exakt som Work:s rapport motiverar (social
mekanik respektive konsekvens).
