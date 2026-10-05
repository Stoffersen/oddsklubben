# Oddsklubben mobilindtastning

Mobil-first prototype til sæson 2026/27.

## Formål
Appen skal gøre rundeindtastning enkel: programmet bestemmer uge, runde, kampe og spillere; brugeren indtaster primært gevinst i kr. og resultat. Senere skrives data til Google Sheet-fanen `📲 Rundeindtastning`.

## Sikker udvikling
Denne branch skriver **ikke** til produktionsarket endnu. Først færdiggøres og testes UI/validering. Sheet-skrivning kobles på via et autoriseret backend-lag, så credentials ikke ligger i browseren.

## Lokal prototype
Åbn `index.html`. Appen er uden build-step og kan hostes statisk, fx på GitHub Pages.
