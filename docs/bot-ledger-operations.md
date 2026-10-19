# Bot ledger drift – anbefalet gate (ikke aktivt)

## Beslutning
SQLite kan bruges som **reference og lokal enkelt-writer løsning**, men ikke som vedvarende autoritativ database i en almindelig GitHub Actions-runner: runnerens filsystem er midlertidigt. GitHub Pages er statisk og må kun modtage et read-only snapshot. Produktionslager skal køre hos en vedvarende, adgangskontrolleret vært med verificerede backups og en enkelt autoriseret skriveproces. Vælg faktisk host/credentials/operatør før aktivering; denne PR vælger ikke en leverandør.

## Anbefalet dataflow
1. Professorens producent udsender kandidatforslag; disse er ikke indsatser.
2. Kun den autoriserede lock-service skriver en dokumenteret ny kupon/transaktion med stabile ID'er og valideret før-kickoff-tid.
3. En settlement-worker læser resultatkilder og skriver idempotente hændelser inkl. korrektioner til samme ledger.
4. En read-only publisher genererer versionsmærket `weeks/totals` JSON. Appen læser kun denne kopi.
5. Automatiske kontrakttests og manuel sammenligning af legacy-tallene gates for aktivering.

## Krav til drift
- Eneste writer med least-privilege credentials og låst transaktionsgrænse.
- Database på persistent volume med dokumenteret recoverability; aldrig commit SQLite-database/secrets til Git.
- Backup med SQLite's konsistente online backup API, kryptering, off-site rotation og tidsstyret restore-prøve. Medfølgende `backup_ledger` er *kun* en primitiv: ingen scheduler, retention, kryptering eller remote lager.
- Valider, at gendannelse kan replaye seneste kendte hændelser, og at revisionskæde/ID'er og summer matcher.
- Appen viser ikke et nyt tal uden verificeret snapshot-kontrol og revisionsspor.
- Udpeg RPO/RTO, advarsler, adgangsrevision og operatør før go-live.

## Migrationsgate
- Bevar historisk `bot-bets.json` uændret, inklusive 18/10-dubletten og +79,20 fiktive kr.
- Importér ikke legacy-rækker som opdigtede lock/settlement-hændelser.
- Start skyggekørsel: beregn snapshot parallelt, sammenlign uden at publicere; ingen dobbeltbet.
- Gennemfør dokumenteret accepttest: dubletter, replay, void, korrektion, ugyldigt beløb, crash/genstart, restore og producent/app-kompatibilitet.
- Først efter godkendt producentadapter og driftsreview skiftes dataflow under kontrolleret rollbackplan.

## Afgrænsning
Dette dokument fastlægger sikkerhedsgates, ikke produktionsstatus. Se issue #11 og PR #9, #10, #12, #13.
