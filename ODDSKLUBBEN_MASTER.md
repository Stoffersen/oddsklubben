# ODDSKLUBBEN – fælles teknisk master

Status: Forslag til fælles styring. Oprettet 2026-10-19. Dette dokument beskriver ansvar og arbejdsprocesser, ikke verificeret implementeringsstatus.

## Formål
Én fælles kilde til beslutninger for ODDSKLUBBEN-appen, Professorens spilforslag og Bottens bet. Forskellige chats må gerne specialisere sig, men de må ikke træffe modstridende tekniske beslutninger eller antage, at andre chats automatisk kender ændringer.

## Roller
- **ODDSKLUBBEN-app-masterchat = teknisk master**: endeligt ansvar for systemarkitektur, fælles datakontrakter, GitHub, deployment, integrationer, afregning, saldi og regressionstests.
- **Professoren og Botten-masterchat = betting-specialist**: ansvar for analysemetoder, spiludvælgelse, oddsstrategi, evaluering og læring; foreslår tværgående ændringer til teknisk master.
- App-masteren håndterer også UX, klubfunktioner, stillinger og rundeindtastning.
- Kun ét ansvarligt arbejdsforløb må ændre et delt område ad gangen. Rollefordeling er en arbejdsaftale, ikke en teknisk adgangsbegrænsning.

## Regler for ændringer
1. Læs dette dokument og den relevante aktuelle kildekode **før** en ændring. Kontrollér branch, seneste commits, åbne PR'er og eksisterende dokumentation.
2. Betting-specialisten kan arbejde på isolerede analyseændringer, men ændringer i delte datamodeller, saldi, afregning, API'er, visning, Sheets eller workflows skal koordineres med den tekniske master.
3. Arbejd på særskilt branch og brug pull request ved tværgående ændringer. Undgå direkte ændringer i main fra konkurrerende chats.
4. Verificér automatiske tests, deployment og bagudkompatibilitet, før ændringer betragtes som afsluttede. Rapportér præcist, hvad der er verificeret, og hvad der ikke er.
5. Registrér ændringer, beslutninger og åbne fejl i GitHub; antag aldrig, at chat-historik alene er en fælles hukommelse.
6. Foretag ikke ændringer i andre repositories eller apps uden særskilt instruktion.

## Fælles integritetskrav (mål – skal verificeres mod kode)
- Hvert reelt bet har en stabil unik identitet og kan ikke krediteres/debiteres to gange; gentagelse af samme anbefaling er ikke automatisk et nyt bet.
- Et bet kan have status pending, won, lost, void eller tilsvarende eksplicit afregning; afregning er idempotent.
- Kun fremtidige, ikke-afgjorte kampe må fremgå af nye spilforslag; tidszoner og resultatkilde skal kontrolleres.
- Appvisning, historik og saldo skal baseres på samme autoritative afregningsdata.
- Google Sheets-indtastning og øvrige integrationsstatusser må kun vises som aktive, hvis de er testet.
- Fejlsituationer og manuelle rettelser logges, så data ikke tavst ændres.

## Prioriteret fælles kvalitetsliste
1. Gennemgå mulige dubletter i Bottens bets og saldo.
2. Undersøg gamle bets, der stadig står som afventende.
3. Kontroller tidsfilter for Professorens foreslåede kampe.
4. Verificér rundeindtastning -> Google Sheets -> opdaterede stillinger.
5. Etablér automatiske tests for ovenstående, og identificér derefter øvrige forbedringer.

Denne liste er baseret på tidligere rapporterede problemer og angiver **ikke**, at problemerne fortsat er til stede eller er løst.

## Overdragelse mellem chats
Ved afslutning af et udviklingsforløb skal chatten notere:
- Hvad der blev ændret, hvilke filer/PR'er/commits, og hvorfor.
- Hvilke tests der er udført og deres faktiske resultater.
- Hvad der mangler, næste sikre handling og eventuelle risici.
- Om der kræves ændring af fælles kontrakter eller indgriben fra teknisk master.

## Startinstruktion for alle nye chats
1. Find og verificér repository `Stoffersen/oddsklubben` og den aktuelle standardbranch.
2. Læs `ODDSKLUBBEN_MASTER.md`, øvrig relevant dokumentation, commits, PR'er og faktisk kode.
3. Fortsæt kun inden for din rolles mandat; koordinér fælles ændringer.
4. Afslut med dokumenteret status i GitHub og tydelig besked om eventuelle begrænsninger.
