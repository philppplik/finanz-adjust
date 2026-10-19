"""Visual building blocks for the PDF Tagesbericht: sparklines, heatmap, breadth bar,
stock cards (Intel logo with editorial permission, otherwise monograms) and news source icons.
No network access; every asset is read from the repository and embedded as data URI."""
import base64, collections, json, re
from html import escape as esc
from pathlib import Path
from news_media import identity

ROOT = Path(__file__).resolve().parent
UP, DN, MUT = '#0b8a5e', '#c62828', '#6b7080'


def _stocks():
    try:
        return json.loads((ROOT / 'stocks.json').read_text())
    except (OSError, ValueError):
        return []


def stock_meta(q):
    """Match a quote row to stocks.json by ticker (SAP.DE -> SAP)."""
    t = q['sym'].split('.')[0].upper()
    return next((s for s in _stocks() if s['ticker'].upper() == t), None)


def _uri(path):
    p = Path(path)
    if not p.is_file():
        return None
    mime = 'image/png' if p.suffix == '.png' else 'image/svg+xml'
    return 'data:%s;base64,%s' % (mime, base64.b64encode(p.read_bytes()).decode())


def spark(hist, w=90, h=26, color=None):
    pts = [float(x) for x in (hist or []) if x is not None]
    if len(pts) < 2:
        return '<span class="mut">–</span>'
    lo, hi = min(pts), max(pts)
    rng = (hi - lo) or 1.0
    xs = [i * (w - 2) / (len(pts) - 1) + 1 for i in range(len(pts))]
    ys = [h - 2 - (v - lo) / rng * (h - 4) for v in pts]
    c = color or (UP if pts[-1] >= pts[0] else DN)
    line = ' '.join('%.1f,%.1f' % (x, y) for x, y in zip(xs, ys))
    area = '1,%d %s %.1f,%d' % (h, line, xs[-1], h)
    return ('<svg class="sp" viewBox="0 0 %d %d" width="%d" height="%d" xmlns="http://www.w3.org/2000/svg">'
            '<polygon points="%s" fill="%s" fill-opacity=".12"/>'
            '<polyline points="%s" fill="none" stroke="%s" stroke-width="1.4" stroke-linejoin="round" stroke-linecap="round"/>'
            '<circle cx="%.1f" cy="%.1f" r="1.8" fill="%s"/></svg>') % (w, h, w, h, area, c, line, c, xs[-1], ys[-1], c)


def mark(q, size=30):
    """Logo (only if licensed file exists in site/logos) or ticker monogram."""
    s = stock_meta(q)
    if s and s.get('logo'):
        u = _uri(ROOT / 'logos' / s['logo'])
        if u:
            return '<span class="lg" style="width:%dpx;height:%dpx"><img src="%s" alt=""></span>' % (size, size, u)
    t = (s['ticker'] if s else q['sym'].split('.')[0])[:2].upper()
    return '<span class="lg mono" style="width:%dpx;height:%dpx;font-size:%dpt">%s</span>' % (size, size, (6 if size < 20 else size // 3), esc(t))


def has_licensed_logo(Q):
    return any((stock_meta(q) or {}).get('logo') for q in Q)


def heatmap(stocks, sg, big=False):
    if not stocks:
        return ''
    tiles = []
    for q in sorted(stocks, key=lambda q: -q['pct']):
        a = min(abs(q['pct']) / 4.0, 1.0)
        base = (11, 138, 94) if q['pct'] >= 0 else (198, 40, 40)
        alpha = 0.18 + 0.72 * a
        dark = alpha > .5
        tiles.append('<div class="ht" style="background:rgba(%d,%d,%d,%.2f);color:%s"><b>%s</b><span>%s %%</span></div>' % (
            base + (alpha, '#fff' if dark else '#1a1d29', esc(q['name']), sg(q['pct']))))
    return '<div class="heat%s">%s</div><p class="foot">Farbe = Tagesveränderung, Sättigung bis ±4 %%. Reihenfolge nach Veränderung.</p>' % (' big' if big else '', ''.join(tiles))


def breadth(stocks):
    n = len(stocks)
    if not n:
        return ''
    up = sum(1 for q in stocks if q['pct'] > 0)
    dn = sum(1 for q in stocks if q['pct'] < 0)
    flat = n - up - dn
    seg = lambda c, k: '<i style="width:%.1f%%;background:%s"></i>' % (100.0 * k / n, c) if k else ''
    return ('<div class="breadth"><div class="bar">%s%s%s</div><div class="bl"><span class="up"><b>%d</b> im Plus</span>'
            '<span class="mut">%d unverändert</span><span class="dn"><b>%d</b> im Minus</span></div>'
            '<p class="foot">Marktbreite der %d gelisteten Aktien. Reine Zählung der Tagesveränderung, keine Prognose.</p></div>') % (
        seg(UP, up), seg('#c9ceda', flat), seg(DN, dn), up, flat, dn, n)


def stock_cards(L, num, sg, cls, cur_fn):
    out = []
    for q in L:
        out.append('<div class="sc">%s<div class="sn"><b class="el">%s</b><small>%s</small></div><div class="sv"><b>%s</b><span class="%s">%s %%</span></div>%s</div>' % (
            mark(q), esc(q['name']), esc(q['sym'].split('.')[0]), num(q['price']), cls(q['pct']), sg(q['pct']), spark(q.get('hist'), 70, 24)))
    return '<div class="scs">%s</div>' % ''.join(out)


def mover_bars(L, sg, cls):
    if not L:
        return ''
    m = max(abs(q['pct']) for q in L) or 1
    rows = ''.join('<div class="mb"><span class="mn">%s%s</span><span class="mt"><i class="%s" style="width:%.0f%%"></i></span><span class="mp %s">%s %%</span></div>' % (
        mark(q, 14), esc(q['name']), 'bu' if q['pct'] >= 0 else 'bd', 100 * abs(q['pct']) / m, cls(q['pct']), sg(q['pct'])) for q in L)
    return rows


def src_icon(item, size=15):
    host, label, mono, color, icon = identity(item)
    u = _uri(ROOT / 'news-assets' / 'icons' / (host + '.png')) if icon else None
    if u:
        return '<img class="fv" src="%s" width="%d" height="%d" alt="">' % (u, size, size)
    return '<span class="fv mono" style="width:%dpx;height:%dpx;font-size:6pt">%s</span>' % (size, size, esc(mono))


def source_strip(N, limit=10):
    c = collections.Counter(); first = {}
    for i in N:
        host = identity(i)[0]
        c[host] += 1; first.setdefault(host, i)
    chips = ''.join('<span class="chip">%s%s<em>%d</em></span>' % (src_icon(first[h], 13), esc(h), n) for h, n in c.most_common(limit))
    return '<div class="chips">%s</div>' % chips if chips else ''


def news_rows(N, limit=14):
    import datetime
    rows = []
    for i in N[:limit]:
        host = identity(i)[0]
        try:
            when = datetime.datetime.fromtimestamp(i['ts']).astimezone().strftime('%d.%m. %H:%M') if i.get('ts') else ''
        except (TypeError, ValueError, OSError):
            when = ''
        rows.append('<li>%s<div><a href="%s">%s</a><span class="s">%s%s</span></div></li>' % (
            src_icon(i), esc(i['url']), esc(i['title']), esc(host), (' · ' + when) if when else ''))
    return ''.join(rows)


CSS = '''
.sp{vertical-align:middle;display:inline-block}
td.spc{text-align:right;padding:2px 6px;width:92px}
.kpi .sp{display:block;margin-top:2mm;width:100%;height:auto}
.lg{display:inline-flex;align-items:center;justify-content:center;border-radius:8px;background:#eaf3fe;color:#1A6ACD;font-weight:800;flex:none;overflow:hidden;border:1px solid #cfe0f7}
.lg img{max-width:78%;max-height:78%;object-fit:contain}
.lg.mono{letter-spacing:-.04em;text-overflow:clip;white-space:nowrap}
.heat{display:grid;grid-template-columns:repeat(4,1fr);gap:2mm}
.ht{border-radius:5px;padding:2.4mm 2.6mm;display:flex;flex-direction:column;gap:1px;font-size:9pt}
.ht b{font-size:9.4pt}.ht span{font-size:8.6pt;font-variant-numeric:tabular-nums}
.breadth{margin:1mm 0 2mm}
.bar{display:flex;height:4.2mm;border-radius:3mm;overflow:hidden;background:#eceff6}.bar i{display:block}
.bl{display:flex;justify-content:space-between;margin-top:1.6mm;font-size:9pt}
.scs{display:grid;grid-template-columns:repeat(2,1fr);gap:3mm}
.sc{display:flex;align-items:center;gap:3mm;border:1px solid #dfe3ee;border-radius:6px;padding:2.6mm 3mm;background:#f7f9fd;break-inside:avoid}
.sc .sn{flex:1;min-width:0}.sc .sn b{display:block;font-size:10pt;color:#0b2a55}.sc .sn small{color:#6b7080;font-size:8pt}
.sc .sv{text-align:right;font-variant-numeric:tabular-nums}.sc .sv b{display:block;font-size:10pt}.sc .sv span{font-size:9pt;font-weight:700}
.mb{display:flex;align-items:center;gap:2.5mm;margin:1.4mm 0;font-size:9pt}
.mt{flex:1;height:3mm;background:#eceff6;border-radius:2mm;overflow:hidden}.mt i{display:block;height:100%}
.bu{background:#0b8a5e}.bd{background:#c62828}.mp{width:17mm;text-align:right;font-weight:700;font-variant-numeric:tabular-nums}
.chips{display:flex;flex-wrap:wrap;gap:2mm;margin:0 0 3mm}
.chip{display:inline-flex;align-items:center;gap:5px;border:1px solid #dfe3ee;background:#f7f9fd;border-radius:20px;padding:1.2px 8px 1.2px 5px;font-size:8.4pt}
.chip em{font-style:normal;color:#6b7080;font-weight:700}
.fv{border-radius:3px;flex:none;vertical-align:middle}.fv.mono{display:inline-flex;align-items:center;justify-content:center;background:#eaf3fe;color:#1A6ACD;font-weight:800}
.nw li{display:flex;gap:3mm;align-items:flex-start}.nw li .fv{margin-top:1px}.nw li div{flex:1;min-width:0}
.sub{font-size:9.6pt;font-weight:700;color:#0b2a55;margin:3.5mm 0 1.5mm}
'''


def universe(Q):
    """All stocks with a cached quote (data/stock-quotes.json, written by stocks.py) plus the
    sparkline history of the main quote list where available. Falls back to Q stocks only."""
    hist = {q['sym'].split('.')[0].upper(): q for q in Q}
    out, seen = [], set()
    try:
        cache = json.loads((ROOT.parent / 'data' / 'stock-quotes.json').read_text())
    except (OSError, ValueError):
        cache = {}
    for s in _stocks():
        c = cache.get(s['slug'])
        if not c or c.get('price') is None or c.get('percent_change') is None:
            continue
        t = s['ticker'].upper()
        h = hist.get(t, {})
        out.append({'sym': t, 'name': s['name'], 'grp': 'US', 'cur': c.get('currency') or s.get('currency'),
                    'price': float(c['price']), 'chg': float(c.get('change') or 0), 'pct': float(c['percent_change']),
                    'hist': h.get('hist'), 'src': c.get('source', 'Twelve Data')})
        seen.add(t)
    for q in Q:
        if q['grp'] in ('US', 'DE') and q['sym'].split('.')[0].upper() not in seen:
            out.append(q)
    return out


def compact_table(L, num, sg, cls):
    def part(P):
        return '<table class="cp"><thead><tr><th>Titel</th><th>Kurs</th><th>in %%</th></tr></thead><tbody>%s</tbody></table>' % ''.join(
            '<tr><td class="nm">%s<span>%s</span></td><td>%s <small>%s</small></td><td class="%s">%s</td></tr>' % (
                mark(q, 15), esc(q['name']), num(q['price']), esc(q.get('cur') or ''), cls(q['pct']), sg(q['pct'])) for q in P) if P else ''
    half = (len(L) + 1) // 2
    return '<div class="two">%s%s</div>' % ('<div>' + part(L[:half]).replace('%%', '%') + '</div>', '<div>' + part(L[half:]).replace('%%', '%') + '</div>')


CSS += '''
.el,.nm>span:last-child,.mn>span:last-child,.ht b{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:block}
.nm{display:flex;align-items:center;gap:5px;max-width:52mm}.nm .lg{border-radius:4px}
.mn{display:flex;align-items:center;gap:4px;width:38mm}.mn .lg{border-radius:4px}
.sc .sn{overflow:hidden}
.two2{display:grid;grid-template-columns:1fr 1fr;gap:6mm}
.cp td,.cp th{padding:2.2px 5px;font-size:8pt}.cp td small{color:#6b7080;font-size:6.6pt}
.heat.big{grid-template-columns:repeat(6,1fr);gap:1.6mm}.heat.big .ht{padding:1.8mm 2mm;font-size:7.6pt}.heat.big .ht b{font-size:7.8pt}.heat.big .ht span{font-size:7.4pt}
'''
