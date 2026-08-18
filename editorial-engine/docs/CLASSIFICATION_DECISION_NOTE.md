# D. Classification Decision Note — Canonical Data Integration V1

De fem tidigare oppna klassificeringsfragorna (Work-rapportens "Classification
Review Required", 5 poster) ar avgjorda av projektledningen i denna order,
avsnitt 4. Ingen av dem krävde en ny enum eller ett nytt schema-falt; alla fem
ar representerade med befintliga medel. Kallfil for implementationen:
`canonical_data/series_registry.py` (`_CLASSIFICATION_DECISIONS`-tabellen).

## A. Kära …

**Beslut:** SERIES, status `canonical`.
**Teknisk representation:** `series-dear-001.provenance.certainty =
EvidenceCertainty.VERIFIED` (mappningen "canonical" -> `VERIFIED`, se
`docs/DATA_MAPPING_NOTE.md`). Beslutets motivering ("formbärande pelare som
kan bära flera ämnen, hindrar inte att den samtidigt är ett etablerat
seriespår") citeras verbatim i `provenance.notes`.
**Ingen ny enum-medlem krävdes.**

## B. Välkommen till tvärtomvärlden

**Beslut:** SERIES, status `canonical`.
**Teknisk representation:** `series-upside-down-world-001.provenance.certainty
= EvidenceCertainty.VERIFIED`. Beslutets motivering citeras verbatim i
`provenance.notes`.
**Ingen ny enum-medlem krävdes.**

## C. Om du bara fick välja en sak …

**Beslut:** SERIES, status `strongly_supported`. Ingen uppgradering till canonical.
**Teknisk representation:** `series-one-thing-001.provenance.certainty =
EvidenceCertainty.STRONGLY_SUPPORTED` (oförändrat från pack:ens egen
status). Beslutets motivering citeras verbatim i `provenance.notes`.
**Ingen ny enum-medlem krävdes.**

## D. Ubuntu. det mänskliga

**Beslut:** Behåll i Series Registry V1. Klassificera som SERIES CANDIDATE,
status `strongly_supported`.
**Teknisk representation:** Schema V1.1 har inget separat tekniskt fält för
"SERIES CANDIDATE" (bekräftat -- `Series` har bara `role: SeriesRole`, som
inte har ett sådant candidate-koncept, och ett nytt fält skapades
uttryckligen INTE, per ordern: "Om Schema V1.1 inte har ett separat
tekniskt fält för SERIES CANDIDATE ska du inte ändra schemat automatiskt").
Klassificeringen bevaras istället i `series-ubuntu-human-001.provenance.notes`
som den exakta strängen `"SERIES CANDIDATE"` inbäddad i beslutstexten, sökbar
och verifierad av
`tests/test_canonical_data_integration.py::test_decision_d_ubuntu_is_strongly_supported_and_documented_as_series_candidate`.
Status: `provenance.certainty = EvidenceCertainty.STRONGLY_SUPPORTED`.
**Flaggning:** ingen schemaändring krävdes eller gjordes.

## E. Gör det enkelt att välja dig / Make It Easy To Choose You

**Beslut:** Behåll i Series Registry V1. Klassificering: SERIES / EDITORIAL
TRACK, status `strongly_supported`. Ingen uppgradering till canonical.
**Teknisk representation:** Samma mönster som D -- Schema V1.1 har inget
separat "EDITORIAL TRACK"-fält, och ingen ny enum skapades. Klassificeringen
bevaras i `series-easy-to-choose-001.provenance.notes` som strängen
`"SERIES / EDITORIAL TRACK"`, verifierad av
`tests/test_canonical_data_integration.py::test_decision_e_easy_to_choose_you_is_strongly_supported_and_documented_as_editorial_track`.
Status: `provenance.certainty = EvidenceCertainty.STRONGLY_SUPPORTED`.
**Flaggning:** ingen schemaändring krävdes eller gjordes.

## Sammanfattning

| Beslut | Serie | Status i Schema V1.1 | Extra klassificering i notes | Ny enum? |
|---|---|---|---|---|
| A | Kära … | VERIFIED (=canonical) | — | Nej |
| B | Välkommen till tvärtomvärlden | VERIFIED (=canonical) | — | Nej |
| C | Om du bara fick välja en sak … | STRONGLY_SUPPORTED | — | Nej |
| D | Ubuntu. det mänskliga | STRONGLY_SUPPORTED | "SERIES CANDIDATE" | Nej |
| E | Gör det enkelt att välja dig / Make It Easy To Choose You | STRONGLY_SUPPORTED | "SERIES / EDITORIAL TRACK" | Nej |

Samtliga fem beslut är verifierade av dedikerade tester i
`tests/test_canonical_data_integration.py` (se `docs/FINAL_REPORT_DATA_INTEGRATION_V1.md`
punkt J för testresultat).
