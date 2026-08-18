# V1A Memory Limitation

Canonical Foundation V1 ar INTE en fullstandig karta over allt publicerat
LUF-material (dokumenterat sedan Canonical Data Integration V1: `data_quality
= medium`, se `docs/VALIDATION_REPORT_DATA_INTEGRATION_V1.md`). Saknat
underlag inkluderar fortfarande en komplett export av publicerade
LinkedIn-inlagg, saker publiceringsstatus, och ett komplett engelskt
corpus.

## Regeln (order sektion 10)

> Avsaknad av evidens ar inte evidens for avsaknad.

`engine/comparison.py::compare_to_existing_content()` jamfor ENDAST mot
den `ContentRecord`-lista som faktiskt skickas in som `existing_content`
-- inte mot nagon fullstandig historik, for en sadan finns inte annu.

Nar inget matchar returneras `ComparisonOutcome.NO_MATCH_IN_AVAILABLE_MEMORY`,
ALDRIG "vi har aldrig publicerat detta". Varje `ComparisonResult` bar
dessutom ett fast, oforanderligt varningsmeddelande
(`NEVER_PUBLISHED_CLAIM_FORBIDDEN_NOTE`, engine/models.py) som reser med
resultatet -- inte bara star i denna dokumentation:

```
"Absence of a match in available canonical memory is not evidence the idea
was never published -- Canonical Foundation V1 is not a complete
publication history."
```

`ComparisonResult.corpus_size` rapporterar dessutom explicit HUR MANGA
poster som faktiskt jamfordes -- sa att omfattningen av pastaendet alltid
ar synlig (en jamforelse mot 0 poster ser uttryckligen annorlunda ut an
en jamforelse mot 50).

Testat i `tests/test_v1a_comparison.py` (TEST 8) -- inklusive en explicit
kontroll att inga "aldrig publicerat"-liknande formuleringar smyger sig in
som ett PASTAENDE (skillnad mot att NAMNGE och NEKA pastaendet, vilket ar
tillatet och avsett).

## Framtida forbattring

Nar en verklig publikationshistorik finns tillganglig kan
`existing_content` fyllas med hela corpuset utan nagon andring av
`compare_to_existing_content()`s signatur eller logik -- funktionen tar
redan emot vilken lista som helst. Se
`docs/V1A_FUTURE_EXTENSION_POINTS.md`.
