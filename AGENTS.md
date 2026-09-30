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
- `📲 Rundeindtastning` – autoritativ lodret indtastningsmodel
- `Tabellen` – stillinger og konkurrencer
- `Diagram_Aktiv` – statistik/diagramgrundlag
- `All Time Pokaler`
- `Ture`
- `Ark16`
- `test` – skjult

De gamle faner `Program_Aktiv` og `📱 Program · overblik` er fjernet fra arbejdsarket og må ikke genindføres som afhængigheder.

## Rundeindtastning

Kolonner:
A Uge
B Runde
C Kamp
D Spiller
E Kr
F Mål F
G Mål M
H Point
I Resultat

Grundidé: én spiller pr. række. Når flere spillere hører til samme aktivitet, bør kamp/aktivitet ikke gentages unødigt i kolonne C.

Normalt skal en spiller i D høre til aktiviteten i C. **Fri Odds / "Alle Fri odds" er en særlig fælles aktivitet**, hvor alle fem spillere kan have hver sin række under samme aktivitet.

Kr er én samlet kolonne. Der skal ikke igen opdeles i "Kr Fri" og "Kr CL".

## Statistik og historik

Vær opmærksom på historiske særtilfælde. En tidligere migrering fra den gamle brede model til den lodrette model kunne miste værdier, hvis statistik lå på en aktivitet, hvor spillernavnet ikke stod direkte i kampteksten.

Særligt vigtigt: Pingvinus havde historisk **986 kr** i Fri Odds i uge 37 under "Alle Fri odds". Denne værdi skal bevares i den autoritative model/statistik. Hvis den lodrette model kun viser 716,5 kr for Pingvinus samlet, mangler de 986 kr.

Historiske samlede vundne beløb, før nye indtastninger:
- Kardinalus: 792,72 kr
- King: 1200,55 kr
- Pingvinus: 1702,50 kr
- Kaninus: 660,20 kr
- Gorilla: 1051,50 kr
- Total: 5407,47 kr

Historisk indsats: 1440 kr pr. spiller / 7200 kr samlet.

## Tabellen

Tabellen indeholder bl.a. Champions League, Årets Manager, Topscorer, Hattrick, Saksespark, Årets Mål, Det Gyldne Bur og Sommer Cup.

Designpræference: behold den enkle eksisterende stil. En tidligere redesign-idé med mørkegrønne dashboard-sektioner, ekstra luft og kraftig styling blev fravalgt og rullet tilbage.

Kendt teknisk gæld: Sommer Cup har haft `#REF!`, fordi gamle formler pegede på den slettede `Program_Aktiv`-fane. Reparer dette ud fra de faktiske historiske data/perioder – gæt ikke.

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

## Når denne fil vedligeholdes

Opdatér denne håndbog, når projektets datamodel, faste regler eller brugerpræferencer ændres. Undgå at fylde den med midlertidige samtaledetaljer. Dokumentér især beslutninger, der ellers let kan blive glemt og føre til datatab eller gentagelse af tidligere fejl.
