# Bot'ens Bet – stabil identitet (kontraktforslag v1)

Status: **Forslag til review, ikke aktiveret**. Teknisk master ejer den fælles kontrakt; Professor-/Bot-specialisten ejer udvælgelse og strategi. Ingen historiske data omskrives af dette forslag.

## Adskil disse begreber

- `recommendation_id`: identitet for et *forslag*, der kan genpubliceres uændret uden at skabe ny økonomisk aktivitet.
- `coupon_id`: uforanderlig identitet for en **reelt låst** 80 kr-kupon. Ny publiceringsdato alene skaber **ikke** ny `coupon_id`.
- `bet_id`: uforanderlig identitet for en individuel placeret/virtuelt låst indsats inden for en `coupon_id`. Genafspilning af samme feed skal bevare samme ID.
- `fixture_id`: stabilt kamp-ID fra en defineret kilde, plus `kickoff_utc` i ISO 8601. Navne og lokale datoer er ikke sikre identitetsnøgler.
- `settlement_id`: unik idempotensnøgle for en afregningshændelse. Genbehandling af samme hændelse ændrer aldrig totals.
- `duplicate_of`: historisk henvisning til oprindelig kupon; `excluded_from_totals: true` for bevidst udelukket kopi.

## Invarianter

1. En anbefaling er ikke en indsats. Kun eksplicit låst kupon med `coupon_id` kan tilføje indsats.
2. Samme `coupon_id` og `bet_id` må kun forekomme én gang som tællende indførsel; gentagelse er idempotent.
3. Afregning må ikke bygge saldo på antal JSON-records. En autoritativ ledger tæller kun gyldige, ikke-ekskluderede låste bets.
4. Resultatændringer kræver en revisionshændelse med kilde og tidspunkt; ingen tavs overskrivning.
5. `pending/won/lost/void` valideres, og profit beregnes konsekvent af indsats og retur.
6. Den eksisterende `weeks`-struktur og `totals` bibeholdes i overgangsperioden; ekstra felter er valgfrie, indtil producent og forbruger er koordineret og testet.

## Migration uden datatab

A. Bevar historiske records inklusive dubletten 18/10 og `duplicate_of`; ændr ikke eksisterende saldo +79,20 kr.
B. Aftal sammen med specialist, **hvor** ID'erne genereres og låses. Slutbrugeren/visningsappen skal ikke selv opfinde økonomiske identiteter.
C. Tilføj separate testfixtures for ny kupon, identisk genpublicering, delvist afgjort, rettet resultat og void. Test feed mod ledger og UI.
D. Udrul først som additive felter; slå derefter nye valideringskrav til, når både producent og forbruger er klar. Kræv review af kontraktændringer.

## Beslutninger før aktivering

- Hvilken producent/lagringskilde ejer `coupon_id`, `bet_id` og `settlement_id`?
- Hvordan håndteres to reelt særskilt låste kuponer med identiske valg?
- Hvilken kampdatakilde og resultattid er autoritative?
- Hvor gemmes revisionshistorik?

Denne fil er handoff til Professor-/Bot-specialisten og grundlag for kommende PR'er – **ingen runtime-ændring**.
