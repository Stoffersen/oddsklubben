# Bot Bet – kontrolleret aktivering og rollback

**Status: PLAN, IKKE PRODUKTION.** Teknisk master ejer godkendelser. Professor/Bot-specialist ejer analyse og producentadapter efter aftalt kontrakt. Se issue #11, PR #9, #10, #12, #13, #14.

## Merge- og release-graf
- PR #9 er et **særskilt dokumentforslag** direkte mod `mobile-round-entry`.
- Implementeringsstakken er `#10 → #12 → #13 → #14 → denne PR`. Merge kun nedefra og op, genbasér om nødvendigt, og kontrollér hver PR's diff efter retarget.
- En grøn PR-test er **ikke** godkendelse af runtime. Hvert merge til `mobile-round-entry` starter Pages-deployment; derfor skal produktionsuafhængighed verificeres før hver merge.
- Ingen af de ovenstående PR'er aktiverer ledgeren; hold integrationen bag eksplicit konfigurationsgate (default OFF), og verificér det via tests.

## Gate 0: ejerskab og sikkerhed
- [ ] Godkend kontraktens felter og schema-version sammen med Professor-specialist via issue #11.
- [ ] Udpeg ledger-host med **persistent storage**, backup-ansvarlig, single-writer-identitet og placering af hemmeligheder.
- [ ] Vælg autoritativ fixture/scorekilde, UTC-felter, void-policy og dokumenteret kildehierarki.
- [ ] Godkend adgangsmodel, monitorering, RPO/RTO, backuprotation og gendannelsesprocedure.
- [ ] Bekræft ingen produktionsledger på kortlivet GitHub Actions-runner eller GitHub Pages.

## Gate 1: isoleret teknik
- [ ] Alle unit-/kontrakt-/restart-/backup-tests grønne på præcis SHA.
- [ ] Review SQLite-håndtering af samtidige processer, fejlscenarier og kædede revisionshændelser.
- [ ] Security-review og arkitekturtest: ugyldige id'er, replay, forkert korrektion, fejl i kilde, rollback.
- [ ] Review schema/migrationskode; ingen syntetiske historiske lock-events.

## Gate 2: producent/forbruger-kontrakt
- [ ] Specialist tilføjer stabile `recommendation_id` i producent (separat aftalt PR).
- [ ] Autoritativ låsekomponent udsteder `coupon_id`/`bet_id` og persisterer før publicering.
- [ ] Publisher afleder read-only `weeks/totals` med schema-version og opdateringsstempel.
- [ ] Appen understøtter gamle data samt nye valgfrie felter; kontrakttests fra producent til snapshot til UI.
- [ ] Genpublicering samme ID ændrer aldrig saldo; særskilt låsning kræver eksplicit autoriseret handling før kickoff.

## Gate 3: shadow mode
- [ ] Skriv isoleret ledger i skyggetilstand, uden at skifte appens datafeed.
- [ ] Sammenlign afledte totals og historik med nuværende publicerede feed uden at omskrive legacy.
- [ ] Bevar dubletten 18/10 som ekskluderet historik; baseline = indsats **160,00 kr**, retur **239,20 kr**, saldo **+79,20 fiktive kr** (snapshot observeret 19/10/2026, ikke fremtidig fast forventning).
- [ ] Dokumentér reelle og forventede afvigelser, indtil der ikke findes uafklarede økonomiske forskelle.

## Gate 4: go-live og verificering
- [ ] Tag gendannelsestestet backup og fastfrys feedversion / rollback-commit.
- [ ] Aktiver ny publisher/ledger med ét kontrolleret skift, uden dobbelt writer.
- [ ] Kontrollér konkret bet-ID, afregning, historiestatus, totals, kildeangivelse og appvisning.
- [ ] Kør gentagen sync og revisionsscenario; sikre ingen ekstra udbetaling.
- [ ] Først derefter erklæres systemet aktivt; dokumentér SHA, databasens identitet og verifikation i issue #11.

## Rollback
1. Stop ny writer/publisher og forebyg fortsatte transaktioner; opbevar database, logs og backup.
2. Peg appens read-only feed tilbage på den sidste verificerede legacy-snapshot/commit; **slet ikke** nye hændelser.
3. Kontroller saldo og historik mod før-skift baseline samt transaktioner efter skift; markér evt. afvigelse åbent.
4. Udfør årsagsanalyse og afstem hændelser idempotent før genaktivering. Restore kræver eksplicit godkendelse; overskriv ikke en nyere auditlog med gammel backup uden afstemning.

## Ikke-opfyldt indtil bevis foreligger
Persistent runtime-host, producentadapter, single-writer-drift, scorekilde, automatiseret krypteret/off-site backup, fuld revisionskæde, real-world end-to-end-afregning og rollback-øvelse. Dokumentation alene tæller ikke som test.
