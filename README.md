# Oddsklubben

Oddsklubbens website og mobilapp med program, rundeindtastning, stillinger, pokaler, ture, spillerarkiv, regler og historisk statistik.

## Aktiv udvikling

Den aktuelle arbejds-/previewgren er `mobile-round-entry`. `main` holdes urørt, indtil ændringer er testet og godkendt.

Mobilappen bruger Google Sheet som source of truth for sæsonprogram og live rundeindtastning. Website-delen er primært udviklet til desktop/PC; mobilbesøgende på website anbefales at bruge appen.

## Vigtige projektregler

Læs `AGENTS.md` før ændringer i repo, Google Sheet, statistik eller datamodel. Den fil er projektets vedvarende agenthåndbog og beskriver bl.a. dataflow, Grundloven, release/cache-regler, Transfermarkt-verifikation og deployment-gates.

Alle commits på den aktive arbejdsgren skal efterfølges af en succesfuld GitHub Actions-deployment, før ændringen betragtes som færdig.

## Visuel retning

Mobilappen skal fortsat være lys, enkel og funktionel. Desktop-websitet må være mere redaktionelt og legende. Et illustreret Oddsklubben-univers med King, Kaninus, Gorilla, Kardinalus og Pingvinus er godkendt som retning, men billed-assets er endnu ikke implementeret i repoet.
