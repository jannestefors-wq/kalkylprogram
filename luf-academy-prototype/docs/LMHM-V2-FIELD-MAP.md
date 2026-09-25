# LMHM version 2. Fältkarta och datamigrering

Order 014. Källa för innehållet: docs/LMHM-V2-FINAL-CONTENT-SPEC.md.
Utgångspunkt: commit 0242434, gren claude/ledarskap-vecka-1-prototype-7sy98p.

## Regler

1. En befintlig nyckel ändras aldrig. En ny eller ändrad fråga får en ny nyckel.
2. Svar under pensionerade nycklar ligger kvar i databasen. De kan inte skrivas och visas inte i version 2.
3. Ingen rad i lr_entry skrivs om, flyttas eller tas bort. Ingen migrering av innehåll.
4. Förändringsområdet sparas som nummer ("1", "2", "3") eller "nytt". Områdets text finns bara i vecka 1.

## Schemaändringar

Endast additivt. Migration `server/migrations/0003_lmhm_v2.sql`.

| Tabell | Innehåll | Vem läser |
|---|---|---|
| `lr_talk_request` | enrollment_id, created_at. Ingen text, ingen källa. | Deltagaren själv. Jan ser namn, grupp och tidpunkt. |
| `lr_support_prompt` | enrollment_id, streak_end_step, choice (not_now eller requested), created_at. Skapas bara när deltagaren svarar på rutan. | Bara deltagarens egen vy. Aldrig Jan, aldrig admin. |

Inga befintliga tabeller, kolumner eller CHECK-villkor ändras. `lr_event` får inga nya händelser.
Startsamtalet och Samtal med Jan ger inga händelser alls.

Förhandsvisningen (claude.ai-databasen) får en ny sökväg: `requests/<id>` med bara `requestedAt`.

## Ersättningsrelationer (spec avsnitt 24)

| Pensionerad | Ersätts av | Kommentar |
|---|---|---|
| `w1:karta.skaver_mest` | `start:infor.skaver` | Flyttad till Inför startsamtalet |
| `w1:karta.varfor_har` | ingen | Ställs muntligt i startsamtalet |
| `w1:forandring.mal_n_marks` | `w1:forandring.mal_n_hur` | Ny fråga |
| `w1:manniskor.person_n`, `person_n_note` | `w1:manniskor.vem_1` till `vem_4` | Högst fyra rader, ett fält per rad |
| `w1:situation.sag_horde`, `gjorde`, `gjorde_inte` | `w1:situation.vad_hande` (oförändrad), `w1:situation.gjorde_lat` | |
| `w1:situation.hande_sedan`, `vet_inte`, `w1:triangel.ser_nu`, `w1:stanna.lyssna_utan_losa` | ingen | Borttagna |
| `w1:narvaro.*` (sex fält) | ingen | Momentet Närvaro i mötet borttaget |
| `wN:handling.prova`, `situation` | `wN:handling.gora` | I2 |
| `wN:handling.annorlunda`, `lagga_marke`, `forvantan` | `wN:handling.omrade`, `nytt`, `marks` | I1, I1b, I3 |
| `wN:vad-hande.missbedomde`, `battre`, `svarare`, `larde`, `upptackte`, `annorlunda_an_tankt`, `fortsatta`, `prova_annorlunda` | `wN:vad-hande.blev`, `markte`, `bygger`, `stoppade`, `kostar`, `nasta` | J0 till L1. Frågorna ställs muntligt av Jan |
| `w2:stanna.skjutit_upp` | `w2:stanna.skjutit_upp_beslut` | Ny fråga |
| `w2:situation.*` (När jag inte klev fram) | ingen | Momentet borttaget |
| `w2:triangel.ansvar_t` | `w2:triangel.ansvar_leder` | Ny fråga |
| `w3:se-hora-kanna.tolkning`, `vet_inte` | `w3:se-hora-kanna.tolkning_vet_inte` | Sammanslagna |
| `w3:se-hora-kanna.fraga`, `w3:stanna.sett_hort` | `w3:aterkoppling.fraga`, `w3:aterkoppling.sett_hort` | Nytt moment Min återkoppling |
| `w4:trygghet.trygghet_t` | `w4:trygghet.trygghet_sett` | Ny digital fråga, order 011 |
| `w4:halvvags.fokus`, `w4:trygghet.borja`, `w4:samtalet.tolkning`, `deras_sida`, `w4:stanna.trygghet_team`, `relation_tid`, `konflikt_irritation` | ingen | Borttagna |
| `w5:niva.problem`, `individ`, `team`, `organisation`, `eget_ansvar` | `w5:niva.problem_hos`, `annan_niva`, `fatt`, `byggt` | Hörnfrågor ersatta av en fråga. P4 i jag-form |
| `w5:stanna.slappa` | `w5:privat.slappa` | Veckans privata fråga |
| `w5:teamet.*`, `w5:ny-eller-vaxa.*`, `w5:stanna.individfraga`, `potential`, `grupp_team` | `w5:stanna.grupp_team_saknas` | Momenten Teamet och Någon som är ny borttagna |
| `w6:stanna.stannade` | `w6:stanna.tog_hand` | Bokens s. 202 |
| `w6:trycket.tryck`, `val`, `riktning`, `mellanrum` | `w6:trycket.nar_trycket` | Ett gemensamt fält |
| `w6:tillbaka.nar_jag_borjade`, `manniskorna` | `w6:tillbaka.forandrats`, `inte_forandrats`, `w6:spegel.*` | Hela resan och Spegeln |
| `w6:avslut.lofte` | ingen | Mitt ledarskapslöfte borttaget helt |
| `w6:avslut.annorlunda_nu`, `marka_framover`, `fortsatta_3`, `folja_upp_3` | `w6:avslut.testar`, `gor_da` | |
| `w6:vad-hande.*` | `d30:kvar.blev`, `hande_markte`, `stoppade` | Vecka 6 följs upp vid 30 dagar |
| `w6:misstaget.radd_for`, `w6:principer.marks` | ingen | Borttagna |
| `d30:kvar.foll_bort`, `reagerat` | `d30:kvar.foll_bort_stoppade`, `reagerat_bygger` | Nya frågor |
| `d30:kvar.svarare`, `borja_igen` | ingen | Borttagna |
| `samtal:infor.forsta`, `inte_gruppen` | `start:infor.forsta`, `start:infor.inte_gruppen` | Flyttade till Startsamtalet |
| `samtal:infor.forsta_steg`, `samtal:efter.sag`, `tydligare`, `folja_upp` | `samtal:efter.tar_med`, `start:efter.*` | |
| privata frågor nummer två (`w1:privat.hjalp_samtal`, `w2:privat.vet_redan`, `w3:privat.vet_redan`, `w4:privat.undviker`, `w5:privat.forsvarar`, `w5:privat.vet_redan`, `w6:privat.hjalp_samtal`) | ingen | En privat fråga per vecka |

## Nycklar som behålls (78)

Samma nyckel, samma fråga, samma typ. Kontrollerat maskinellt: ingen behållen nyckel har fått ny frågetext.

| Nyckel | Fråga |
|---|---|
| `w1:stanna.filter` | Vilket filter känner du igen mest hos dig själv: corporatespråk, prestige, rädsla eller fasad? |
| `w1:stanna.pratar_for_lite` | Vem i din närhet pratar du mycket om arbete med, men för lite om hur personen faktiskt har det? |
| `w1:forandring.mal_1` | 1. Jag vill förändra |
| `w1:forandring.mal_2` | 2. Jag vill förändra |
| `w1:forandring.mal_3` | 3. Jag vill förändra |
| `w1:situation.vad_hande` | Vad hände? |
| `w1:situation.tolkning` | Vad är din egen tolkning? |
| `w1:triangel.filter` | Filter. Vad lägger sig mellan dig och den andra? |
| `w1:triangel.manniska` | Människa. Vem står framför dig, bortom rollen? |
| `w1:triangel.narvaro_t` | Närvaro. Var är du själv när ni pratar? |
| `w1:handling.nar` | När tänker jag göra det? |
| `w1:vad-hande.gjorde_faktiskt` | Vad gjorde du faktiskt? |
| `w1:vad-hande.hande` | Vad hände? |
| `w1:privat.vet_redan` | Vad vet jag egentligen redan? |
| `w1:traffen.vackte` | Efter träffen. Vad väckte dagens samtal i mitt eget ledarskap? |
| `w2:stanna.kostar_vanta` | Vad kostar det att fortsätta vänta? |
| `w2:triangel.radsla` | Rädsla. Vad är du rädd för här? |
| `w2:triangel.mod_t` | Mod. Vad vore det modiga steget? |
| `w2:triangel.obehag_risk` | Vad är obehag, och vad är verklig risk? |
| `w2:handling.nar` | När tänker jag göra det? |
| `w2:vad-hande.gjorde_faktiskt` | Vad gjorde du faktiskt? |
| `w2:vad-hande.hande` | Vad hände? |
| `w2:vad-hande.nasta` | Vad gör du nu? |
| `w2:privat.undviker` | Vad undviker jag just nu? |
| `w2:traffen.vackte` | Efter träffen. Vad väckte dagens samtal i mitt eget ledarskap? |
| `w3:stanna.for_snabbt` | Vilket problem försöker du lösa för snabbt? |
| `w3:stanna.kansla_tolkning` | Vilken del är din egen känsla eller tolkning? |
| `w3:se-hora-kanna.vem` | Vilken situation gäller det? |
| `w3:se-hora-kanna.se` | Se. Vad har du faktiskt observerat? |
| `w3:se-hora-kanna.hora` | Höra. Vad har du hört från personen själv? |
| `w3:se-hora-kanna.kanna` | Känna. Vad är din känsla, som du behöver vara medveten om men inte låta styra? |
| `w3:handling.nar` | När tänker jag göra det? |
| `w3:vad-hande.gjorde_faktiskt` | Vad gjorde du faktiskt? |
| `w3:vad-hande.hande` | Vad hände? |
| `w3:vad-hande.nasta` | Vad gör du nu? |
| `w3:privat.forsvarar` | Vad försvarar jag hos mig själv? |
| `w3:traffen.vackte` | Efter träffen. Vad väckte dagens samtal i mitt eget ledarskap? |
| `w4:halvvags.forandrats` | Vad har faktiskt förändrats? |
| `w4:halvvags.medveten` | Vad har jag bara blivit mer medveten om? |
| `w4:halvvags.inte_gjort` | Vad har jag fortfarande inte gjort? |
| `w4:stanna.for_tidigt` | Vem försöker du utveckla innan grunden är på plats? |
| `w4:trygghet.vem` | Vem eller vilka gäller det? |
| `w4:trygghet.relation_t` | Relation. Finns det en relation där feedback kan landa? |
| `w4:trygghet.utveckling_t` | Utveckling. Är utvecklingsmålen realistiska? |
| `w4:samtalet.observerat` | Vad har du observerat? |
| `w4:samtalet.konflikt` | Konflikt. Vad är konflikten? |
| `w4:samtalet.losning` | Lösning. Vilken lösning är möjlig? |
| `w4:samtalet.ansvar_k` | Ansvar. Vem tar ansvar för vad? |
| `w4:handling.nar` | När tänker jag göra det? |
| `w4:vad-hande.gjorde_faktiskt` | Vad gjorde du faktiskt? |
| `w4:vad-hande.hande` | Vad hände? |
| `w4:vad-hande.nasta` | Vad gör du nu? |
| `w4:privat.hjalp_samtal` | Vad behöver jag hjälp med i ett enskilt samtal? |
| `w4:traffen.vackte` | Efter träffen. Vad väckte dagens samtal i mitt eget ledarskap? |
| `w5:stanna.tolererar` | Vad tolererar ni idag som försvagar laget? |
| `w5:niva.sett_hort` | Vad har du faktiskt sett och hört? |
| `w5:niva.tror` | Var tror du att det sitter? |
| `w5:handling.nar` | När tänker jag göra det? |
| `w5:vad-hande.gjorde_faktiskt` | Vad gjorde du faktiskt? |
| `w5:vad-hande.hande` | Vad hände? |
| `w5:vad-hande.nasta` | Vad gör du nu? |
| `w5:traffen.vackte` | Efter träffen. Vad väckte dagens samtal i mitt eget ledarskap? |
| `w6:stanna.stress_gor` | Vad gör stress med ditt sätt att leda? |
| `w6:misstaget.se_m` | Se. Vad var situationen? Vad valde du? |
| `w6:misstaget.lara` | Lära. Vad hade du gjort annorlunda om du inte var rädd? |
| `w6:misstaget.vanda` | Vända. Vad gör du nu? |
| `w6:principer.vald` | Den som skaver mest |
| `w6:handling.nar` | När tänker jag göra det? |
| `w6:avslut.fortsatta_1` | 1. Det här ska jag fortsätta träna på |
| `w6:avslut.folja_upp_1` | Så följer jag upp att det händer |
| `w6:avslut.fortsatta_2` | 2. Det här ska jag fortsätta träna på |
| `w6:avslut.folja_upp_2` | Så följer jag upp att det händer |
| `w6:privat.vet_redan` | Vad vet jag egentligen redan? |
| `w6:traffen.vackte` | Efter träffen. Vad väckte dagens samtal i mitt eget ledarskap? |
| `d30:kvar.fortfarande` | Vad gör du fortfarande? |
| `d30:kvar.nasta_steg` | Vad är ditt nästa konkreta steg? |
| `samtal:infor.tanka_kring` | Vad vill jag få hjälp att tänka kring? |
| `samtal:efter.gora_nu` | Vad ska jag göra nu? |

## Nya nycklar (107)

| Nyckel | Fråga |
|---|---|
| `w1:forandring.mal_1_hur` | Hur skulle det märkas, och vem skulle kunna märka det? |
| `w1:forandring.mal_2_hur` | Hur skulle det märkas, och vem skulle kunna märka det? |
| `w1:forandring.mal_3_hur` | Hur skulle det märkas, och vem skulle kunna märka det? |
| `w1:manniskor.vem_1` | Vem, och vad behöver jag förstå bättre om hen? |
| `w1:manniskor.vem_2` | Vem, och vad behöver jag förstå bättre om hen? |
| `w1:manniskor.vem_3` | Vem, och vad behöver jag förstå bättre om hen? |
| `w1:manniskor.vem_4` | Vem, och vad behöver jag förstå bättre om hen? |
| `w1:situation.gjorde_lat` | Vad gjorde du, och vad lät du bli att göra? |
| `w1:handling.omrade` | Vilket av mina förändringsområden arbetar jag med nu? |
| `w1:handling.nytt` | Vad är det, och varför passar inte de tre? |
| `w1:handling.gora` | Vad ska jag göra, och i vilken situation? |
| `w1:handling.marks` | Hur skulle det märkas, och vem skulle kunna märka det? |
| `w1:vad-hande.blev` | Blev det av? |
| `w1:vad-hande.markte` | Märkte någon något? |
| `w1:vad-hande.bygger` | Vad bygger du det på? |
| `w1:vad-hande.stoppade` | Vad stoppade dig? |
| `w1:vad-hande.kostar` | Vad kostar det att vänta? |
| `w1:vad-hande.nasta` | Vad gör du nu? |
| `w2:stanna.skjutit_upp_beslut` | Vilket samtal, beslut eller besked har du skjutit upp? |
| `w2:triangel.galler` | Vad gäller det? |
| `w2:triangel.vad_det_ar` | Vad är det, och hur länge har det legat? |
| `w2:triangel.ansvar_leder` | Ansvar. Vad är ditt ansvar här, eftersom du leder? Och vad är inte ditt? |
| `w2:triangel.sta_kvar` | Hur står du kvar i det när någon ifrågasätter? |
| `w2:handling.omrade` | Vilket av mina förändringsområden arbetar jag med nu? |
| `w2:handling.nytt` | Vad är det, och varför passar inte de tre? |
| `w2:handling.gora` | Vad ska jag göra, och i vilken situation? |
| `w2:handling.marks` | Hur skulle det märkas, och vem skulle kunna märka det? |
| `w2:vad-hande.blev` | Blev det av? |
| `w2:vad-hande.markte` | Märkte någon något? |
| `w2:vad-hande.bygger` | Vad bygger du det på? |
| `w2:vad-hande.stoppade` | Vad stoppade dig? |
| `w2:vad-hande.kostar` | Vad kostar det att vänta? |
| `w3:se-hora-kanna.tolkning_vet_inte` | Vad är min tolkning, och vad vet jag inte? |
| `w3:aterkoppling.sett_hort` | Det jag har sett eller hört. Så konkret att en kamera kunde bekräfta det. |
| `w3:aterkoppling.fraga` | Vilken fråga kan jag ställa som öppnar utan att styra svaret? |
| `w3:aterkoppling.signal` | Min egen signal, om jag vill säga den. |
| `w3:handling.omrade` | Vilket av mina förändringsområden arbetar jag med nu? |
| `w3:handling.nytt` | Vad är det, och varför passar inte de tre? |
| `w3:handling.gora` | Vad ska jag göra, och i vilken situation? |
| `w3:handling.marks` | Hur skulle det märkas, och vem skulle kunna märka det? |
| `w3:vad-hande.blev` | Blev det av? |
| `w3:vad-hande.markte` | Märkte någon något? |
| `w3:vad-hande.bygger` | Vad bygger du det på? |
| `w3:vad-hande.stoppade` | Vad stoppade dig? |
| `w3:vad-hande.kostar` | Vad kostar det att vänta? |
| `w4:spegel.vem` | Vem frågade du? |
| `w4:spegel.tog_med` | Vad tog du med dig från samtalet? |
| `w4:trygghet.trygghet_sett` | Trygghet. Vad har du sett eller hört som tyder på att personen vågar säga vad den tänker, fråga, göra fel eller säga emot? |
| `w4:samtalet.med_vem` | Vem är samtalet med? |
| `w4:samtalet.pagatt` | Det här har pågått länge, och stöd har redan getts. |
| `w4:samtalet.gjorts` | Vad har redan gjorts, och vad hände? |
| `w4:samtalet.sitter` | Sitter det hos personen, eller i det runt personen? |
| `w4:handling.omrade` | Vilket av mina förändringsområden arbetar jag med nu? |
| `w4:handling.nytt` | Vad är det, och varför passar inte de tre? |
| `w4:handling.gora` | Vad ska jag göra, och i vilken situation? |
| `w4:handling.marks` | Hur skulle det märkas, och vem skulle kunna märka det? |
| `w4:vad-hande.blev` | Blev det av? |
| `w4:vad-hande.markte` | Märkte någon något? |
| `w4:vad-hande.bygger` | Vad bygger du det på? |
| `w4:vad-hande.stoppade` | Vad stoppade dig? |
| `w4:vad-hande.kostar` | Vad kostar det att vänta? |
| `w5:stanna.grupp_team_saknas` | Har ni en grupp eller ett riktigt team? Vad saknas? |
| `w5:niva.problem_hos` | Vilket problem, och hos vem? |
| `w5:niva.annan_niva` | Vad talar för att det sitter på en annan nivå? |
| `w5:niva.fatt` | Vilka av de här har personen fått av mig? |
| `w5:niva.byggt` | Vad har jag själv byggt runt problemet? Eller låtit bli att bygga? |
| `w5:handling.omrade` | Vilket av mina förändringsområden arbetar jag med nu? |
| `w5:handling.nytt` | Vad är det, och varför passar inte de tre? |
| `w5:handling.vag` | Vad gör jag? |
| `w5:handling.skapa` | Vad skapar jag, och hur vet personen att det finns nu? |
| `w5:handling.resultat` | Vilket resultat lämnar jag över? Inte uppgiften. Resultatet. |
| `w5:handling.ramar` | Vilka ramar gäller, och när följer vi upp? |
| `w5:handling.chef_veta` | Vad behöver min chef veta som hen inte vet idag? |
| `w5:handling.hur_saga` | Hur säger jag det så att det går att ta emot? |
| `w5:handling.marks` | Hur skulle det märkas, och vem skulle kunna märka det? |
| `w5:vad-hande.blev` | Blev det av? |
| `w5:vad-hande.markte` | Märkte någon något? |
| `w5:vad-hande.bygger` | Vad bygger du det på? |
| `w5:vad-hande.stoppade` | Vad stoppade dig? |
| `w5:vad-hande.kostar` | Vad kostar det att vänta? |
| `w5:privat.slappa` | Vad behöver jag släppa för att någon annan ska kunna växa? |
| `w6:stanna.tog_hand` | När tog du senast hand om dig själv på riktigt? Inte för att prestera bättre. Bara för att du behövde det. |
| `w6:trycket.nar_trycket` | När trycket kommer: vad pressar dig, vad brukar du välja och vilken riktning vill du hålla? |
| `w6:tillbaka.forandrats` | Vad har faktiskt förändrats? |
| `w6:tillbaka.inte_forandrats` | Vad har inte förändrats? |
| `w6:spegel.vem` | Vem frågade du? |
| `w6:spegel.tog_med` | Vad tog du med dig från samtalet? |
| `w6:avslut.testar` | Vilken situation vet du redan kommer att testa dig? |
| `w6:avslut.gor_da` | Vad gör du när den kommer? |
| `w6:handling.omrade` | Vilket av mina förändringsområden arbetar jag med nu? |
| `w6:handling.nytt` | Vad är det, och varför passar inte de tre? |
| `w6:handling.gora` | Vad ska jag göra, och i vilken situation? |
| `w6:handling.marks` | Hur skulle det märkas, och vem skulle kunna märka det? |
| `d30:kvar.blev` | Handlingen du valde i vecka 6. Blev det av? |
| `d30:kvar.hande_markte` | Vad hände? Märkte någon något? Vad bygger du det på? |
| `d30:kvar.stoppade` | Vad stoppade dig? |
| `d30:kvar.foll_bort_stoppade` | Vad föll bort, och vad stoppade det? |
| `d30:kvar.reagerat_bygger` | Har någon reagerat på något? Vad bygger du det på? |
| `d30:kvar.testade` | Situationen du visste skulle testa dig. Kom den? Vad gjorde du? |
| `d30:kvar.undvikit` | Vad har du undvikit sedan kursen slutade? |
| `start:infor.forsta` | Vad vill jag att Jan ska förstå om min situation? |
| `start:infor.skaver` | Vad skaver mest i mitt ledarskap just nu? |
| `start:infor.inte_gruppen` | Vad vill jag inte ta i gruppen just nu? |
| `start:efter.tar_med` | Vad tar jag med mig från samtalet? |
| `start:efter.gora_nu` | Vad ska jag göra nu? |
| `samtal:infor.monster` | Vilket mönster ser jag hos mig själv? |
| `samtal:efter.tar_med` | Vad tar jag med mig från samtalet? |

## Pensionerade nycklar (157)

Svar under dessa nycklar ligger kvar i lr_entry. De kan inte skrivas i version 2 och visas inte.

| Nyckel | Fråga i version 1 |
|---|---|
| `w1:stanna.lyssna_utan_losa` | Vad skulle förändras om du lyssnade utan att lösa under en hel vecka? |
| `w1:karta.varfor_har` | Varför är jag här? |
| `w1:karta.skaver_mest` | Vad skaver mest i mitt ledarskap just nu? |
| `w1:forandring.mal_1_marks` | Hur märker jag att något faktiskt har förändrats? |
| `w1:forandring.mal_2_marks` | Hur märker jag att något faktiskt har förändrats? |
| `w1:forandring.mal_3_marks` | Hur märker jag att något faktiskt har förändrats? |
| `w1:manniskor.person_1` | Vem |
| `w1:manniskor.person_1_note` | Relation, ansvar, det jag behöver förstå bättre |
| `w1:manniskor.person_2` | Vem |
| `w1:manniskor.person_2_note` | Relation, ansvar, det jag behöver förstå bättre |
| `w1:manniskor.person_3` | Vem |
| `w1:manniskor.person_3_note` | Relation, ansvar, det jag behöver förstå bättre |
| `w1:manniskor.person_4` | Vem |
| `w1:manniskor.person_4_note` | Relation, ansvar, det jag behöver förstå bättre |
| `w1:manniskor.person_5` | Vem |
| `w1:manniskor.person_5_note` | Relation, ansvar, det jag behöver förstå bättre |
| `w1:manniskor.person_6` | Vem |
| `w1:manniskor.person_6_note` | Relation, ansvar, det jag behöver förstå bättre |
| `w1:situation.sag_horde` | Vad såg eller hörde du faktiskt? |
| `w1:situation.gjorde` | Vad gjorde du? |
| `w1:situation.gjorde_inte` | Vad gjorde du inte? |
| `w1:situation.hande_sedan` | Vad hände sedan? |
| `w1:situation.vet_inte` | Vad vet du fortfarande inte? |
| `w1:narvaro.eget_svar` | När började jag tänka på mitt eget svar? |
| `w1:narvaro.slutade_lyssna` | När slutade jag egentligen lyssna? |
| `w1:narvaro.losa_for_tidigt` | Försökte jag lösa något innan jag förstått? |
| `w1:narvaro.missade` | Vad missade jag? |
| `w1:narvaro.splittrad` | Vad hände med samtalet när jag blev splittrad? |
| `w1:narvaro.stanna_kvar` | Vad skulle kunna hända om jag stannade kvar lite längre? |
| `w1:triangel.ser_nu` | Vad ser du nu, när du ser de tre tillsammans? |
| `w1:handling.prova` | Den här veckan ska jag prova |
| `w1:handling.situation` | I vilken situation? |
| `w1:handling.annorlunda` | Vad vill jag själv göra annorlunda? |
| `w1:handling.lagga_marke` | Vad vill jag försöka lägga märke till? |
| `w1:vad-hande.annorlunda_an_tankt` | Vad blev annorlunda än du hade tänkt? |
| `w1:vad-hande.upptackte` | Vad upptäckte du om ditt eget sätt att leda? |
| `w1:vad-hande.fortsatta` | Vad vill du fortsätta göra? |
| `w1:vad-hande.prova_annorlunda` | Vad behöver du prova annorlunda nästa gång? |
| `w1:privat.hjalp_samtal` | Vad behöver jag hjälp med i ett enskilt samtal? |
| `w2:stanna.skjutit_upp` | Vilket samtal har du skjutit upp? |
| `w2:stanna.soker_dig_till` | Vem söker du dig till när det verkligen skaver? |
| `w2:stanna.obekvam_sanning` | Vilken obekväm sanning behöver sägas? |
| `w2:situation.vad_hande` | Vad hände? |
| `w2:situation.sag_horde` | Vad såg eller hörde du? |
| `w2:situation.radd` | Vad var du rädd skulle hända? |
| `w2:situation.trodde_om_andra` | Vad trodde du om de andra? |
| `w2:situation.gjorde` | Vad gjorde du? |
| `w2:situation.gjorde_inte` | Vad gjorde du inte? |
| `w2:situation.kostade` | Vad kostade det att du inte klev fram? |
| `w2:situation.om_klivit` | Vad hade hänt om du hade gjort det? |
| `w2:triangel.ansvar_t` | Ansvar. Vad är ditt ansvar, och vad är inte ditt? |
| `w2:handling.prova` | Den här veckan ska jag prova |
| `w2:handling.situation` | I vilken situation? |
| `w2:handling.annorlunda` | Vad vill jag själv göra annorlunda? |
| `w2:handling.lagga_marke` | Vad vill jag försöka lägga märke till? |
| `w2:handling.forvantan` | Vad tror jag kommer att hända? |
| `w2:vad-hande.missbedomde` | Vad bedömde du fel? |
| `w2:vad-hande.battre` | Vad blev bättre? |
| `w2:vad-hande.svarare` | Vad blev svårare? |
| `w2:vad-hande.larde` | Vad lärde du dig om ditt sätt att leda? |
| `w2:privat.vet_redan` | Vad vet jag egentligen redan? |
| `w3:stanna.sett_hort` | Vad har du faktiskt sett och hört? |
| `w3:se-hora-kanna.tolkning` | Vad är min tolkning? |
| `w3:se-hora-kanna.vet_inte` | Vad vet jag inte? |
| `w3:se-hora-kanna.fraga` | Vilken fråga kan jag ställa som öppnar utan att styra svaret? |
| `w3:handling.prova` | Den här veckan ska jag prova |
| `w3:handling.situation` | I vilken situation? |
| `w3:handling.annorlunda` | Vad vill jag själv göra annorlunda? |
| `w3:handling.lagga_marke` | Vad vill jag försöka lägga märke till? |
| `w3:handling.forvantan` | Vad tror jag kommer att hända? |
| `w3:vad-hande.missbedomde` | Vad bedömde du fel? |
| `w3:vad-hande.battre` | Vad blev bättre? |
| `w3:vad-hande.svarare` | Vad blev svårare? |
| `w3:vad-hande.larde` | Vad lärde du dig om ditt sätt att leda? |
| `w3:privat.vet_redan` | Vad vet jag egentligen redan? |
| `w4:halvvags.fokus` | Vad vill jag fokusera på under andra halvan? |
| `w4:stanna.trygghet_team` | Var finns tryggheten i ditt team idag? |
| `w4:stanna.relation_tid` | Vilken relation behöver mer tid innan du driver nästa förändring? |
| `w4:stanna.konflikt_irritation` | Vad är konflikt och vad är bara irritation? |
| `w4:trygghet.trygghet_t` | Trygghet. Känner den här personen sig trygg? |
| `w4:trygghet.borja` | Var börjar du idag? Och var borde du börja? |
| `w4:samtalet.tolkning` | Vad är din tolkning? |
| `w4:samtalet.deras_sida` | Vad vet du inte om hur det ser ut från den andras sida? |
| `w4:handling.prova` | Den här veckan ska jag prova |
| `w4:handling.situation` | I vilken situation? |
| `w4:handling.annorlunda` | Vad vill jag själv göra annorlunda? |
| `w4:handling.lagga_marke` | Vad vill jag försöka lägga märke till? |
| `w4:handling.forvantan` | Vad tror jag kommer att hända? |
| `w4:vad-hande.missbedomde` | Vad bedömde du fel? |
| `w4:vad-hande.battre` | Vad blev bättre? |
| `w4:vad-hande.svarare` | Vad blev svårare? |
| `w4:vad-hande.larde` | Vad lärde du dig om ditt sätt att leda? |
| `w4:privat.undviker` | Vad undviker jag just nu? |
| `w5:stanna.individfraga` | Vilket problem har ni gjort till en individfråga? |
| `w5:stanna.grupp_team` | Har ni en grupp eller ett team? |
| `w5:stanna.potential` | Vem har potential att leda men har ännu inte fått chansen? |
| `w5:stanna.slappa` | Vad behöver du släppa för att någon annan ska kunna växa? |
| `w5:niva.problem` | Vilket problem gäller det? |
| `w5:niva.individ` | Vad talar för att det sitter hos individen? |
| `w5:niva.team` | Vad talar för att det sitter i teamet? |
| `w5:niva.organisation` | Vad talar för att det sitter i organisationen? |
| `w5:niva.eget_ansvar` | Vad är ditt eget ansvar här, oavsett nivå? |
| `w5:teamet.relation_r` | Relation. Hur är det mellan er? |
| `w5:teamet.ansvar_r` | Ansvar. Tar ni ansvar för varandra, eller bara för er egen del? |
| `w5:teamet.resultat_r` | Resultat. Vad blir resultatet av det? |
| `w5:teamet.saknas` | Grupp eller team? Vad saknas? |
| `w5:ny-eller-vaxa.valkomna` | Välkomna. Hur tas personen emot? |
| `w5:ny-eller-vaxa.fortroende` | Förtroende. Vad behöver finnas för att personen ska våga? |
| `w5:ny-eller-vaxa.utveckla` | Utveckla. Vilket ansvar kan du lämna över? |
| `w5:handling.prova` | Den här veckan ska jag prova |
| `w5:handling.situation` | I vilken situation? |
| `w5:handling.annorlunda` | Vad vill jag själv göra annorlunda? |
| `w5:handling.lagga_marke` | Vad vill jag försöka lägga märke till? |
| `w5:handling.forvantan` | Vad tror jag kommer att hända? |
| `w5:vad-hande.missbedomde` | Vad bedömde du fel? |
| `w5:vad-hande.battre` | Vad blev bättre? |
| `w5:vad-hande.svarare` | Vad blev svårare? |
| `w5:vad-hande.larde` | Vad lärde du dig om ditt sätt att leda? |
| `w5:privat.forsvarar` | Vad försvarar jag hos mig själv? |
| `w5:privat.vet_redan` | Vad vet jag egentligen redan? |
| `w6:stanna.stannade` | När stannade du senast utan att försöka prestera bättre? |
| `w6:trycket.tryck` | Tryck. Vad pressar dig just nu? |
| `w6:trycket.val` | Val. Vad väljer du när trycket kommer? |
| `w6:trycket.riktning` | Riktning. Vart vill du egentligen? |
| `w6:trycket.mellanrum` | Vad händer i mellanrummet mellan trycket och valet? |
| `w6:misstaget.radd_for` | Vad var du rädd för? |
| `w6:principer.marks` | Hur märks det i din vardag? |
| `w6:tillbaka.nar_jag_borjade` | När jag började. Vad gjorde du, undvek du eller fastnade du i? |
| `w6:tillbaka.manniskorna` | Människorna omkring mig. Vad tror du att de har märkt? Vad har någon faktiskt sagt? |
| `w6:handling.prova` | Den här veckan ska jag prova |
| `w6:handling.situation` | I vilken situation? |
| `w6:handling.annorlunda` | Vad vill jag själv göra annorlunda? |
| `w6:handling.lagga_marke` | Vad vill jag försöka lägga märke till? |
| `w6:handling.forvantan` | Vad tror jag kommer att hända? |
| `w6:vad-hande.gjorde_faktiskt` | Vad gjorde du faktiskt? |
| `w6:vad-hande.hande` | Vad hände? |
| `w6:vad-hande.missbedomde` | Vad bedömde du fel? |
| `w6:vad-hande.battre` | Vad blev bättre? |
| `w6:vad-hande.svarare` | Vad blev svårare? |
| `w6:vad-hande.larde` | Vad lärde du dig om ditt sätt att leda? |
| `w6:vad-hande.nasta` | Vad gör du nu? |
| `w6:avslut.annorlunda_nu` | Vad gör du annorlunda nu? |
| `w6:avslut.marka_framover` | Vad vill du att människorna runt dig ska märka framöver? |
| `w6:avslut.fortsatta_3` | 3. Det här ska jag fortsätta träna på |
| `w6:avslut.folja_upp_3` | Så följer jag upp att det händer |
| `w6:avslut.lofte` | Jag lovar mig själv att |
| `w6:privat.hjalp_samtal` | Vad behöver jag hjälp med i ett enskilt samtal? |
| `d30:kvar.foll_bort` | Vad föll bort? |
| `d30:kvar.svarare` | Vad blev svårare än du trodde? |
| `d30:kvar.reagerat` | Vad har människorna runt dig reagerat på? |
| `d30:kvar.borja_igen` | Vad behöver du börja med igen? |
| `samtal:infor.forsta` | Vad vill jag att Jan ska förstå om min situation? |
| `samtal:infor.inte_gruppen` | Vad vill jag inte ta i gruppen just nu? |
| `samtal:infor.forsta_steg` | Vilket första steg vill jag lämna samtalet med? |
| `samtal:efter.sag` | Vad såg jag som jag inte såg innan? |
| `samtal:efter.tydligare` | Vad blev tydligare? |
| `samtal:efter.folja_upp` | Vad vill jag att Jan följer upp med mig senare? |
