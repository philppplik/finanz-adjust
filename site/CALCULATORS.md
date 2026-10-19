# Original FA finance calculators

Eight model calculators at `/rechner/`: savings, compound growth, ETF fee comparison,
withdrawals, inflation, fully amortizing loan, CAGR, and gross dividends. Own code,
copy and inline SVGs. No new packages, provider feeds, affiliate links, tax tables,
logos or third-party scripts. finanzen.net was inspected only for categories.

## Model semantics

- Annual effective investment returns become `(1+r)^(1/12)-1`. Payments and withdrawals
  occur at month-end. Investments reinvest all modeled returns.
- ETF cost rates become multiplicative monthly asset deductions; not an assertion
  about actual fund accounting. No fees on new month-end deposits in that month.
- Withdrawals stop at zero; the final partial payout counts toward actual withdrawals.
  Constant return is not a safe withdrawal model or sequence-risk simulation.
- Inflation is fixed and user-defined; both today's purchasing power and the future
  nominal amount needed for the same purchasing power are shown.
- Loans use nominal annual interest / 12 and fully amortize over whole years.
  No bank rounding, fees, effective APR, interest resets or prepayments.
- CAGR excludes intervening flows. Dividends are gross only; no tax-law claims.
- All defaults are examples, not current data, recommendations or forecasts.

Inputs use strict German notation. `1.5` is rejected instead of silently becoming
1.5 or 15; `1.500` is 1500, `1,5` is 1.5. Query URLs use machine decimal points
and restore to German form. Ranges and whole-year restrictions are validated.
No `eval`, network calls or storage in the new scripts. Sharing is explicit: it
puts values in the URL and warns that history, logs and recipients may see them.
The existing site shell still has its own theme/consent behavior.

Static explanations, formulas, risks, FAQ and links work without JS. Computation
needs JS and says so. SVG charts have titles/descriptions, distinguish lines by
color and dashes, and have a complete annual table alternative. Results use a
polite live region, invalid input is announced and focused. Keyboard controls are
native. Source links and fixed review dates appear on each tool. Structured FAQ
matches visible content, without promising rich results.

Integration: three-line import/build hook after glossary (before sitemap), nav
entry and footer link. Output-only glossary cross-links avoid changing glossary.py.
All nine URLs are registered in the sitemap. No workflow changes. Existing payload
must be unpacked on a fresh clone as CI already does.

## Validation

```sh
cat payload-*.b64 | base64 -d | tar xz --skip-old-files
cd site
node test_calculator_math.js
python3 -m unittest test_calculators test_glossary test_stocks test_news_media -v
node --check calculators.js
node --check calculator-math.js
python3 build.py
```

32 mathematical assertions: zero/negative return, compound annual-to-monthly,
month-end contributions, fee compounding/equal fees, depletion/partial withdrawal,
inflation/deflation, zero-rate loan, annuity known value and final balance,
CAGR/total loss, gross dividend. Python tests cover static page structure, glossary
references and no new storage/network. Local Chromium tested all eight initial
outputs, German invalid input, query share/reload/reset and zero exceptions at
390px. Hub/detail screenshots at 1440/390 in light/dark were inspected.

Not included: live broker/depot/Tagesgeld comparisons. No licensed free data feed
has been selected; that is separate product/reuse research, not a reason to ship
unverified offers. No accounts, contracts or affiliate programs were created.
