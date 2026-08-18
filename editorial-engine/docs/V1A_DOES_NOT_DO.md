# V1A Does Not Do

Uttryckligen utanfor V1A:s avgransning (order sektionerna 25-27, 33).
Verifierat strukturellt av `tests/test_v1a_canonical_boundary.py`, inte
bara pastatt i prosa.

## Ingen generator
V1A producerar ALDRIG:
- LinkedIn-inlagg, artikel, caption
- slutlig hook, CTA, signatur
- svensk eller engelsk publiceringstext

`CandidateAngle` (engine/models.py) har inget `final_text`-, `caption`-
eller `cta_text`-falt. Ingen `ContentRecord` konstrueras nagonstans i
`engine/*.py` -- verifierat av
`tests/test_v1a_canonical_boundary.py::test_18_no_content_record_is_ever_constructed_by_the_pipeline`.

## Ingen UI
Ingen adminpanel, dashboard, hemsiderum, Work-interface, formular eller
React-komponent byggd.

## Ingen hemsideintegration
`huset`, `Adam`, `physical-house.tsx`, navigation, Akademin, Runda bordet,
PR-rummet, SEO, sitemap, robots -- allt orort. All V1A-kod ligger under
`editorial-engine/engine/`.

## Inget RAG / inga embeddings
`engine/classification.py` och `engine/comparison.py` anvander enkel,
transparent ord-overlappning (`engine/text_utils.py`) -- ingen vector
database, inget embeddings-pipeline, inget semantiskt index, inget externt
soktjanst.

## Ingen stor scoringmodell
`engine/recommendation.py` anvander en liten, namngiven poangsumma
(`AngleScore.breakdown`) -- inte inlard viktning, inte en likhetsmodell en
manniska inte kan granska for hand.

## Ingen automatisk loop
`engine/human_decision.py` bygger exakt ETT `HumanDecision` per anrop och
anropar aldrig pipeline igen pa egen hand. Ett nytt analyssteg kraver ett
nytt, explicit anrop fran den kod som ager kedjan.

## Ingen andring av Canonical Foundation V1
V1A skapar aldrig en ny Series, ny Thesis Family, nytt Territory, ny
Voice Principle eller ny Reader Effect. Se
`docs/V1A_CANONICAL_BOUNDARY.md`.

## Ingen databas, inget API
Hela V1A ar ren domanlogik, korbar via tester eller en liten intern
runner (`engine/pipeline.py`). Ingen server, ingen extern lagring.
