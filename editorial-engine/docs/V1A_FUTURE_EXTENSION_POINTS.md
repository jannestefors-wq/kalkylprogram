# V1A Future Extension Points

Var framtida komponenter kan kopplas in senare, UTAN att bygga dem nu
(order sektion 32). Ingen av dessa punkter ar implementerade -- de ar
dokumenterade seams.

## 1. Riktig LLM-baserad `AnalysisProvider`
`engine/provider.py::AnalysisProvider` (Protocol) definierar exakt tva
metoder domanlogiken beror pa: `interpret()` och `propose_angle_seeds()`.
En framtida `LLMAnalysisProvider` skulle implementera samma Protocol och
kunna bytas in i `run_v1a_pipeline(..., provider=LLMAnalysisProvider(...))`
utan att `interpretation.py`, `classification.py`, `comparison.py`,
`angles.py` eller `recommendation.py` andras alls.

## 2. Battre retrieval an ord-overlappning
`engine/text_utils.py::normalize_words()` ar medvetet den enklast mojliga
losningen. En framtida embeddings-/vector-baserad `compare_to_existing_content()`
skulle kunna ersatta implementationen bakom SAMMA funktionssignatur --
`ClassificationResult`/`ComparisonResult`-formerna behover inte andras
forran den verkliga publikationshistoriken finns (se
`docs/V1A_MEMORY_LIMITATION.md`).

## 3. Variation Engine
Skulle konsumera `CandidateAngle` (och sarskilt dess `voice_alignment`
och `repetition_risk`) for att generera faktiska textvarianter -- helt
utanfor V1A:s scope. `CandidateAngle.angle` (en riktig `schema.Angle`) ar
redan formad for att bli input till nagot sadant senare.

## 4. Quality Gate
Skulle konsumera en framtida `ContentRecord` (byggd av en generator som
INTE finns i V1A) och anvanda `schema.QualityAssessment` -- redan en del
av Canonical Foundation V1, oanvand av V1A.

## 5. Skriva godkanda `Angle`/`Idea` till canonical lagring
Idag lever `CandidateAngle`/`Idea` bara i minnet under en pipeline-korning.
Ett framtida beslut kan lagga till en explicit "persist efter mansklig
approval"-mekanism -- men det kraver ett eget projektledarbeslut om VAR
(egen `canonical_data/`-liknande yta? en riktig databas?), inte nagot
V1A forutsatter eller bygger i forvag.

## 6. Generator (nasta fas, separat startorder)
`CandidateAngle` + `RecommendationResult` + `HumanDecision` ar exakt det
en framtida generator skulle behova som input -- men ingen sadan
komponent finns eller paborjas i V1A. Se
`docs/V1A_DOES_NOT_DO.md`.
