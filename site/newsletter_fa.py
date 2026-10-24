# Wochenbriefing-Seiten (Newsletter) fuer finanz adjust.
# Anmeldung laeuft ueber das Backend daily-hob-newsletter.vercel.app (Double-Opt-In, Resend).
import os, re

API = 'https://daily-hob-newsletter.vercel.app/lw/api/fasub'

CONSENT = ('Ja, ich m\u00f6chte den kostenlosen Wochenr\u00fcckblick von finanz adjust erhalten '
 '(sonntags per E-Mail, jederzeit abbestellbar). Ich kann meine Einwilligung jederzeit mit Wirkung '
 'f\u00fcr die Zukunft widerrufen, z. B. \u00fcber den Abmeldelink in jeder E-Mail oder per E-Mail an '
 '<a href="mailto:philipp.l.paulik@gmail.com">philipp.l.paulik@gmail.com</a>. '
 'Der Versand erfolgt \u00fcber den Dienstleister Resend (PLUS FIVE FIVE, Inc., USA); eine \u00dcbermittlung '
 'in die USA kann dabei stattfinden; Details in der <a href="/datenschutz/#wochenbriefing">Datenschutzerkl\u00e4rung</a>.')

CSS = ('<style>.fanl{max-width:620px}.fanl label.el{display:block;font-weight:600;margin:18px 0 6px}'
 '.fanl input[type=email]{box-sizing:border-box;width:100%;min-height:46px;padding:10px 12px;border:1px solid #b9c2d0;border-radius:10px;font:inherit;background:var(--bg,#fff);color:inherit}'
 '.fanl .cons{display:flex;gap:10px;margin:16px 0;font-size:14px;line-height:1.55}.fanl .cons input{margin-top:4px;flex:none}'
 '.fanl .hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}'
 '.fanl .msg{margin-top:14px;font-size:15px}.fanl .msg.ok{color:#157f3d}.fanl .msg.err{color:#b3261e}'
 '.fanl .btn{cursor:pointer;border:0;font:inherit}</style>')

FORM = '''<div class="pg fanl"><h1>Wochenbriefing von finanz adjust</h1>
<p>Jeden Sonntagmorgen der Wochenr\u00fcckblick: die wichtigsten Marktbewegungen, Nachrichten und Artikel der Woche von finanz adjust, kompakt in einer E-Mail. Kostenlos, jederzeit abbestellbar.</p>
<form id="fanl-f" novalidate>
<label class="el" for="fanl-e">E-Mail-Adresse</label>
<input type="email" id="fanl-e" name="email" autocomplete="email" required>
<label class="cons"><input type="checkbox" id="fanl-c" required><span>''' + CONSENT + '''</span></label>
<div class="hp" aria-hidden="true"><label>Website <input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>
<button class="btn" type="submit">Kostenlos anmelden</button>
<p class="msg" id="fanl-m" role="status"></p>
<p style="font-size:13px;color:#667">Nach der Anmeldung erh\u00e4ltst du eine E-Mail mit einem Best\u00e4tigungslink (Double-Opt-In). Erst nach dem Klick ist die Anmeldung aktiv.</p>
</form></div>
<script>(function(){var f=document.getElementById('fanl-f'),m=document.getElementById('fanl-m');
f.addEventListener('submit',function(ev){ev.preventDefault();
var e=document.getElementById('fanl-e').value.trim(),c=document.getElementById('fanl-c').checked;
if(!e||!c){m.className='msg err';m.textContent='Bitte E-Mail-Adresse eingeben und die Einwilligung best\u00e4tigen.';return}
m.className='msg';m.textContent='Wird gesendet\u2026';
fetch('__FA_API__',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:e,consent:c,website:f.website?f.website.value:''})})
.then(function(r){return r.json()}).then(function(j){if(j&&j.ok){m.className='msg ok';m.textContent='Fast geschafft: Bitte best\u00e4tige deine Anmeldung \u00fcber den Link in der E-Mail, die wir dir gerade gesendet haben.';f.reset()}
else{m.className='msg err';m.textContent='Das hat leider nicht geklappt. Bitte pr\u00fcfe die E-Mail-Adresse und versuche es erneut.'}})
.catch(function(){m.className='msg err';m.textContent='Netzwerkfehler. Bitte versuche es sp\u00e4ter erneut.'})})})()</script>'''

CONFIRMED = '''<div class="pg"><h1>Anmeldung best\u00e4tigt</h1>
<p id="fanl-ok">Danke! Deine Anmeldung zum Wochenbriefing von finanz adjust ist best\u00e4tigt. Der n\u00e4chste Wochenr\u00fcckblick kommt am Sonntag in dein Postfach.</p>
<p id="fanl-err" style="display:none">Der Best\u00e4tigungslink ist leider ung\u00fcltig oder abgelaufen. Du kannst dich jederzeit erneut <a href="/newsletter/">anmelden</a>.</p>
<p><a class="btn" href="/">Zur Startseite</a></p></div>
<script>if(/[?&]e=1/.test(location.search)){document.getElementById('fanl-ok').style.display='none';document.getElementById('fanl-err').style.display='block'}</script>'''

FORM = FORM.replace('__FA_API__', API)

ABMELDEN = '''<div class="pg"><h1>Wochenbriefing abmelden</h1>
<p>Jede Ausgabe des Wochenbriefings enth\u00e4lt am Ende einen Abmeldelink. Ein Klick darauf beendet den Versand sofort und zuverl\u00e4ssig, ohne Anmeldung und ohne R\u00fcckfragen.</p>
<p>Alternativ kannst du deine Einwilligung jederzeit per E-Mail an <a href="mailto:philipp.l.paulik@gmail.com">philipp.l.paulik@gmail.com</a> widerrufen.</p></div>'''

DSG_SECTION = ('<h2 id="wochenbriefing">Wochenbriefing (Newsletter)</h2><p>Auf der Seite '
 '<a href="/newsletter/">Wochenbriefing</a> k\u00f6nnen Sie sich freiwillig f\u00fcr unseren kostenlosen '
 'Wochenr\u00fcckblick (sonntags per E-Mail) anmelden. Wir verarbeiten dabei Ihre E-Mail-Adresse sowie '
 'Anmelde- und Best\u00e4tigungszeitpunkt, die Version des Einwilligungstextes und die IP-Adresse als '
 'Einwilligungsnachweis (Art. 6 Abs. 1 lit. a DSGVO, \u00a7 7 Abs. 2 UWG). Die Anmeldung erfolgt im '
 'Double-Opt-In: Wir senden Ihnen eine einmalige Best\u00e4tigungsmail; erst nach Ihrem Klick auf den Link '
 'darin ist die Anmeldung aktiv. Die E-Mails (Best\u00e4tigung und Wochenr\u00fcckblick) versenden wir \u00fcber '
 'den Dienstleister Resend (PLUS FIVE FIVE, Inc., USA). Resend ver\u00f6ffentlicht einen '
 'Auftragsverarbeitungsvertrag (Data Processing Addendum), der nach Angaben des Anbieters automatisch mit '
 'der Nutzung des Dienstes gilt und EU-Standardvertragsklauseln enth\u00e4lt; eine \u00dcbermittlung in die USA '
 'kann dabei stattfinden. In unseren E-Mails werden keine Tracking-Pixel und keine Cookies gesetzt. Sie '
 'k\u00f6nnen Ihre Einwilligung jederzeit mit Wirkung f\u00fcr die Zukunft widerrufen, z. B. \u00fcber den '
 'Abmeldelink in jeder E-Mail oder per E-Mail an philipp.l.paulik@gmail.com.</p>')

def _noindex(path):
    p = path + ('index.html' if path.endswith('/') else '')
    s = open(p, encoding='utf-8').read()
    s = s.replace('<meta name="robots" content="index,follow,max-image-preview:large">',
                  '<meta name="robots" content="noindex,follow">')
    open(p, 'w', encoding='utf-8').write(s)

def build(page, out_dir):
    urls = []
    urls.append(page('/newsletter/', 'Wochenbriefing | finanz adjust',
        'Der Wochenr\u00fcckblick von finanz adjust: jeden Sonntag die wichtigsten Marktbewegungen und Artikel der Woche per E-Mail. Kostenlos, jederzeit abbestellbar.',
        CSS + FORM, crumbs=[('/newsletter/', 'Wochenbriefing')]))
    urls.append(page('/newsletter-bestaetigt/', 'Anmeldung best\u00e4tigt | finanz adjust',
        'Best\u00e4tigung der Anmeldung zum Wochenbriefing von finanz adjust.', CONFIRMED))
    urls.append(page('/abmelden/', 'Wochenbriefing abmelden | finanz adjust',
        'So melden Sie sich vom Wochenbriefing von finanz adjust ab.', ABMELDEN))
    for u in ('/newsletter-bestaetigt/', '/abmelden/'):
        _noindex(out_dir + u)
    return urls
