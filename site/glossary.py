"""Curated, source-linked glossary. No network requests or automatic fact imports."""
import json, re, shutil, unicodedata
from pathlib import Path
from html import escape as e
ROOT = Path(__file__).resolve().parent

def normalize(text):
    text=text.lower().replace('ß','ss').replace('ae','ä').replace('oe','ö').replace('ue','ü')
    return ''.join(c for c in unicodedata.normalize('NFD',text) if unicodedata.category(c)!='Mn')

def load_entries():
    entries=json.loads((ROOT.parent/'content/glossary.json').read_text())['entries']
    slugs={g['slug'] for g in entries}
    assert len(slugs)==len(entries), 'Duplicate glossary slug'
    for g in entries:
        assert re.fullmatch('[a-z0-9-]+',g['slug'])
        assert all(g.get(k) for k in ('term','category','short','explain','caution','sources','verified','faq'))
        assert all(s in slugs for s in g['related']), 'Broken related term'
        assert all(s['url'].startswith('https://') and s['section'] and s['checked'] for s in g['sources'])
    return sorted(entries,key=lambda g:normalize(g['term']))

def matching_articles(g,articles):
    terms=[g['term'].split(' (')[0]]+g.get('aliases',[])
    return [a for a in articles if any(re.search(r'(?<!\w)'+re.escape(normalize(t))+r'(?!\w)',normalize(a['title']+' '+a.get('description',''))) for t in terms)][:4]

def schemas(g,base):
    url=base+'/glossar/'+g['slug']+'/'
    term={'@context':'https://schema.org','@type':'DefinedTerm','@id':url+'#term','name':g['term'],'description':g['short'],'url':url,'inDefinedTermSet':{'@type':'DefinedTermSet','@id':base+'/glossar/#terms','name':'FA Börsen-Glossar'},'alternateName':g.get('aliases',[])}
    web={'@context':'https://schema.org','@type':'WebPage','url':url,'name':g['term']+' einfach erklärt','inLanguage':'de-DE','dateModified':g['verified'],'author':{'@type':'Organization','name':'FA Redaktion'},'about':{'@id':url+'#term'},'citation':[s['url'] for s in g['sources']]}
    faq={'@context':'https://schema.org','@type':'FAQPage','mainEntity':[{'@type':'Question','name':f['q'],'acceptedAnswer':{'@type':'Answer','text':f['a']}} for f in g['faq']]}
    return [term,web,faq]

def build_glossary(page,urls,articles,out,base):
    entries=load_entries(); byslug={g['slug']:g for g in entries}
    for asset in ('glossary.css','glossary.js'):shutil.copyfile(ROOT/asset,Path(out)/asset)
    assets='<link rel="stylesheet" href="/glossary.css"><script src="/glossary.js" defer></script>'
    def link(g):return '<a href="/glossar/%s/">%s <span aria-hidden="true">↗</span></a>'%(g['slug'],e(g['term']))
    categories=sorted({g['category'] for g in entries})
    letters=sorted({normalize(g['term'])[0].upper() for g in entries})
    paths=[('Start mit Aktien',['was-ist-eine-aktie','was-ist-eine-dividende','boersenindex']),('Fonds verstehen',['was-ist-ein-etf','gesamtkostenquote','diversifikation']),('Nachrichten einordnen',['leitzins','inflation','einkaufsmanagerindex'])]
    routes=''.join('<section><h2>%s</h2><ol>%s</ol></section>'%(e(title),''.join('<li>'+link(byslug[s])+'</li>' for s in slugs)) for title,slugs in paths)
    groups=''
    for letter in letters:
        cards=''
        for g in entries:
            if normalize(g['term'])[0].upper()!=letter:continue
            search=normalize(' '.join([g['term'],g['short']]+g.get('aliases',[])))
            cards+='<a class="gl-card" href="/glossar/%s/" data-term="%s" data-category="%s"><span class="gl-category">%s</span><h3>%s <span aria-hidden="true">↗</span></h3><p>%s</p></a>'%(g['slug'],e(search,quote=True),e(g['category'],quote=True),e(g['category']),e(g['term']),e(g['short']))
        groups+='<section class="gl-letter" id="letter-%s" aria-labelledby="heading-%s"><h2 id="heading-%s">%s</h2><div class="gl-cards">%s</div></section>'%(letter,letter,letter,letter,cards)
    alphabet=''.join('<a href="#letter-%s" data-letter="%s">%s</a>'%(x,x,x) if x in letters else '<span aria-hidden="true">%s</span>'%x for x in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    body=assets+'''<main class="gl-wrap"><section class="gl-hero"><div><p class="gl-kicker">FA WISSEN / BÖRSEN-GLOSSAR</p><h1>Weniger Börsenlatein.<br>Mehr Durchblick.</h1><p class="gl-lead">Von Aktie bis Zins: Finanzbegriffe verständlich erklärt. Mit Quellen, Zusammenhängen und einem klaren Blick auf die Risiken.</p><div class="gl-pills"><span>%d Begriffe</span><span>%d Themenwelten</span><span>FA Redaktion</span></div></div><aside class="gl-hero-note"><span aria-hidden="true">Aa</span><h2>Erst verstehen.<br>Dann einordnen.</h2><p>Kurze Definition, Hintergründe und typische Missverständnisse. Kein Fachwissen vorausgesetzt.</p><a href="#verzeichnis">Zum A-Z-Verzeichnis ↓</a></aside></section><div class="gl-routes">%s</div><section class="gl-directory" id="verzeichnis" aria-labelledby="gl-heading"><div class="gl-section-title"><h2 id="gl-heading">Dein Wissen von A bis Z</h2><span id="gl-count" role="status" aria-live="polite">%d Begriffe</span></div><form class="gl-controls" role="search" action="/glossar/" method="get"><div><label for="gl-query">Begriff oder Abkürzung suchen</label><input type="search" name="q" id="gl-query" placeholder="Zum Beispiel ETF, Dividende oder ZEW" aria-controls="gl-results" autocomplete="off"></div><div><label for="gl-topic">Themenwelt</label><select id="gl-topic" name="thema"><option value="">Alle Themen</option>%s</select></div><button type="button" id="gl-reset" hidden>Zurücksetzen</button></form><noscript><p>Die Suche benötigt JavaScript. Alle Begriffe sind unten alphabetisch verlinkt.</p></noscript><nav class="gl-alphabet" aria-label="Alphabet">%s</nav><div id="gl-results">%s</div><p id="gl-empty" hidden>Kein passender Begriff. Versuche einen anderen Suchbegriff oder setze die Filter zurück.</p></section><aside class="gl-method"><h2>Wissen, das seine Quellen zeigt.</h2><p>Jeder Eintrag nennt die fachliche Quelle und den Prüfstand. Die Auswahl ist kuratiert und wird erweitert, sie ist kein vollständiges Finanzlexikon. Beispiele dienen dem Verständnis, nicht der Prognose.</p><p>Die Inhalte entstehen mit <a href="/transparenz/">KI-Unterstützung</a>. Fehler entdeckt? <a href="/korrekturen/">Korrektur melden</a>. Keine Anlageberatung oder Kaufempfehlung.</p></aside></main>'''%(len(entries),len(categories),routes,len(entries),''.join('<option value="%s">%s</option>'%(e(c,quote=True),e(c)) for c in categories),alphabet,groups)
    ld=[{'@context':'https://schema.org','@type':'DefinedTermSet','@id':base+'/glossar/#terms','url':base+'/glossar/','name':'FA Börsen-Glossar','inLanguage':'de-DE','hasDefinedTerm':[{'@type':'DefinedTerm','name':g['term'],'url':base+'/glossar/'+g['slug']+'/'} for g in entries]}]
    urls.append(page('/glossar/','Börsen-Glossar: %d Finanzbegriffe von A bis Z | finanz adjust'%len(entries),'Finanzbegriffe einfach erklärt: Aktien, ETF, Anleihen und Wirtschaft. A-Z, Suche, Themenfilter und Quellen der FA Redaktion.',body,ld,act='/glossar/',crumbs=[('/glossar/','Glossar')]))
    for g in entries:
        matches=matching_articles(g,articles)
        reads=''
        if matches:reads='<section class="gl-detail-box"><h2>Aus der FA Redaktion</h2><ul>'+''.join('<li><a href="/artikel/%s/">%s</a></li>'%(e(a['slug']),e(a['title'])) for a in matches)+'</ul></section>'
        if g['category']=='Aktien & Börse' or g['slug'] in ('isin','wkn','boersenplatz','xetra','depotauszug'):
            reads+='<section class="gl-detail-box"><h2>Vom Begriff zum Wertpapier</h2><p>Unternehmen, Ticker und Handelsplätze im <a href="/aktien/">FA-Aktienverzeichnis</a> ansehen. Beispiele: <a href="/aktien/apple/">Apple</a> und <a href="/aktien/msft/">Microsoft</a>. Die Verknüpfung erklärt den Seitentyp, sie ist keine Auswahl- oder Kaufempfehlung.</p></section>'
        src=''.join('<li><a href="%s" rel="noopener noreferrer">%s ↗</a><span>Abschnitt: %s · geprüft am %s</span></li>'%(e(s['url'],quote=True),e(s['name']),e(s['section']),e(s['checked'])) for s in g['sources'])
        aliases='<p class="gl-alias">Auch bekannt als: '+e(', '.join(g['aliases']))+'</p>' if g.get('aliases') else ''
        example='<section class="gl-example"><h2>Ein Beispiel</h2><p>'+e(g['example'])+'</p></section>' if g.get('example') else ''
        body=assets+'''<main class="gl-wrap gl-detail"><a class="gl-back" href="/glossar/">← Alle Finanzbegriffe</a><div class="gl-detail-layout"><article><p class="gl-kicker">%s</p><h1>%s</h1><p class="gl-by">FA Redaktion · Fachlicher Prüfstand: %s · <a href="/transparenz/">Mit KI-Unterstützung</a></p><div class="gl-definition"><span>KURZ ERKLÄRT</span><p>%s</p></div>%s<section><h2>So funktioniert's</h2><p>%s</p></section>%s<section class="gl-caution"><h2>Wichtig zu unterscheiden</h2><p>%s</p></section><section class="faq"><h2>Häufige Fragen</h2>%s</section><section class="gl-sources"><h2>Quellen &amp; Prüfstand</h2><ul>%s</ul><p>Eigenständige Zusammenfassung der FA Redaktion. Quellen dienen der fachlichen Einordnung, nicht als Anlageempfehlung.</p></section></article><aside class="gl-sidebar"><section class="gl-detail-box"><h2>Hängt zusammen mit</h2><ul>%s</ul></section>%s<section class="gl-detail-box"><h2>Einordnen statt empfehlen</h2><p>Allgemeine Information, keine Anlageberatung. <a href="/risikohinweis/">Risiken verstehen</a></p></section></aside></div><nav class="gl-prevnext" aria-label="Weitere Begriffe">%s</nav></main>'''%(e(g['category']),e(g['term']).replace('Einkaufsmanagerindex','Einkaufsmanager&shy;index'),e(g['verified']),e(g['short']),aliases,e(g['explain']),example,e(g['caution']),''.join('<details><summary>%s</summary><p>%s</p></details>'%(e(f['q']),e(f['a'])) for f in g['faq']),src,''.join('<li>'+link(byslug[s])+'</li>' for s in g['related']),reads,' · '.join(link(entries[i]) for i in [entries.index(g)-1,entries.index(g)+1] if 0<=i<len(entries)))
        urls.append(page('/glossar/'+g['slug']+'/',g['term']+' einfach erklärt | FA Glossar',g['short'],body,schemas(g,base),act='/glossar/',crumbs=[('/glossar/','Glossar'),('/glossar/'+g['slug']+'/',g['term'])]))
    # Add contextual links to existing articles, without changing their URLs or bodies.
    for a in articles:
        related=[g for g in entries if a in matching_articles(g,[a])][:5]
        path=Path(out)/'artikel'/a['slug']/'index.html'
        if related and path.exists():
            text=path.read_text(); block='<aside class="gl-article-links"><h2>Begriffe zum Weiterlesen</h2>'+''.join(link(g)+' ' for g in related)+'</aside>'
            text=text.replace('</head>','<link rel="stylesheet" href="/glossary.css"></head>')
            text=text.replace('<div class="faq">',block+'<div class="faq">',1) if '<div class="faq">' in text else text.replace('<footer>',block+'<footer>',1)
            path.write_text(text)
    return entries
