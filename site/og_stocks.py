"""OG-/Bildgrafiken der Aktienseiten (1200x630): Firmenlogo gross mittig, FA-Domain unten.

Logo quer gross mittig, unten finanz-adjust.de, als OG-Vorschau UND sichtbare, crawlbare
Grafik auf der Aktienseite. Nur dokumentierte Logoquellen (logos/SOURCES.md).
Keine neuen Abhaengigkeiten: Rendering ueber das bereits fuer Artikel-OGs genutzte Headless-Chrome.
"""
import base64, json, os, re, subprocess
from html import escape as esc
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def fa_logo_svg():
    # LOGO-Konstante aus build.py lesen (dort versioniert; out/logo.svg wird daraus geschrieben)
    src = (ROOT / 'build.py').read_text(encoding='utf-8')
    i = src.index("LOGO='<svg") + len("LOGO='")
    j = src.index('</svg>', i) + len('</svg>')
    return src[i:j].replace('\\n', '')


def og_stock_html(logo_svg, s):
    lf = ROOT / 'logos' / s['logo']
    if s['logo'].endswith('.svg'):
        svg = lf.read_text(encoding='utf-8')
        svg = svg[svg.index('<svg'):]
        tag = svg[:svg.index('>') + 1]
        def _dim(attr):
            m = re.search(attr + r'="([0-9.]+)', tag)
            return m.group(1) if m else None
        if 'viewBox' not in tag:
            w, h = _dim('width'), _dim('height')
            if w and h:
                svg = svg.replace('<svg', '<svg viewBox="0 0 %s %s"' % (w, h), 1)
        svg = re.sub(r'(<svg[^>]*?)\swidth="[^"]*"', r'\1', svg, count=1)
        svg = re.sub(r'(<svg[^>]*?)\sheight="[^"]*"', r'\1', svg, count=1)
        mark = svg
    else:
        mark = '<img src="data:image/png;base64,%s" alt="">' % base64.b64encode(lf.read_bytes()).decode()
    return ('<!doctype html><html><head><meta charset="utf-8"><style>*{margin:0;box-sizing:border-box}body{width:1200px;height:630px;overflow:hidden;'
        'font-family:Helvetica,Arial,sans-serif;background:#f6f8fc;color:#131722;display:flex;flex-direction:column}'
        '.top{background:linear-gradient(120deg,#131722,#1A6ACD);padding:24px 48px;display:flex;align-items:center;gap:16px}'
        '.top svg{height:40px;width:auto}.wm{color:#fff;font-weight:800;font-size:24px;letter-spacing:-.01em}.wm b{color:#7cc4ff}'
        '.mid{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:20px;padding:24px}'
        '.logo{background:#fff;border:1px solid #e2e8f3;border-radius:26px;padding:34px 54px;display:flex;align-items:center;justify-content:center;'
        'box-shadow:0 14px 34px -18px rgba(19,23,34,.28);max-width:820px}'
        '.logo svg{width:560px;max-width:100%%;height:auto;max-height:230px}.logo img{width:auto;max-width:560px;max-height:230px}'
        '.nm{color:#5a6070;font-size:21px;font-weight:600}'
        '.ft{padding:0 48px 26px;color:#8a90a0;font-size:18px;display:flex;justify-content:space-between}.ft b{color:#0086F5}</style></head>'
        '<body><div class="top">%s<span class="wm">finanz<b>adjust</b></span></div>'
        '<div class="mid"><div class="logo">%s</div><div class="nm">%s &middot; %s &middot; %s</div></div>'
        '<div class="ft"><span>finanz-adjust.de</span><span><b>%s Aktie</b> · FA Redaktion</span></div></body></html>'
        ) % (logo_svg, mark, esc(s['name']), esc(s['ticker']), esc(s['exchange']), esc(s['name']))


def build_stock_ogs(out, chrome, logo_svg, stocks=None):
    """Schreibt out/og/aktien/<slug>-logo.png fuer jeden Titel mit logo. Ohne chrome: uebersprungen."""
    if not chrome:
        print('no chrome, skip stock og images')
        return
    if stocks is None:
        stocks = json.loads((ROOT / 'stocks.json').read_text())
    os.makedirs(os.path.join(out, 'og', 'aktien'), exist_ok=True)
    tmp = ROOT / '_og_stock.html'
    for s in stocks:
        if not s.get('logo'):
            continue
        tmp.write_text(og_stock_html(logo_svg, s), encoding='utf-8')
        subprocess.run([chrome, '--headless', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
                        '--window-size=1200,630', '--screenshot=' + os.path.abspath(os.path.join(out, 'og', 'aktien', '%s-logo.png' % s['slug'])),
                        'file://' + str(tmp)], capture_output=True)


if __name__ == '__main__':
    import shutil
    chrome = shutil.which('google-chrome') or shutil.which('chromium') or shutil.which('chromium-browser')
    build_stock_ogs(str(ROOT / 'out'), chrome, fa_logo_svg())
