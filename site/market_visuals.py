"""Static, dependency-free market visuals for the website: market breadth, mover cards,
heatmap page and per-stock sparkline. Uses existing data only (data/quotes.json, data/stock-quotes.json)."""
import json
from html import escape as e
from pathlib import Path
from report_visuals import universe, spark as _spark, stock_meta

ROOT = Path(__file__).resolve().parent
LINK = '<link rel="stylesheet" href="/market.css">'


def _num(v, d=2):
    s = '{:,.{d}f}'.format(v, d=d)
    return s.replace(',', 'X').replace('.', ',').replace('X', '.')


def _sg(p):
    return ('+' if p > 0 else '') + _num(p)


def _cls(p):
    return 'up' if p > 0 else 'dn' if p < 0 else 'mut'


def _stocks():
    try:
        Q = json.loads((ROOT.parent / 'data' / 'quotes.json').read_text())
    except (OSError, ValueError):
        Q = []
    return Q, universe(Q)


def spark_svg(hist, w=240, h=56):
    return _spark(hist, w, h).replace('class="sp"', 'class="mv-spark" role="img" aria-label="Kursverlauf der letzten Wochen"', 1)


def breadth(stocks):
    n = len(stocks)
    if not n:
        return ''
    up = sum(1 for q in stocks if q['pct'] > 0)
    dn = sum(1 for q in stocks if q['pct'] < 0)
    flat = n - up - dn
    seg = lambda c, k: '<i class="%s" style="width:%.1f%%"></i>' % (c, 100.0 * k / n) if k else ''
    return ('<section class="mv-breadth" aria-label="Marktbreite"><h2>Marktbreite <small>%d Aktien</small></h2>'
            '<div class="mv-bar" role="img" aria-label="%d im Plus, %d unverändert, %d im Minus">%s%s%s</div>'
            '<div class="mv-bl"><span class="up"><b>%d</b> im Plus</span><span class="mut"><b>%d</b> unverändert</span><span class="dn"><b>%d</b> im Minus</span></div>'
            '<p class="mv-note">Zählung der Tagesveränderung, keine Prognose und keine Empfehlung.</p></section>') % (
        n, up, flat, dn, seg('u', up), seg('f', flat), seg('d', dn), up, flat, dn)


def _mark(q):
    s = stock_meta(q)
    t = (s['ticker'] if s else q['sym'])[:2].upper()
    if s and s.get('logo'):
        return '<img class="mv-logo" src="/stock-logos/%s" alt="" width="28" height="28">' % e(s['logo'], quote=True)
    return '<span class="mv-mono" aria-hidden="true">%s</span>' % e(t)


def _card(q):
    s = stock_meta(q)
    href = '/aktien/%s/' % s['slug'] if s else None
    inner = '%s<span class="mv-n"><b>%s</b><small>%s</small></span><span class="mv-v"><b>%s</b><span class="%s">%s %%</span></span>' % (
        _mark(q), e(q['name']), e(q['sym'].split('.')[0]), _num(q['price']), _cls(q['pct']), _sg(q['pct']))
    return '<a class="mv-card" href="%s">%s</a>' % (href, inner) if href else '<div class="mv-card">%s</div>' % inner


def movers(stocks):
    r = sorted(stocks, key=lambda q: -q['pct'])
    gl = [q for q in r if q['pct'] > 0][:4]
    lo = [q for q in r if q['pct'] < 0][-4:][::-1]
    col = lambda t, L, c: '<div><h3 class="%s">%s</h3>%s</div>' % (c, t, ''.join(_card(q) for q in L) or '<p class="mv-note">Heute keine Aktie in dieser Richtung.</p>')
    return '<section class="mv-movers"><h2>Bewegung des Tages</h2><div class="mv-two">%s%s</div></section>' % (
        col('Größte Gewinner', gl, 'up'), col('Größte Verlierer', lo, 'dn'))


def heat_tiles(stocks):
    tiles = []
    for q in sorted(stocks, key=lambda q: -q['pct']):
        a = min(abs(q['pct']) / 4.0, 1.0)
        rgb = '20,116,60' if q['pct'] >= 0 else '198,40,40'
        al = 0.16 + 0.74 * a
        s = stock_meta(q)
        tag = ('a href="/aktien/%s/"' % s['slug'], 'a') if s else ('div', 'div')
        tiles.append('<%s class="mv-tile%s" style="background:rgba(%s,%.2f)"><b>%s</b><span>%s %%</span></%s>' % (
            tag[0], ' strong' if al > .6 else '', rgb, al, e(q['name']), _sg(q['pct']), tag[1]))
    return '<div class="mv-heat">%s</div>' % ''.join(tiles)


def home_block(stocks):
    if not stocks:
        return ''
    return LINK + '<div class="mv-home">%s%s<p class="mv-note"><a href="/heatmap/">Zur Aktien-Heatmap →</a></p></div>' % (breadth(stocks), movers(stocks))


def heatmap_page(stocks, stamp):
    body = ('<div class="w">%s<div class="hero" style="grid-template-columns:1fr"><div class="hl"><h1>Aktien-Heatmap</h1>'
            '<p>Tagesveränderung von %d Aktien auf einen Blick. Stand %s. Kursdaten von Twelve Data und Yahoo Finance, ggf. verzögert, ohne Gewähr.</p></div></div>'
            '<div class="pn">%s%s<p class="mv-note">Farbe zeigt die Tagesveränderung, die Sättigung steigt bis ±4 %%. Die Kacheln sind nach Veränderung sortiert, '
            'nicht nach Börsenwert. Keine Anlageberatung. <a href="/risikohinweis/">Risiken verstehen</a></p></div></div>') % (LINK, len(stocks), e(stamp), breadth(stocks), heat_tiles(stocks))
    return body


def stock_spark_panel(stock):
    """Sparkline panel for a stock page, only when a verified history exists."""
    try:
        Q = json.loads((ROOT.parent / 'data' / 'quotes.json').read_text())
    except (OSError, ValueError):
        return ''
    q = next((x for x in Q if x['sym'].split('.')[0].upper() == stock['ticker'].upper() and x.get('hist')), None)
    if not q or len(q['hist']) < 5:
        return ''
    h = q['hist']
    ch = (h[-1] / h[0] - 1) * 100 if h[0] else 0
    return (LINK + '<section class="stock-panel mv-stockspark" style="margin-top:24px"><h2>Kursverlauf</h2>%s'
            '<p class="stock-note">Letzte %d Handelstage, Quelle: %s. Verlauf im Zeitraum <b class="%s">%s %%</b>. Vergangene Entwicklung ist kein Indikator für die Zukunft.</p></section>') % (
        spark_svg(h, 640, 120), len(h), e(q.get('src', 'Yahoo Finance')), _cls(ch), _sg(ch))
