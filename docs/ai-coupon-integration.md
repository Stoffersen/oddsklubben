# AI-kuponaflæsning – sikker integration

Den eksisterende lokale OCR er en begrænset fallback. Den nye AI-knap i `app/bet-image-upload.js` vises **kun**, når `window.ODDSKLUBBEN_COUPON_AI_ENDPOINT` er sat til en godkendt HTTPS-backend.

## Krav til backend

- En billedforstående model skal udtrække bookmaker, hold/kampe, spilvalg, spiltype, samlede odds, indsats og potentiel/udbetalt gevinst.
- Returnér JSON med `coupon` (felter `bookmaker`, `selection`, `bet_type`, `decimal_odds`, `stake_dkk`, `payout_dkk`) og `warnings` (array af strenge).
- Manglende oplysninger skal være `null`, aldrig opdigtede. Udledte odds skal mærkes eksplicit i `warnings`.
- AI-output er et **forslag**. Brugeren skal kontrollere og godkende før lokal lagring.
- Beskyt API-nøgler udelukkende som server-side secrets. Implementér adgangskontrol, rate limiting, maksimal billedstørrelse, CORS-allowlist, logredaktion og passende opbevaringspolitik.
- Kræv eksplicit samtykke før billedet sendes til AI-tjenesten.
- Der må **ikke** skrives til Google Sheet eller central bettingjournal uden særskilt tilladelse og en sikker, testet integration.

## Aktiveringsprocedure

1. Deploy og test en sikret AI-backend med ovenstående kontrakt.
2. Test med rigtige kuponbilleder, inkl. kombinationskuponer og delvist synlige billeder.
3. Konfigurér frontend med den korrekte HTTPS-URL **før** kuponlæser-scriptet indlæses, eksempelvis via en separat, gennemgået konfigurationsfil.
4. Først derefter kan AI-knappen aktiveres. Indtil da er ingen billeder sendt til eksterne AI-tjenester.

**Status:** Frontend-kontrakten er implementeret; ingen backend eller API-nøgle er provisioneret. AI-aflæsning er derfor endnu ikke aktiv.
