# Aktienverzeichnis und Datenadapter

## Auslieferung

GitHub Pages liefert statische HTML-Seiten unter `/aktien/` und `/aktien/<slug>/` aus. Die Suche filtert lokal nach Name, Ticker, Alias und vorhandener ISIN. Alle Einträge sind auch ohne JavaScript verlinkt. Kanonische URLs, Breadcrumbs, WebPage/Corporation-Daten und Sitemap kommen aus dem bestehenden Builder. Es gibt keine neue npm/Python-Abhängigkeit, keinen Server und kein Edge-Abonnement.

Die Quellen lagen bisher als tar.gz/base64 in `payload-1.b64`. `site/build.py` wird absichtlich als lesbare Quelldatei versioniert: der vorhandene Workflow entpackt mit `--skip-old-files` und erhält diese neuere Version. Neue Dateien `stocks.*` und `stock_data.py` werden ebenfalls normal versioniert.

## Daten und Rechte: wichtig

Ein kostenloser API-Zugang ist keine Erlaubnis zur öffentlichen Anzeige. Der Eigentümer wurde am 19.10.2026 über die ausdrückliche Gratisplan-Beschränkung informiert und entschied danach: "Oke mach trotzdem mit api live". Der Workflow aktiviert deshalb die Kursanzeige mit `STOCK_QUOTES_ENABLED=1`. Dies dokumentiert eine bewusste Veröffentlichungsentscheidung des Eigentümers, KEINE vom Anbieter erteilte Lizenz. Die Nutzung bleibt möglicherweise vertragswidrig; Quellenangabe und Verzögerungshinweis heilen das nicht. Abhilfe: auf einen Anbieter mit passenden öffentlichen Anzeigerechten wechseln oder eine geeignete Erlaubnis von Twelve Data erhalten. Zum Abschalten die Variable entfernen oder auf `0` setzen; dann wird auch kein Cache ausgeliefert.

Twelve Data untersagt Free-Tier-Nutzung zu kommerziellen Zwecken und verlangt eine ausdrückliche Erlaubnis für Redistribution/externe Anzeige:
- https://twelvedata.com/terms
- https://support.twelvedata.com/en/articles/5332349-commercial-and-personal-usage
- https://support.twelvedata.com/en/articles/5335783-trial

Yahoo Finance untersagt Weiterverbreitung: https://help.yahoo.com/kb/SLN2310.html
Stooq §5.3 verlangt Zustimmung: https://stooq.com/terms.html
ECB erlaubt genaue Wiedergabe mit Quellenangabe, bietet aber keine Aktienkurse: https://www.ecb.europa.eu/services/disclaimer/html/index.en.html

Die bestehende allgemeine Marktübersicht verwendet bereits Yahoo/Twelve Data. Das ist kein Rechtebeleg und wird mit diesem Patch nicht erweitert. Die neuen Aktienseiten übernehmen diese Kurse NICHT; auch der globale Kursticker wird dort nicht übernommen. Die bisherige Marktübersicht muss separat geprüft werden.

## Aktivierung und Betrieb

Der Builder liest `STOCK_QUOTES_ENABLED=1` und `TWELVEDATA_API_KEY` ausschließlich serverseitig. Der Workflow setzt die Aktivierungsvariable; der API-Key kommt aus dem bestehenden Actions-Secret. Der API-Schlüssel wird nicht in HTML/JS geschrieben. Keine Schlüssel in Repository-Dateien, Fehlermeldungen oder Browsercode.

Adapter: `TwelveData.quote(stock)` liefert eine normalisierte Quote oder `None`; `refresh()` akzeptiert alternative Provider mit derselben Methode. Keine stillen Yahoo-Fallbacks oder Börsenplatz-/Währungswechsel. Fehler erhalten nur bereits zulässige und datierte Cachewerte. Ohne Aktivierungsschalter wird auch ein alter Cache NICHT ausgeliefert.

Cache: `data/stock-quotes.json`, drei Stunden TTL, maximal 16 neue Einzelabfragen je Build, älteste Werte zuerst. Twelve Data: höchstens 8 Abfragen pro 61 Sekunden. Der Workflow läuft sechsmal täglich, maximal 96 neue Credits/Tag für diesen Adapter, zusätzlich zum Altbestand. Builddaten sind keine Livekurse. Cachewerte werden mit Kurszeit, Abrufzeit und einem Hinweis ab sechs Stunden Cachealter angezeigt. Die tatsächliche Börsenverzögerung wird nicht erfunden, wenn der Anbieter sie nicht liefert. Internationale Titel können im Gratisplan fehlen und bleiben dann ohne Kurs. Keine Quote wird als null dargestellt.

## Stammdaten

US-Ticker und Handelsplätze: https://www.sec.gov/files/company_tickers_exchange.json (Abruf 19.10.2026). Slug/Anzeigename sind lokale Navigationslabels. ADR/US-Notierungen werden ausdrücklich benannt. Deutsche Titel: verlinkte TradingView-Symbolseiten, einzelne ISINs zusätzlich durch Börse Frankfurt/Finanztrends geprüft. `stocks.json` enthält je Eintrag Quelle und Prüfdatum. ISINs werden nicht geraten. Startumfang 34 Titel, keine Zusage einer weltweiten Suche.

Prüfen: `cd site && python3 -m unittest test_stocks.py` und `python3 build.py`. Anschließend HTML, Sitemap, Suche (inklusive leerer Trefferliste), Tastatur und mobile Ansicht prüfen. Keine erfolgreichen Live-API-Preise behaupten, bevor ein Test mit dem echten API-Key erfolgreich war. Der lokale Workspace hat keinen API-Key; der erste echte Abruf muss im Actions-Build geprüft werden.
