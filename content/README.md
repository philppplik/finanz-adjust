# Artikel-Pipeline (FA Redaktion)

Artikel liegen als JSON in `content/articles/<slug>.json` und werden beim Build
zu `/artikel/<slug>/` gerendert (NewsArticle- und FAQPage-Schema, Breadcrumbs,
Quellen, Risikohinweis-Box, Byline "FA Redaktion").

Schema:
```json
{
  "slug": "dax-wochenausblick-2026-10-19",
  "title": "...",
  "description": "(Meta-Description, ~150 Zeichen)",
  "section": "markt|einordnung|glossar|krypto",
  "date": "2026-10-19T07:00:00+02:00",
  "body": "<p>HTML-Absätze</p><h2>Zwischenüberschrift</h2>...",
  "image": "/images/<slug>.jpg",
  "sources": [{"title": "...", "url": "https://..."}],
  "faq": [{"q": "...", "a": "..."}]
}
```

Redaktionelle Regeln (Pflicht):
- Keine Anlageberatung: keine Kursziele, keine Kauf-/Verkaufsempfehlungen,
  keine Handlungsaufforderungen. Einordnung mit Quellen statt Tipps.
- Nur verifizierbare Fakten mit echten, abrufbaren Quellen (am Artikelende).
- Keine erfundenen Zitate, keine Politikberichterstattung.
- Ton: trendy, aber seriös; kurze Sätze, Einsteiger-Erklärungen.
- KI-Hinweis und Risikohinweis werden automatisch ergänzt.
- "image" (optional): Titelbild unter /images/<slug>.jpg (1600x900),
  Variante /images/<slug>-800.jpg (800px) wird per srcset eingebunden.

Kursdaten benötigen das Repo-Secret `TWELVEDATA_API_KEY` (Free Tier,
twelvedata.com). Ohne Secret fällt `data.py` auf Yahoo Finance zurück.
Krypto läuft über CoinGecko (kein Key nötig, Attribution im Footer).
