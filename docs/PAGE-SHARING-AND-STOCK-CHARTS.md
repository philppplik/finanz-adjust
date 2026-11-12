# Page sharing and optional stock charts

Implemented 2026-11-12 for the explicit request covering broker, stock and learning-path pages.

- `tools/page_sharing.py` injects exactly one passive sharing group into supported directory and detail pages. Targets are the canonical page URL, not the current URL or its query string. Existing article sharing remains unchanged. No share service is contacted until the visitor follows a link; copy and native-share actions remain local browser actions.
- Broker overview cards now link only to the internal broker detail page. Provider and official pricing links remain in each detail page. Existing facts and source dates are unchanged. Detail titles use a real h1.
- Stock pages previously showed TradingView only when an individual API quote was missing. The separate historical-series panel is available only for stocks present in the aggregate history cache, so TTWO could have a quote but no chart. The optional advanced chart now appears independently of the quote, using the existing exchange-qualified symbol mapping (`NASDAQ:TTWO`). No additional quote API calls, provider subscriptions, backend or keys were added.
- TradingView code/iframes load only on an explicit per-page click, with disclosure of the data transfer. Consent is not persisted. The attribution/source link remains visible, and space is reserved for the 420px widget plus attribution. Source and time of the static API quote are not conflated with the chart. No holdings, trades or personal portfolio were created.

Validation: `cd site && python -m unittest test_site_sharing_chart test_stocks test_broker`. The local layout build uses existing source data and skips remote refresh/PDF/OG rendering, without changing production build logic. Pixel inspection covers 390px and 1280px, both themes, chart consent before/after, and passive share targets. Production CI runs the normal build.

TradingView references checked during this change:
- https://www.tradingview.com/symbols/NASDAQ-TTWO/
- https://www.tradingview.com/widget-docs/widgets/charts/advanced-chart/

## Yahoo previous-close correction

The five-day chart API's `chartPreviousClose` refers to the range baseline, not necessarily the previous trading session. It was incorrectly labelled as prior close (TTWO208.90 while current231.31 and reported dailychange2.969%). The parser now accepts only explicit `regularMarketPreviousClose` or `previousClose` metadata and stores its provenance. Old Yahoo cache entries without that provenance do not render the misleading prior-close field. The main price, source and timestamps are unchanged. No number is reconstructed from rounded percentages and no extra API fetch is introduced. Regression tests cover the mismatched range baseline and safe explicit previous close.
