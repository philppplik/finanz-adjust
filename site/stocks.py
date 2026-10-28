"""Dependency-free, static stock directory. No quote scraping or third-party requests."""
import json, re, shutil
from pathlib import Path
from html import escape as e

ROOT = Path(__file__).resolve().parent

def normalize(text):
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFD', text.lower().replace('ß','ss')) if unicodedata.category(c) != 'Mn')

def related(stock, articles):
    terms = [normalize(x) for x in stock['aliases'] + [stock['name']]]
    return [a for a in articles if any(re.search(r'(?<!\w)' + re.escape(t) + r'(?!\w)', normalize(a.get('title','')+' '+a.get('description',''))) for t in terms)][:6]

def build_stock_pages(page, urls, articles, out, base):
    profiles=json.loads((ROOT/'company_profiles.json').read_text()) if (ROOT/'company_profiles.json').exists() else {}
    stocks = json.loads((ROOT/'stocks.json').read_text())
    assert len({s['slug'] for s in stocks}) == len(stocks)
    for s in stocks:
        assert re.fullmatch('[a-z0-9-]+', s['slug'])
    shutil.copyfile(ROOT/'stocks.js', Path(out)/'stocks.js')
    shutil.copyfile(ROOT/'stocks.css', Path(out)/'stocks.css')
    shutil.copyfile(ROOT/'tradingview.js', Path(out)/'tradingview.js')
    if (ROOT/'logos').is_dir(): shutil.copytree(ROOT/'logos',Path(out)/'stock-logos',dirs_exist_ok=True)
    assets = '<link rel="stylesheet" href="/stocks.css"><script src="/stocks.js" defer></script><script src="/tradingview.js" defer></script>'
    def search():
        return '''<form class="stock-search" action="/aktien/" role="search"><label for="stock-query">Aktie suchen</label><div class="stock-search-field"><input id="stock-query" name="q" type="search" placeholder="Name, Ticker oder ISIN" autocomplete="off" aria-controls="stock-results"><button type="submit">Suchen</button></div><p class="stock-note">Suche im FA-Verzeichnis. Nicht alle börsennotierten Unternehmen sind enthalten.</p></form>'''
    def mark(stock):
        if stock.get('logo'):return '<img class="stock-logo" src="/stock-logos/'+e(stock['logo'],quote=True)+'" alt="'+e(stock['name'],quote=True)+' Logo" width="28" height="28">'
        return e(stock['ticker'][:2])
    def cards():
        return ''.join('<a class="stock-card" href="/aktien/%s/" data-stock="%s"><span class="stock-monogram" aria-hidden="true">%s</span><span><strong>%s</strong><small>%s · %s%s</small></span><span aria-hidden="true">↗</span></a>' % (s['slug'],e(normalize(' '.join([s['name'],s['ticker'],s.get('isin','')]+s['aliases'])),quote=True),mark(s),e(s['name']),e(s['ticker']),e(s['exchange']),(' · '+e(s['isin'])) if s.get('isin') else '') for s in stocks)
    body = assets + '<main class="stock-wrap"><div class="stock-hero"><p class="stock-kicker">FA MARKTDATEN</p><h1>Aktien finden. Märkte besser einordnen.</h1><p>Aktien finden, Handelsplätze unterscheiden und die Berichterstattung der FA Redaktion lesen.</p>'+search()+'</div><section aria-labelledby="directory-title"><div class="stock-heading"><h2 id="directory-title">Aktienverzeichnis</h2><span id="stock-count" role="status" aria-live="polite">%d Aktien</span></div><div class="stock-grid" id="stock-results">%s</div><p id="stock-empty" hidden>Keine Aktie gefunden. Prüfe die Schreibweise oder versuche den Ticker. Das Verzeichnis wird schrittweise erweitert.</p></section><aside class="stock-info"><h2>Was du hier findest</h2><p>Jede Aktie hat eine eigene Seite mit Handelsplatz, Ticker und passenden FA-Artikeln. Kursdaten kommen nach Verfügbarkeit vom API-Anbieter; bei Ausfällen kann TradingView nach deinem Klick einspringen. Fehlende Kurse sind kein Kurs von null.</p><p>Keine Kaufempfehlungen, keine Kursziele. <a href="/risikohinweis/">Zum Risikohinweis</a></p></aside></main>' % (len(stocks),cards())
    urls.append(page('/aktien/','Aktien suchen: Ticker und Unternehmensseiten | finanz adjust','Aktien nach Name, Ticker oder ISIN finden. Unternehmensseiten mit Handelsplatz und Artikeln der FA Redaktion.',body,act='/aktien/',crumbs=[('/aktien/','Aktien')]))
    from stock_data import refresh, render_quote
    quotes=refresh(stocks, ROOT.parent/'data'/'stock-quotes.json')
    for s in stocks:
        matches=related(s,articles)
        news=''.join('<li><a href="/artikel/%s/">%s</a><p>%s</p></li>'%(e(a['slug']),e(a['title']),e(a.get('description',''))) for a in matches)
        if not news: news='<li>Noch kein eigener FA-Artikel zu dieser Aktie. <a href="/artikel/">Alle Artikel lesen</a></li>'
        facts=[('Ticker',s['ticker']),('Handelsplatz',s['exchange']),('Währung',s['currency'])]
        if s.get('isin'): facts.append(('ISIN',s['isin']))
        path='/aktien/%s/'%s['slug']
        body=assets+'''<main class="stock-wrap"><div class="stock-back"><a href="/aktien/">← Alle Aktien</a></div><header class="stock-title"><div><p class="stock-kicker">%s · %s</p><h1>%s Aktie</h1><p>Unternehmensseite · FA Redaktion</p></div><span class="stock-tag">%s</span></header><nav class="stock-tabs" aria-label="Seitenabschnitte"><a href="#kurs">Kursdaten</a><a href="#stammdaten">Stammdaten</a><a href="#news">FA-Artikel</a></nav><section id="kurs" class="stock-quote"><div><p class="stock-kicker">KURSDATEN</p><h2>Kurs noch nicht verfügbar</h2><p>Für diesen Handelsplatz ist noch keine Kursdatenquelle angebunden.</p></div><dl><div><dt>Kurszeit</dt><dd>Nicht verfügbar</dd></div><div><dt>Verzögerung</dt><dd>Nicht verfügbar</dd></div></dl><p class="stock-note">Keine geschätzten Kurse. Keine Vermischung von Börsenplätzen oder Währungen.</p></section><div class="stock-columns"><section id="stammdaten" class="stock-panel"><h2>Wertpapier &amp; Handelsplatz</h2><dl class="stock-facts">%s</dl><p class="stock-note">Die Angaben beziehen sich auf die hier genannte Notierung. Andere Handelsplätze können andere Ticker und Währungen verwenden.</p><p><a class="stock-source" href="%s" target="_blank" rel="noopener noreferrer">Stammdatenquelle öffnen ↗</a></p><p class="stock-note">Quelle geprüft: %s. Stammdaten können sich ändern.</p></section><section id="news" class="stock-panel"><h2>Aus der FA Redaktion</h2><ul class="stock-news">%s</ul></section></div><section class="stock-info"><h2>Wie aktuell sind die Daten?</h2><p>Die Stammdaten werden beim Seitenaufbau übernommen. Wenn die API keine Kursdaten liefert, kann TradingView nach ausdrücklichem Klick geladen werden. Kurse und Kennzahlen sind nicht für alle Titel verfügbar. Quelle, Kurszeit und mögliche Verzögerung stehen direkt bei den verfügbaren Daten.</p><p>Diese Seite dient der Information, nicht der Anlageberatung. <a href="/risikohinweis/">Risiken verstehen</a></p></section>%s</main>'''%(e(s['exchange']),e(s['currency']),e(s['name']),(mark(s) if s.get('logo') else e(s['ticker'])),''.join('<div><dt>%s</dt><dd>%s</dd></div>'%(e(k),e(v)) for k,v in facts),e(s['source'],quote=True),e(s['verified']),news,search())
        quote_html=render_quote(quotes.get(s['slug']),s)
        if quote_html:
            body=re.sub(r'<section id="kurs".*?</section>',lambda _:quote_html,body,count=1,flags=re.S)
            body=body.replace('Wenn die API keine Kursdaten liefert, kann TradingView nach ausdrücklichem Klick geladen werden. Kurse und Kennzahlen sind nicht für alle Titel verfügbar.', 'Kursdaten werden beim Seitenaufbau vom genannten Anbieter abgerufen und zwischengespeichert. Es gibt keine Live-Aktualisierung im Browser.')
        else:
            from stock_fallback import fallback
            body=body.replace('<div class="stock-columns">',fallback(s)+'<div class="stock-columns">')
        try:
            from market_visuals import stock_spark_panel
            body=body.replace('<div class="stock-columns">',stock_spark_panel(s)+'<div class="stock-columns">',1)
        except ImportError: pass
        if s.get('logo_credit'):
            cap='Logo: '+e(s['logo_credit'])+'. Nur redaktionelle Kennzeichnung, keine Partnerschaft. <a class="stock-source" href="'+e(s['logo_source'],quote=True)+'" target="_blank" rel="noopener noreferrer">Bildquelle und Nutzungsbedingungen</a>'
            if s.get('logo'):
                ogp='/og/aktien/%s-logo.png'%s['slug']
                cap_html='<figure class="stock-ogimg"><img src="'+ogp+'" alt="'+e(s['name'],quote=True)+' Logo auf finanz adjust" width="1200" height="630" loading="lazy"><figcaption>'+cap+'</figcaption></figure>'
            else:
                cap_html='<p class="stock-note">'+cap+'</p>'
            body=body.replace('<div class="stock-columns">',cap_html+'<div class="stock-columns">')
        if s.get('isin_source'):
            body=body.replace('<div class="stock-columns">','<p class="stock-note"><a class="stock-source" href="'+e(s['isin_source'],quote=True)+'" target="_blank" rel="noopener noreferrer">ISIN-Quelle</a> · Einzelwerte können sich durch Kapitalmaßnahmen ändern.</p><div class="stock-columns">')
        profile=profiles.get(s['ticker']) if s['currency']=='USD' else None
        if profile:
            info='<section class="stock-panel" style="margin-top:24px"><h2>Unternehmen im Überblick</h2><p>'+e(profile['name'])+'</p><dl class="stock-facts">'+''.join('<div><dt>'+e(k)+'</dt><dd>'+e(str(v))+'</dd></div>' for k,v in [('Branche (SEC-Klassifikation)',profile.get('industry')),('SIC-Code',profile.get('sic'))] if v)+'</dl><p class="stock-note">Originalklassifikation des US-Melderegisters, keine aktuelle Unternehmensbewertung. Geprüft: '+e(profile['verified'])+'. <a class="stock-source" href="'+e(profile['source'],quote=True)+'" target="_blank" rel="noopener noreferrer">Quelle: SEC EDGAR</a></p></section>'
            body=body.replace('<div class="stock-columns">',info+'<div class="stock-columns">')
        ld={'@context':'https://schema.org','@type':'WebPage','name':s['name']+' Aktie','url':base+path,'inLanguage':'de-DE','about':{'@type':'Corporation','name':s['name'],'tickerSymbol':s['exchange']+':'+s['ticker']}}
        if s.get('logo'): ld['image']=base+'/og/aktien/%s-logo.png'%s['slug']
        urls.append(page(path,s['name']+' Aktie: Ticker, Handelsplatz & Nachrichten | finanz adjust',s['name']+' ('+s['ticker']+'): Kursdaten nach Verfügbarkeit, Stammdaten, Handelsplatz und passende Berichte der FA Redaktion.',body,[ld],act='/aktien/',crumbs=[('/aktien/','Aktien'),(path,s['name'])],og=('/og/aktien/%s-logo.png'%s['slug']) if s.get('logo') else None))
    return stocks
