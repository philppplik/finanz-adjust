# PDF-Tagesbericht (A4, helles Theme, druckfreundlich). Wird von build.py aufgerufen.
# Aufbau: 1 Titel+Kurse | 2 Märkte | 3 Letzte 6 Artikel | 4 Schlagzeilen | letzte Seite: Impressum & Redaktionsschluss
import html, re

DAYS = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']

CSS = '''
@page{size:A4;margin:16mm 15mm 18mm 15mm;
 @bottom-left{content:"finanz adjust · Tagesbericht %(date)s";font:8pt "Helvetica Neue",Helvetica,Arial,sans-serif;color:#8a90a2}
 @bottom-right{content:"Seite " counter(page) " von " counter(pages);font:8pt "Helvetica Neue",Helvetica,Arial,sans-serif;color:#8a90a2}}
@page:first{margin-top:0;margin-left:0;margin-right:0;
 @bottom-left{content:"finanz adjust · Tagesbericht %(date)s";font:8pt "Helvetica Neue",Helvetica,Arial,sans-serif;color:#8a90a2;margin-left:15mm}
 @bottom-right{content:"Seite " counter(page) " von " counter(pages);font:8pt "Helvetica Neue",Helvetica,Arial,sans-serif;color:#8a90a2;margin-right:15mm}}
*{box-sizing:border-box}
html{-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{margin:0;font:9.6pt/1.5 "Helvetica Neue",Helvetica,Arial,"Liberation Sans",sans-serif;color:#1a1d29}
a{color:#1A6ACD;text-decoration:none}
.pg{break-after:page}.pg:last-child{break-after:auto}
.cover{background:linear-gradient(120deg,#0b3a7a 0%%,#1A6ACD 55%%,#00A7F8 100%%);color:#fff;padding:14mm 15mm 11mm;margin-bottom:8mm}
.brand{display:flex;align-items:center;gap:10px;font-weight:800;font-size:15pt;letter-spacing:-.01em}
.brand svg{height:30px;width:auto}
.brand .wm b{font-weight:800;color:#bfe6ff}
.cover h1{margin:12mm 0 2mm;font-size:27pt;line-height:1.1;letter-spacing:-.02em}
.cover p{margin:0;font-size:10.5pt;color:#dcecff}
.wrap{padding:0 15mm}
.kpis{display:flex;gap:4mm;margin:0 0 6mm}
.kpi{flex:1;border:1px solid #dfe3ee;border-top:3px solid #0086F5;border-radius:4px;padding:3mm 3.5mm;background:#f7f9fd}
.kpi .n{font-size:8pt;color:#6b7080;text-transform:uppercase;letter-spacing:.05em}
.kpi .p{font-size:16pt;font-weight:700;margin:1px 0}
.kpi .c{font-size:9.5pt;font-weight:700}
h2{font-size:12.5pt;margin:6mm 0 2.5mm;padding-bottom:1.5mm;border-bottom:2px solid #0086F5;color:#0b2a55;break-after:avoid}
h2 small{font-size:8.5pt;font-weight:400;color:#6b7080;margin-left:6px}
table{width:100%%;border-collapse:collapse;break-inside:auto}tr{break-inside:avoid}
th{font-size:8pt;color:#6b7080;font-weight:600;text-transform:uppercase;letter-spacing:.04em;padding:4px 6px;text-align:right;border-bottom:1px solid #cfd5e4}
td{padding:4.5px 6px;text-align:right;border-bottom:1px solid #eceff6;font-variant-numeric:tabular-nums}
th:first-child,td:first-child{text-align:left}td:first-child{font-weight:600}
tbody tr:nth-child(even) td{background:#f9fafd}
.up{color:#0b8a5e}.dn{color:#c62828}.mut{color:#6b7080}
.two{display:flex;gap:6mm}.two>div{flex:1;min-width:0}
.fx{display:flex;flex-wrap:wrap;gap:3mm;margin-top:1mm}.fx span{border:1px solid #dfe3ee;background:#f7f9fd;border-radius:20px;padding:2px 10px;font-size:9pt}
.art{border:1px solid #dfe3ee;border-left:4px solid #0086F5;border-radius:4px;padding:3.2mm 4mm;margin-bottom:3.2mm;break-inside:avoid}
.art .m{font-size:8pt;color:#6b7080;text-transform:uppercase;letter-spacing:.05em}
.art .t{font-size:11.5pt;font-weight:700;color:#0b2a55;margin:1px 0 2px;line-height:1.3}
.art .d{font-size:9.3pt;color:#3a3f52}
.art .u{font-size:8pt;color:#1A6ACD;margin-top:2px;word-break:break-all}
.nw{list-style:none;margin:0;padding:0}.nw li{padding:5px 0;border-bottom:1px solid #eceff6;break-inside:avoid}
.nw .s{font-size:8pt;color:#6b7080;display:block}
.note{background:#f1f6fd;border:1px solid #cfe0f7;border-radius:4px;padding:3mm 4mm;font-size:9pt;color:#2b3350;margin:3mm 0}
.last h3{font-size:10pt;margin:4.5mm 0 1mm;color:#0b2a55}
.last p{margin:0 0 1.5mm;font-size:9.2pt}
.imp{display:flex;gap:6mm}.imp>div{flex:1}
.foot{margin-top:5mm;font-size:8pt;color:#6b7080}
'''


SRCURLS = {'Twelve Data': 'https://twelvedata.com', 'Yahoo Finance': 'https://finance.yahoo.com', 'CoinGecko': 'https://www.coingecko.com'}


def build(Q, ARTS, fx, N, NOW, num, sg, cls, esc, srcs_plain, LOGO, adate):
    def srclink(name):
        url = next((u for k, u in SRCURLS.items() if k in name), None)
        return '<a href="%s">%s</a>' % (esc(url), esc(name)) if url else esc(name)
    srcs_html = ', '.join(srclink(x) for x in srcs_plain.split(', '))
    day = DAYS[NOW.weekday()] + ', ' + NOW.strftime('%d.%m.%Y')
    stamp = NOW.strftime('%d.%m.%Y, %H:%M') + ' Uhr'
    icon = re.sub(r'<svg[^>]*>', '<svg viewBox="0 0 98 129" xmlns="http://www.w3.org/2000/svg">', LOGO, count=1)

    def rows(L, cur=True):
        return ''.join('<tr><td>%s</td><td>%s</td><td class="%s">%s</td><td class="%s">%s %%</td></tr>' % (
            esc(q['name']), num(q['price']), cls(q['chg']), sg(q['chg']), cls(q['pct']), sg(q['pct'])) for q in L)

    def tbl(L, first='Titel'):
        if not L:
            return '<p class="mut">Aktuell keine Daten verfügbar.</p>'
        return '<table><thead><tr><th>%s</th><th>Stand</th><th>Änderung</th><th>in %%</th></tr></thead><tbody>%s</tbody></table>' % (first, rows(L))

    idx = [q for q in Q if q['grp'] == 'Index']
    stocks = [q for q in Q if q['grp'] in ('US', 'DE')]
    other = [q for q in Q if q['grp'] in ('Rohstoff', 'FX', 'Krypto')]
    ranked = sorted(stocks, key=lambda q: -q['pct'])
    kp = ''.join('<div class="kpi"><div class="n">%s</div><div class="p">%s</div><div class="c %s">%s %%</div></div>' % (
        esc(q['name']), num(q['price']), cls(q['pct']), sg(q['pct'])) for q in idx[:4])
    fxs = ''.join('<span>EUR/%s <b>%s</b></span>' % (k, num(fx[k], 4)) for k in ('USD', 'GBP', 'CHF', 'JPY', 'CNY') if k in fx) \
        or '<span class="mut">Aktuell nicht verfügbar</span>'

    arts = ''
    for a in ARTS[:6]:
        d = a.get('description') or re.sub(r'<[^>]+>', ' ', a.get('body', ''))[:200]
        d = re.sub(r'\s+', ' ', html.unescape(d)).strip()
        if len(d) > 230:
            d = d[:227].rsplit(' ', 1)[0] + '…'
        arts += '<div class="art"><div class="m">%s · %s</div><div class="t">%s</div><div class="d">%s</div><div class="u"><a href="https://finanz-adjust.de/artikel/%s/">finanz-adjust.de/artikel/%s/</a></div></div>' % (
            esc(a.get('section', 'Artikel')), adate(a).strftime('%d.%m.%Y'), esc(a['title']), esc(d), esc(a['slug']), esc(a['slug']))
    if not arts:
        arts = '<p class="mut">Die ersten Artikel der FA Redaktion erscheinen in Kürze.</p>'

    news = ''.join('<li><a href="%s">%s</a><span class="s">%s</span></li>' % (esc(i['url']), esc(i['title']), esc(i['src'])) for i in N[:12])

    page1 = '''<div class="pg"><div class="cover"><div class="brand">%s<span class="wm">finanz<b>adjust</b></span></div>
<h1>Tagesbericht</h1><p>%s · Märkte, Artikel und Schlagzeilen im Überblick · FA Redaktion</p></div>
<div class="wrap"><div class="kpis">%s</div>
<h2>Indizes <small>Stand %s</small></h2>%s
<h2>Devisen <small>EZB-Referenzkurse</small></h2><div class="fx">%s</div>
<div class="note"><b>Hinweis:</b> Dieser Bericht dient ausschließlich der Information und ist keine Anlageberatung, Anlageempfehlung oder Kauf- bzw. Verkaufsempfehlung.</div></div></div>''' % (
        icon, esc(day), kp, esc(stamp), tbl(idx, 'Index'), fxs)

    page2 = '''<div class="pg"><h2>Aktien <small>Kursdaten Stand %s, ggf. verzögert</small></h2>%s
<div class="two"><div><h2>Top-Gewinner</h2>%s</div><div><h2>Top-Verlierer</h2>%s</div></div>
<h2>Rohstoffe, Devisen, Krypto</h2>%s</div>''' % (
        esc(stamp), tbl(stocks), tbl(ranked[:4]), tbl(ranked[-4:][::-1]) if len(ranked) > 4 else tbl([]), tbl(other, 'Wert'))

    page3 = '<div class="pg"><h2>Die letzten 6 Artikel der FA Redaktion</h2>%s<p class="foot">Alle Artikel mit Quellenangaben auf <a href="https://finanz-adjust.de/artikel/">finanz-adjust.de/artikel/</a></p></div>' % arts

    page4 = '<div class="pg"><h2>Aktuelle Schlagzeilen <small>nur Überschriften, Rechte bei den Quellen</small></h2><ul class="nw">%s</ul></div>' % (news or '<li class="mut">Aktuell keine Schlagzeilen.</li>')

    last = '''<div class="pg last"><h2>Impressum &amp; Redaktionsschluss</h2>
<div class="imp"><div><h3>Anbieter nach § 5 DDG</h3><p>Philipp Paulik<br>Mozartstraße 1<br>53819 Neunkirchen-Seelscheid<br>Nordrhein-Westfalen</p>
<h3>Kontakt</h3><p>E-Mail: philipp.l.paulik@gmail.com<br>Web: finanz-adjust.de</p></div>
<div><h3>Verantwortlich nach § 18 Abs. 2 MStV</h3><p>Philipp Paulik, Anschrift wie links</p>
<h3>Redaktion</h3><p>Die Inhalte erscheinen unter der Redaktionsbezeichnung „FA Redaktion“.</p></div></div>
<h3>Redaktionsschluss</h3><p>Dieser Bericht wurde am %s automatisch erstellt. Später veröffentlichte Kurse und Meldungen sind nicht berücksichtigt.</p>
<h3>Hinweis zu KI</h3><p>Die Inhalte werden mit Unterstützung von KI erstellt und redaktionell geprüft. Trotz Prüfung können Fehler nicht ausgeschlossen werden.</p>
<h3>Risikohinweis</h3><p>Alle Inhalte dienen ausschließlich der Information und sind keine Anlageberatung, Anlageempfehlung oder Kauf- bzw. Verkaufsempfehlung. Der Handel mit Finanzinstrumenten ist mit Verlustrisiken bis zum Totalverlust verbunden. Vergangene Wertentwicklung ist kein verlässlicher Indikator für künftige Ergebnisse.</p>
<h3>Datenquellen</h3><p>Kursdaten: %s (ggf. verzögert, ohne Gewähr). Wechselkurse: <a href="https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.de.html">Europäische Zentralbank</a> (Referenzkurse). Schlagzeilen: <a href="https://www.gdeltproject.org">GDELT Project</a> (nur Überschriften mit Link zur Quelle).</p>
<h3>Haftung</h3><p>Fremde Inhalte stammen von den genannten Quellen. Für Inhalte verlinkter Seiten ist der jeweilige Anbieter verantwortlich.</p>
<p class="foot">© %d finanz adjust · Redaktion: FA Redaktion · Stand %s</p></div>''' % (
        esc(stamp), srcs_html, NOW.year, esc(stamp))

    return '<!doctype html><html lang="de"><head><meta charset="utf-8"><title>finanz adjust Tagesbericht %s</title><style>%s</style></head><body>%s%s%s%s%s</body></html>' % (
        esc(day), CSS % {'date': NOW.strftime('%d.%m.%Y')}, page1, page2, page3, page4, last)
