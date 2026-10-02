# Oddsklubben – agenthåndbog

Denne fil er den vedvarende projektkontekst for AI-agenter, der arbejder på Oddsklubben. Læs den før ændringer i repo, Google Sheet, statistik eller datamodel.

## Arbejdsprincipper

- Arbejd autonomt og udfør oplagte, sikre rettelser direkte. Stop kun for input, når et reelt valg eller manglende information kræver det.
- Bevar eksisterende data og afhængigheder. Kontrollér relevante formler efter strukturelle ændringer.
- Foretræk enkel, funktionel og mobilvenlig UX frem for et tungt "dashboard"-udtryk.
- Lav ikke hjemmeside/GitHub Pages-udvikling, medmindre det specifikt bliver ønsket.
- Skjul ikke rækker eller centrale data som en UX-løsning.
- Ved designændringer: vær konservativ. Oddsklubben-stilen er enkel, kompakt og genkendelig.

## Spillere

- 🐧 Pingvinus
- 👑 King
- 🦍 Gorilla
- 🐰 Kaninus
- 🙏 Kardinalus

## Google Sheet

Arbejdsarket er **Oddsklubben – Program UX**.

Spreadsheet ID:
`1uwVA8dDX_K0Hb1NfDuacWgQGZg1_pDhgfrY5quccJRc`

Det oprindelige ark **Program Aktiv** skal betragtes som historisk reference og må ikke ændres uden udtrykkelig besked.

Vigtige faner i arbejdsarket:
- `📅 Program 26-27` – autoritativ kilde til sæsonprogrammet, som mobilappen læser dynamisk
- `📲 Rundeindtastning` – autoritativ lodret indtastningsmodel for faktiske resultater og gevinster
- `Tabellen` – stillinger og konkurrencer
- `Diagram_Aktiv` – statistik/diagramgrundlag
- `All Time Pokaler`
- `Ture`
- `Ark16`
- `test` – skjult

De gamle faner `Program_Aktiv` og `📱 Program · overblik` er fjernet fra arbejdsarket og må ikke genindføres som afhængigheder.

## Mobilapp og dataflow

- `📅 Program 26-27` er **source of truth for programmet**. Mobilappen skal hente uge, runde/aktivitet, kampe og Fri Odds dynamisk herfra. Programmet må ikke igen blive afhængigt af hardcodede kampe i frontend; en lokal kopi må kun bruges som fallback ved forbindelsesfejl.
- Når en pokalkamp eller anden programoplysning ændres i `📅 Program 26-27`, skal ændringen kunne ses i appen efter genindlæsning uden ny GitHub-deployment.
- Appens indtastede Kr og Resultat skal ved live-drift skrives til `📲 Rundeindtastning`. Hjælpe-/formelkolonnerne F:H og J:K må ikke overskrives af appen.
- Skrivning fra appen skal forblive dry-run/deaktiveret, indtil sæson 2026/27 er migreret og live-skrivning udtrykkeligt er godkendt.
- Efter en succesfuld live-gemning skal Sheet-formlerne genberegnes, og relevante stillinger i `Tabellen` skal sorteres på ny efter Grundlovens regler. Sortering må ikke være en manuel efteropgave og må ikke være en simpel alfabetisk eller generisk sortering af hele fanen.
- Super League-stillingen sorteres efter de gældende tie-breaks (point → målscore → scorede mål; brug Grundloven for eventuelle yderligere afgørelser). Andre konkurrencer skal bruge deres egne regler.

## Rundeindtastning

Kolonner:
A Uge
B Runde
C Kamp
D Spiller
E Kr
F Mål F (automatisk, skjult)
G Mål M (automatisk, skjult)
H Point (automatisk, skjult)
I Resultat
J Runde-hjælper (automatisk, skjult)
K Uge-hjælper (automatisk, skjult)

Grundidé: én spiller pr. række. Når flere spillere hører til samme aktivitet, bør kamp/aktivitet ikke gentages unødigt i kolonne C.

Normalt skal en spiller i D høre til aktiviteten i C. **Fri Odds / "Alle Fri odds" er en særlig fælles aktivitet**, hvor alle fem spillere kan have hver sin række under samme aktivitet.

Kr er én samlet kolonne. Der skal ikke igen opdeles i "Kr Fri" og "Kr CL".

Brugeren skal kun indtaste Uge, Runde, Kamp, Spiller, Kr og Resultat. F:H beregnes automatisk og er skjult. J fører seneste rundenavn videre til beregningsmotoren og er også skjult. K fører seneste uge videre og bruges bl.a. til periodebaseret statistik. Champions League-beregningen gælder kun runder hvis navn starter med `Runde` og ignorerer kampe markeret `Fri odds`.

Pointregel: vinder 3 point, taber 0. Ved uafgjort får spilleren med flest vundne kroner 3 point og den anden 1 point. Ved 0-0 får begge 1 point. Ved helt lige kroner i en øvrig uafgjort kamp gives 1 point til begge.

## Statistik og historik

Vær opmærksom på historiske særtilfælde. En tidligere migrering fra den gamle brede model til den lodrette model kunne miste værdier, hvis statistik lå på en aktivitet, hvor spillernavnet ikke stod direkte i kampteksten.

Særligt vigtigt: Pingvinus havde historisk **986 kr** i Fri Odds i uge 37 under "Alle Fri odds". Værdien er nu genskabt i den lodrette model; Pingvinus' samlede Kr må derfor ikke falde tilbage til 716,5 kr.

Historiske samlede vundne beløb, før nye indtastninger:
- Kardinalus: 792,72 kr
- King: 1200,55 kr
- Pingvinus: 1702,50 kr
- Kaninus: 660,20 kr
- Gorilla: 1051,50 kr
- Total: 5407,47 kr

Historisk indsats: 1440 kr pr. spiller / 7200 kr samlet.

## Grundloven og konkurrenceregler

Oddsklubbens Grundlov er facit for konkurrencereglerne. Hvis en eksisterende formel eller implementering strider mod Grundloven, må agenten ikke gætte eller stiltiende ændre historiske data. Identificér konflikten og ret først modellen, når konsekvensen er afklaret.

- Super League: Resultat angiver antal vundne kuponer, fx `2-1`. Det er grundlag for Mål F, Mål M, Topscorer og ligapoint.
- Super League-point: sejr giver 3 point og nederlag 0. Ved uafgjort i antal vundne kuponer får spilleren med flest vundne kroner 3 point og den anden 1. Ved samme kr-beløb får begge 1 point; dermed giver 0-0 uden gevinst 1-1 i point.
- Super League tie-break: point → målscore → flest scorede mål. TV-penge har yderligere tie-breaks; brug Grundloven ved behov frem for at gætte.
- Årets Manager og Muldvarpen: alle gyldige gevinster i hele sæsonen tæller.
- Topscorer: kun vundne kuponer fra de 10 Super League-runder tæller.
- Det Gyldne Bur: færrest indkasserede mål → målscore → flest vundne kroner.
- Årets Mål: største ugegevinst fra de konkurrencer, Grundloven tillader: Super League, pokal, Supercup, Match Odds og Toto Cup.
- Sommer-/Julecup: flest vundne kroner i de relevante cupuger; ved lighed afgør placeringen i ligaen.
- Pokal, Supercup og Toto har særlige tie-breaks, som kan kræve højeste kuponodds. Hvis oddsdata mangler, må agenten ikke gætte vinderen.
- Pokalrunder kombineres med Fri Odds for spillere, der ikke deltager i pokalkampene: uge 47 indledende pokal har 2 lodtrukne spillere i kampen og de øvrige 3 direkte i semifinalen + Fri Odds; i semifinaler har den 5. spiller Fri Odds; i finalen har de 3 ikke-finalister Fri Odds. Denne regel skal slå igennem i program, app, `📲 Rundeindtastning`, formler og relevante statistikker.
- Ugyldige kuponer: gevinst går i klubkassen, men må ikke automatisk tælles med i konkurrencestillinger, hvor Grundloven udelukker dem.

Bevar `📲 Rundeindtastning` enkel. Tilføj ikke permanente synlige felter for sjældne tie-break-data som odds, medmindre der er et konkret behov; særdata kan håndteres separat.

## Tabellen

Tabellen indeholder bl.a. Champions League, Årets Manager, Topscorer, Hattrick, Saksespark, Årets Mål, Det Gyldne Bur og Sommer Cup.

Designpræference: behold den enkle eksisterende stil. En tidligere redesign-idé med mørkegrønne dashboard-sektioner, ekstra luft og kraftig styling blev fravalgt og rullet tilbage.

Sommer Cup er repareret og beregnes nu fra den lodrette model for uge 23–26 via den skjulte uge-hjælper K. Den må ikke igen afhænge af den slettede `Program_Aktiv`-fane.

## Diagram_Aktiv

Historiske baseline-tal skal ikke ændres ved migration. Nye indtastninger skal lægges ovenpå korrekt.

Historisk balance:
- Kardinalus: 1440 / 792,72 / -647,28
- King: 1440 / 1200,55 / -239,45
- Pingvinus: 1440 / 1702,50 / +262,50
- Kaninus: 1440 / 660,20 / -779,80
- Gorilla: 1440 / 1051,50 / -388,50
- Total: 7200 / 5407,47 / -1792,53

## GitHub-agent

Repository: `Stoffersen/oddsklubben`

Vigtige workflows:
- `.github/workflows/oddsklubben.yml` – ugentlig Oddsklubben Agent
- `.github/workflows/refresh-cache.yml` – opdaterer holdhistorik/cache fire gange dagligt

Cache-workflowets cron er:
`10 0,6,12,18 * * *`

Det svarer under dansk sommertid cirka til 02:10, 08:10, 14:10 og 20:10. GitHub Actions schedules kan være forsinkede; en manglende kørsel på præcis klokkeslættet er ikke i sig selv bevis på fejl.

Den ugentlige agent bruger Copenhagen-tid og er tiltænkt søndag kl. 10:00.


## Mobilapp – UX, releases og visninger

- Mobilappen ligger på branch `mobile-round-entry`; `main` skal forblive urørt, indtil hele live-kæden er testet og brugeren godkender merge.
- Appens visuelle retning skal følge den endelige Pokaloversigt: rolig mobilhierarki, én tydelig hovedhistorie, ens komposition for beslægtede kort, få simple faner, god luft og ingen regnearks-/dashboard-følelse. Undgå "card soup" og grandiose labels som "Hall of Fame".
- Undersider skal have en tydelig bundknap `⌂ Tilbage til forsiden` samt diskret `© 2026 Kardinal IT`.
- Forsiden skal holdes enkel. Funktioner, der naturligt hører til en eksisterende sektion, skal placeres dér frem for at skabe endnu en forsideknap.
- Forsiden har et kompakt "Næste runde"-kort. På sigt skal det drives af `📅 Program 26-27`, ikke være en permanent hardcoded programkopi.
- Spillerprofiler viser de fem aktive spillere og bruger data fra `All Time Pokaler` og `Diagram_Aktiv`. Profildata skal på sigt være dynamiske via Sheet/backend frem for hardcodede snapshots.
- Pokaloversigt, Aktuel stilling og All Time Leader indeholder aktuelt snapshot-data i frontend. Hvor data ændrer sig løbende, er målet at gøre Sheet/backend til source of truth.
- Under Aktuel stilling findes fanen `Udvikling`. For sæson 2026/27 skal den vise hver spillers akkumulerede saldo uge for uge: `samlede gyldige gevinster til og med ugen − akkumuleret indsats`.
- Fast indsatsmodel for 2026/27: alle fem spillere belastes med **80 kr pr. relevant spilleuge**. Diagram_Aktiv og appens sæsonudvikling skal bruge samme beregningsregel. Den historiske sæson må ikke omskrives for at efterligne denne model.
- Udviklingsgrafen må ikke opfinde datapunkter før sæsonstart; vis en tom/starttilstand indtil faktiske data findes.
- Installeret PWA/hjemmeskærmsapp skal kunne opdatere uden manuel cache-rydning. Repoet bruger `sw.js`, network-first fetch, `skipWaiting()`, `clients.claim()`, eksplicit `registration.update()`, `updateViaCache: "none"` og reload ved `controllerchange`.
- Ved hver app-release, der ændrer shell/CSS/JS, skal service-workerens cacheversion og relevante asset-query-versioner hæves konsekvent. Glemte versionsløft kan få den installerede app til at vise gamle filer.
- Når en bruger siger, at en ændring ikke er synlig, kontrollér først GitHub Pages-workflowets status og deployet commit; antag ikke automatisk browser-cache.
- Den originale logo-fil er `assets/oddsklub_logo.jpg` og er den aktive logo-/appikon-kilde. Det gamle SVG-logo må ikke genindføres som primært logo.
- Mobilfrontend bør fortsat være enkel vanilla HTML/CSS/JS uden unødvendigt build-system. Af hensyn til ældre mobilbrowsere foretrækkes konservativ JavaScript-syntaks ved ny funktionalitet.

## Når denne fil vedligeholdes

Opdatér denne håndbog, når projektets datamodel, faste regler eller brugerpræferencer ændres. Undgå at fylde den med midlertidige samtaledetaljer. Dokumentér især beslutninger, der ellers let kan blive glemt og føre til datatab eller gentagelse af tidligere fejl.
