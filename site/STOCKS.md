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

Adapter: `TwelveData.quote(stock)` liefert eine normalisierte Quote oder `None`; `refresh()` nutzt eine Provider-Kette mit derselben Methode. Keine stillen Börsenplatz-/Währungswechsel; jeder Kurs nennt seinen tatsächlichen Anbieter. Fehler erhalten nur bereits zulässige und datierte Cachewerte. Ohne Aktivierungsschalter wird auch ein alter Cache NICHT ausgeliefert.

Cache: `data/stock-quotes.json`, drei Stunden TTL, maximal 16 neue Einzelabfragen je Build, älteste Werte zuerst. Twelve Data: höchstens 8 Abfragen pro 61 Sekunden. Der Workflow läuft sechsmal täglich, maximal 96 neue Credits/Tag für diesen Adapter, zusätzlich zum Altbestand. Builddaten sind keine Livekurse. Cachewerte werden mit Kurszeit, Abrufzeit und einem Hinweis ab sechs Stunden Cachealter angezeigt. Die tatsächliche Börsenverzögerung wird nicht erfunden, wenn der Anbieter sie nicht liefert. Internationale Titel können im Gratisplan fehlen und bleiben dann ohne Kurs. Keine Quote wird als null dargestellt.

## Stammdaten

US-Ticker und Handelsplätze: https://www.sec.gov/files/company_tickers_exchange.json (Abruf 19.10.2026). Slug/Anzeigename sind lokale Navigationslabels. ADR/US-Notierungen werden ausdrücklich benannt. Deutsche Titel: verlinkte TradingView-Symbolseiten, einzelne ISINs zusätzlich durch Börse Frankfurt/Finanztrends geprüft. `stocks.json` enthält je Eintrag Quelle und Prüfdatum. ISINs werden nicht geraten. Startumfang 34 Titel, keine Zusage einer weltweiten Suche.

Prüfen: `cd site && python3 -m unittest test_stocks.py` und `python3 build.py`. Anschließend HTML, Sitemap, Suche (inklusive leerer Trefferliste), Tastatur und mobile Ansicht prüfen. Keine erfolgreichen Live-API-Preise behaupten, bevor ein Test mit dem echten API-Key erfolgreich war. Der lokale Workspace hat keinen API-Key; der erste echte Abruf muss im Actions-Build geprüft werden.

## Ausbau 19.10.2026: Verzeichnis, Unternehmensdaten, Fallback

195 Notierungen (statt 34), davon 183 mit aus Quellen gelesener ISIN. Keine Aussage, dass DAX/MDAX/Nasdaq/S&P heute vollständig abgebildet sind: historische Indexlisten dienen nur der Stammdaten-Kreuzprüfung. Deka ETF-Portfolios (13./16.10.2026) liefern aktuelle Wertpapier-Identitäten; SEC liefert die US-Notierung. Kein Fuzzy-Matching zur Laufzeit. Der kuratierte Katalog enthält nur geprüfte Crosswalk-Ergebnisse, keine alternativen Vorzugs-/Schuld-/Optionswerte aus ähnlichen Emittentennamen. Fehlende ISINs bleiben leer.

Quellen:
- https://www.deka-etf.de/etfs/Deka-Nasdaq-100-UCITS-ETF
- https://www.deka-etf.de/etfs/Deka-DAX-UCITS-ETF/composition_data
- https://www.deka-etf.de/etfs/Deka-MDAX-UCITS-ETF/composition_data
- https://www.deka-etf.de/etfs/Deka-EURO-STOXX-50-UCITS-ETF/composition_data
- https://markets.businessinsider.com/index/market-capitalization/s&p_100
- https://en.wikipedia.org/wiki/DAX und https://en.wikipedia.org/wiki/MDAX (historische Ticker-Kreuzprüfung, KEINE aktuelle Mitgliedschaftszusage)

API-Rotation: nur US-Titel sind für den Gratis-API-Abruf (Twelve Data) eingeplant. Europäische Titel nutzen seit 28.10.2026 den Yahoo-Fallback (siehe unten), danach den freiwilligen Widget-Fallback. Erfolgreiche Kurse und fehlgeschlagene Abrufversuche haben getrennte Zeitstempel; Ausfälle blockieren deshalb nicht dauerhaft die übrigen Titel. Bei 16 neuen Abfragen/Build und sechs geplanten Builds/Tag sind es weiterhin höchstens 96 neue Quote-Credits/Tag. Größeres Verzeichnis bedeutet nicht Echtzeitkurse für alle Titel; komplette Rotation braucht mehrere Builds/Tage. Zusätzliche manuelle Builds verbrauchen zusätzliche Credits, ebenso die bisherige Marktübersicht.

## Yahoo-Fallback 28.10.2026

Ursache des Ausbaus: Alle 67 Xetra-Titel (api_enabled=false) und BRK-B hatten keinen API-Kurs; die Seiten zeigten "keine Kursdatenquelle angebunden". Twelve Data Basic deckt XETR nur als Tagesendstand in hoeheren Tarifen (geprueft 28.10.2026: https://twelvedata.com/exchanges/xetr), ein kostenpflichtiger Tarif ist nicht freigegeben.

Umsetzung in `stock_data.py`: Provider-Kette Twelve Data (nur api_enabled-Titel, Credit-Budget 16/Build), danach Yahoo Finance (chart-Schnittstelle ohne Schluessel, eigenes Budget 48/Build, 429/999 stoppt weitere Yahoo-Abrufe des Builds). Getrennte Budgets blockieren sich nicht gegenseitig. Gleiche Strenge wie bisher: Symbol-, Handelsplatz- (Yahoo exchangeName GER fuer Xetra, NMS fuer Nasdaq, NYQ fuer NYSE) und Waehrungsabgleich; Abweichungen werden verworfen. Jeder Kurs traegt Quelle und Quell-Link seines tatsaechlichen Anbieters ("Kursdaten: Yahoo Finance" bzw. Twelve Data). Angezeigt werden Boersenzeit (Anbieter-Zeitstempel) und Abrufzeit getrennt; die Xetra-Verzoegerung von 15 Minuten laut Yahoo-Hilfeseite (https://help.yahoo.com/kb/exchanges-data-providers-yahoo-finance-sln2310.html) wird am Kurs ausgewiesen, sonst "nicht ausgewiesen, kein Echtzeitversprechen".

Rechtliche Einordnung unveraendert: Der Eigentuemer waehlte diesen Weg am 18.10.2026 ("als fallback yahoo") und 19.10.2026 ("mach trotzdem mit api live") ausdruecklich nach Hinweis auf die Anzeigebeschraenkungen; das ist seine bewusste Entscheidung, keine Anbieterfreigabe. Yahoo untersagt Weiterverbreitung (oben verlinkt). Der TradingView-Klick-Fallback bleibt fuer Titel ohne verwertbare API-Antwort bestehen.

TradingView: vom Eigentümer am 19.10.2026 ausdrücklich als API-Fallback gewünscht. Offizielles Symbol-Info-Widget, ausschließlich bei fehlendem gültigen API-Kurs, exchange-qualifiziert. KEIN Netzwerkaufruf, Skript, iframe, Prefetch oder gespeicherte Einwilligung vor Klick. Der Klick nennt die übertragenen Daten (IP, Seitenadresse, Symbol, Widgettyp). Laut Anbieter keine Cookies: https://www.tradingview.com/widget-docs/faq/general/ . Datenschutz ist entsprechend angepasst. Widgetfläche reserviert 352px und verhindert dadurch nachträgliche Layoutverschiebung. Branding/Attribution bleiben sichtbar. Xetra wird vom Anbieter mit EOD-Daten geführt; manche Symbole sind nur auf TradingView selbst verfügbar. Ein Widget ist keine Garantie für Datenabdeckung.
- https://www.tradingview.com/widget-docs/widgets/symbol-details/symbol-info/
- https://www.tradingview.com/widget-docs/markets/europe/
- https://www.tradingview.com/widget-docs/faq/data/
- https://www.tradingview.com/policies/

Unternehmensdaten: zwölf US-Starttitel enthalten lokal gespeicherte SEC-Registerfakten (Legalname, SIC/Branche) mit einzelnem Quelllink und Abrufdatum. Keine vollständigen Wikipedia-Texte kopiert, keine ungeprüften KGV/Dividenden oder vermischten XBRL-Perioden. Die SEC-API ist kostenlos und ohne Schlüssel; Entwicklungshinweise: https://www.sec.gov/search-filings/edgar-application-programming-interfaces . Keine neuen Browseranfragen an die SEC.

Mehr freie Daten: Wikidata ist für strukturierte Profile attraktiv (CC0; https://www.wikidata.org/wiki/Wikidata:Licensing). SEC Company Facts liefert kostenlose Fundamentaldaten, die aber Perioden/Einheiten/Restatements korrekt unterscheiden müssen. Nicht in diesem Patch als KGV o.ä. versprochen. Wikipedia-Text erfordert passende Lizenz/Attribution, Commons-Bilder individuelle Rechteprüfung.

Logos: Iconify-Frameworklizenz gilt nicht pauschal für seine Icons. Simple Icons erklärt selbst, dass CC0 für das Projekt nicht alle enthaltenen Marken freigibt; individuelle Rechte/Markenrichtlinien prüfen: https://raw.githubusercontent.com/simple-icons/simple-icons/develop/DISCLAIMER.md . Keine pauschale Übernahme oder Hotlink-Logo-API eingebaut; aktuelle Monogramme bleiben bis zur Einzelprüfung. Empfohlen: kleine geprüfte lokale SVG-Auswahl, Marken nur zur redaktionellen Identifikation, Quellen/Lizenz/Markenhinweise dokumentiert, keine neue Paketabhängigkeit nötig.

On demand: Die Suche fügt keine Aktien hinzu. GitHub Pages nimmt keine sicheren serverseitigen Besucheranfragen an. Keine API-Keys oder GitHub-Tokens in JS. Ohne neuen Dienst kann ein geplanter Build einen verifizierten Symbolkatalog erweitern, aber nicht Besucherwünsche speichern. Echter Besucher-Request -> Warteschlange -> geprüfter Build verlangt ein Backend/Edge-Endpunkt mit Rate-Limit/Missbrauchsschutz und Eigentümerfreigabe für diesen neuen Dienst. Noch nicht implementiert.

Ein erstes Unternehmenslogo ist umgesetzt: Intel, lokal aus dem offiziellen Pressepaket, nur zur redaktionellen Identifikation mit sichtbarem Copyright-Credit Intel Corporation. Intels eigene Presse-Seite erlaubt ausdrücklich redaktionelle Online-Nutzung; siehe `logos/SOURCES.md`. Keine pauschale Markennutzungsfreigabe für andere Unternehmen behauptet.

## Firmenlogos und OG-/Bildgrafiken 28.10.2026

18 Trending-Titel (u. a. Nvidia, Apple, Tesla, SAP, Rheinmetall) erhalten echte Firmenlogos statt Monogrammen: Karten auf /aktien/, Movers/Heatmap (market_visuals) und Kopfbereich der Aktienseite nutzen das vorhandene logo-Feld in stocks.json; Dateien in site/logos/, Auslieferung unter /stock-logos/. Logos liegen auf einer weissen Kachel (stocks.css/market.css), damit dunkle Marken auf den dunklen Flaechen lesbar bleiben. Quellen/Lizenzen je Datei in site/logos/SOURCES.md (Commons-Einzelpruefung: 17x Public domain, NVIDIA Apache-2.0; Markenrecht unberuehrt, nur redaktionelle Kennzeichnung).

Pro Titel mit Logo erzeugt build.py zusaetzlich /og/aktien/<slug>-logo.png (1200x630): Firmenlogo gross mittig auf weisser Kachel, Name/Ticker/Handelsplatz, unten finanz-adjust.de. Nutzung: og:image/twitter:image und Schema-image der Aktienseite, sichtbare Einbindung als <figure class="stock-ogimg"> mit Caption/Bildnachweis auf der Aktienseite sowie <image:image>-Eintraege in sitemap.xml (xmlns:image). Hintergrund: Google Bilder indexiert nur sichtbare <img>-Grafiken im Seitenkontext, OG allein reicht nicht (gepruefter Stand 28.10.2026: https://developers.google.com/search/docs/appearance/google-images). Keine Ranking- oder Indexierungszusage.


## Firmenlogos, zweiter Ausbau 28.10.2026

59 weitere Katalogtitel erhalten echte Firmenlogos nach demselben Vorgehen wie der erste Ausbau: gleiche Darstellung (weisse Logo-Kachel), gleiche OG-/Bildgrafik pro Aktienseite, Einzelpruefung jeder Commons-Datei (alle Public domain; Markenrecht unberuehrt, nur redaktionelle Kennzeichnung). Quellen je Datei in site/logos/SOURCES.md. Einige Dateien liegen als hochaufloesender PNG-Render der Commons-SVG vor, weil der Wikimedia-Originaldienst die SVG-Bytes zeitweise begrenzt hat (HTTP 429); Darstellung und Rechteangabe sind identisch. Nicht uebernommen wurden Titel ohne gepruefte aktuelle Konzernmarke auf Commons (u. a. BASF, E.ON, Novo Nordisk); diese behalten vorerst ihre Monogramme statt eines veralteten oder fremden Logos.
