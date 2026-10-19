"""Rights-gated source information. No foreign teasers, article scraping or ad runtime."""
import argparse
import datetime
import html
import json
import re
from pathlib import Path
from zoneinfo import ZoneInfo
from news_media import domain, permitted_news, source_badge
ROOT = Path(__file__).resolve().parent
from news_policy import HEADLINE_SOURCES, TEASER_SOURCES, detail_path, has_detail


def related_terms(item, entries):
    title = item['title'].casefold()
    return [g for g in entries if any(re.search(r'(?<!\w)' + re.escape(t.casefold()) + r'(?!\w)', title)
                for t in [g['term'].split(' (')[0]] + g.get('aliases', []) if len(t) >= 3)][:4]


def content(item, entries):
    if not has_detail(item):
        raise ValueError('Source is not approved for headline source info')
    e = lambda s: html.escape(str(s), quote=True)
    terms = related_terms(item, entries)
    stocks = json.loads((ROOT/'stocks.json').read_text())
    matches = [a for a in stocks if re.search(r'(?<!\w)' + re.escape(a['name']) + r'(?!\w)', item['title'], re.I) and (ROOT/'out/aktien'/a['slug']/'index.html').is_file()][:3]
    cards = ''.join('<a href="/glossar/%s/"><b>%s</b><span>%s</span></a>' % (e(g['slug']), e(g['term']), e(g['short'])) for g in terms)
    try:
        when = datetime.datetime.fromtimestamp(item['ts'], datetime.timezone.utc).astimezone(ZoneInfo("Europe/Berlin")).strftime('%d.%m.%Y, %H:%M') + ' (im Archiv erfasst)'
    except (KeyError, ValueError, TypeError, OSError):
        when = 'Zeitpunkt nicht verfügbar'
    original = '<a class="nd-original" href="%s" target="_blank" rel="noopener noreferrer nofollow">Original bei %s lesen <span aria-hidden="true">↗</span></a>' % (e(item['url']), e(domain(item['url'])))
    leaving = '<aside class="nd-leaving" aria-label="Hinweis zum externen Link"><span aria-hidden="true">↗</span><p>Beim Klick auf den Original-Link verlässt du finanz adjust und wechselst zu <strong>%s</strong>. Der Beitrag öffnet sich in einem neuen Tab.</p></aside>' % e(domain(item['url']))
    cards += ''.join('<a href="/aktien/%s/"><b>%s · %s</b><span>FA Aktienprofil und Kursübersicht. Keine Aussage zur Meldung.</span></a>' % (e(a['slug']), e(a['name']), e(a['ticker'])) for a in matches)
    # Never output item['sum'], even if old Yahoo metadata contains it.
    return '''<link rel="stylesheet" href="/news-detail.css"><main class="nd-wrap">
<a class="nd-back" href="/nachrichten/">← Zum Nachrichtenarchiv</a>
<section class="nd-source"><p class="nd-kicker">EXTERNE SCHLAGZEILE / QUELLENINFO</p>%s<h1>%s</h1><p class="nd-time">%s</p>
<p class="nd-disclosure">Dies ist eine Quelleninfo von finanz adjust, kein eigener Nachrichtenartikel. Den vollständigen Beitrag findest du beim verlinkten Anbieter.</p>%s%s</section>
<section class="nd-context"><p class="nd-kicker">FA WISSEN</p><h2>Passendes Wissen zur Schlagzeile</h2><p>Automatisch anhand der Überschrift zugeordnet. Glossar und Aktienprofile erklären Grundlagen, nicht den Inhalt oder die Richtigkeit der Meldung.</p><div class="nd-terms">%s</div>%s</section>
<aside class="nd-report"><div><p class="nd-kicker">DER BLICK AUFS GANZE</p><h2>Dein Tagesbericht als PDF.</h2><p>Marktübersicht, Indizes und Schlagzeilen von finanz adjust. Kostenlos, ohne Anmeldung und ohne E-Mail.</p></div><a class="btn" href="/berichte/aktuell.pdf">Tagesbericht laden (PDF) ↓</a><a class="nd-textlink" href="/berichte/">Alle Berichte ansehen</a></aside>
<aside class="nd-ad" hidden aria-label="Anzeigenplatz, derzeit ohne Werbung"><span>Anzeige · Platzhalter</span><p>Hier wird keine Werbung geladen.</p><small>Erst nach separater Einrichtung und erforderlicher Einwilligung. Kein externer Abruf durch diesen Platzhalter.</small></aside>
<section class="nd-bottom"><h2>Zur vollständigen Meldung</h2>%s<p>Es gelten die Bedingungen des Anbieters. finanz adjust ist nicht mit der Quelle verbunden.</p></section>
</main>''' % (source_badge(item), e(item['title']), e(when), leaving, original, cards, '' if cards else '<a class="nd-textlink" href="/glossar/">Zum Börsen-Glossar von A bis Z →</a>', original)


def build_details(page, items, out=ROOT/'out'):
    out = Path(out)
    entries = json.loads((ROOT.parent/'content/glossary.json').read_text())['entries']
    (out/'news-detail.css').write_text((ROOT/'news-detail.css').read_text())
    paths = []
    for item in items:
        if not has_detail(item):
            continue
        path = detail_path(item)
        page(path, item['title']+' | Quelleninfo | finanz adjust',
             'Externe Schlagzeile mit Quellenlink und passenden Grundlagen von finanz adjust.',
             content(item, entries), act='/nachrichten/',
             crumbs=[('/nachrichten/','Nachrichten'),(path,'Quelleninfo')])
        target = out/path.strip('/')/'index.html'
        h = target.read_text()
        h = re.sub(r'<meta name="robots" content="[^"]*">', '<meta name="robots" content="noindex,follow">', h, count=1)
        h = re.sub(r'<link rel="canonical"[^>]*>', '', h)
        target.write_text(h)
        paths.append(path)
    return paths


def render_preview(out=ROOT/'out'):
    """Render one local item in an existing shell, without altering archive links."""
    out = Path(out)
    shell = (out/'nachrichten/index.html').read_text()
    start = shell.index('<div class="w"><div class="news-intro">')
    stop = shell.index('<footer>', start)
    entries = json.loads((ROOT.parent/'content/glossary.json').read_text())['entries']
    items = json.loads((ROOT.parent/'data/fin_archive.json').read_text())
    item = max((i for i in items if has_detail(i)), key=lambda i:len(related_terms(i,entries)))
    path = detail_path(item)
    h = shell[:start]+content(item,entries)+shell[stop:]
    h = re.sub(r'<title>.*?</title>', '<title>'+html.escape(item['title'])+' | Quelleninfo | finanz adjust</title>',h,count=1)
    h = re.sub(r'<meta name="robots" content="[^"]*">','<meta name="robots" content="noindex,follow">',h,count=1)
    h = re.sub(r'<link rel="canonical"[^>]*>','',h)
    h = re.sub(r'<script type="application/ld\+json">.*?</script>','',h,flags=re.S)
    h = re.sub(r'<meta property="og:[^"]*"[^>]*>','',h)
    target=out/path.strip('/')/'index.html';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(h)
    (out/'news-detail.css').write_text((ROOT/'news-detail.css').read_text())
    print('LOCAL PREVIEW:',path)
    return path

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--preview', action='store_true')
    a=p.parse_args()
    if a.preview:render_preview()
    else:p.print_help()
