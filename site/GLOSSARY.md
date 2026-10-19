# FA glossary

## First release

58 curated German entries across seven topic areas. This is a growing selection,
not an exhaustive finance dictionary. No prices, price targets, current rates,
trading signals or personalized recommendations are generated.

## Data and sources

`content/glossary.json` stores plain text, never executable HTML. Each entry has:
slug, term, aliases, category, short definition, explanation, caution, related
slugs, visible FAQ, verification date and sources (name, exact URL, source
section, checked date). Definitions are independently worded summaries, not
copied source articles. The source date is a factual check date, not the build
time; subsequent scheduled builds do not silently refresh it.

Sources read for this release: Bundesbank glossary, Verbraucherzentrale finance
glossary, STOXX DAX profile, S&P Global PMI FAQ, ZEW expectations methodology and
Morningstar volatility glossary. The Verbraucherzentrale's general glossary is
older and contains historical/current-policy details that are not suitable for
blind reuse. Such details (tax amounts, deposit-insurance deadlines, current
index composition, policy targets) were intentionally not copied. DAX's 40
constituents are checked against STOXX, not the older overview. No third-party
logos, remote scripts or paid data providers are introduced.

## Rendering and compatibility

`site/glossary.py` renders the index and all detail pages through the existing
page wrapper, so canonical URLs, breadcrumbs, sitemap registration, theme and
header remain consistent. The six original glossary slugs remain unchanged.
Existing `/artikel/glossar-zew-index/` and
`/artikel/glossar-einkaufsmanagerindex/` remain articles at their old addresses;
contextual cross-links are added after rendering. No existing article wording
is overwritten. Related articles are matched with normalized whole-word terms
and aliases; related glossary terms are explicitly curated. Selected entries
also link to the stock directory and existing stock pages, without implying a
recommendation.

The index uses static, crawlable links and a DefinedTermSet. Detail pages have
DefinedTerm, WebPage with FA Redaktion and source citations, and FAQPage with
answers identical to visible text. Valid structured data does not guarantee
rich results or search ranking. FAQ rich results are subject to search engine
eligibility rules, not something this project can promise.

`glossary.js` filters locally, including ae/oe/ue spellings and aliases. Search
and topic state can be shared via query parameters. No cookies, storage or
network requests are used by the glossary search. Without JavaScript, all
entries remain linked alphabetically and a note explains the search limit.
CSS is scoped to glossary classes; the shared footer fix is limited to pages
with the glossary main element.

## Validate

```sh
# Fresh checkout: unpack legacy build dependencies, as CI already does.
cat payload-*.b64 | base64 -d | tar xz --skip-old-files
cd site
python3 build.py
python3 -m unittest test_glossary test_stocks -v
node --check glossary.js
```

No workflow, API enablement or quote configuration is changed by this feature.
Local validation does not need data.py or fresh quote collection.
Browser QA: light/dark at 1440px and 390px; detail pages; no horizontal overflow;
Umlaut search, TER alias, combined topic filter, empty state and reset; no
JavaScript page errors. Source dates and related links must be reviewed when
adding or editing definitions. Keep examples clearly illustrative and check
all arithmetic rather than treating an example as market data.
