# Parastoo Integration — Gap Report

Ordern for Final Canonical Data Closure kravde uttryckligen: "Om du trots
detta upptacker att verklig originaldata inte kan representeras korrekt:
STOPPA. Andra inte Schema V1.1. Rapportera exakt vilket falt eller vilken
relation som saknas. Det blir i sa fall ett separat projektledarbeslut."

Denna integration stotte pa exakt en sadan situation. Ingen schemaandring
gjordes. Har foljer den exakta rapporten.

## Gapet

`ReaderFeedback.content_reference` (`schema/reader_effect.py`) ar ett
**obligatoriskt** (`str`, inget `Optional`) falt, dokumenterat pa faltet
sjalvt som: `"FK -> ContentRecord.content_id this feedback responds to."`

Parastoos recension ar evidens om en **BOK** ("Leadership Without Filter"
av Jan Stefors), inte om nagon `ContentRecord` (t.ex. ett LinkedIn-inlagg
eller utkast) i detta system. Det finns ingen `ContentRecord` for boken,
och en sadan far inte hittas pa (forbjudet: fabrikation av data).

**Rot orsak:** `content_reference` antar att all Reader Feedback svarar
mot en `ContentRecord`. Det stammer for LinkedIn-recensioner av publicerat
inlagg, men inte for en bokrecension. Schemat har ingen alternativ, redan
befintlig vag att peka pa en bok som "det denna feedback handlar om" pa
samma FK-validerade satt.

## Vad som INTE gjordes

- Ingen `ContentRecord` skapades for boken.
- `content_reference`s typ andrades INTE till `Optional[str]`.
- Inget nytt falt (t.ex. `book_reference` eller `evidence_subject_id`)
  lades till.
- Inget nytt schemakoncept (t.ex. en generell "EvidenceSubject"-union av
  ContentRecord/Source) infordes.

## Vad som gjordes istallet (tekniska, icke-schemaandrande losningar)

1. **`ReaderFeedback.source_id`** (redan `Optional[str]`, redan avsett for
   "vilken Source denna feedback ar arkiverad under/relaterar till")
   pekar pa en ny `Source(source_type=SourceType.BOOK)`-post
   (`source-book-leadership-without-filter`) som representerar boken.
   `SourceType.BOOK` fanns redan i schemat sedan V1 -- inget nytt.
2. **`content_reference`** satts till den ordagranna strangen
   `"UNDERLAG SAKNAS"` -- detta projekts etablerade, igenkannbara
   konvention (anvand i `docs/OPEN_QUESTIONS.md` sedan V1.1) for ett
   uttryckligen flaggat, ALDRIG gissat, saknat varde. Det ar INTE ett
   fabricerat content_id och far aldrig lasas som ett verkligt FK-varde.
   Se TP-12 i `docs/TECHNICAL_PROPOSALS.md`.
3. **Reader Effect-koppling**: `ReaderEffectAssociation` (Beslut 15) --
   den formella, FK-validerade kopplingen mellan en `ReaderEffect` och
   dess evidens -- finns bara inbaddad pa `ContentRecord.reader_effects`.
   Utan en `ContentRecord` finns ingen plats att lagga en formell
   association. Losning: `ReaderFeedback.effect_observations` (redan
   `list[str]`, redan dokumenterat pa faltet som "Free-text notes on what
   effect this feedback seems to evidence, PRIOR TO being formalized into
   a ReaderEffectAssociation") anvands for exakt detta syfte -- faltet var
   redan designat for precis denna situation.

## Vad detta betyder for framtiden (projektledarbeslut, inte gjort har)

Om Editorial Engine ska kunna knyta formell, FK-validerad Reader
Effect-evidens till boklasare i stor skala (fler bokrecensioner an denna
enda), bor projektledningen senare besluta om nagot av:

- Gora `ReaderFeedback.content_reference` `Optional[str]`, sa att
  bokrecensioner legitimt kan lamna faltet tomt (`None`) istallet for
  ett sentinel-varde.
- Eller inforsa ett generellt "evidence subject"-begrepp som kan vara
  antingen en `ContentRecord` eller en `Source` (t.ex. en bok), med
  formell FK-koppling for Reader Effects i bada fallen.

Ingetdera gjordes i denna integration -- det ar, exakt som ordern kravde,
"ett separat projektledarbeslut."

## Reader Effect-taxonomigap (separat, mindre gap)

Recensionens text stodjer tydligt att lasaren *reconnect[ed] with their
own inner voice, emotions, and judgment* och *regain[ed] a sense of
clarity*. Detta motsvarar INTE nagon av de tva befintliga
`ReaderEffect`-posterna (`RE-001` "obehag"/discomfort, `RE-002`
"perspektivskifte"). Ingen ny `ReaderEffect` skapades (forbjudet av
ordern). Denna specifika effekt ar darfor INTE kopplad till recensionen,
och gapet rapporteras har for projektledningens framtida beslut om
`ReaderEffect`-taxonomin ska utokas (t.ex. med en effekt i kategorin
`AFTEREFFECT`, "atererovrat omdome"/"regained judgment").

Endast `RE-002` (perspektivskifte / "sprak for monster") ar kopplad,
eftersom det ar direkt och otvetydigt stott av texten ("There are patterns
behind them, and those patterns can be recognized and understood.").
