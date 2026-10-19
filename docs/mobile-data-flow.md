# Mobilapp – dataflow

Browseren indeholder aldrig Google credentials.

## Flow
1. Appen viser programmet for valgt uge.
2. Brugeren indtaster Kr og Resultat.
3. Frontend validerer og viser en bekræftelse.
4. Payload består af `week`, `round` og strukturerede `entries` med kamp, spiller, money og resultat.
5. Apps Script validerer payload igen.
6. Backend skriver **kun** A:E og I i `📲 Rundeindtastning`.
7. F:H og J:K er beskyttet af designet: backend adresserer aldrig disse kolonner.
8. Script lock forhindrer samtidige dobbelt-skrivninger.
9. Hvis en eksisterende uge/runde-blok har et andet antal rækker end den nye payload, stoppes skrivningen i stedet for at gætte.

## Aktuel aktivering og status (19. oktober 2026)
Frontend er koblet til en deployet Apps Script-URL i `app/app.js`. Backend er **dry-run som standard**, men skriver, når Script Properties har `SPREADSHEET_ID` og `WRITE_ENABLED=true`.

Projektets `AGENTS.md` dokumenterer en tidligere vellykket end-to-end 0-kr-test og aktiveret live-skrivning. Det er **ikke** en live-kontrol af den aktuelle Script Property. Ved ny session skal backendens GET (`writeEnabled`) og respons på en autoriseret faktisk gemning (`status: "written"`) bruges som bevis; undgå testskrivning til produktionsark uden tilladelse.

Appen viser forbindelsesstatus i `#sheetWriteStatus`. Kun `status:"written"` udløser teksten `Gemt i Google Sheet`. Efter skrivning anvendes `SpreadsheetApp.flush()`, `sortStandings_(ss)` og endnu en `flush()` til genberegning og sortering af de relevante blokke i `Tabellen`. Om alle stillingsformler er semantisk korrekte kræver særskilt kontrol.

Denne sektion erstatter den forældede besked om, at frontend endnu ikke var koblet på.
