// Developer-only GA4/consent test (not part of the production build). Needs playwright outside the tree:
//   NODE_PATH=/path/to/node_modules ROOT=site/out PREFIX=fa ID=G-T2V8C566K9 node tools/monetization/test-ga4.cjs
const { chromium } = require('playwright'), http = require('http'), fs = require('fs'), path = require('path'), assert = require('assert');
let root = process.env.ROOT || path.resolve(__dirname, '../../site/out'), prefix = process.env.PREFIX || 'fa', id = process.env.ID || 'G-T2V8C566K9', shots = process.env.SCREENSHOT_DIR || '/tmp/ga3-' + prefix;
fs.mkdirSync(shots, { recursive: true });
let server = http.createServer((req, res) => { let f = path.join(root, decodeURI(req.url.split('?')[0])); if (f.endsWith('/')) f += 'index.html'; if (!path.extname(f) && fs.existsSync(f + '.html')) f += '.html'; try { res.setHeader('Content-Type', f.endsWith('.js') ? 'text/javascript' : f.endsWith('.css') ? 'text/css' : f.endsWith('.svg') ? 'image/svg+xml' : 'text/html'); res.end(fs.readFileSync(f)); } catch (e) { res.statusCode = 404; res.end('missing'); } });
(async () => {
  await new Promise(r => server.listen(0, '127.0.0.1', r)); let b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] }), n = 0;
  function ok(x, m) { assert(x, m); n++; }
  try {
    for (let width of [1440, 390, 320]) {
      let ctx = await b.newContext({ viewport: { width, height: 900 } }), page = await ctx.newPage(), remote = [];
      await ctx.route('https://**/*', r => { remote.push(r.request().url()); return r.fulfill({ contentType: 'application/javascript', body: '/* intercepted */' }); });
      let base = 'http://127.0.0.1:' + server.address().port;
      // utm_source ist freigegebener Wert, utm_campaign-Wert und q sind es nicht
      await page.goto(base + (prefix === 'fa' ? '/cookies/' : '/cookies.html') + '?utm_source=newsletter&utm_campaign=geheim123&q=private@example.test');
      ok(remote.length === 0, 'kein Remote ohne Consent');
      ok(!(await page.locator('#' + prefix + '-statistics').isDisabled()), 'Statistik waehlbar');
      ok(await page.locator('#' + prefix + '-advertising').isDisabled(), 'Werbung gesperrt');
      ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'kein Overflow');
      await page.screenshot({ path: shots + '/drawer-' + width + '.png' });
      await page.locator('[data-consent="reject"]').click(); await page.reload();
      ok(remote.length === 0, 'kein Remote nach Ablehnen');
      await page.locator('[data-' + prefix + '-consent-open]').click();
      await page.locator('#' + prefix + '-statistics').check();
      await page.locator('[data-consent="save"]').click();
      await page.waitForFunction(() => document.querySelector('script[src*="googletagmanager"]'));
      ok(remote.length === 1 && remote[0].includes(id), 'gtag nur nach Einwilligung');
      let q = await page.evaluate(() => dataLayer.map(x => Array.from(x))), cf = q.find(x => x[0] === 'config')[2], v = q.find(x => x[0] === 'event')[2];
      ok(cf.cookie_expires === 15552000 && cf.cookie_update === false, 'Cookie-Profil 180 Tage, kein Update');
      ok(cf.allow_google_signals === false && cf.allow_ad_personalization_signals === false, 'Signals/Werbung aus');
      ok(cf.send_page_view === false, 'manueller page_view');
      ok(cf.cookie_domain === '127.0.0.1', 'Cookie host-only');
      ok(!('page_location' in cf) && !('page_referrer' in cf), 'Config ohne location/referrer');
      ok(v.page_location.includes('utm_source=newsletter'), 'freigegebener utm-Wert bleibt');
      ok(!v.page_location.includes('geheim123') && !v.page_location.includes('q='), 'nicht freigegebene Query-Werte verworfen');
      ok(v.page_referrer === '', 'kein Roh-Referrer');
      ok(v.content_group === 'other', 'content_group gesetzt');
      ok(q[0][2].analytics_storage === 'denied' && q[1][2].analytics_storage === 'granted', 'Consent-Reihenfolge');
      // excludePaths: Tokenrouten bleiben trotz Einwilligung komplett ohne Tag
      await page.goto(base + '/newsletter-bestaetigt/');
      ok((await page.locator('script[src*="googletagmanager"]').count()) === 0, 'Exclude-Route ohne gtag');
      ok(remote.length === 1, 'Exclude-Route ohne Remote');
      await page.goto(base + (prefix === 'fa' ? '/cookies/' : '/cookies.html'));
      await page.waitForFunction(() => document.querySelector('script[src*="googletagmanager"]'));
      ok(remote.length === 2, 'Tag laedt auf erlaubter Route wieder');
      // Widerruf: Cookies geloescht, Tag weg
      await page.evaluate(() => document.cookie = '_ga=fixture;path=/');
      await page.locator('[data-' + prefix + '-consent-open]').click();
      await page.locator('[data-consent="reject"]').click();
      await page.waitForFunction(() => !window.dataLayer);
      ok(!(await ctx.cookies()).some(x => x.name === '_ga'), '_ga geloescht');
      ok(remote.length === 2, 'kein Remote nach Widerruf');
      await page.goto(base + (prefix === 'fa' ? '/datenschutz/' : '/datenschutz.html'));
      ok((await page.locator('#ga4-disclosure').textContent()).includes('19. Oktober 2026'), 'GA4-Offenlegung vorhanden');
      ok(!(await page.locator('body').textContent()).includes('noch kein Statistikdienst'), 'kein Alt-Text');
      ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'kein Overflow Datenschutz');
      await page.locator('#ga4-disclosure').scrollIntoViewIfNeeded();
      await page.screenshot({ path: shots + '/privacy-' + width + '.png' });
      await ctx.close();
    }
    console.log(prefix + ': ' + n + ' assertions; all HTTPS intercepted');
  } finally { await b.close(); server.close(); }
})().catch(e => { console.error(e); server.close(); process.exitCode = 1; });
