"""Krypto-Seiten: /krypto/ Uebersicht + /krypto/<slug>/ Detailseiten am Aktien-Rahmen.

Datenlage: Kurswerte aus data/quotes.json (Quelle je Eintrag, Stand = Seitenaufbau).
Chart: TradingView-Widget NUR per Klick (click-to-load, siehe tradingview.js) —
vor dem Klick keine Verbindung zu Dritten. Texte: siehe quellen je Coin.
"""
from html import escape as e
import json, re
from pathlib import Path
ROOT = Path(__file__).parent

def _quotes():
    try: return {q['sym']: q for q in json.loads((ROOT.parent/'data'/'quotes.json').read_text())}
    except (OSError, ValueError): return {}

def _num(x):
    s = ('%.2f' % x)
    return s.replace(',', 'X').replace('.', ',').replace('X', '.')

def _quote_panel(c, q):
    if not q or q.get('price') is None:
        return '<section id="kurs" class="stock-quote"><div><p class="stock-kicker">KURSDATEN</p><h2>Kurs derzeit nicht verfügbar</h2><p>Die Datenquelle liefert aktuell keinen nutzbaren Kurs. Der Chart unten kann optional direkt von TradingView geladen werden.</p></div><p class="stock-note">Keine geschätzten Kurse. Fehlende Daten sind kein Kurs von null.</p></section>'
    pct = q.get('pct')
    pcls = 'up' if (pct or 0) >= 0 else 'dn'
    ptxt = ('+' if (pct or 0) >= 0 else '') + _num(pct) + ' %' if pct is not None else 'nicht verfügbar'
    return ('<section id="kurs" class="stock-quote"><div><p class="stock-kicker">LETZTER VERFÜGBARER KURS</p><h2>%s USD</h2>'
            '<p><span class="%s">%s</span> <span class="mut" style="font-size:12px">(24 h, Quelle: %s)</span></p></div>'
            '<dl><div><dt>Kurszeit</dt><dd>Abruf beim Seitenaufbau</dd></div><div><dt>Datenquelle</dt><dd>%s</dd></div></dl>'
            '<p class="stock-note">Keine Live-Aktualisierung im Browser. Der jeweilige Stand der Seite steht im Footer. '
            '24-Stunden-Angaben beziehen sich auf den rollierenden Tag, nicht auf den Börsenschluss.</p></section>'
            % (_num(q['price']), pcls, ptxt, e(q.get('src', 'ohne Angabe')), e(q.get('src', 'ohne Angabe'))))

def _spark(q):
    try:
        from market_visuals import spark_svg
        if q and q.get('hist') and len(q['hist']) >= 5:
            return '<section class="stock-panel"><h2>Verlauf (3 Monate, Tageswerte)</h2>' + spark_svg(q['hist']) + '<p class="stock-note">Quelle wie Kursdaten oben; Abruf beim Seitenaufbau.</p></section>'
    except ImportError: pass
    return ''

def _tv_panel(c):
    return ('<section class="stock-tv stock-panel" data-tv-symbol="%s" data-tv-widget="advanced-chart"><h2>Kursverlauf interaktiv (TradingView)</h2>'
            '<p>Optional kannst du den interaktiven Chart direkt von TradingView laden (Symbol %s).</p>'
            '<p class="stock-note">Erst beim Klick wird eine Verbindung zu TradingView hergestellt. Dabei werden IP-Adresse, Seitenadresse, Widgettyp und das Symbol übertragen. Laut Anbieter setzt das Widget keine Cookies.</p>'
            '<button type="button" data-tv-load>TradingView-Chart laden und Daten übertragen</button><p role="status" aria-live="polite">Noch nicht geladen.</p>'
            '<div class="tradingview-widget-container"><div class="tradingview-widget-copyright"><a href="https://www.tradingview.com/" rel="noopener noreferrer" target="_blank"><span class="blue-text">Track all markets on TradingView</span></a></div></div>'
            '<p class="stock-note">Falls für dieses Symbol keine Widgetdaten verfügbar sind, bleibt der Chart leer. Keine geschätzten Werte.</p></section>'
            % (e(c['tv_symbol'], quote=True), e(c['tv_symbol'])))

def build_crypto_pages(page, urls, articles, out, base, og_png=None):
    coins = json.loads((ROOT/'crypto.json').read_text())
    assert len({c['slug'] for c in coins}) == len(coins)
    for c in coins:
        assert re.fullmatch('[a-z0-9-]+', c['slug'])
        assert (ROOT/'logos'/c['logo']).is_file(), c['logo']
    from stocks import related
    quotes = _quotes()
    assets = ('<link rel="stylesheet" href="/stocks.css"><script src="/tradingview.js" defer></script>'
            '<style>.crypto-grid .stock-card{grid-template-columns:64px minmax(0,1fr) auto}</style>')

    def card(c):
        q = quotes.get(c['sym'])
        if q and q.get('price') is not None:
            pct = q.get('pct'); pcls = 'up' if (pct or 0) >= 0 else 'dn'
            ptxt = ('+' if (pct or 0) >= 0 else '') + _num(pct) + ' %' if pct is not None else ''
            price = '<span><strong>' + _num(q['price']) + ' USD</strong> <small class="' + pcls + '">' + ptxt + ' (24 h)</small></span>'
        else:
            price = '<span><strong>Kurs derzeit nicht verfügbar</strong></span>'
        return ('<a class="stock-card" href="/krypto/%s/"><span class="stock-monogram" aria-hidden="true">'
                '<img class="stock-logo" src="/stock-logos/%s" alt="%s Logo" width="40" height="40" loading="lazy"></span>'
                '<span><strong>%s</strong><small>%s · %s · Kryptowert</small></span>%s<span aria-hidden="true">↗</span></a>'
                % (c['slug'], e(c['logo'], quote=True), e(c['name'], quote=True), e(c['name']), e(c['unit']), e(c['sym']), price))

    body = (assets + '<main class="stock-wrap"><div class="stock-hero"><p class="stock-kicker">FA MARKTDATEN</p>'
            '<h1>Kryptowerte einordnen.</h1><p>Die auf finanz adjust gelisteten Kryptowerte mit Kurs, Verlauf und redaktioneller Einordnung. Keine Anlageberatung.</p></div>'
            '<section aria-labelledby="crypto-title"><div class="stock-heading"><h2 id="crypto-title">Gelistete Kryptowerte</h2><span>%d Werte</span></div>'
            '<div class="stock-grid crypto-grid">%s</div></section>'
            '<aside class="stock-info"><h2>Was du hier findest</h2><p>Jeder gelistete Kryptowert hat eine eigene Seite mit Kursdaten, Verlauf und Einordnung der FA Redaktion. Kursdaten kommen nach Verfügbarkeit vom genannten Anbieter; ein interaktiver Chart kann optional per Klick von TradingView geladen werden.</p>'
            '<p>Keine Kaufempfehlungen, keine Kursziele. <a href="/risikohinweis/">Zum Risikohinweis</a></p></aside></main>'
            % (len(coins), ''.join(card(c) for c in coins)))
    urls.append(page('/krypto/', 'Bitcoin und Ethereum: Kurse und Einordnung | finanz adjust',
                     'Die gelisteten Kryptowerte mit aktuellem Kurs, Verlauf und sachlicher Einordnung der FA Redaktion. Keine Anlageberatung.',
                     body, act='/maerkte/', crumbs=[('/maerkte/', 'Märkte'), ('/krypto/', 'Kryptowerte')]))
    if og_png: og_png(out + '/og/krypto.png', 'Bitcoin · Ethereum: Kurse und Einordnung', 'Kryptowerte', 'Kurs, Verlauf und Einordnung · finanz-adjust.de')

    for c in coins:
        q = quotes.get(c['sym'])
        matches = related(c, articles)
        news = ''.join('<li><a href="/artikel/%s/">%s</a><p>%s</p></li>' % (e(a['slug']), e(a['title']), e(a.get('description', ''))) for a in matches)
        if not news: news = '<li>Noch kein eigener FA-Artikel zu diesem Thema. <a href="/artikel/">Alle Artikel lesen</a></li>'
        src_q = (q or {}).get('src', '')
        facts = [('Symbol', c['sym']), ('Werteinheit', c['unit']), ('Netzwerk', c['name']), ('Kurswährung', 'USD')]
        if src_q: facts.append(('Kursdatenquelle', src_q))
        facts.append(('Logo', c['logo_credit']))
        quel = ''.join('<li><a href="%s" target="_blank" rel="noopener noreferrer">%s ↗</a></li>' % (e(u, quote=True), e(t)) for t, u in c['quellen'])
        ein = ''.join('<p>%s</p>' % e(p) for p in c['einordnung'])
        path = '/krypto/%s/' % c['slug']
        body = (assets + '<main class="stock-wrap"><div class="stock-back"><a href="/maerkte/">← Alle Märkte</a></div>'
                '<header class="stock-title"><div><p class="stock-kicker">KRYPTOWERT · USD</p><h1>%s</h1><p>Marktseite · FA Redaktion</p></div>'
                '<span class="stock-tag"><img class="stock-logo" src="/stock-logos/%s" alt="%s Logo" width="40" height="40"></span></header>'
                '<nav class="stock-tabs" aria-label="Seitenabschnitte"><a href="#kurs">Kursdaten</a><a href="#steckbrief">Steckbrief</a><a href="#einordnung">Einordnung</a><a href="#news">FA-Artikel</a></nav>'
                '%s%s%s'
                '<div class="stock-columns"><section id="steckbrief" class="stock-panel"><h2>Steckbrief</h2><dl class="stock-facts">%s</dl>'
                '<p class="stock-note">Die Angaben beziehen sich auf die hier genannte Notierung in US-Dollar. Andere Handelsplätze können andere Kurse stellen.</p>'
                '<p><a class="stock-source" href="%s" target="_blank" rel="noopener noreferrer">Logo-Quelle und Lizenz ↗</a></p></section>'
                '<section id="news" class="stock-panel"><h2>Aus der FA Redaktion</h2><ul class="stock-news">%s</ul></section></div>'
                '<section id="einordnung" class="stock-info"><h2>Einordnung und Risiken</h2>%s'
                '<h3>Quellen für diese Einordnung</h3><ul class="stock-news">%s</ul>'
                '<p>Diese Seite dient der Information, nicht der Anlageberatung. <a href="/risikohinweis/">Risiken verstehen</a></p></section></main>'
                % (e(c['name']), e(c['logo'], quote=True), e(c['name'], quote=True),
                   _quote_panel(c, q), _spark(q), _tv_panel(c),
                   ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (e(k), e(v)) for k, v in facts),
                   e(c['logo_source'], quote=True), news, ein, quel))
        urls.append(page(path, '%s (%s): Kurs, Verlauf und Einordnung | finanz adjust' % (c['name'], c['unit']),
                         '%s aktuell: Kurs in USD, 3-Monats-Verlauf und sachliche Einordnung der FA Redaktion. Keine Anlageberatung.' % c['name'],
                         body, act='/maerkte/', crumbs=[('/maerkte/', 'Märkte'), ('/krypto/', 'Kryptowerte'), (path, c['name'])],
                         og='/og/krypto-%s.png' % c['slug'] if og_png else None))
        if og_png: og_png(out + '/og/krypto-%s.png' % c['slug'], '%s (%s): Kurs und Einordnung' % (c['name'], c['unit']), 'Kryptowerte', 'Kurs, Verlauf und Einordnung · finanz-adjust.de')
