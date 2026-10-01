# Mobilapp – dataflow

Browseren må aldrig indeholde Google credentials.

Flow når integrationen aktiveres:
1. Appen viser kun programdata for valgt uge.
2. Brugeren indtaster Kr og Resultat.
3. Browseren validerer felterne og viser en bekræftelse.
4. Payload sendes til Apps Script-webappen.
5. Apps Script validerer igen og skriver kun til de tilladte inputkolonner i `📲 Rundeindtastning`: A-E og I.
6. F-H samt J-K forbliver Sheet-formler/hjælpekolonner og må ikke overskrives af appen.
7. Backend skal være idempotent pr. uge/runde, så et dobbelttryk ikke opretter dubletter.

Aktuel status: frontend-validering og lokal kladde er implementeret. Backend-skelettet er dry-run og skriver ikke til arket, før sæsonskiftet er gennemført/godkendt.
