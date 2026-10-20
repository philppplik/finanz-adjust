"""Lernpfade: Uebersicht /lernpfade/ und je Pfad eine Seite /lernpfade/<slug>/.
Quelle: content/lernpfade-fa-*.json (Felder id, name, frage, intro, level, zielgruppe, dauer, voraussetzungen, lernziel, steps, terms, abschluss_check, danach).
Fortschritt nur im localStorage (Schluessel fa-lernpfad-<id>), kein Server, kein Tracking."""
import json, re, html, glob, shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parent
LEVELS = ['Einsteiger', 'Fortgeschritten', 'Profi']
esc = lambda s: html.escape(str(s), quote=True)

def slugify(t):
    t = t.lower().replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')

def load_paths():
    out = []
    for f in sorted(glob.glob(str(ROOT.parent / 'content/lernpfade-fa-*.json'))):
        d = json.load(open(f, encoding='utf-8'))
        out += d.get('pfade') or d.get('lernpfade') or []
    ids = [p['id'] for p in out]
    assert len(ids) == len(set(ids)), 'doppelte Lernpfad-ID'
    out.sort(key=lambda p: p['id'])
    for p in out:
        p['slug'] = slugify(p['id'] + ' ' + p['name'].split(':')[0])
    return out

def norm_check(p):
    c = p.get('abschluss_check') or p.get('check')
    if not isinstance(c, dict): return None
    tasks, quiz = [], []
    for key, v in c.items():
        if not isinstance(v, list) or key == 'quiz': continue
        for t in v:
            if isinstance(t, str): t = {'frage': t}
            q = t.get('frage') or t.get('szenario') or t.get('aufgabe') or ''
            a = t.get('loesung') or t.get('musterloesung') or ''
            if q: tasks.append((q, a))
    for t in c.get('quiz') or []:
        if not isinstance(t, dict): continue
        q = t.get('frage') or t.get('q') or ''
        a = t.get('antwort', t.get('loesung', t.get('a')))
        o = t.get('optionen')
        if isinstance(a, int) and isinstance(o, list) and 0 <= a < len(o):
            a = o[a] + ((' ' + t['erklaerung']) if t.get('erklaerung') else '')
        if q and isinstance(a, str) and a: quiz.append((q, a))
    intro = c.get('einleitung') or c.get('beschreibung') or ''
    return (intro, tasks, quiz) if tasks or quiz else None

def iso_dur(z):
    m = re.search(r'(\d+)\s*(?:-|bis)\s*(\d+)\s*(min|h|std)', z or '', re.I) or re.search(r'()(\d+(?:[.,]\d+)?)\s*(min|h|std)', z or '', re.I)
    if not m: return None
    v = float((m.group(2)).replace(',', '.')); mins = round(v if m.group(3).lower().startswith('min') else v * 60)
    h, mm = divmod(mins, 60)
    return 'PT' + ('%dH' % h if h else '') + ('%dM' % mm if mm else '')

PROGRESS_JS = r'''(function(){var K="fa-lernpfad-",ls=null;try{ls=window.localStorage;ls.setItem(K+"t","1");ls.removeItem(K+"t")}catch(e){ls=null}
function get(id){try{return JSON.parse(ls.getItem(K+id)||"[]")}catch(e){return[]}}
function put(id,a){try{if(a.length)ls.setItem(K+id,JSON.stringify(a));else ls.removeItem(K+id)}catch(e){}}
var sec=document.querySelector(".lp-path");
if(sec&&ls){var id=sec.dataset.id,boxes=sec.querySelectorAll(".lp-check"),pr=sec.querySelector(".lp-prog"),pt=sec.querySelector(".lp-prog-t"),rs=sec.querySelector(".lp-reset");
function upd(){var n=0;boxes.forEach(function(b){if(b.checked)n++;b.closest(".lp-step").classList.toggle("done",b.checked)});var t="Fortschritt: "+n+" von "+boxes.length+" Schritten";pt.textContent=t;pr.value=n;pr.max=boxes.length;pr.setAttribute("aria-valuetext",t);rs.hidden=!n}
var done=get(id);boxes.forEach(function(b){b.disabled=false;b.checked=done.indexOf(+b.dataset.i)>-1;b.addEventListener("change",function(){var a=[];boxes.forEach(function(x){if(x.checked)a.push(+x.dataset.i)});put(id,a);upd()})});
rs.addEventListener("click",function(){boxes.forEach(function(b){b.checked=false});put(id,[]);upd()});
sec.querySelectorAll(".lp-js").forEach(function(e){e.hidden=false});upd()}
var cards=document.querySelectorAll(".lp-card");
if(cards.length&&ls){cards.forEach(function(c){var n=get(c.dataset.id).length,tot=+c.dataset.n,el=c.querySelector(".lp-cardprog");if(n&&el){el.textContent=n+" von "+tot+" erledigt"}})}
var bar=document.querySelector(".lp-filter");if(bar){bar.hidden=false;var cnt=document.getElementById("lp-count");
function apply(v){var s=0;cards.forEach(function(c){var ok=!v||c.dataset.l===v;c.hidden=!ok;if(ok)s++});if(cnt)cnt.textContent=s+" von "+cards.length+" Pfaden"}
bar.addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;bar.querySelectorAll("button").forEach(function(x){x.setAttribute("aria-pressed",x===b?"true":"false")});apply(b.dataset.v)});apply("")}})();'''

def build_lernpfade(page, urls, OUT, BASE):
    paths = load_paths()
    shutil.copyfile(ROOT / 'lernpfade.css', Path(OUT) / 'lernpfade.css')
    gl = {g['slug']: g['term'] for g in json.load(open(ROOT.parent / 'content/glossary.json', encoding='utf-8'))['entries']}
    byid = {p['id']: p for p in paths}
    def title_of(st):
        f = Path(OUT + st['slug'] + 'index.html')
        if f.exists():
            t = f.read_text(encoding='utf-8')
            m = re.search(r'<h1[^>]*>(.*?)</h1>', t, re.S) or re.search(r'<title>(.*?)</title>', t, re.S)
            if m: return html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).replace(' | finanz adjust', '').strip()
        return st.get('title') or st['slug'].strip('/').split('/')[-1].replace('-', ' ').capitalize()
    for p in paths:
        for st in p['steps']:
            if not Path(OUT + st['slug'] + 'index.html').exists(): print('WARN lernpfade: Seite fehlt (nur Titel aus Daten):', st['slug'])
            st['_t'] = title_of(st)
        p['_check'] = norm_check(p)
    css = '<link rel="stylesheet" href="/lernpfade.css">'
    def badge(p):
        return '<span class="lp-badge lp-%s">%s</span>' % (slugify(p['level']), esc(p['level'])) if p.get('level') else ''
    def meta(p):
        return ' · '.join(x for x in ['%d Schritte' % len(p['steps']), p.get('dauer', '')] if x)
    # Pfadseiten
    for p in paths:
        url = '/lernpfade/%s/' % p['slug']
        lis, parts = [], []
        for i, st in enumerate(p['steps'], 1):
            parts.append({'@type': 'WebPage', 'name': st['_t'], 'url': BASE + st['slug']})
            lis.append('<li class="lp-step"><input class="lp-check" type="checkbox" id="s%d" data-i="%d" disabled aria-label="Schritt %d erledigt: %s"><span class="lp-num" aria-hidden="true">%d</span><div><h3><a href="%s">%s</a></h3><p>%s</p></div></li>' % (i, i, i, esc(st['_t']), i, st['slug'], esc(st['_t']), esc(st['warum'])))
        facts = ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (l, esc(v if isinstance(v, str) else '; '.join(v))) for l, v in (('Zielgruppe', p.get('zielgruppe')), ('Dauer', p.get('dauer')), ('Voraussetzungen', p.get('voraussetzungen')), ('Lernziel', p.get('lernziel'))) if v)
        chips = ''.join('<a class="lp-chip" href="/glossar/%s/">%s</a>' % (esc(t), esc(gl[t])) for t in p.get('terms', []) if t in gl)
        for t in p.get('terms', []):
            if t not in gl: print('WARN lernpfade: Glossarbegriff fehlt:', t)
        c = p['_check']; ch = ''
        if c:
            intro, tasks, quiz = c
            ch = '<section class="lp-checkbox" id="check" aria-labelledby="check-h"><h2 id="check-h">Abschluss-Check</h2>' + ('<p>%s</p>' % esc(intro) if intro else '')
            if tasks:
                ch += '<h3>Aufgaben</h3><p class="lp-hint">Überlege zuerst selbst, dann klappe die Musterlösung auf.</p>' + ''.join(
                    ('<details class="lp-qa"><summary>%s</summary><div class="lp-ans"><strong>Musterlösung</strong><p>%s</p></div></details>' % (esc(q), esc(a))) if a else '<p class="lp-task">%s</p>' % esc(q) for q, a in tasks)
            if quiz:
                ch += '<h3>Quiz-Selbsttest</h3><p class="lp-hint">Antworte zuerst im Kopf, dann klappe die Antwort auf.</p>' + ''.join(
                    '<details class="lp-qa"><summary>%s</summary><div class="lp-ans"><strong>Antwort</strong><p>%s</p></div></details>' % (esc(q), esc(a)) for q, a in quiz)
            ch += '</section>'
        nxt = []
        for x in p.get('danach', []):
            xid = x['id'] if isinstance(x, dict) else x
            if xid in byid: nxt.append('<li><a href="/lernpfade/%s/">%s</a>%s</li>' % (byid[xid]['slug'], esc(byid[xid]['name']), (' <span class="lp-why">- ' + esc(x['warum']) + '</span>') if isinstance(x, dict) and x.get('warum') else ''))
        nxt_h = '<section class="lp-next"><h2>Danach weiter mit</h2><ul>%s</ul></section>' % ''.join(nxt) if nxt else ''
        toc = '<nav class="lp-toc" aria-label="In diesem Pfad"><a href="#schritte">Schritte</a>%s%s</nav>' % ('<a href="#begriffe">Begriffe</a>' if chips else '', '<a href="#check">Abschluss-Check</a>' if c else '')
        prog = '<div class="lp-js" hidden><progress class="lp-prog" value="0" max="%d" aria-label="Fortschritt im Pfad %s"></progress> <span class="lp-prog-t" aria-live="polite"></span> <button type="button" class="lp-reset" hidden>Zurücksetzen</button><p class="lp-hint">Dein Fortschritt bleibt nur auf diesem Gerät gespeichert (localStorage), nicht auf einem Server.</p></div>' % (len(p['steps']), esc(p['name']))
        body = (css + '<main class="lp-wrap"><section class="lp-path" data-id="%s"><p class="lp-kicker">FA WISSEN / LERNPFAD</p><h1>%s</h1><div class="lp-pmeta">%s<span>%s</span></div><p class="lp-q">%s</p><p class="lp-lead">%s</p><dl class="lp-facts">%s</dl>%s'
                '<h2 id="schritte">Schritte</h2>%s<ol class="lp-steps">%s</ol>%s%s%s'
                '<p class="lp-disc">Allgemeine Information, keine Anlageberatung. <a href="/risikohinweis/">Risikohinweis</a></p><p class="lp-top"><a href="/lernpfade/">Alle Lernpfade</a></p></section></main><script>%s</script>') % (
            esc(p['id']), esc(p['name']), badge(p), esc(meta(p)), esc(p['frage']), esc(p['intro']), facts, toc, prog, ''.join(lis),
            ('<h2 id="begriffe">Begriffe auf diesem Weg</h2><p class="lp-terms">%s</p>' % chips) if chips else '', ch, nxt_h, PROGRESS_JS)
        lr = {'@type': 'LearningResource', '@id': BASE + url + '#path', 'url': BASE + url, 'name': p['name'], 'description': p.get('lernziel') or p['frage'], 'inLanguage': 'de-DE',
              'learningResourceType': 'Lernpfad', 'isPartOf': {'@id': BASE + '/lernpfade/#page'}, 'hasPart': parts}
        if p.get('level'): lr['educationalLevel'] = p['level']
        if p.get('zielgruppe'): lr['audience'] = {'@type': 'Audience', 'audienceType': p['zielgruppe']}
        d = iso_dur(p.get('dauer', ''))
        if d: lr['timeRequired'] = d
        if p.get('lernziel'): lr['teaches'] = p['lernziel']
        if c: lr['assesses'] = p.get('lernziel') or p['name']
        urls.append(page(url, '%s | Lernpfad | finanz adjust' % p['name'], ('%s %s' % (p['frage'], p.get('lernziel', '')))[:300].strip(), body, ld=[lr],
                         act='/lernpfade/', crumbs=[('/lernpfade/', 'Lernpfade'), (url, p['name'])]))
    # Uebersicht
    cards = ''.join('<a class="lp-card" href="/lernpfade/%s/" data-id="%s" data-n="%d" data-l="%s">%s<strong>%s</strong><span>%s</span><em class="lp-meta">%s</em><em class="lp-cardprog" aria-hidden="true"></em></a>' % (
        p['slug'], esc(p['id']), len(p['steps']), esc(p.get('level', '')), badge(p), esc(p['name']), esc(p['frage']), esc(meta(p))) for p in paths)
    levels = [l for l in LEVELS if any(p.get('level') == l for p in paths)]
    filt = ''
    if len(levels) > 1:
        filt = '<div class="lp-filter" role="group" aria-label="Pfade nach Level filtern" hidden><button type="button" data-v="" aria-pressed="true">Alle</button>%s<p id="lp-count" class="lp-count" role="status" aria-live="polite"></p></div>' % ''.join('<button type="button" data-v="%s" aria-pressed="false">%s</button>' % (esc(l), esc(l)) for l in levels)
    intro = 'Lernpfade führen dich Schritt für Schritt durch Artikel, Glossar und Rechner von finanz adjust: in sinnvoller Reihenfolge, mit Abschluss-Check und Fortschritt auf deinem Gerät.'
    body = (css + '<main class="lp-wrap"><p class="lp-kicker">FA WISSEN / LERNPFADE</p><h1>Finanzwissen in %d Lernpfaden</h1><p class="lp-lead">%s</p>%s<div class="lp-cards">%s</div>'
            '<p class="lp-disc">Allgemeine Information, keine Anlageberatung. <a href="/risikohinweis/">Risikohinweis</a> · Nachschlagen im <a href="/glossar/">Glossar</a>. Dein Fortschritt wird nur lokal in deinem Browser gespeichert.</p></main><script>%s</script>') % (len(paths), intro, filt, cards, PROGRESS_JS)
    ld = [{'@type': 'CollectionPage', '@id': BASE + '/lernpfade/#page', 'url': BASE + '/lernpfade/', 'name': 'Lernpfade', 'inLanguage': 'de-DE', 'description': intro,
           'mainEntity': {'@type': 'ItemList', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': p['name'], 'url': '%s/lernpfade/%s/' % (BASE, p['slug'])} for i, p in enumerate(paths)]}}]
    urls.append(page('/lernpfade/', 'Lernpfade: Finanzwissen Schritt für Schritt | finanz adjust', intro, body, ld=ld, act='/lernpfade/', crumbs=[('/lernpfade/', 'Lernpfade')]))
    return paths
