# FA Nachrichten: media policy and source audit

Checked 2026-10-19. This records evidence and implementation limits, not legal advice.

## Publisher image findings

- tagesschau: https://www.tagesschau.de/rssfeed-ts-104.html limits website RSS reuse to noncommercial offers and prohibits archiving. Removed on the owner's explicit request: 195 archive rows, the two input feeds, source mentions in page/footer/PDF templates. GDELT input and build also reject its domain/subdomains or named source. There were no local news-detail URLs to redirect. Editorial articles were scanned; none cite this publisher.
- FinanzNachrichten.de: https://www.finanznachrichten.de/service/rss.htm explicitly permits revocable reuse of headlines with active links opening a new window. This does not establish image reuse rights. No publisher photos enabled.
- finanzen.net: https://www.finanzen.net/dienste/rss describes RSS subscriptions for private readers. https://www.finanzen.net/nutzungsbedingungen does not provide a blanket photo republication license. Current news RSS https://www.finanzen.net/rss/news was inspected: 10 entries, no enclosure/media:thumbnail/content image elements. No publisher photos enabled.
- GDELT is a discovery source, not a photo license. No socialimage/OG extraction or automatic image copying.
- Yahoo Finance is an old aggregator label in the archive, not necessarily the publisher. Cards label the actual linked domain (e.g. fool.com), not Yahoo.

## Icons

Icons are 16-64px raster copies from publisher-hosted endpoints. They identify linked sources only; no endorsement or affiliation is claimed. This is source identification, not a claim of a blanket copyright/trademark license. Endpoint availability does not establish such a license. icon-sources.json records exact download URLs. No Google favicon service, visitor hotlinks, SVG imports, or automatic retries against blocked sites. Missing icons use monograms. New domains require a reviewed local icon to replace that fallback.

## Thumbnail gate

No external publisher photos currently enabled. news-assets/thumbnails.json is empty. A reviewed exact-article entry may include file (under thumbnails/), credit, rights_url, source_url and reviewed ISO date; a local raster asset must exist. No automatic scraping, OG hotlinking, feed-image harvesting, or license inference. Developer must inspect the image and verify source permission before adding an entry. Do not treat the mere presence of a feed image as permission. Unverified / malformed / remote entries fail closed to a source card. Decorative line graphics in fallback cards are not market data or article photos.

## All currently linked publishers

Default for every unreviewed publisher: no image rights established, photos disabled. The table explicitly distinguishes a found icon from photo permission.

| Linked publisher | Rows | Local icon | Article-photo status |
|---|---:|---|---|
| fool.com | 518 | yes | No image permission established; disabled |
| finance.yahoo.com | 331 | yes | No image permission established; disabled |
| 247wallst.com | 68 | yes | No image permission established; disabled |
| trefis.com | 63 | yes | No image permission established; disabled |
| stocktwits.com | 43 | yes | No image permission established; disabled |
| finanzen.net | 33 | yes | RSS subscriptions described, no photo republication grant found; disabled |
| finanznachrichten.de | 32 | yes | Headline permission only; photos disabled |
| thestreet.com | 30 | monogram | No image permission established; disabled |
| app.moby.co | 14 | monogram | No image permission established; disabled |
| beincrypto.com | 11 | monogram | No image permission established; disabled |
| tikr.com | 10 | monogram | No image permission established; disabled |
| finanzen.ch | 8 | yes | No image permission established; disabled |
| benzinga.com | 6 | yes | No image permission established; disabled |
| investorshub.advfn.com | 4 | yes | No image permission established; disabled |
| qz.com | 3 | yes | No image permission established; disabled |
| t-online.de | 3 | yes | No image permission established; disabled |
| handelsblatt.com | 3 | monogram | No image permission established; disabled |
| zvw.de | 3 | yes | No image permission established; disabled |
| aktiencheck.de | 3 | yes | No image permission established; disabled |
| myfirstmillion.videonest.co | 2 | yes | No image permission established; disabled |
| badische-zeitung.de | 2 | yes | No image permission established; disabled |
| gmx.at | 2 | yes | No image permission established; disabled |
| cnn.com | 2 | yes | No image permission established; disabled |
| weser-kurier.de | 2 | monogram | No image permission established; disabled |
| welt.de | 2 | yes | No image permission established; disabled |
| ibtimes.com | 2 | yes | No image permission established; disabled |
| unchainedcrypto.com | 2 | monogram | No image permission established; disabled |
| moneylion.com | 2 | yes | No image permission established; disabled |
| sn.at | 2 | monogram | No image permission established; disabled |
| deraktionaer.de | 2 | monogram | No image permission established; disabled |
| faz.net | 2 | yes | No image permission established; disabled |
| merkur.de | 2 | yes | No image permission established; disabled |
| deutschlandfunk.de | 1 | yes | No image permission established; disabled |
| wn.de | 1 | monogram | No image permission established; disabled |
| cdn.jwplayer.com | 1 | monogram | No image permission established; disabled |
| marketbeat.com | 1 | yes | No image permission established; disabled |
| independent.co.uk | 1 | monogram | No image permission established; disabled |
| verdict.co.uk | 1 | yes | No image permission established; disabled |
| decrypt.co | 1 | monogram | No image permission established; disabled |
| uk.finance.yahoo.com | 1 | yes | No image permission established; disabled |
| wsj.com | 1 | yes | No image permission established; disabled |
| euronews.com | 1 | yes | No image permission established; disabled |
| proactiveinvestors.com | 1 | yes | No image permission established; disabled |
| usatoday.com | 1 | yes | No image permission established; disabled |
| marketwatch.com | 1 | yes | No image permission established; disabled |
| mopo.de | 1 | monogram | No image permission established; disabled |
| wiwo.de | 1 | yes | No image permission established; disabled |
| sueddeutsche.de | 1 | yes | No image permission established; disabled |
| op-online.de | 1 | yes | No image permission established; disabled |
| ruhrnachrichten.de | 1 | monogram | No image permission established; disabled |
| come-on.de | 1 | yes | No image permission established; disabled |
| nwzonline.de | 1 | monogram | No image permission established; disabled |
| abendzeitung-muenchen.de | 1 | monogram | No image permission established; disabled |
| presseportal.de | 1 | monogram | No image permission established; disabled |
| aerzteblatt.de | 1 | yes | No image permission established; disabled |
| berliner-zeitung.de | 1 | monogram | No image permission established; disabled |
| vol.at | 1 | yes | No image permission established; disabled |
| rbb24.de | 1 | yes | No image permission established; disabled |
| zeit.de | 1 | yes | No image permission established; disabled |
| nw.de | 1 | yes | No image permission established; disabled |
| shz.de | 1 | yes | No image permission established; disabled |
| wa.de | 1 | yes | No image permission established; disabled |
| hna.de | 1 | yes | No image permission established; disabled |
| boerse-online.de | 1 | yes | No image permission established; disabled |

## Integration notes

- Base: 8ae5246 (includes dcbf56c premium UI). data.py/report.py were extracted from the existing payload and are now tracked overrides; the workflow uses tar --skip-old-files, so these patched copies win. Do not drop these files during integration.
- Existing content articles, stock files, navigation, footer design, production workflow, paid services and keys are unchanged. build.py changes to footer are source text only.
- Build-time filter protects public output even if site-bot archive data conflicts during a later rebase. Reapply archive deletion if integrating onto a newer archive.
- No local external-news detail pages existed. Site/news sitemaps contain own pages/articles only. feed.xml and newly generated PDF receive the filtered list. Every build replaces the entire output tree, so old generated reports are not retained. Historic Git commits are not rewritten.
- No recurring network requests for source icons; committed assets work offline.
- Run from site/: python3 -m unittest test_news_media test_stocks; python3 build.py. Local rendering used Playwright with installed Chrome, not a new production dependency. 37 browser assertions passed at 1440/390/320px in light and dark; screenshots inspected in all four requested combinations. Existing generic footer horizontal overflow at mobile widths was reported to the separate footer worker and is outside these news-card changes. The .news-grid itself stays within each viewport.
