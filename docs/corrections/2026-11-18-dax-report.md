# Sachliche Korrektur: archivierter Tagesbericht 18.11.2026

Die Ausgabe mit Redaktionsschluss 00:55 Uhr bleibt dieselbe historische Ausgabe.
Korrigiert wurden nur die drei DAX-Veränderungsangaben auf Seite 1:

- KPI: -2,63 % zu -2,08 %.
- Tabellenzeile: -704,58 Punkte zu -553,27 Punkte und -2,63 % zu -2,08 %.
- Ein sichtbarer Korrekturhinweis wurde auf Seite 1 ergänzt.

Der Schlussstand bleibt 26.045,37 Punkte. Seiten 2 bis 11 sind textlich und pixelweise unverändert. Die Originalfassung ist in der Git-Historie erhalten (SHA-256 b4277fbd3bfe61ff6278b589dc22e0c9aa85da2fcb1e5f2e95767bb14e9a1511).

## Nachweise

- Schlussbericht vom 17.11.2026: https://www.finanznachrichten.de/nachrichten-2026-11/70157924-boersenschluss-nvidia-nervositaet-drueckt-dax-um-2-08-ins-minus-665.htm . Live gelesen am 18.11.2026 gegen 12:15 Uhr: 26.045,37 Punkte, -2,08 %, 553 Punkte Tagesverlust.
- Timestamp-basierte Tageshistorie: https://query1.finance.yahoo.com/v8/finance/chart/%5EGDAXI?range=5d&interval=1d . Live gelesen am 18.11.2026 gegen 12:15 Uhr: Schlusswerte 13.11. 26749.94921875, 16.11. 26598.640625, 17.11. 26045.369140625. Auf zwei Stellen gerundet ergibt die Veränderung zum 16.11. -553,27 Punkte und -2,08 %.

## Ursache und Schutz

Der Yahoo-Helfer nahm zuvor positionsbasiert den vorletzten gültigen historischen Schlusswert. Wenn eine Tageskerze fehlt, passt dieser Wert nicht zwingend zur Sitzung des aktuellen Kurses. Die falsche Veränderung entspricht rechnerisch dem Vergleich des 17.11. mit dem 13.11. statt mit dem 16.11. Die exakte damalige Yahoo-Rohantwort liegt nicht vor; die fehlende/versetzte Kerze ist daher die rekonstruierte Erklärung, kein archivierter API-Befund.

Der Helfer nutzt jetzt die Zeitstempel und Börsenzeitzone und wählt die letzte historische Sitzung vor dem Kursdatum. Fehlende oder ungültige Referenzen scheitern geschlossen statt eine Nullveränderung zu erfinden. Tests decken Tageskerze vorhanden/fehlend, intraday, Wochenende, Zukunftskerze und fehlende Referenzen ab.

Keine Änderung an Archivpolitik, Zeitplänen, Workflows oder Kosten. Aktuelle Ausgabe und andere Archivtage werden nicht mit den heutigen Intradaykursen überschrieben. Reproduktionsskript: `tools/correct_dax_2026_11_18.py` (nur für die ursprüngliche PDF-Prüfsumme).
