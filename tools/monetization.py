#!/usr/bin/env python3
"""Final, idempotent static postprocessor: advertising pages, consent UI, activation gates.
Loads no remote resource. Usage: python3 tools/monetization.py <output-directory>"""
import sys, json, pathlib, html, re, shutil
from urllib.parse import quote, urlparse
ROOT = pathlib.Path(__file__).resolve().parent.parent
E = lambda text: html.escape(str(text), quote=True)
SITE = {'key': 'fa',
 'p': 'fa',
 'name': 'finanz adjust',
 'base': 'https://finanz-adjust.de',
 'urls': {'werben': '/werben/', 'werbung': '/werbung/', 'cookies': '/cookies/', 'datenschutz': '/datenschutz/', 'impressum': '/impressum/'},
 'files': {'werben': 'werben/index.html', 'werbung': 'werbung/index.html', 'cookies': 'cookies/index.html', 'datenschutz': 'datenschutz/index.html', 'impressum': 'impressum/index.html'},
 'body_start': '<div class="pg">',
 'wrap_open': '<div class="pg @@cls@@">',
 'wrap_close': '</div>',
 'titles': {'werben': 'Werben & Kooperationen | finanz adjust', 'werbung': 'Werbung & Affiliate | finanz adjust', 'cookies': 'Cookies & Einstellungen | finanz adjust'},
 'descs': {'werben': 'Dezente, klar gekennzeichnete Werbung und Kooperationen auf finanz adjust. Formate und unverbindliche Anfrage per E-Mail. Keine Anlageberatung.',
           'werbung': 'Wie finanz adjust Anzeigen, gesponserte Inhalte und Affiliate-Links kennzeichnet und von der Redaktion trennt.',
           'cookies': 'Datenschutzauswahl und lokaler Speicher auf finanz adjust. Statistik und Werbung sind derzeit deaktiviert.'},
 'cards': [('Anzeige · Gesponsert',
            'Artikel bewerben',
            'Ein klar abgegrenzter Hinweis auf einen passenden Artikel oder ein Angebot. Bezahlte Platzierung, kein Einfluss auf Kursdaten oder redaktionelle Einordnung.'),
           ('Anzeige · Affiliate',
            'Affiliate-Kooperation',
            'Passende Angebote mit transparentem Provisionshinweis direkt am Link. Keine versteckten Empfehlungen und keine Kauf- oder Verkaufssignale.'),
           ('Anzeige',
            'Dezente Display-Anzeige',
            'Eine ruhige Platzierung außerhalb von Kurstabellen und Lesetext. Google AdSense ist erst nach gesonderter Einrichtung, Prüfung und passender Einwilligung vorgesehen.')],
 'werben': '<div class="@@p@@-ad-page"><span class="@@p@@-tag">Kooperationen</span><h1>Werbung, die zum Thema passt.<br>Klar gekennzeichnet.</h1><p class="@@p@@-lead">Auf finanz adjust steht Werbung '
           'getrennt vom redaktionellen Inhalt und ist als Anzeige erkennbar. Sie beeinflusst weder Kursdaten noch redaktionelle Einordnung.</p><a class="@@p@@-button primary" '
           'href="@@CTA@@">Kooperation per E-Mail anfragen</a><p class="@@p@@-muted">Unverbindlich an philipp.l.paulik@gmail.com. Kein Formular, keine automatische Buchung.</p>\n'
           '<div class="@@p@@-ad-grid">@@CARDS@@</div>\n'
           '<section class="@@p@@-commercial"><span class="@@p@@-label">Platzierungskonzept, keine aktive Anzeige</span><h2>Raum für einen passenden Hinweis.</h2><p>Geplant: ein abgetrennter Spot '
           'nach dem redaktionellen Inhalt, höchstens eine direkte Kampagne pro Seite. Keine Werbe-Pop-ups, keine Video-Autostarts, kein Sticky-Werbebanner über dem Text und nie innerhalb von '
           'Kurstabellen.</p><p>Solange kein geprüftes Angebot vorliegt, bleibt dieser Platz unsichtbar.</p></section>\n'
           '<h2>Finanzthemen brauchen mehr Sorgfalt</h2><p>Eine Anzeige ist keine Anlageberatung, keine Empfehlung der FA Redaktion und kein Kauf- oder Verkaufssignal. Wir sagen keine Rendite, keine '
           'Kursentwicklung und keine Sicherheit zu. Für Angebote zu Finanzprodukten (zum Beispiel Broker, Kryptowerte oder gehebelte Produkte) prüfen wir vor jeder Buchung, ob der Anbieter die '
           'vorgeschriebenen Risikohinweise nennt. Bisher gibt es keine solche Zusammenarbeit. Mehr dazu im <a href="/risikohinweis/">Risikohinweis</a>.</p>\n'
           '<h2>Redaktion bleibt Redaktion</h2><p>Eine bezahlte Platzierung kauft Sichtbarkeit, keine positive Bewertung. Werbung wird vor dem Inhalt mit „Anzeige“ gekennzeichnet. „Gesponsert“ oder '
           '„Affiliate“ ergänzt die Einordnung. Bei Affiliate-Links steht der Provisionshinweis direkt am Link.</p>\n'
           '<h2>So läuft eine Anfrage ab</h2><ol><li>Schicken Sie Unternehmen, Ziel-URL, Thema und gewünschten Zeitraum per Mail. Ein Budgetrahmen ist optional.</li><li>Wir prüfen, ob das Angebot '
           'zur Seite passt, und besprechen Format, Kennzeichnung und Konditionen.</li><li>Erst eine gesonderte Vereinbarung macht daraus eine Buchung. Es gibt keine garantierte Veröffentlichung und '
           'keine positive redaktionelle Bewertung.</li></ol>\n'
           '<h2>Reichweite und Messung</h2><p>Wir nennen keine erfundenen Reichweiten, Klickzahlen oder CPMs. Eine spätere Auswertung kann nur tatsächlich gemessene, freigegebene Daten abdecken. '
           'AdSense-Abrechnung und eigene Kampagnen sind getrennte Auswertungen.</p>\n'
           '<p>Aktuell sind keine Werbe- oder Statistikdienste aktiviert. <a href="/werbung/">Wie wir Werbung kennzeichnen</a> · <a href="/cookies/">Datenschutzeinstellungen</a></p><p>E-Mail: <a '
           'href="mailto:philipp.l.paulik@gmail.com">philipp.l.paulik@gmail.com</a></p></div>',
 'werbung': '<h1>Werbung &amp; Affiliate: klar getrennt</h1><p>Wir bereiten Möglichkeiten vor, finanz adjust durch passende Werbung zu finanzieren. Aktuell sind Google AdSense, Affiliate-Netzwerke '
            'und Statistikdienste nicht aktiviert. Es bestehen durch diese Vorbereitung keine Partnerverträge oder Werbebuchungen.</p>\n'
            '<h2>Anzeige</h2><p>Bezahlte Platzierungen werden vor ihrem Inhalt gut sichtbar mit <strong>Anzeige</strong> gekennzeichnet und vom redaktionellen Inhalt getrennt. Sie beeinflussen keine '
            'redaktionelle Bewertung und sind kein Gütesiegel.</p>\n'
            '<h2>Gesponsert</h2><p>Bei einer gesponserten Platzierung ergänzen wir die Kennzeichnung <strong>Anzeige</strong> um <strong>Gesponsert</strong> und nennen den Auftraggeber. Eine '
            'Bewerbung ist keine Garantie für redaktionelle Berichterstattung. Ein vollständig bezahlter Artikel müsste zusätzlich direkt am Anfang und in allen Vorschauen als Anzeige erkennbar '
            'sein.</p>\n'
            '<h2>Affiliate</h2><p>Ein Affiliate-Link kann bei einem Kauf oder einer anderen vereinbarten Handlung eine Provision auslösen. Der Hinweis auf diesen Zusammenhang steht direkt beim Link. '
            'Ein bloßer Hinweis auf dieser Seite ersetzt die Kennzeichnung am Link nicht.</p>\n'
            '<h2>Finanzinhalte</h2><p>Werbung auf finanz adjust ist keine Anlageberatung, Anlageempfehlung oder Finanzanalyse und kein Kauf- oder Verkaufssignal. Kursdaten, Artikel und Kennzahlen '
            'werden nicht gegen Bezahlung verändert. Wir versprechen weder Rendite noch Kursentwicklung. Werbung für Finanzprodukte wie Broker, Kryptowerte oder gehebelte Produkte wird nur nach '
            'gesonderter Prüfung der Anbieterangaben und der vorgeschriebenen Risikohinweise geschaltet. Derzeit gibt es keine solche Kooperation. Siehe auch <a '
            'href="/risikohinweis/">Risikohinweis</a>.</p>\n'
            '<h2>Zurückhaltende Platzierung</h2><p>Geplant sind klar abgegrenzte Hinweise nach dem redaktionellen Inhalt. Keine Werbe-Pop-ups, keine automatisch startenden Werbevideos, kein '
            'Sticky-Werbebanner und keine Anzeigen innerhalb von Kurstabellen. Ungebuchte Plätze bleiben unsichtbar.</p>\n'
            '<h2>Anfragen</h2><p>Formate und unverbindliche Anfrage: <a href="/werben/">Werben &amp; Kooperationen</a>. Kontakt: philipp.l.paulik@gmail.com. Preise, Laufzeit und Leistung werden '
            'individuell vereinbart. Es werden keine Reichweite oder Klickzahlen garantiert.</p>\n'
            '<h2>Datenschutz</h2><p>Ohne Einwilligung laden wir keine Statistik- oder Werbedienste. Derzeit ist keiner dieser Dienste aktiviert. Mehr dazu: <a href="/datenschutz/">Datenschutz</a> '
            'und <a href="/cookies/">Cookies &amp; Einstellungen</a>.</p>',
 'cookies': '<h1>Cookies &amp; Einstellungen</h1><p>Statistik- und Werbedienste sind derzeit ausgeschaltet. Ohne Einwilligung werden sie nicht geladen. Sie können die Datenschutzeinstellungen '
            'jederzeit über die gleichnamige Schaltfläche im Footer öffnen, Ihre Auswahl ändern oder eine Einwilligung zurücknehmen. Ablehnen schränkt die Nutzung der Seite nicht ein.</p>\n'
            '<h2>Gespeicherte Auswahl</h2><p>Wir speichern Ihre Datenschutzauswahl im lokalen Speicher Ihres Browsers (Eintrag <strong>fa-consent-v1</strong>) und zusätzlich in einem technisch notwendigen First-Party-Cookie <strong>fa_consent_v1</strong> (Pfad /, 180 Tage, SameSite=Lax, erst nach Ihrem Klick gesetzt). Der Eintrag enthält die gewählten '
            'Kategorien, die Version des Hinweises und den Zeitpunkt der Auswahl. Er wird nicht an einen Statistik- oder Werbedienst übertragen. Nach spätestens 180 Tagen oder bei einer neuen '
            'Version fragen wir erneut. Sind lokaler Speicher und Cookies gesperrt, gilt Ihre Auswahl nur für den aktuellen Seitenaufruf.</p><p>Diese Speicherung dient ausschließlich dazu, Ihre ausdrücklich '
            'gewählte Datenschutzeinstellung zu beachten. Rechtsgrundlagen: § 25 Abs. 2 Nr. 2 TDDDG und Art. 6 Abs. 1 lit. f DSGVO. Keine nutzerübergreifende Kennung und kein Tracking-Profil. Sie '
            'können den Eintrag jederzeit in den Website-Daten Ihres Browsers löschen.</p>\n'
            '<h2>Design-Wahl</h2><p>Wenn Sie zwischen hellem und dunklem Design wechseln, merkt sich Ihr Browser die Wahl lokal unter <strong>fa-theme</strong>. Der Eintrag wird nicht übertragen und '
            'dient nur der Darstellung.</p>\n'
            '<h2>Kursdaten</h2><p>Kurse und Nachrichten werden beim Erstellen der Seite serverseitig von den unter <a href="/quellen/">Quellen und Daten</a> genannten Anbietern abgerufen, nicht in '
            'Ihrem Browser. Dabei werden keine Daten von Besuchern an diese Anbieter übertragen.</p>\n'
            '<h2>TradingView-Widget auf Aktienseiten</h2><p>Auf Aktienseiten kann bei fehlenden Kursen ein TradingView-Widget freiwillig per Klick geladen werden. Diese Entscheidung gilt nur für die '
            'aktuell geöffnete Seite, wird nicht gespeichert und gilt nicht für andere Seiten. Erst beim Klick werden IP-Adresse, Seitenadresse, Widgettyp und Symbol an TradingView übertragen. Das '
            'ist unabhängig von den Kategorien oben. Einzelheiten stehen in der <a href="/datenschutz/">Datenschutzerklärung</a>.</p>\n'
            '<h2>Statistik: derzeit aus</h2><p>Es ist noch kein Statistikdienst aktiviert. Es werden keine Analytics-Cookies und keine Analytics-Anfragen gesendet. Die vorbereitete Statistikoption '
            'ist deshalb nicht auswählbar. Vor einer Aktivierung werden Anbieter, Datenarten, Zwecke, Speicherdauer und mögliche Übermittlungen hier und in der Datenschutzerklärung konkret benannt. '
            'Optionale Statistik erfordert eine eigene freiwillige Einwilligung.</p>\n'
            '<h2>Werbung: derzeit aus</h2><p>Google AdSense und andere externe Werbedienste sind nicht aktiviert. Es werden keine Werbe-Cookies gesetzt und keine Google-Werbeanfragen gesendet. Die '
            'vorbereitete Werbeoption ist deshalb nicht auswählbar. Eine künftige AdSense-Integration erfordert eine gesonderte technische und datenschutzrechtliche Einrichtung. Dieser '
            'Einstellungsdialog ist keine Google-zertifizierte Consent-Plattform.</p>\n'
            '<h2>Externe Angebote</h2><p>Werbe- oder Affiliate-Links sind normale Links. Erst beim Anklicken verlassen Sie gegebenenfalls diese Website; dort gelten die Datenschutzregeln des '
            'jeweiligen Anbieters. Eine Kennzeichnung ist keine Zustimmung zu dessen Tracking.</p>\n'
            '<p><a href="/datenschutz/">Datenschutzerklärung</a> · <a href="/werbung/">Werbung &amp; Affiliate</a> · <a href="/impressum/">Impressum</a> · <a '
            'href="/risikohinweis/">Risikohinweis</a></p><p class="fa-muted">Stand: 19. Oktober 2026, Vorbereitung ohne aktive Statistik- oder Werbedienste.</p>',
 'panel': {'h': 'Ihre Privatsphäre.',
           'intro': 'Sie entscheiden über Statistik und Werbung. Ohne Zustimmung bleibt beides aus.',
           'q': 'Wofür dürfen Daten genutzt werden?',
           'nec': 'Seite, Design- und Datenschutzauswahl. Kein Tracking.',
           'foot': 'Ohne Auswahl bleiben Statistik und Werbung aus. Jederzeit im Footer änderbar.'},
 'footer_anchor': '<a href="/datenschutz/">Datenschutz</a>',
 'footer_links': ' <a href="/werben/">Werben</a> <a href="/werbung/">Werbung &amp; Affiliate</a> <a href="/cookies/">Cookies</a> <button type="button" class="@@p@@-consent-open" '
                 'data-@@p@@-consent-open>Datenschutzeinstellungen</button><span id="@@p@@-consent-status" class="@@p@@-sr" role="status"></span>',
 'privacy_replacements': [('<h2>Kein Tracking, keine Cookies</h2>',
                           '<h2>Datenschutzauswahl, Tracking und Cookies</h2><p>Ihre Datenschutzauswahl speichern wir ausschließlich im lokalen Speicher Ihres Browsers (Eintrag '
                           '<strong>fa-consent-v1</strong>: Kategorien, Zeitpunkt, Hinweisversion, bis zu 180 Tage). Zweck ist nur, Ihre Auswahl zu beachten; Rechtsgrundlagen sind § 25 Abs. 2 Nr. 2 '
                           'TDDDG und Art. 6 Abs. 1 lit. f DSGVO. Ebenso speichert Ihr Browser die Wahl von hellem oder dunklem Design lokal (<strong>fa-theme</strong>). Bei gesperrtem Speicher gilt '
                           'die Auswahl nur für den aktuellen Seitenaufruf. Die Datenschutzeinstellungen lassen sich jederzeit im Footer öffnen; Details unter <a href="/cookies/">Cookies &amp; '
                           'Einstellungen</a>.</p><p>Statistik und externe Werbung sind derzeit nicht aktiv. Sie würden erst nach gesonderter Einrichtung, ergänzten Datenschutzhinweisen und Ihrer '
                           'freiwilligen Einwilligung aktiviert (Art. 6 Abs. 1 lit. a DSGVO; soweit erforderlich § 25 Abs. 1 TDDDG). Ein Widerruf ist jederzeit möglich und wirkt für die Zukunft. '
                           'Derzeit sind Google Analytics, Google AdSense und Affiliate-Netzwerke nicht eingebunden; es werden weder Google-Tags noch ein Tag Manager vorgeladen. Der '
                           'Einstellungsdialog ist keine Google-zertifizierte Consent-Plattform.</p>')],
 'spot_note': 'Anzeige: bezahlte Platzierung, keine Anlageberatung und keine Empfehlung der Redaktion.',
 'spot_dirs': ['artikel'],
 'spot_wrap': '<div class="c">%s</div>',
 'css_vars': ':root{--mn-line:var(--b);--mn-soft:var(--p2);--mn-ac:var(--ac);--mn-bg:var(--p);--mn-fg:var(--fg);--mn-mut:var(--mut)}',
 'css_extra': '.fa-sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 '
              '0)}.fa-tag{display:inline-block;font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--ac);background:var(--acbg);padding:4px '
              '9px;border-radius:99px}.fa-ad-page h1,.fa-doc '
              'h1{color:var(--hd)}.fa-muted{color:var(--mut);font-size:13px}.fa-ad-page,.fa-doc{max-width:980px}.fa-doc{max-width:800px}.fa-consent-open{font:inherit;color:inherit}footer '
              '.fa-consent-open{font:inherit;font-weight:500;color:var(--fg);text-decoration:none;min-height:0;padding:0;margin-right:16px;display:inline}footer '
              '.fa-consent-open:hover{color:var(--ac);text-decoration:underline}'}
P = SITE['p']
SKIP_DIRS = {'content', 'tools', 'docs', 'tests', 'site', 'authorpage', '.github', 'node_modules', 'berichte'}

def validate(cfg):
    if cfg['advertising']['enabled']:
        raise ValueError('AdSense is locked: integrate and test a Google-certified TCF CMP first')
    if cfg['analytics']['enabled']:
        if cfg['analytics']['provider'] != 'ga4' or not re.fullmatch(r'G-[A-Z0-9]+', cfg['analytics']['measurementId']):
            raise ValueError('An approved GA4 property ID is required')
        if not cfg['analytics'].get('privacyReviewed'):
            raise ValueError('Update privacy/cookies, processor agreement, retention and settings before activation')
    if cfg['metrics']['enabled'] and not cfg['analytics']['enabled']:
        raise ValueError('No collector selected: local events alone are not an aggregate metrics system')
    if len(cfg['spots']) > 1:
        raise ValueError('Unobtrusive v1: at most one direct campaign')
    for s in cfg['spots']:
        if not re.fullmatch(r'[a-z0-9-]{1,80}', s['id']): raise ValueError('Invalid spot ID')
        if s['kind'] not in ('sponsored', 'affiliate'): raise ValueError('Unknown campaign type')
        if not all(s.get(x) for x in ('sponsor', 'title', 'description', 'url')): raise ValueError('Missing campaign disclosure')
        u = urlparse(s['url'])
        if not (u.scheme == 'https' and u.netloc and not u.username): raise ValueError('Use a verified HTTPS destination; paid local content needs its own labelling pass')
        if not s.get('approved'): raise ValueError('Campaign recipient, wording and destination must be approved')
    return cfg

def u(name): return SITE['urls'][name]

PANEL = '''<section id="@@p@@-consent" class="@@p@@-consent" role="region" aria-labelledby="@@p@@-consent-title" hidden>
<h2 id="@@p@@-consent-title">%(h)s</h2>
<p>%(intro)s</p>
<fieldset><legend>%(q)s</legend>
<label><input type="checkbox" checked disabled><span><strong>Notwendig</strong><small>%(nec)s</small></span></label>
<label><input type="checkbox" id="@@p@@-statistics"><span><strong>Statistik</strong><small>Seitenaufrufe und Interaktionen. Derzeit aus.</small></span></label>
<label><input type="checkbox" id="@@p@@-advertising"><span><strong>Werbung</strong><small>AdSense und Werbedienste. Derzeit aus.</small></span></label>
</fieldset><div class="@@p@@-consent-actions"><button type="button" data-consent="reject">Alle ablehnen</button><button type="button" data-consent="all">Alle verfügbaren akzeptieren</button><button type="button" data-consent="save">Auswahl speichern</button></div>
<p><a href="%(ds)s">Datenschutz</a> · <a href="%(ck)s">Cookies &amp; Einstellungen</a> · <a href="%(im)s">Impressum</a></p><p class="@@p@@-muted">%(foot)s</p></section>'''.replace('@@p@@', P) % dict(SITE['panel'], ds=u('datenschutz'), ck=u('cookies'), im=u('impressum'))

def mailto(kind):
    body = 'Hallo Philipp,\n\nich interessiere mich für: ' + kind + '\n\nUnternehmen / Website:\nBeworbener Artikel oder Ziel-URL:\nThema und Zielgruppe:\nGewünschter Zeitraum:\nOptionaler Budgetrahmen:\nHinweise / Kontakt:\n\nMir ist klar: Die Anfrage ist keine Buchung.\n'
    return 'mailto:philipp.l.paulik@gmail.com?subject=' + quote('Werbeanfrage ' + SITE['name'] + ': ' + kind) + '&body=' + quote(body)

def advertiser_page():
    cards = ''
    for label, title, desc in SITE['cards']:
        cards += '<section class="@@p@@-ad-card"><span class="@@p@@-label">%s</span><h2>%s</h2><p>%s</p><a class="@@p@@-button" href="%s">Format anfragen</a></section>'.replace('@@p@@', P) % (E(label), E(title), E(desc), E(mailto(title)))
    t = SITE['werben'].replace('@@p@@', P)
    return t.replace('@@CTA@@', E(mailto('Kooperation'))).replace('@@CARDS@@', cards)

def wrap_body(inner, cls=''):
    return SITE['wrap_open'].replace('@@cls@@', cls) + inner + SITE['wrap_close']

def page_path(out, name):
    return out / SITE['files'][name]

def build_page(out, shell, name, title, desc, inner, cls=''):
    t = shell
    i = t.index(SITE['body_start']); k = t.index('<footer')
    head, foot = t[:i], t[k:]
    canon = SITE['base'] + u(name)
    head = re.sub(r'<div class="crumbs">.*?</div>', '', head, flags=re.S)
    head = re.sub(r'<title>.*?</title>', '<title>' + E(title) + '</title>', head, flags=re.S)
    head = re.sub(r'<meta (?:property="og:(?:title|description|url|type)"|name="description")[^>]*>', '', head)
    head = re.sub(r'<link rel="canonical"[^>]*>', '<link rel="canonical" href="%s">' % canon, head)
    head = re.sub(r'<script type="application/ld\+json">.*?</script>', '', head, flags=re.S)
    head = head.replace('</head>', '<meta name="description" content="%s"><meta property="og:title" content="%s"><meta property="og:description" content="%s"><meta property="og:url" content="%s"><meta property="og:type" content="website"></head>' % (E(desc), E(title), E(desc), canon), 1)
    f = page_path(out, name); f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(head + wrap_body(inner, cls) + foot)

def patch_privacy(out):
    f = page_path(out, 'datenschutz')
    if not f.exists(): raise ValueError('Datenschutz page missing: ' + str(f))
    t = f.read_text()
    if SITE['key'] + '-consent-v1' in t: return
    for old, new in SITE['privacy_replacements']:
        if old not in t: raise ValueError('Privacy marker not found: ' + old[:60])
        t = t.replace(old, new, 1)
    f.write_text(t)

def main(out):
    out = pathlib.Path(out).resolve()
    cfg = validate(json.loads((ROOT / 'content/monetization.json').read_text()))
    if cfg['analytics']['enabled'] or cfg['metrics']['enabled']:
        raise ValueError('Activation is a separate reviewed release: replace off-state privacy text and banner provider disclosure first')
    asset = out / 'assets/monetization'; asset.mkdir(parents=True, exist_ok=True)
    for name in ('consent.css', 'consent.js'): shutil.copy(ROOT / 'tools/monetization' / name, asset / name)
    shell = page_path(out, 'impressum').read_text()
    # Shell is taken from the imprint page of the build, minus its own consent artefacts if re-run in place.
    shell = re.sub(r'<link rel="stylesheet" href="/assets/monetization/consent.css">', '', shell)
    shell = re.sub(r'<section id="%s-consent".*?</section>' % P, '', shell, flags=re.S)
    shell = re.sub(r'<script type="application/json" id="%s-monetization-config">.*?</script><script src="/assets/monetization/consent.js" defer></script>' % P, '', shell, flags=re.S)
    build_page(out, shell, 'werben', SITE['titles']['werben'], SITE['descs']['werben'], advertiser_page(), P + '-ad-page')
    build_page(out, shell, 'werbung', SITE['titles']['werbung'], SITE['descs']['werbung'], SITE['werbung'], P + '-doc')
    build_page(out, shell, 'cookies', SITE['titles']['cookies'], SITE['descs']['cookies'], SITE['cookies'], P + '-doc')
    patch_privacy(out)
    config = '<script type="application/json" id="%s-monetization-config">' % P + json.dumps(cfg, ensure_ascii=True).replace('<', '\\u003c') + '</script>'
    extra = PANEL + config + '<script src="/assets/monetization/consent.js" defer></script>'
    spot = ''
    for s in cfg['spots']:
        label = 'Anzeige · ' + ('Affiliate' if s['kind'] == 'affiliate' else 'Gesponsert')
        notice = '<p>Affiliate-Link: Bei einem Kauf über diesen Link können wir eine Provision erhalten.</p>' if s['kind'] == 'affiliate' else ''
        spot += '<aside class="%s-commercial" aria-label="Anzeige" data-%s-spot="%s"><span class="%s-label">%s · Auftraggeber: %s</span><h2>%s</h2><p>%s</p>%s<p class="%s-muted">%s</p><a class="%s-button" data-%s-promotion href="%s" rel="sponsored nofollow noopener">Angebot ansehen</a></aside>' % (P, P, E(s['id']), P, E(label), E(s['sponsor']), E(s['title']), E(s['description']), notice, P, E(SITE['spot_note']), P, P, E(s['url']))
    footer_anchor = SITE['footer_anchor']
    links = SITE['footer_links'].replace('@@p@@', P)
    for f in out.rglob('*.html'):
        rel = f.relative_to(out)
        if rel.parts[0] in SKIP_DIRS or any(x.startswith('.') for x in rel.parts): continue
        t = f.read_text()
        if 'id="%s-monetization-config"' % P in t and 'id="%s-consent"' % P in t: continue
        if '</body>' not in t or '<footer' not in t: continue
        t = t.replace('</head>', '<link rel="stylesheet" href="/assets/monetization/consent.css"></head>', 1)
        fi = t.find('<footer')
        if '/werben' not in t[fi:] and footer_anchor in t[fi:]:
            t = t[:fi] + t[fi:].replace(footer_anchor, footer_anchor + links, 1)
        if spot and rel.name == 'index.html' and (len(rel.parts) == 1 or rel.parts[0] in SITE['spot_dirs']):
            at = t.find('<footer'); t = t[:at] + SITE['spot_wrap'] % spot + t[at:]
        t = t.replace('</body>', extra + '</body>', 1); f.write_text(t)
    p = out / 'sitemap.xml'
    if p.exists():
        xml = p.read_text(); add = ''
        for n in ('werben', 'werbung', 'cookies'):
            loc = SITE['base'] + u(n)
            if '<loc>' + loc + '</loc>' not in xml: add += '<url><loc>%s</loc></url>' % loc
        if add: p.write_text(xml.replace('</urlset>', add + '</urlset>'))
    print('Monetization: inert configuration, consent UI and advertiser pages generated')

if __name__ == '__main__': main(sys.argv[1])
