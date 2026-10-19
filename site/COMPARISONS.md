# FA comparisons: data, scope and rights

## Sources read on 2026-10-19

- https://vermoegen-sparen.de/daten states its provider JSON data is CC BY 4.0,
  reusable commercially with attribution. The actual JSON has the same licence,
  author, documentation and licence URL. The downloaded snapshot has editorial
  `stand` 2026-10-18, despite the documentation page showing an older summary.
- Feed: https://vermoegen-sparen.de/api/konditionen.json
- Licence: https://creativecommons.org/licenses/by/4.0/deed.de
- https://www.ecb.europa.eu/stats/ecb_statistics/governance_and_quality_framework/html/usage_policy.en.html
  permits free commercial/non-commercial ESCB statistics reuse with source credit,
  unchanged statistics and metadata; excludes third-party data.
- German equivalent: https://www.bundesbank.de/de/startseite/benutzerhinweise/nutzungsbedingungen-regelung-fuer-die-weiterverwendung-von-eszb-statistiken-613500
- API documentation: https://data.ecb.europa.eu/help/api/data

No provider logos, photos, review prose, affiliate URLs or ratings are used. The
provider data subset is credited with CC BY 4.0 and explicitly marked as selected,
rearranged and modeled by FA. No new agreement, account, fee or dependency.

## What ships

`/vergleiche/`, `/vergleiche/tagesgeld/`, `/vergleiche/depot/`,
`/vergleiche/zinsmonitor/`, linked from calculator hub and shared footer, sitemap.

Three savings models: 1822direkt (6-month promo then variable base, cap), GEFA
(whole-balance band), willbe EUR (interest cap). Licensed facts were checked against:

- https://www.1822direkt.de/sparen/tagesgeldkonto/
- https://www.gefa-bank.de/produkt/tagesgeld/
- https://willbe-invest.com/en/save-money/money-market-account

These provider pages are used for validation, not as a recurring scraping feed.
Their copy, images and layouts are not reproduced. Conditions have original concise
FA wording. Broker conditions are a CC-licensed data subset with both editorial and
price-source dates, prominently labeled as not fully verified by FA. Never use
`ordergebuehrEur` to rank: for example flatex has additional venue costs, ZERO has
volume thresholds, and several brokers use percentage/minimum fees. Structured
condition text is shown to avoid pretending one scalar is total cost. Ratings,
regulator/protection claims and comparison scores are not adopted.

The broker A/B calculator is generic, fictional and user-entered, not automatically
assigned to named brokers. Formula includes fixed + percentage order fees and
monthly custody, not tier/min/max/spread/FX taxes. No best-broker recommendation.

ECB: three German monthly MIR series for overnight deposits, deposits <=1 year,
and consumer-credit APRC. Raw CSV retains all observation fields and metadata.
Source status `P` is provisional. All three latest API observations at capture were
2026-08: 0.51%, 2.28%, 8.99%. These are dated official statistics, not live offers.
APRC is not silently substituted for the nominal rate in the loan calculator.
Overnight deposits are broader than advertised Tagesgeld accounts.

## Freshness and refresh

Intentionally dated snapshots, not an unverified auto-updating offer engine. No
visitor-side data requests. Rebuild dates do not change source dates. Age warning
appears after 45 days, including per-broker underlying source date. The feed isn't
blindly refreshed because schema and conditions can change. Review before replacing
`content/comparisons/conditions-2026-10-19.json` or savings-models.json, check licence,
conditions, source dates and calculations, then update visible capture dates.

An explicit `python3 comparisons_data.py` refreshes only three official ECB CSVs,
validates series/unit/date/finite observations and retains the last dated snapshot
on network failures. This is not run automatically by build. After an explicit
refresh, update the visible snapshot date/latest-period copy in comparisons.py.
No implied promise of continuous/current availability.

## Tests

`node test_comparison_math.js`: 14 assertions for promo/base splits, high-balance
cap, eligible/noneligible customer, GEFA boundary and above-band zero, capped willbe,
zero principal, generic broker costs and invalid values.
`python3 -m unittest test_comparisons -v`: CSV units, identity, dates, age banner,
licence/provenance, static page count and no network/storage in client scripts.
Build with standard payload-unpack. Chromium screenshots at 1440/390px light/dark;
all four pages, savings calculations/defaults/invalids/caps and broker input/error
handling. No horizontal overflow or JS exceptions. Rendered pixels inspected.

No package/typechecker added: plain JS is checked with `node --check`; Python
with py_compile and unit tests.
