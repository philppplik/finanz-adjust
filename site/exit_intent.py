"""Exit-hint dialog promoting the free daily PDF report (Tagesbericht).

No tracking, no cookies, no data collection: the only storage is a
sessionStorage flag so the dialog appears at most once per browser session
(disclosed in the Datenschutz text). Desktop trigger: mouse leaves the window
toward the top. Mobile has no real exit intent, so the honest fallback is a
fast scroll-up after reading deep into the page (address-bar gesture).
Never fires in the first seconds, never while the mobile menu or another
modal is open, and closes via X, Escape or backdrop tap.
"""

ARM_MS = 8000
STORAGE_KEY = "fa-exit-report"

SNIPPET = '''<style>
.fa-exit{position:fixed;inset:0;z-index:60;display:flex;align-items:flex-end;justify-content:center;padding:16px;background:rgba(10,16,26,.5)}
.fa-exit[hidden]{display:none}
.fa-exit .dlg{background:var(--p);color:var(--fg);border:1px solid var(--b);border-radius:16px;box-shadow:var(--sh-lg);max-width:430px;width:100%;padding:22px 22px 16px;position:relative}
@media(min-width:640px){.fa-exit{align-items:center}}
.fa-exit h2{margin:0 36px 8px 0;font-size:19px;color:var(--hd);letter-spacing:-.01em}
.fa-exit .txt{margin:0 0 14px;font-size:13.5px;color:var(--mut);line-height:1.55}
.fa-exit .row{display:flex;flex-direction:column;gap:9px}
@media(min-width:420px){.fa-exit .row{flex-direction:row;align-items:center}.fa-exit a.arc{padding:6px 4px}}
.fa-exit a.go{background:linear-gradient(180deg,#2f83e8,#1c66cb);color:#fff;padding:10px 16px;border-radius:9px;font-weight:700;text-align:center;box-shadow:0 1px 2px rgba(20,80,170,.35);transition:filter .15s ease}
.fa-exit a.go:hover{color:#fff;filter:brightness(1.07)}
.fa-exit a.arc{color:var(--ac);font-weight:600;text-align:center;padding:6px 0}
.fa-exit a.arc:hover{text-decoration:underline;text-underline-offset:3px}
.fa-exit .x{position:absolute;top:10px;right:10px;width:34px;height:34px;border:1px solid var(--b);background:none;color:var(--mut);border-radius:9px;font-size:16px;line-height:1;cursor:pointer;display:grid;place-items:center}
.fa-exit .x:hover{background:var(--p2);color:var(--hd)}
.fa-exit .no{display:block;margin:12px auto 0;background:none;border:0;color:var(--mut);font-size:12.5px;cursor:pointer;padding:4px 8px}
.fa-exit .no:hover{color:var(--hd);text-decoration:underline;text-underline-offset:3px}
.fa-exit .fine{margin:12px 0 0;font-size:11.5px;color:var(--mut)}
.fa-exit :focus-visible{outline:3px solid var(--ring);outline-offset:2px}
@media(prefers-reduced-motion:no-preference){.fa-exit .dlg{animation:faex .22s ease}@keyframes faex{from{transform:translateY(10px);opacity:0}}}
</style>
<div class="fa-exit" id="fa-exit" hidden>
<div class="dlg" role="dialog" aria-modal="true" aria-labelledby="fa-exit-t">
<button type="button" class="x" data-x aria-label="Hinweis schlie&szlig;en">&times;</button>
<h2 id="fa-exit-t">Geh noch nicht!</h2>
<p class="txt">Sichere dir noch schnell gratis den Tagesbericht: Indizes, Gewinner und Verlierer, Devisen und die wichtigsten Schlagzeilen kompakt als PDF &ndash; kostenlos, ohne Anmeldung, ohne E-Mail.</p>
<div class="row"><a class="go" href="/berichte/aktuell.pdf">Gratis-Tagesbericht sichern (PDF)</a><a class="arc" href="/berichte/">Alle Berichte ansehen</a></div>
<button type="button" class="no" data-x>Nein, danke</button>
<p class="fine">Kein Newsletter, keine Datenabfrage &ndash; nur der PDF-Download. Dieser Hinweis erscheint h&ouml;chstens einmal pro Browsersitzung.</p>
</div>
</div>
<script>(function(){
var el=document.getElementById("fa-exit");if(!el)return;
var ARM=__ARM__,armed=false,shown=false,lastFocus=null;
try{if(sessionStorage.getItem("__KEY__"))shown=true}catch(e){}
setTimeout(function(){armed=true},ARM);
function blocked(){return shown||!armed||!el.hidden||(document.getElementById("mt")||{}).checked||document.querySelector("body>[aria-modal=true]")}
function show(){if(blocked())return;shown=true;try{sessionStorage.setItem("__KEY__","1")}catch(e){}
lastFocus=document.activeElement;el.hidden=false;var b=el.querySelector("a.go");if(b)b.focus()}
function hide(){if(el.hidden)return;el.hidden=true;if(lastFocus&&lastFocus.focus)lastFocus.focus()}
document.addEventListener("mouseout",function(e){if(!e.relatedTarget&&e.clientY<=8)show()});
if(window.matchMedia&&matchMedia("(pointer:coarse)").matches){
var deep=0,lastY=window.scrollY,lastT=0;
addEventListener("scroll",function(){var y=window.scrollY,t=Date.now();
if(y>deep)deep=y;
if(deep>=500&&lastY-y>140&&t-lastT<300&&y<deep-300)show();
lastY=y;lastT=t},{passive:true})}
el.addEventListener("click",function(e){if(e.target===el||e.target.hasAttribute("data-x"))hide()});
document.addEventListener("keydown",function(e){if(el.hidden)return;
if(e.key==="Escape"){hide();return}
if(e.key!=="Tab")return;
var f=el.querySelectorAll("a[href],button"),first=f[0],last=f[f.length-1];
if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus()}
else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus()}});
})()</script>'''.replace('__ARM__', str(ARM_MS)).replace('__KEY__', STORAGE_KEY)


def attach(html, path):
    """Inject the dialog before </body> on every page except the reports page itself."""
    if path == '/berichte/':
        return html
    return html.replace('</body></html>', SNIPPET + '</body></html>')
