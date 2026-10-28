"""FA Broker: neutral, alphabetical, no affiliate links, only facts read on official provider pages."""
from pathlib import Path
from html import escape as e
import json,re
ROOT=Path(__file__).resolve().parent;DATA=ROOT.parent/'content/broker/brokers.json'
def de_date(iso):y,m,d=iso.split('-');return '%s.%s.%s'%(d,m,y)
CRITERIA=[
 ('Gesamtkosten statt Schlagzeile','Orderprovision, Fremdkosten, Spread und Handelsplatz zusammen betrachten. "0 €" heißt nicht automatisch kostenlos: Auch Spreads und Fremdkosten gehören zu den Handelskosten.'),
 ('Handelsplatz','Außerbörslich (z. B. gettex, Tradegate) oder Xetra: Preis, Ausführungszeiten und Kosten unterscheiden sich.'),
 ('Sparplan','Mindestrate, Ausführungstage und ob Aktien und ETFs bespart werden können.'),
 ('Steuer und Freistellungsauftrag','Broker mit Sitz in Deutschland führen die Abgeltungsteuer in der Regel automatisch ab. Bei Anbietern ohne Sitz in Deutschland bleibt die Steuererklärung in der Regel bei dir.'),
 ('Sicherheit des Depots','Wertpapiere im Depot sind Sondervermögen und bleiben bei einer Broker-Insolvenz dein Eigentum. Für Guthaben gilt die gesetzliche Einlagensicherung der kontoführenden Bank.'),
 ('Zinsen auf Guthaben','Variabel und oft befristet oder gedeckelt. Aktionszins ist kein Dauerzins.'),
 ('Service und App','Support, Handelszeiten, Steuerberichte und Übertrag zu anderen Brokern.')]
def build_broker(page,urls,out,base):
    d=json.loads(DATA.read_text());brokers=sorted(d['brokers'],key=lambda b:b['name'].lower())
    assets='<link rel="stylesheet" href="/calculators.css"><link rel="stylesheet" href="/comparisons.css">'
    cards=''
    def head(b):
        if b.get('logo'):return '<div class="cmp-offer-head"><img class="cmp-logo" src="/stock-logos/%s" alt="%s Logo" height="28" loading="lazy">'%(e(b['logo'],quote=True),e(b['name'],quote=True))+'<h2>%s</h2></div>'%e(b['name'])
        return '<div class="cmp-offer-head"><span class="cmp-monogram" aria-hidden="true">'+e(b['name'][0])+'</span><h2>%s</h2></div>'%e(b['name'])
    def cards_for(gruppe):
        out=''
        for b in [x for x in brokers if x.get('gruppe','aktien')==gruppe]:
            facts=''.join('<li>'+e(f)+'</li>' for f in b['fakten']);facts='<ul>'+facts+'</ul>' if facts else ''
            out+=('<article class="cmp-broker" id="%s">'+head(b)+'<p class="cmp-date">%s · Preisstand %s</p>%s<p>%s</p>'
              '<p><a href="/broker/%s/">Details ↗</a> · <a href="%s" rel="noopener noreferrer nofollow" target="_blank">Anbieter-Seite ↗</a> · <a href="%s" rel="noopener noreferrer nofollow" target="_blank">Preise und Konditionen ↗</a></p></article>')%(
              e(b['id']),e(b['typ']),de_date(d['stand']),facts,e(b['hinweis']),e(b['id']),e(b['url'],quote=True),e(b['plv'],quote=True))
        return out
    cards=('<h2 class="cmp-group" id="aktien">Aktiendepots und Neobroker</h2><div class="cmp-offers">'+cards_for('aktien')+'</div>'
      '<h2 class="cmp-group" id="cfd">CFD- und Forex-Anbieter</h2>'
      '<p class="cmp-alert">CFDs und Devisenhandel sind gehebelte Produkte mit hohem Verlustrisiko und kein klassisches Aktiendepot. Die Anbieter weisen die Verlustrate der Kleinanlegerkonten auf ihren Seiten aus.</p>'
      '<div class="cmp-offers">'+cards_for('cfd')+'</div>')
    crit=''.join('<li><b>%s:</b> %s</li>'%(e(t),e(x)) for t,x in CRITERIA)
    body=(assets+'<main class="calc-wrap cmp-wrap"><nav class="cmp-nav" aria-label="Broker-Bereich"><a href="/broker/">Broker</a><a href="#kriterien">Worauf achten</a><a href="/vergleiche/depot/">Kostenvergleich Depot &amp; Broker</a><a href="/lernpfade/">Lernpfade</a><a href="/glossar/">Glossar</a></nav>'
      '<p class="calc-kicker">FA BROKER / ANZEIGENFREI</p><h1>Broker für Aktien: Konditionen im Überblick</h1>'
      '<p class="calc-lead">Wo kann man die Aktien von finanz adjust eigentlich handeln? Hier stehen bekannte Anbieter alphabetisch: zuerst Aktiendepots und Neobroker, darunter getrennt CFD- und Forex-Anbieter. Zahlen nennen wir nur, wenn wir sie am '+de_date(d['stand'])+' in den offiziellen Preisangaben gelesen haben. Wo die Lage unklar ist, steht nur der Link.</p>'
      '<p class="cmp-alert">Keine Empfehlung, kein Testsieger, keine Rangliste. Keine Partnerschaft mit den Anbietern, keine Affiliate-Links, keine Provision für FA. Die Auswahl ist begrenzt und kein vollständiger Marktüberblick. Konditionen ändern sich: Vor einer Kontoeröffnung immer direkt beim Anbieter prüfen. Der Handel mit Wertpapieren birgt Verlustrisiken bis zum Totalverlust. Keine Anlageberatung.</p>'
      '<div class="cmp-offers">'+cards+'</div>'
      '<section class="calc-info" id="kriterien"><h2>Worauf du bei einem Broker achten solltest</h2><ul>'+crit+'</ul></section>'
      '<section class="calc-info"><h2>Weiterlesen auf FA</h2><p><a href="/vergleiche/depot/">Depot &amp; Broker: Kosten für den eigenen Handelsstil vergleichen</a> · <a href="/rechner/">Finanzrechner</a> · <a href="/aktien/">Aktien-Seiten</a> · <a href="/lernpfade/">Lernpfade für Einsteiger</a> · <a href="/glossar/">Glossar</a> · <a href="/risikohinweis/">Risikohinweis</a></p></section>'
      '<p class="cmp-source">Quellen: jeweilige Anbieter-Seiten und Preis- und Leistungsverzeichnisse (verlinkt). Zusammenfassung in eigenen Worten durch FA, Angaben ohne Gewähr. Markennamen gehören den jeweiligen Inhabern.</p></main>')
    desc='Bekannte Broker alphabetisch mit Konditionen aus offiziellen Quellen, Kriterien zur Auswahl, ohne Affiliate-Links und ohne Rangliste.'
    urls.append(page('/broker/','Broker für Aktien: Konditionen im Überblick | finanz adjust',desc,body,crumbs=[('/broker/','Broker')]))
    for b in brokers:
        facts=''.join('<li>'+e(f)+'</li>' for f in b['fakten']);facts='<ul>'+facts+'</ul>' if facts else '<p>Keine Zahlen auf dieser Seite: Die Lage war am Stichtag nicht belastbar aus den offiziellen Angaben lesbar.</p>'
        sub=(assets+'<main class="calc-wrap cmp-wrap"><nav class="cmp-nav" aria-label="Broker-Bereich"><a href="/broker/">Alle Broker</a><a href="/broker/#kriterien">Worauf achten</a><a href="/vergleiche/depot/">Kostenvergleich Depot &amp; Broker</a><a href="/lernpfade/">Lernpfade</a><a href="/glossar/">Glossar</a></nav>'
          +'<p class="calc-kicker">FA BROKER / ANZEIGENFREI</p>'+head(b)
          +'<p class="calc-lead">'+e(b['typ'])+' · Preisstand '+de_date(d['stand'])+'</p>'
          +'<section class="calc-info"><h2>Konditionen im Überblick</h2>'+facts+'</section>'
          +'<p class="cmp-alert">'+e(b['hinweis'])+'</p>'
          +'<section class="calc-info"><h2>Direkt beim Anbieter prüfen</h2><p><a href="'+e(b['url'],quote=True)+'" rel="noopener noreferrer nofollow" target="_blank">Anbieter-Seite ↗</a> · <a href="'+e(b['plv'],quote=True)+'" rel="noopener noreferrer nofollow" target="_blank">Preise und Konditionen ↗</a></p>'
          +'<p>Keine Empfehlung und keine Rangliste: Keine Partnerschaft mit dem Anbieter, keine Affiliate-Links, keine Provision für FA. Konditionen ändern sich; maßgeblich ist die Preisangabe des Anbieters. Der Handel mit Wertpapieren birgt Verlustrisiken bis zum Totalverlust. Keine Anlageberatung.</p></section>'
          +'<section class="calc-info"><h2>Weiterlesen auf FA</h2><p><a href="/broker/">Alle Broker im Überblick</a> · <a href="/broker/#kriterien">Worauf du bei einem Broker achten solltest</a> · <a href="/vergleiche/depot/">Depot &amp; Broker: Kosten vergleichen</a> · <a href="/risikohinweis/">Risikohinweis</a></p></section>'
          +'<p class="cmp-source">Quellen: Anbieter-Seite und Preis- und Leistungsverzeichnis (verlinkt). Zusammenfassung in eigenen Worten durch FA, Angaben ohne Gewähr. Markennamen gehören den jeweiligen Inhabern.</p></main>')
        urls.append(page('/broker/%s/'%e(b['id']),'%s: Konditionen im Überblick | finanz adjust'%e(b['name']),'Konditionen von %s (%s): Fakten aus offiziellen Anbieter-Angaben, Stand %s. Ohne Affiliate-Links und ohne Rangliste.'%(e(b['name']),e(b['typ']),de_date(d['stand'])),sub,crumbs=[('/broker/','Broker'),('/broker/%s/'%e(b['id']),e(b['name']))]))
    # discoverability without touching other renderers
    box=('<aside class="calc-note broker-hint"><p><b>Wo handeln?</b> <a href="/broker/">Broker im Überblick</a> (ohne Werbung, ohne Rangliste) · <a href="/vergleiche/depot/">Handelskosten vergleichen</a></p></aside>')
    for p,marker in [(Path(out)/'aktien/index.html','</main>'),(Path(out)/'vergleiche/index.html','</main>'),(Path(out)/'vergleiche/depot/index.html','</main>'),(Path(out)/'rechner/index.html','</main>')]:
        if p.exists():
            t=p.read_text()
            if 'broker-hint' not in t:p.write_text(t.replace(marker,box+marker,1))
    for p in (Path(out)/'aktien').glob('*/index.html'):
        t=p.read_text()
        if 'broker-hint' not in t and '</main>' in t:p.write_text(t.replace('</main>',box+'</main>',1))
