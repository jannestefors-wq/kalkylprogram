# V1A Purpose

LUF Editorial Engine V1A is the first vertical chain:

```
Raw Idea -> Interpretation -> Canonical Classification ->
Existing Content Comparison -> Candidate Angles -> Recommended Angle ->
Human Decision
```

**Vad V1A bevisar:** att motorn kan utova redaktionellt omdome INNAN den
borjar skriva. Konkret:

1. Att ett rått, oformaterat råmaterial kan tolkas utan att originalet
   forloras eller skrivs over (`engine/interpretation.py`).
2. Att en tolkning kan hallas isar i observation, tolkning och slutledning
   -- utan att nagot av det tvingas bli faststalld avsikt (Beslut 5).
3. Att en ide kan relateras till Canonical Foundation V1:s verkliga
   register (16 Series, 8 Thesis Families, Territory) genom transparent,
   granskningsbar logik -- inte en svart lada (`engine/classification.py`).
4. Att motorn kan jamfora en ide mot det som faktiskt finns tillgangligt,
   och uttryckligen erkanna nar minnet ar ofullstandigt
   (`engine/comparison.py`, se `docs/V1A_MEMORY_LIMITATION.md`).
5. Att motorn kan foresla ett litet antal (max 3) genuint distinkta
   redaktionella vinklar, motiverade och sparbara till evidens
   (`engine/angles.py`).
6. Att en rekommendation kan ges med en fullstandigt genomskinlig
   poangsattning -- eller UTEBLI nar inget kandidat racker till
   (`engine/recommendation.py`).
7. Att kedjan alltid slutar hos en manniska, och att en AI aldrig kan
   representeras som den manskliga beslutsfattaren
   (`engine/human_decision.py`, se `docs/V1A_HUMAN_AUTHORITY.md`).

**Malet ar INTE** att skriva ett LinkedIn-inlagg. Se
`docs/V1A_DOES_NOT_DO.md` for den fullstandiga avgransningen.

## Deterministiskt, inget API-behov

Hela kedjan koras med `engine.provider.RuleBasedAnalysisProvider` --
transparent, regelbaserad, nyckelordsbaserad logik utan LLM-anrop, natverk
eller API-nyckel. Se `engine/provider.py` for `AnalysisProvider`-interfacet
som gor detta utbytbart senare utan att domanlogiken andras.
