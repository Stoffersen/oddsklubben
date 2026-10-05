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

## Sikker aktivering
Backend er dry-run som standard. Script Properties skal have `SPREADSHEET_ID`. Først når `WRITE_ENABLED=true` sættes, kan der skrives. Frontend er endnu ikke koblet til en deployet endpoint-URL.

Det betyder, at koden til live-skrivning nu findes, men den kan ikke ændre Google Sheet i den nuværende tilstand.
