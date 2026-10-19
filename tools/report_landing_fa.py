"""Extra rich-media sections for the finanz adjust /berichte/ landing page.
Everything comes from the repository and the current build: real PDF pages, real quote data, real archive counts.
No tracking, no network, no invented audience numbers. Standard library, optional system pdftoppm/pdfinfo."""
from pathlib import Path
import html, json, re, shutil, subprocess, tempfile

e = html.escape
UP, DN = '#0b8a5e', '#c62828'
de = lambda v, d=0: ('{:,.%df}' % d).format(v).replace(',', 'X').replace('.', ',').replace('X', '.')

ICON = {
 'free': '<path d="M12 3v18M16.5 7.5c-.8-1.2-2.3-1.8-4.5-1.8-2.4 0-4 1.100-4 2.800 0 4 8.500 1.800 8.500 5.800 0 1.700-1.700 2.900-4.500 2.900-2.200 0-3.900-.7-4.800-2" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
 'lock': '<rect x="5" y="10.500" width="14" height="9.500" rx="2" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M8 10.500V8a4 4 0 0 1 8 0v2.500" fill="none" stroke="currentColor" stroke-width="1.8"/>',
 'chart': '<path d="M4 19V5M4 19h16M8 15l3.500-4 3 2.500L20 7" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>',
 'link': '<path d="M10 14a4 4 0 0 0 5.700 0l3-3a4 4 0 0 0-5.700-5.700l-1 1M14 10a4 4 0 0 0-5.700 0l-3 3a4 4 0 0 0 5.700 5.700l1-1" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
 'print': '<path d="M7 9V4h10v5M7 17H5a1 1 0 0 1-1-1v-5a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v5a1 1 0 0 1-1 1h-2" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><rect x="7" y="14" width="10" height="6" rx="1" fill="none" stroke="currentColor" stroke-width="1.8"/>',
 'cal': '<rect x="4" y="5.500" width="16" height="14.500" rx="2" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M4 10h16M8.500 3.500v4M15.500 3.500v4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
}
BENEFITS = [
 ('free', 'Gratis', 'Kein Abo, kein Kauf, keine Bezahlschranke. Das PDF öffnest du direkt.'),
 ('lock', 'Ohne Anmeldung', 'Kein Konto, kein E-Mail-Feld, kein Newsletter-Zwang.'),
 ('chart', 'Märkte auf einen Blick', 'Indizes, Marktbreite, Gewinner, Verlierer und Devisen in einem Dokument.'),
 ('link', 'Quellen dabei', 'Datenquellen, Stand und Redaktionsschluss stehen im PDF.'),
 ('print', 'Für Papier und Bildschirm', 'Helles A4-Layout zum Lesen, Speichern und Drucken.'),
 ('cal', 'Tagesarchiv', 'Pro Berliner Kalendertag bleibt die erste erfolgreich erstellte Ausgabe erhalten.'),
]

def _json(p):
    try: return json.loads(Path(p).read_text(encoding='utf-8'))
    except (OSError, ValueError): return None

def spark(hist, w=120, h=34, color=UP):
    pts = [float(x) for x in (hist or []) if x is not None]
    if len(pts) < 2: return ''
    lo, hi = min(pts), max(pts); rng = (hi - lo) or 1.0
    xy = ['%.1f,%.1f' % (1 + i * (w - 2) / (len(pts) - 1), h - 2 - (v - lo) / rng * (h - 4)) for i, v in enumerate(pts)]
    return '<svg viewBox="0 0 %d %d" width="100%%" height="%d" preserveAspectRatio="none" aria-hidden="true"><polygon points="%s %d,%d 1,%d" fill="%s" fill-opacity=".12"/><polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round"/></svg>' % (w, h, h, ' '.join(xy), w - 1, h, h, color, ' '.join(xy), color)

def pdf_pages(pdf):
    if not (pdf.is_file() and shutil.which('pdfinfo')): return None
    try:
        out = subprocess.run(['pdfinfo', str(pdf)], capture_output=True, text=True, timeout=20).stdout
        m = re.search(r'Pages:\s+(\d+)', out); return int(m.group(1)) if m else None
    except (OSError, subprocess.TimeoutExpired): return None

def page_thumbs(pdf, dest, limit=4):
    """Render the first pages of the real PDF; returns file names. Empty when no renderer is available."""
    if not (pdf.is_file() and shutil.which('pdftoppm')): return []
    try:
        with tempfile.TemporaryDirectory() as tmp:
            r = subprocess.run(['pdftoppm', '-f', '1', '-l', str(limit), '-scale-to', '640', '-jpeg', '-jpegopt', 'quality=80', str(pdf), str(Path(tmp) / 'p')], capture_output=True, timeout=60)
            got = sorted(Path(tmp).glob('p-*.jpg'))
            if r.returncode != 0 or not got: return []
            for old in dest.glob('pdf-*.jpg'): old.unlink()
            names = []
            for i, g in enumerate(got, 1):
                shutil.copy2(g, dest / ('pdf-%d.jpg' % i)); names.append('pdf-%d.jpg' % i)
            return names
    except (OSError, subprocess.TimeoutExpired): return []

def stats(root, pdf, dates, stock_n):
    items = [(str(len(dates)), 'Ausgaben im Archiv')] if dates else []
    n = pdf_pages(pdf)
    if n: items.append((str(n), 'Seiten im aktuellen PDF'))
    if stock_n: items.append((str(stock_n), 'Aktien in der Marktbreite'))
    if pdf.is_file(): items.append((de(pdf.stat().st_size / 1024) + ' KB', 'Dateigröße, schnell geladen'))
    if not items: return ''
    return '<ul class="rf-stats" aria-label="Zahlen zur Ausgabe">%s</ul><p class="rl-fine">Zahlen aus dem aktuellen Seitenbau und dem Archiv, keine Nutzer- oder Downloadzahlen.</p>' % ''.join('<li><b>%s</b><span>%s</span></li>' % (e(a), e(b)) for a, b in items)

def market(root):
    q = _json(Path(root) / 'data/quotes.json') or []
    sq = _json(Path(root) / 'data/stock-quotes.json') or {}
    idx = [x for x in q if x.get('grp') == 'Index' and x.get('hist')][:4]
    rows = [(v.get('symbol') or k.upper(), v.get('percent_change')) for k, v in sq.items() if isinstance(v, dict) and isinstance(v.get('percent_change'), (int, float))]
    return idx, rows

def market_block(root, stamp):
    idx, rows = market(root)
    if not idx and not rows: return ''
    cards = ''
    for x in idx:
        up = (x.get('pct') or 0) >= 0; col = UP if up else DN
        cards += '<div class="rf-ix"><small>%s</small><b>%s</b><span style="color:%s">%s%s %%</span>%s</div>' % (e(x['name']), de(x['price'], 2), col, '+' if up else '', de(x.get('pct') or 0, 2), spark(x['hist'], color=col))
    br = ''
    if rows:
        up = sum(1 for _, p in rows if p > 0); dn = sum(1 for _, p in rows if p < 0); n = len(rows); fl = n - up - dn
        seg = lambda c, k: '<i style="width:%.1f%%;background:%s"></i>' % (100.0 * k / n, c) if k else ''
        top = sorted(rows, key=lambda r: -r[1])
        li = lambda L, c: ''.join('<li><span>%s</span><b style="color:%s">%s%s %%</b></li>' % (e(s), c, '+' if p > 0 else '', de(p, 2)) for s, p in L)
        br = ('<div class="rf-br"><h3>Marktbreite der %d Aktien</h3><div class="rf-bar" role="img" aria-label="%d im Plus, %d im Minus">%s%s%s</div><p><span style="color:%s"><b>%d</b> im Plus</span> · <span style="color:%s"><b>%d</b> im Minus</span>%s</p>'
              '<div class="rf-two"><div><h4>Größte Gewinner</h4><ul>%s</ul></div><div><h4>Größte Verlierer</h4><ul>%s</ul></div></div></div>') % (
            n, up, dn, seg(UP, up), seg('#9aa3b2', fl), seg(DN, dn), UP, up, DN, dn, (' · <b>%d</b> unverändert' % fl) if fl else '', li(top[:3], UP), li(top[::-1][:3], DN))
    return '<section class="rl-section"><p class="rl-tag">Ein Blick ins PDF</p><h2>So sieht dein Marktüberblick aus.</h2><div class="rf-ixs">%s</div>%s<p class="rl-fine">Datenstand des Seitenbaus (%s), Kurse ggf. verzögert. Reine Zählung der Tagesveränderung, keine Prognose, keine Anlageberatung.</p></section>' % (cards, br, e(stamp))

def thumbs_block(names):
    if not names: return ''
    figs = ''.join('<a href="/berichte/aktuell.pdf" aria-label="PDF öffnen, Seite %d"><img src="/assets/report-preview/%s" width="640" height="905" alt="Seite %d des aktuellen PDFs" loading="lazy"><span>Seite %d</span></a>' % (i, n, i, i) for i, n in enumerate(names, 1))
    return '<section class="rl-section"><p class="rl-tag">Echte Seiten</p><h2>Blätter durch die Ausgabe.</h2><div class="rf-pages">%s</div><p class="rl-fine">Die ersten %d Seiten des aktuellen PDFs, automatisch aus der Datei erzeugt.</p></section>' % (figs, len(names))

def benefits_block():
    cards = ''.join('<li><svg viewBox="0 0 24 24" width="26" height="26" aria-hidden="true">%s</svg><b>%s</b><span>%s</span></li>' % (ICON[k], e(t), e(d)) for k, t, d in BENEFITS)
    return '<section class="rl-section"><p class="rl-tag">Deine Vorteile</p><h2>Lesen. Speichern. Wiederfinden.</h2><ul class="rf-ben">%s</ul><p class="rl-fine">Das PDF enthält kein Tracking-Skript. Auf der Website gelten die Datenschutz- und Cookie-Einstellungen.</p></section>' % cards

CSS = '''
.rf-stats{list-style:none;display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;padding:0;margin:0 0 6px}.rf-stats li{border:1px solid var(--rl-line);background:var(--rl-soft);border-radius:12px;padding:16px}.rf-stats b{display:block;font-size:30px;letter-spacing:-.03em;color:var(--rl-fg);font-variant-numeric:tabular-nums}.rf-stats span{font-size:13px;color:var(--rl-muted)}
.rf-ben{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.rf-ben li{border:1px solid var(--rl-line);background:var(--rl-bg);border-radius:14px;padding:20px;line-height:1.5}.rf-ben svg{display:block;color:var(--rl-ac);background:var(--rl-soft);border-radius:10px;padding:8px;box-sizing:content-box;margin-bottom:12px}.rf-ben b{display:block;font-size:16px;margin-bottom:6px;color:var(--rl-fg)}.rf-ben span{color:var(--rl-muted);font-size:13.5px}
.rf-ixs{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}.rf-ix{border:1px solid var(--rl-line);background:var(--rl-bg);border-radius:12px;padding:14px 16px;display:grid;gap:2px}.rf-ix small{color:var(--rl-muted);font-weight:700;letter-spacing:.04em;text-transform:uppercase;font-size:11px}.rf-ix b{font-size:22px;letter-spacing:-.02em;color:var(--rl-fg);font-variant-numeric:tabular-nums}.rf-ix span{font-size:13px;font-weight:700}.rf-ix svg{margin-top:6px;display:block}
.rf-br{margin-top:22px;border:1px solid var(--rl-line);background:var(--rl-soft);border-radius:14px;padding:20px}.rf-br h3{margin:0 0 12px;font-size:16px;color:var(--rl-fg)}.rf-br h4{margin:0 0 6px;font-size:12px;color:var(--rl-muted);text-transform:uppercase;letter-spacing:.06em}.rf-bar{display:flex;height:12px;border-radius:6px;overflow:hidden;background:var(--rl-line)}.rf-bar i{display:block}.rf-br p{margin:10px 0 0;font-size:13.5px}.rf-two{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:16px}.rf-two ul{list-style:none;margin:0;padding:0}.rf-two li{display:flex;justify-content:space-between;border-bottom:1px solid var(--rl-line);padding:7px 0;font-size:14px}
.rf-pages{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}.rf-pages a{display:block;text-decoration:none;color:var(--rl-muted);font-size:12px;text-align:center}.rf-pages img{width:100%;height:auto;display:block;border:1px solid var(--rl-line);border-radius:4px;box-shadow:0 6px 18px #0002;margin-bottom:8px;background:#fff}
@media(max-width:700px){.rf-ben{grid-template-columns:1fr}.rf-ixs{grid-template-columns:repeat(2,minmax(0,1fr))}.rf-two{grid-template-columns:1fr}.rf-pages{grid-template-columns:repeat(2,minmax(0,1fr))}.rf-stats b{font-size:26px}}
'''

BEN_RX = re.compile(r'<section class="rl-section"><p class="rl-tag">Dein Überblick, ohne Umwege</p>.*?</section>', re.S)

def enhance(landing, root, out, dates, pdf_name='aktuell.pdf', stamp=''):
    """Return the landing HTML with real stats, benefits, market snapshot and PDF pages. Falls back to the input on any gap."""
    root, out = Path(root), Path(out)
    pdf = out / 'berichte' / pdf_name; dest = out / 'assets' / 'report-preview'; dest.mkdir(parents=True, exist_ok=True)
    (dest / 'landing-fa.css').write_text(CSS)
    sq = _json(root / 'data/stock-quotes.json') or {}
    names = page_thumbs(pdf, dest)
    if not names: names = sorted(p.name for p in dest.glob('pdf-*.jpg'))[:4]
    s = stats(root, pdf, dates, len(sq)) if sq or dates else ''
    html_ = landing.replace('<link rel="stylesheet" href="/assets/report-preview/landing.css">', '<link rel="stylesheet" href="/assets/report-preview/landing.css"><link rel="stylesheet" href="/assets/report-preview/landing-fa.css">', 1)
    html_, n = BEN_RX.subn(lambda m: benefits_block() + (('<section class="rl-section"><p class="rl-tag">Die Ausgabe in Zahlen</p><h2>Echte Werte, keine Reichweitenversprechen.</h2>%s</section>' % s) if s else ''), html_, count=1)
    if not n: return landing
    mk = market_block(root, stamp) + thumbs_block(names)
    return html_.replace('<section class="rl-section rl-inside">', mk + '<section class="rl-section rl-inside">', 1)
