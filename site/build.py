import json,os,re,shutil,subprocess,glob
import newsletter_fa
from common import *
from news_media import permitted_news, source_badge, news_cards
from news_policy import destination
from exit_intent import attach as exit_attach
from report_visuals import stock_href
def mid(q): return 'm-'+re.sub(r'[^a-z0-9]','',q['sym'].lower())
CRYPTO_HREF={c['sym']:'/krypto/%s/'%c['slug'] for c in json.load(open('crypto.json'))}
def crypto_href(q): return CRYPTO_HREF.get(q['sym'],'')
def mhref(q):
    h=stock_href(q) or crypto_href(q)
    if h: return h
    return '/maerkte/#devisen' if q['grp']=='FX' else '/maerkte/#%s'%mid(q)
OUT='out'; shutil.rmtree(OUT,ignore_errors=True); os.makedirs(OUT+'/berichte')
if os.path.isdir('../images'): shutil.copytree('../images',OUT+'/images',dirs_exist_ok=True)
from zoneinfo import ZoneInfo
BASE='https://finanz-adjust.de'; NOW=datetime.datetime.now(ZoneInfo('Europe/Berlin'))
Q=json.load(open('../data/quotes.json')); N=permitted_news(json.load(open('../data/fin_archive.json')))
import sys
sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parent.parent/'tools'))
from licensed_news import collect, merge_current
from news_media import diverse as _feed_diverse
from share import share_block, SHARE_CSS
licensed_archive=collect('..','fa',N)
N=merge_current(N,licensed_archive)
fx={}
b=get('https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml')
if b:
    for m in re.finditer(rb"currency='(\w+)' rate='([\d.]+)'",b): fx[m.group(1).decode()]=float(m.group(2))
LOGO='<svg width="98" height="129" viewBox="0 0 98 129" fill="none" xmlns="http://www.w3.org/2000/svg">\n<path d="M20.7486 99.5475L0 110L0.428488 49.0228C0.467307 43.4986 3.53937 38.4429 8.42457 35.8635L29 25V86.1513C29 91.8166 25.8081 96.9986 20.7486 99.5475Z" fill="#00A7F8"/>\n<path d="M89.5674 92.4971L68 103L68.4423 42.162C68.4829 36.5645 71.637 31.4553 76.6229 28.9106L98 18V79.0112C98 84.7494 94.7264 89.9848 89.5674 92.4971Z" fill="#1A6ACD"/>\n<path d="M54.7189 118.62L34 129L34.3966 36.9829L34.4526 23.991C34.4766 18.4399 37.5643 13.3558 42.4791 10.7751L63 0V105.209C63 110.886 59.7948 116.077 54.7189 118.62Z" fill="#0086F5"/>\n</svg>\n'
CSS='''
:root{--bg:#eff1f5;--p:#fff;--p2:#f3f5f8;--b:#e2e5ec;--fg:#333a45;--mut:#67707d;--up:#14743c;--dn:#c62828;--ac:#1c66cb;--ac2:#00A7F8;--ac3:#1A6ACD;--hd:#0f1722;--upbg:rgba(20,116,60,.1);--dnbg:rgba(198,40,40,.09);--acbg:rgba(28,102,203,.07);--ring:rgba(28,102,203,.35);--sh:0 1px 2px rgba(15,23,34,.05),0 10px 28px -14px rgba(15,23,34,.14);--sh-lg:0 2px 6px rgba(15,23,34,.07),0 20px 44px -16px rgba(15,23,34,.22);--pA:rgba(255,255,255,.85);--background:var(--bg);--foreground:var(--fg);--card:var(--p);--card-foreground:var(--hd);--muted:var(--p2);--muted-foreground:var(--mut);--primary:var(--ac);--primary-foreground:#fff;--border:var(--b);--input:var(--b);--accent:var(--p2);--accent-foreground:var(--hd);--radius:12px;color-scheme:light}
html[data-theme=dark]{--bg:#0f141f;--p:#181e2b;--p2:#202738;--b:#2a3243;--fg:#d4d9e2;--mut:#8b93a4;--up:#2fbb92;--dn:#f27070;--ac:#66b3ff;--hd:#f2f5fa;--upbg:rgba(47,187,146,.16);--dnbg:rgba(242,112,112,.16);--acbg:rgba(102,179,255,.1);--ring:rgba(102,179,255,.4);--sh:0 1px 2px rgba(0,0,0,.45),0 12px 32px -16px rgba(0,0,0,.6);--sh-lg:0 2px 8px rgba(0,0,0,.5),0 24px 48px -16px rgba(0,0,0,.65);--pA:rgba(15,20,31,.82);color-scheme:dark}
*{box-sizing:border-box}html{overflow-x:clip}body{margin:0;overflow-x:clip;font:14px/1.55 "Work Sans",-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--fg);-webkit-font-smoothing:antialiased}::selection{background:rgba(28,102,203,.2)}html[data-theme=dark] ::selection{background:rgba(102,179,255,.28)}a{color:inherit;text-decoration:none}a:hover{color:var(--hd)}.btn:hover{color:#fff}
@media(prefers-reduced-motion:no-preference){body,header,footer,.tk,.pn,.ic,.kpi,.gc{transition:background-color .18s ease,border-color .18s ease}}
header{background:var(--pA);-webkit-backdrop-filter:blur(14px) saturate(1.5);backdrop-filter:blur(14px) saturate(1.5);border-bottom:1px solid var(--b);position:sticky;top:0;z-index:9}.nav{display:flex;align-items:center;gap:22px;height:56px;padding:0 20px;max-width:1500px;margin:0 auto;position:relative}.logo{font-weight:800;font-size:18px;color:var(--hd);display:flex;align-items:center;gap:9px}.logo img{height:26px;width:auto;display:block}.logo .wm{white-space:nowrap;letter-spacing:-.01em}.logo b{color:var(--ac)}.links{display:flex;align-items:center;gap:22px;flex:1}.links a.l{color:var(--mut);font-weight:500;padding:6px 0;position:relative;transition:color .15s ease}.links a.l::after{content:"";position:absolute;left:0;right:0;bottom:0;height:2px;border-radius:2px;background:var(--ac);transform:scaleX(0);transform-origin:left;transition:transform .18s ease}.links a.l:hover::after,.links a.act::after{transform:scaleX(1)}.links a.l:hover,.links a.act{color:var(--hd)}.sp{flex:1}.btn{background:linear-gradient(180deg,#2f83e8,#1c66cb);color:#fff;padding:8px 15px;border-radius:9px;font-weight:600;box-shadow:0 1px 2px rgba(20,80,170,.35),inset 0 1px 0 rgba(255,255,255,.18);transition:transform .15s ease,box-shadow .15s ease,filter .15s ease}.btn:hover{filter:brightness(1.07);box-shadow:0 4px 14px -4px rgba(20,80,170,.5),inset 0 1px 0 rgba(255,255,255,.18)}.btn:active{transform:translateY(1px)}
.mt{position:absolute;opacity:0;pointer-events:none}.bg{display:none;flex-direction:column;justify-content:center;gap:5px;width:40px;height:40px;cursor:pointer;padding:8px;margin-left:auto}.bg span{display:block;height:2px;background:var(--fg);border-radius:2px;transition:.2s}
.tk{background:var(--p);border-bottom:1px solid var(--b);overflow:hidden;white-space:nowrap;-webkit-mask-image:linear-gradient(90deg,transparent,#000 40px,#000 calc(100% - 40px),transparent);mask-image:linear-gradient(90deg,transparent,#000 40px,#000 calc(100% - 40px),transparent)}.tk div{display:inline-block;padding:7px 0;font-size:12.5px;animation:s 90s linear infinite}.tk:hover div{animation-play-state:paused}@media(max-width:900px) and (prefers-reduced-motion:reduce){.links{transition:none}}
@media(prefers-reduced-motion:reduce){.tk div{animation:none}.tk{white-space:normal}}.tk span{margin:0 18px}.tk b{font-weight:600}@keyframes s{to{transform:translateX(-50%)}}
.up{color:var(--up)}.dn{color:var(--dn)}.mut{color:var(--mut)}
.w{max-width:1500px;margin:0 auto;padding:20px}.g{display:grid;grid-template-columns:2.2fr 1fr;gap:16px}.g>*,.idx>*{min-width:0}
.pn{box-shadow:var(--sh);background:var(--p);border:1px solid var(--b);border-radius:14px;padding:18px;margin-bottom:16px}.pn h2{margin:0 0 12px;font-size:15.5px;font-weight:700;letter-spacing:-.01em;color:var(--hd);display:flex;justify-content:space-between;align-items:baseline}.pn h2 a{font-size:12.5px;color:var(--ac);font-weight:600}.pn h2 a:hover{text-decoration:underline;text-underline-offset:3px}
.idx{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-bottom:16px}.ic{box-shadow:var(--sh);background:var(--p);border:1px solid var(--b);border-radius:14px;padding:14px 16px}.tt-txt{display:none}.tt{background:none;border:1px solid var(--b);color:var(--fg);border-radius:9px;width:36px;height:36px;font-size:17px;line-height:1;cursor:pointer;display:grid;place-items:center;flex-shrink:0;transition:background .15s ease,border-color .15s ease}.tt:hover{background:var(--p2);border-color:var(--mut)}.tt:focus-visible,.btn:focus-visible,a:focus-visible,summary:focus-visible{outline:3px solid var(--ring);outline-offset:2px;border-radius:6px}
.ic .n{color:var(--mut);font-size:12px;font-weight:600}.ic .p{font-size:22px;font-weight:800;letter-spacing:-.01em;color:var(--hd);margin:3px 0 5px;font-variant-numeric:tabular-nums}.ic .c,.kpi .c{display:inline-block;padding:2px 9px;border-radius:999px;font-size:12.5px;font-weight:600;font-variant-numeric:tabular-nums}.c.up{background:var(--upbg)}.c.dn{background:var(--dnbg)}
.tw{overflow-x:auto}table{width:100%;border-collapse:collapse}th{text-align:right;color:var(--mut);font-weight:600;font-size:11.5px;letter-spacing:.01em;padding:8px 10px;border-bottom:1px solid var(--b)}th:first-child,td:first-child{text-align:left}td{text-align:right;padding:10px;border-bottom:1px solid var(--p2);font-variant-numeric:tabular-nums;white-space:nowrap;transition:background-color .12s ease}tr:last-child td{border-bottom:0}tr:hover td{background:var(--p2)}td b{color:var(--hd);font-weight:700}.tw tr[data-href]{cursor:pointer}.tw a.rl{color:inherit;text-decoration:none}.tw a.rl:hover b{text-decoration:underline;text-underline-offset:2px}.tk a.tkl{color:inherit;text-decoration:none}.tk a.tkl:hover b{text-decoration:underline;text-underline-offset:2px}
.nw{list-style:none;margin:0;padding:0}.nw li{padding:11px 0;border-bottom:1px solid var(--p2)}.nw li:last-child{border-bottom:0}.nw a{color:var(--hd);font-weight:500;display:block;line-height:1.4;transition:color .12s ease}.nw a:hover{color:var(--ac)}.nw .m{font-size:12px;color:var(--mut);margin-top:3px}
.fxr{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--p2)}.idx a.ic,.kpis a.kpi{display:block;color:inherit;text-decoration:none}.idx a.ic:hover .n,.kpis a.kpi:hover .n{text-decoration:underline;text-underline-offset:2px}a.fxr{color:inherit;text-decoration:none}a.fxr:hover span{text-decoration:underline;text-underline-offset:2px}
.hero{display:grid;grid-template-columns:1.4fr 1fr;gap:16px;padding:14px 0 24px;align-items:stretch}.hero .hl h1{margin:0 0 8px;font-size:clamp(26px,3.4vw,38px);font-weight:800;color:var(--hd);letter-spacing:-.03em;line-height:1.15}.hero .hl p{margin:0 0 16px;color:var(--mut);font-size:14.5px}.hero .kpis{display:flex;gap:12px;flex-wrap:wrap}.hero .kpi{box-shadow:var(--sh);background:var(--p);border:1px solid var(--b);border-radius:14px;padding:14px 18px;min-width:160px;flex:1}.hero .kpi .n{color:var(--mut);font-size:12px;font-weight:600}.hero .kpi .p{font-size:26px;font-weight:800;letter-spacing:-.02em;color:var(--hd);font-variant-numeric:tabular-nums}.hero .kpi .c{font-size:12.5px}
.kpi .spk{margin:8px -4px -2px}.kpi .spk svg{display:block;width:100%;height:auto}.hero .hl{background:radial-gradient(farthest-corner at 0% 0%,var(--acbg),transparent 72%);border-radius:14px;padding:6px 10px 6px 0}
.hero .pn{margin-bottom:0}.hero .nw li:first-child a{font-size:15px;font-weight:700;color:var(--hd)}
.badge{display:inline-block;background:var(--p2);border:1px solid var(--b);color:var(--mut);font-size:11px;font-weight:600;padding:3px 10px;border-radius:999px;margin-left:8px;vertical-align:middle;letter-spacing:.01em}
.pg{max-width:800px;margin:0 auto;padding:30px 20px}.pg h1{color:var(--hd);letter-spacing:-.02em}.pg h2{color:var(--hd);margin-top:26px;letter-spacing:-.01em}.pg p{line-height:1.7}
.crumbs{font-size:12px;color:var(--mut);max-width:1500px;margin:14px auto 0;padding:0 20px}.crumbs a{color:var(--mut);text-decoration:underline;text-underline-offset:2px}
.artimg{margin:0 0 18px}.artimg img{width:100%;height:auto;border-radius:14px;display:block;box-shadow:var(--sh)}
.art{max-width:820px;margin:0 auto;padding:24px 20px}.art h1{color:var(--hd);font-size:clamp(26px,3.2vw,34px);font-weight:800;line-height:1.22;margin:0 0 10px;letter-spacing:-.025em}.art .by{color:var(--mut);font-size:13px;margin-bottom:18px}.art .body{font-size:16.5px;line-height:1.78}.art .body h2{color:var(--hd);font-size:22px;font-weight:800;letter-spacing:-.02em;margin:32px 0 10px}.art .body h3{color:var(--hd);font-size:17px;font-weight:700;margin:24px 0 8px}.art .body p{margin:0 0 14px}.art .body ul,.art .body ol{margin:0 0 14px;padding-left:22px}.art .body li{margin-bottom:6px}.art .body a{color:var(--ac);text-decoration:underline;text-underline-offset:3px}
.note{background:var(--acbg);border:1px solid var(--b);border-radius:10px;padding:13px 16px;font-size:13px;color:var(--mut);margin:18px 0}.note b{color:var(--fg)}
.faq{border-top:1px solid var(--b);margin-top:22px;padding-top:14px}.faq h2{color:var(--hd);font-size:19px;margin:0 0 10px;letter-spacing:-.01em}.faq details{border:1px solid var(--b);border-radius:10px;padding:11px 15px;margin-bottom:8px;background:var(--p);transition:border-color .15s ease}.faq details:hover{border-color:var(--mut)}.faq summary{cursor:pointer;font-weight:600;color:var(--hd)}.faq p{color:var(--fg);margin:8px 0 0;line-height:1.6}
.srcl{margin-top:18px;font-size:13px;color:var(--mut)}.srcl a{color:var(--ac);text-decoration:underline;text-underline-offset:3px}
.gl{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}.gc{box-shadow:var(--sh);background:var(--p);border:1px solid var(--b);border-radius:14px;padding:16px;display:block;transition:transform .16s ease,box-shadow .16s ease,border-color .16s ease}.gc:hover{border-color:var(--ac);transform:translateY(-2px);box-shadow:var(--sh-lg)}.gc b{color:var(--hd);font-weight:700;display:block;margin-bottom:4px}.gc span{color:var(--mut);font-size:13px}
footer{background:var(--p);border-top:1px solid var(--b);margin-top:36px;padding:28px 20px;color:var(--mut);font-size:13px}footer .c{max-width:1500px;margin:0 auto}footer a{margin-right:16px;color:var(--fg);font-weight:500;transition:color .15s ease}footer a:hover{color:var(--ac)}.warn{font-size:12px;color:var(--mut);margin-top:10px;max-width:900px}.warn a{color:var(--mut);text-decoration:underline}
.cta{background:linear-gradient(135deg,#1A6ACD,#0086F5 60%,#00A7F8);border:0;box-shadow:var(--sh-lg)}.cta h2,.cta a{color:#fff}.cta a.b{color:#1A6ACD}.cta p{margin:0 0 12px;color:#dbe9ff}.cta a.b{background:#fff;color:#1A6ACD;padding:9px 15px;border-radius:9px;font-weight:700;display:inline-block;box-shadow:0 1px 2px rgba(0,0,0,.15);transition:transform .15s ease}.cta a.b:hover{transform:translateY(-1px)}
@media(max-width:900px){.g{grid-template-columns:1fr}.idx{grid-template-columns:repeat(2,minmax(0,1fr))}.ic svg{width:100%}.idx{gap:8px}.ic .p{font-size:18px}.hero{grid-template-columns:1fr}.gl{grid-template-columns:1fr}.links{display:flex;position:fixed;top:0;right:0;height:100vh;height:100dvh;width:min(320px,86vw);background:var(--p);border-left:1px solid var(--b);box-shadow:var(--sh-lg);flex-direction:column;align-items:stretch;gap:0;padding:72px 22px 24px;overflow-y:auto;overscroll-behavior:contain;-webkit-overflow-scrolling:touch;visibility:hidden;transform:translateX(105%);transition:transform .25s ease,visibility 0s linear .25s;z-index:8}.links a.l{font-size:16px;padding:13px 0;width:100%}.links a.btn{width:100%;text-align:center;padding:12px 15px;margin:10px 0 4px}.links a.l::after{display:none}.mt:checked~.links{transform:none;visibility:visible;transition:transform .25s ease}header:has(.mt:checked){position:fixed;top:0;left:0;right:0;-webkit-backdrop-filter:none;backdrop-filter:none;background:var(--p)}.bg{position:relative;z-index:10}.mt:focus-visible~.bg{outline:3px solid var(--ring);outline-offset:2px;border-radius:9px}.mt:checked~.bg span:nth-child(1){transform:translateY(7px) rotate(45deg)}.mt:checked~.bg span:nth-child(2){opacity:0}.mt:checked~.bg span:nth-child(3){transform:translateY(-7px) rotate(-45deg)}.ovl{display:none}.mt:checked~.ovl{display:block;position:fixed;top:0;left:0;right:0;height:100vh;height:100dvh;background:rgba(10,14,22,.45);z-index:7}.pl{display:none}@media(max-width:640px){.tw{overflow-x:visible}.tw table,.tw tbody,.tw tr{display:block;width:100%}.tw th{display:none}.tw td{display:block;border:0;padding:0;text-align:left;white-space:normal;width:100%}.tw td.hide{display:none}.tw tr{display:grid;grid-template-columns:1fr auto;gap:1px 12px;padding:10px 2px;border-bottom:1px solid var(--b)}.tw tr:last-child{border-bottom:0}.tw td.c-px{grid-column:2;grid-row:1;text-align:right;align-self:end;width:auto}.tw td.c-pct{grid-column:2;grid-row:2;text-align:right;align-self:start;width:auto}.tw td.c-chg{display:none}.tw .pl{display:inline;color:var(--mut);font-size:10.5px;font-weight:400}.tw a.rl{display:inline-block;min-height:44px;padding-top:4px}.tw td.c-sym{grid-column:1;grid-row:1/3}}.links .tt{display:flex;align-items:center;gap:12px;width:100%;height:auto;padding:13px 0;background:none;border:0;border-radius:0;font-size:16px;font-weight:500;color:var(--mut)}.links .tt:hover{background:none;color:var(--hd)}.links .tt .tt-txt{display:inline}.links .tt .tt-ic{font-size:18px}.bg{display:flex}.nav{gap:14px}.hide{display:none}.hero .hl h1{font-size:24px}.art h1{font-size:24px}}
'''
CSS+=SHARE_CSS
open(OUT+'/style.css','w').write(CSS)
shutil.copyfile('theme.css',OUT+'/theme.css')
shutil.copyfile('news.css',OUT+'/news.css')
shutil.copytree('news-assets',OUT+'/news-assets',dirs_exist_ok=True)
POLISH='''
/* polish.css - laedt nach theme.css. Optische Veredelung der Aktien-Seiten (.stock-* aus stocks.css); nur Schatten, Radius, Hover, Fokus - kein Layout-Eingriff. */
.stock-card,.stock-panel,.stock-info{border-radius:14px}
.stock-quote{border-radius:16px}
.stock-tag{border-radius:999px}
.stock-monogram{border-radius:12px}
.stock-card{transition:transform .16s ease,box-shadow .16s ease,border-color .16s ease,background-color .16s ease}
html:not([data-theme=dark]) .stock-card,html:not([data-theme=dark]) .stock-panel,html:not([data-theme=dark]) .stock-info,html:not([data-theme=dark]) .stock-quote{box-shadow:0 1px 2px rgba(15,23,34,.05),0 10px 28px -14px rgba(15,23,34,.14)}
html:not([data-theme=dark]) .stock-card:hover{transform:translateY(-2px);box-shadow:0 2px 6px rgba(15,23,34,.07),0 20px 44px -16px rgba(15,23,34,.22)}
html[data-theme=dark] .stock-card:hover{transform:translateY(-2px)}
.stock-search input{transition:border-color .15s ease,box-shadow .15s ease}
.stock-search input:focus-visible{outline:0;border-color:#1c66cb;box-shadow:0 0 0 3px rgba(28,102,203,.25)}
html[data-theme=dark] .stock-search input:focus-visible{border-color:#66b3ff;box-shadow:0 0 0 3px rgba(102,179,255,.25)}
.stock-search button,.stock-tv button{border-radius:9px;transition:filter .15s ease,transform .15s ease}
.stock-search button:hover,.stock-tv button:hover{filter:brightness(1.07)}
.stock-search button:active,.stock-tv button:active{transform:translateY(1px)}
.stock-tabs a{transition:color .15s ease}
.stock-facts>div{transition:background-color .12s ease}
'''
open(OUT+'/polish.css','w').write(POLISH)
NAV=[('/aktien/','Aktien'),('/maerkte/','Märkte'),('/broker/','Broker'),('/artikel/','Artikel'),('/nachrichten/','Nachrichten'),('/glossar/','Glossar'),('/lernpfade/','Lernpfade'),('/rechner/','Rechner'),('/berichte/','Berichte'),('/risikohinweis/','Risikohinweis')]
def num(x,d=2): return f"{x:,.{d}f}".replace(',','X').replace('.',',').replace('X','.')
def spark(h,up,w=90,hh=26):
    if len(h)<2: return ''
    lo,hi=min(h),max(h); r=(hi-lo) or 1
    pts=' '.join('%.1f,%.1f'%(i*w/(len(h)-1),hh-2-(v-lo)/r*(hh-4)) for i,v in enumerate(h))
    c='#26a69a' if up else '#ef5350'
    return '<svg width="%d" height="%d" viewBox="0 0 %d %d"><polyline fill="none" stroke="%s" stroke-width="1.6" points="%s"/></svg>'%(w,hh,w,hh,c,pts)
def cls(x): return 'up' if x>=0 else 'dn'
def sg(x): return ('+' if x>=0 else '')+num(x)
def qsrc():
    s={q.get('src','') for q in Q}
    parts=[]
    if 'Twelve Data' in s: parts.append('<a href="https://twelvedata.com" rel="noopener">Twelve Data</a>')
    if 'Yahoo Finance' in s: parts.append('Yahoo Finance (öffentliche Schnittstelle)')
    if 'CoinGecko' in s: parts.append('<a href="https://www.coingecko.com" rel="noopener">Powered by CoinGecko</a>')
    return ', '.join(parts) or 'öffentliche Schnittstellen'
def tk_item(q):
    s='<span>%s <b class="%s">%s %s%s%%</b></span>'%(esc(q['name']),cls(q['pct']),num(q['price']),'\u25b2' if q['pct']>=0 else '\u25bc',num(abs(q['pct'])))
    h=mhref(q)
    return '<a class="tkl" href="%s">%s</a>'%(h,s)
def page(path,title,desc,body,ld=None,act='',otype='website',crumbs=None,og=None):
    url=BASE+path
    stock_page=path.startswith('/aktien/')
    tk=''.join(tk_item(q) for q in Q)
    if stock_page: tk='<span>Aktienverzeichnis · Handelsplatz und Datenstand direkt auf der Aktienseite</span>'
    nav=''.join('<a class="l%s" href="%s">%s</a>'%(' act' if act==h else '',h,t) for h,t in NAV)
    ldj='<script type="application/ld+json">%s</script>'%json.dumps(ld,ensure_ascii=False) if ld else ''
    ogurl=BASE+(og or '/og/default.png')
    cb=''
    if crumbs:
        cb='<div class="crumbs">'+' › '.join('<a href="%s">%s</a>'%(h,esc(t)) for h,t in crumbs)+'</div>'
        if not ld: ld=[]
        ld.append({'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':i+1,'name':t,'item':BASE+h} for i,(h,t) in enumerate(crumbs)]})
        ldj='<script type="application/ld+json">%s</script>'%json.dumps(ld,ensure_ascii=False)
    h='''<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>%s</title><meta name="description" content="%s"><link rel="canonical" href="%s"><meta name="robots" content="index,follow,max-image-preview:large"><meta property="og:title" content="%s"><meta property="og:description" content="%s"><meta property="og:url" content="%s"><meta property="og:type" content="%s"><meta property="og:site_name" content="finanz adjust"><meta property="og:locale" content="de_DE"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="%s"><meta property="og:image" content="%s"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="theme-color" content="#eff1f5"><meta name="color-scheme" content="light dark"><script>try{var t=localStorage.getItem("fa-theme");document.documentElement.dataset.theme=t==="dark"?"dark":"light"}catch(e){document.documentElement.dataset.theme="light"}</script><link rel="alternate" type="application/rss+xml" title="finanz adjust" href="/feed.xml"><link rel="icon" href="/logo.svg" type="image/svg+xml"><link rel="stylesheet" href="/style.css">%s<link rel="stylesheet" href="/theme.css"><link rel="stylesheet" href="/news.css"><link rel="stylesheet" href="/polish.css"></head><body><header><div class="nav"><a class="logo" href="/"><img src="/logo.svg" alt="finanz adjust Logo"><span class="wm">finanz<b>adjust</b></span></a><input type="checkbox" id="mt" class="mt" aria-label="Menü umschalten"><label for="mt" class="bg" title="Menü"><span></span><span></span><span></span></label><label for="mt" class="ovl" aria-hidden="true"></label><nav class="links">%s<span class="sp"></span><a class="btn" href="/berichte/">Tagesbericht (PDF)</a><button type="button" class="tt" id="tt" aria-label="Zwischen hellem und dunklem Design wechseln" title="Design wechseln"><span class="tt-ic">☾</span><span class="tt-txt">Design wechseln</span></button></nav></div></header><div class="tk"><div>%s%s</div></div>%s%s<footer><div class="c"><div class="ft"><div class="fb"><a class="fl" href="/" aria-label="finanz adjust Startseite"><img src="/logo.svg" alt="" width="28" height="37"><span class="wm">finanz<b>adjust</b></span></a><p>Märkte, Kurse und Finanznachrichten. Erstellt mit KI-Unterstützung, ohne Anlageberatung.</p></div><nav class="fc" aria-label="Redaktion"><h3>Redaktion</h3><a href="/redaktion/">Redaktion</a><a href="/transparenz/">KI-Transparenz</a><a href="/ueber-uns/">Über uns</a><a href="/korrekturen/">Korrekturen</a><a href="/newsletter/">Wochenbriefing</a></nav><nav class="fc" aria-label="Rechtliches"><h3>Rechtliches</h3><a href="/impressum/">Impressum</a><a href="/datenschutz/">Datenschutz</a><a href="/risikohinweis/">Risikohinweis</a></nav><nav class="fc" aria-label="Daten und Kontakt"><h3>Daten &amp; Werkzeuge</h3><a href="/rechner/">Finanzrechner</a><a href="/lernpfade/">Lernpfade</a><a href="/vergleiche/">Vergleiche</a><a href="/broker/">Broker</a><a href="/quellen/">Quellen</a><a href="/kontakt/">Kontakt</a></nav></div><p class="warn">Alle Inhalte dienen ausschließlich der Information und sind keine Anlageberatung, Anlageempfehlung oder Kauf- bzw. Verkaufsempfehlung. Kursdaten: %s, ggf. verzögert und ohne Gewähr. Wechselkurse: Europäische Zentralbank (Referenzkurse). Nachrichten-Schlagzeilen: GDELT Project / Yahoo Finance (nur Überschriften mit Link zur Quelle). Der Handel mit Finanzinstrumenten ist mit Verlustrisiken bis zum Totalverlust verbunden.</p><p class="warn">© %d finanz adjust · Redaktion: FA Redaktion · Seite erstellt %s</p></div></footer><script>(function(){var b=document.getElementById("tt"),d=document.documentElement,ic=b.querySelector(".tt-ic");function u(){var k=d.dataset.theme==="dark";ic.textContent=k?"☀":"☾";b.setAttribute("aria-pressed",k);var m=document.querySelector("meta[name=theme-color]");if(m)m.content=k?"#0f141f":"#eff1f5"}u();b.onclick=function(){var n=d.dataset.theme==="dark"?"light":"dark";d.dataset.theme=n;try{localStorage.setItem("fa-theme",n)}catch(e){}u()}})();(function(){var mt=document.getElementById("mt");if(!mt)return;function s(){var lk=mt.checked&&window.innerWidth<=900;document.body.style.overflow=lk?"hidden":"";document.documentElement.style.overflow=lk?"hidden":"";mt.setAttribute("aria-expanded",mt.checked?"true":"false")}mt.addEventListener("change",s);document.addEventListener("keydown",function(e){if(e.key==="Escape"&&mt.checked){mt.checked=false;s();mt.focus()}});window.addEventListener("resize",function(){if(window.innerWidth>900)mt.checked=false;s()});s()})()</script></body></html>'''%(esc(title),esc(desc),url,esc(title),esc(desc),url,otype,ogurl,ogurl,ldj,nav,tk,tk,cb,body,qsrc(),NOW.year,NOW.strftime('%d.%m.%Y %H:%M'))
    if stock_page:
        h=h.replace('Kursdaten: %s, ggf. verzögert und ohne Gewähr.'%qsrc(), 'Kursdaten nur bei freigeschalteter Datenquelle; Quelle und Zeit direkt auf der Aktienseite.').replace('<div class="tk"><div>%s%s</div></div>'%(tk,tk), '')
    h=exit_attach(h,path)
    p=OUT+path+('index.html' if path.endswith('/') else ''); os.makedirs(os.path.dirname(p),exist_ok=True); open(p,'w').write(h); return url
def trow(q,selfpage=False):
    cur={'EUR':' \u20ac','USD':' $'}.get(q.get('cur') or '','')  # fehlende Waehrung (z. B. Indexpunkte) ohne Einheit
    href=stock_href(q) or crypto_href(q)
    if not href and not selfpage: href=mhref(q)
    nm='<b>%s</b><div class="mut" style="font-size:11px">%s \u00b7 %s</div>'%(esc(q['name']),esc(q['sym']),q['grp'])
    if href: nm='<a class="rl" href="%s">%s</a>'%(href,nm)
    attr=(' data-href="%s"'%href) if href else ''
    if selfpage: attr+=' id="%s"'%mid(q)
    pl=' <span class="pl">%s</span>'%('24 h' if q['grp']=='Krypto' else '1 T')
    return '<tr%s><td class="c-sym">%s</td><td class="c-px">%s%s</td><td class="c-chg %s">%s</td><td class="c-pct %s">%s%%%s</td><td class="hide">%s</td></tr>'%(attr,nm,num(q['price']),cur,cls(q['chg']),sg(q['chg']),cls(q['pct']),sg(q['pct']),pl,spark(q['hist'],q['hist'][-1]>=q['hist'][0] if q['hist'] else True))
ROWJS='<script>(function(){if(window.__frow)return;window.__frow=1;document.addEventListener("click",function(e){if(e.button||e.metaKey||e.ctrlKey||e.shiftKey||e.altKey)return;if(e.target.closest&&e.target.closest("a"))return;var r=e.target.closest&&e.target.closest("tr[data-href]");if(r)location.href=r.getAttribute("data-href")})})()</script>'
def tbl(rows,selfpage=False): return '<div class="tw"><table><tr><th>Symbol</th><th>Kurs</th><th>Änd.</th><th>Änd. %</th><th class="hide">3 Monate</th></tr>'+''.join(trow(q,selfpage) for q in rows)+'</table></div>'+ROWJS
def news(n,k): from news_media import diverse as _dv; return '<ul class="nw">'+''.join('<li><a href="%s" target="_blank" rel="noopener nofollow">%s</a><div class="m">%s · %s</div></li>'%(esc(destination(i)),esc(i['title']),source_badge(i),fmtd(i['ts'])) for i in _dv(n,k))+'</ul>'
# ---------- Artikel (content/articles/*.json, Redaktion: FA Redaktion) ----------
ARTS=[]
os.makedirs('../content/articles',exist_ok=True)
for f in sorted(glob.glob('../content/articles/*.json')):
    try:
        a=json.load(open(f))
        if a.get('slug') and a.get('title') and a.get('body'): ARTS.append(a)
    except Exception as e: print('ART',f,e)
def adate(a):
    try: return datetime.datetime.fromisoformat(a['date'])
    except: return NOW
ARTS.sort(key=lambda a:adate(a),reverse=True)
def pubdate(a):
    dt=adate(a)
    if dt.tzinfo is None: dt=dt.replace(tzinfo=NOW.tzinfo)
    return dt.isoformat()
def mdate(a):
    # Wahrheitsgemaess: explizites 'modified'-Feld gewinnt, sonst Publikationsdatum
    try: return datetime.datetime.fromisoformat(a['modified']).isoformat()
    except Exception: return pubdate(a)
def art_ld(a):
    dt=adate(a)
    ld=[{'@context':'https://schema.org','@type':'NewsArticle','headline':a['title'],'description':a.get('description',''),'datePublished':dt.isoformat(),'dateModified':mdate(a),'inLanguage':'de-DE','mainEntityOfPage':BASE+'/artikel/%s/'%a['slug'],'author':{'@type':'Organization','name':'FA Redaktion','url':BASE+'/redaktion/'},**({'image':[BASE+a['image']]} if a.get('image') else {}),'publisher':{'@type':'NewsMediaOrganization','name':'finanz adjust','url':BASE}}]
    if a.get('faq'):
        ld.append({'@context':'https://schema.org','@type':'FAQPage','mainEntity':[{'@type':'Question','name':f['q'],'acceptedAnswer':{'@type':'Answer','text':f['a']}} for f in a['faq']]})
    return ld
def _art_body(a):
    dt=adate(a)
    img=''
    if a.get('image'):
        im=a['image']; im8=im[:-4]+'-800.jpg' if im.endswith('.jpg') else ''
        srcset=' srcset="%s 800w, %s 1600w" sizes="(max-width: 860px) 100vw, 820px"'%(esc(im8),esc(im)) if im8 and os.path.exists('../images/'+im8.split('/')[-1]) else ''
        img='<figure class="artimg"><img src="%s"%s alt="%s" width="1600" height="900" loading="lazy"></figure>'%(esc(im),srcset,esc(a['title']))
    chip='<span class="badge">%s</span>'%esc(a.get('section','Artikel'))
    faq=''
    if a.get('faq'):
        faq='<div class="faq"><h2>Häufige Fragen</h2>'+''.join('<details><summary>%s</summary><p>%s</p></details>'%(esc(f['q']),esc(f['a'])) for f in a['faq'])+'</div>'
    src=''
    if a.get('sources'):
        src='<div class="srcl"><b>Quellen:</b> '+' · '.join('<a href="%s" target="_blank" rel="noopener nofollow">%s</a>'%(esc(s['url']),esc(s['title'])) for s in a['sources'])+'</div>'
    return '''<div class="art"><h1>%s</h1><div class="by">Von der <b>FA Redaktion</b> · %s · <a href="/transparenz/" style="color:inherit;text-decoration:underline">mit KI-Unterstützung erstellt</a> %s</div>%s<div class="body">%s</div>@@SHAREB@@%s%s<div class="note"><b>Hinweis:</b> Dieser Artikel dient der Information und Einordnung. Er ist keine Anlageberatung und keine Kauf- oder Verkaufsempfehlung. Kursdaten können verzögert oder fehlerhaft sein. Mehr dazu im <a href="/risikohinweis/" style="text-decoration:underline">Risikohinweis</a>.</div></div>'''%(esc(a['title']),dt.strftime('%d.%m.%Y, %H:%M Uhr'),chip,img,a['body'],faq,src)
def art_body(a):
    h=_art_body(a); u=BASE+'/artikel/%s/'%a['slug']
    return h.replace('<div class="body">',share_block(u,a['title'],'fa',True)+'<div class="body">',1).replace('@@SHAREB@@',share_block(u,a['title'],'fa'),1)
urls=[]
org={'@context':'https://schema.org','@type':'NewsMediaOrganization','name':'finanz adjust','url':BASE,'email':'philipp.l.paulik@gmail.com'}
site_ld={'@context':'https://schema.org','@type':'WebSite','name':'finanz adjust','url':BASE,'inLanguage':'de-DE'}
arturls=[]
for a in ARTS:
    arturls.append(page('/artikel/%s/'%a['slug'],'%s | finanz adjust'%a['title'],a.get('description',a['title']),art_body(a),art_ld(a),act='/artikel/',otype='article',crumbs=[('/artikel/','Artikel'),('/artikel/%s/'%a['slug'],a['title'])],og='/og/%s.png'%a['slug']))
def artlist(k):
    out=[]
    for a in ARTS[:k]:
        out.append('<li><a href="/artikel/%s/">%s</a><div class="m">%s · FA Redaktion</div></li>'%(a['slug'],esc(a['title']),adate(a).strftime('%d.%m.%Y')))
    return '<ul class="nw">'+''.join(out)+'</ul>' if out else '<p class="mut">Die ersten Artikel der FA Redaktion erscheinen in Kürze.</p>'
# ---------- Startseite: Hero mit Kursen + Schlagzeilen ----------
idx=[q for q in Q if q['grp']=='Index'][:4]
cards=''.join('<a class="ic" href="/maerkte/#%s"><div class="n">%s</div><div class="p">%s</div><div class="%s">%s (%s%%)</div>%s</a>'%(mid(q),esc(q['name']),num(q['price']),cls(q['pct']),sg(q['chg']),sg(q['pct']),spark(q['hist'],q['hist'][-1]>=q['hist'][0] if q['hist'] else True,200,40)) for q in idx)
kpis=''.join('<a class="kpi" href="/maerkte/#%s"><div class="n">%s</div><div class="p">%s</div><div class="c %s">%s%%</div><div class="spk">%s</div></a>'%(mid(q),esc(q['name']),num(q['price']),cls(q['pct']),sg(q['pct']),spark(q['hist'],q['hist'][-1]>=q['hist'][0] if q['hist'] else True,150,34)) for q in idx[:3])
sorted_q=sorted([q for q in Q if q['grp'] in('US','DE')],key=lambda q:-q['pct'])
def fx_rows(link=True):
    rows=[(k,fx[k]) for k in ['USD','GBP','CHF','JPY','CNY'] if k in fx]
    if link: return ''.join('<a class="fxr" href="/maerkte/#devisen"><span>EUR/%s</span><b>%s</b></a>'%(k,num(v,4)) for k,v in rows)
    return ''.join('<div class="fxr"><span>EUR/%s</span><b>%s</b></div>'%(k,num(v,4)) for k,v in rows)
fxbox=fx_rows()
fxbox=fxbox or '<p class="mut">Aktuell nicht verfügbar.</p>'
home='''<div class="w"><div class="hero"><div class="hl"><h1>Märkte und Börsennews im Überblick</h1><p>Kurse, Schlagzeilen und Einordnungen der FA Redaktion. Seite neu erstellt %s. Kursdaten ohne gesicherten Datenstand - Werte können verzögert oder veraltet sein.</p><div class="kpis">%s</div><div class="pn" style="margin:16px 0 0"><h2>Neueste Artikel <a href="/artikel/">Alle →</a></h2>%s</div></div><div class="pn"><h2>Aktien-Schlagzeilen <a href="/nachrichten/">Alle →</a></h2>%s</div></div><div class="idx">%s</div><div class="g"><div><div class="pn"><h2>Watchlist <a href="/maerkte/">Alle Märkte →</a></h2>%s</div></div><div><div class="pn"><h2>Top-Gewinner</h2>%s</div><div class="pn"><h2>Top-Verlierer</h2>%s</div><div class="pn"><h2>Devisen (EZB-Referenzkurse)</h2>%s</div></div></div><div class="g"><div class="pn"><h2>Aktuelle Nachrichten <a href="/nachrichten/">Archiv →</a></h2>%s</div><div class="pn cta"><h2>Tagesbericht als PDF</h2><p>Der Marktbericht mit Indizes, Gewinnern, Verlierern, Devisen und Schlagzeilen als PDF zum Herunterladen und Weitergeben.</p><a class="b" href="/berichte/">Berichte ansehen</a></div></div></div>'''%(NOW.strftime('%d.%m.%Y %H:%M'),kpis,artlist(3),news(N,6),cards,tbl([q for q in Q if q['grp']!='Index']),tbl(sorted_q[:4]),tbl(sorted_q[-4:][::-1]),fxbox,news(N,12))
import market_visuals as MV
_MQ,_MU=MV._stocks()
home=home.replace('<div class="idx">',MV.home_block(_MU)+'<div class="idx">',1)
shutil.copyfile('market.css',OUT+'/market.css')
if _MU: urls.append(page('/heatmap/','Aktien-Heatmap: Tagesveränderung auf einen Blick | finanz adjust','Heatmap mit der Tagesveränderung von über 60 Aktien. Kursdaten von Twelve Data und Yahoo Finance, ggf. verzögert, keine Anlageberatung.',MV.heatmap_page(_MU,NOW.strftime("%d.%m.%Y %H:%M")),act="/maerkte/",crumbs=[("/heatmap/","Heatmap")]))
urls.append(page('/','finanz adjust: Märkte, Kurse und Börsennews live','Aktuelle Kurse zu DAX, S&P 500, Nasdaq, Aktien, Gold, Bitcoin und Devisen, Börsen-Schlagzeilen und Einordnungen der FA Redaktion. Kostenlos, ohne Anmeldung, keine Anlageberatung.',home,[org,site_ld]))
urls+=arturls
urls.append(page('/artikel/','Artikel der FA Redaktion | finanz adjust','Marktüberblicke, Einordnungen und Erklärungen der FA Redaktion: verständlich, quellenbasiert und ohne Anlageempfehlungen.','<div class="w"><div class="hero" style="grid-template-columns:1fr"><div class="hl"><h1>Artikel der FA Redaktion</h1><p>Einordnungen statt Empfehlungen: Was die Märkte bewegt, verständlich erklärt und mit Quellen belegt.</p></div></div><div class="pn">%s</div></div>'%artlist(60),act='/artikel/',crumbs=[('/artikel/','Artikel')]))
urls.append(page('/maerkte/','Märkte: Indizes, Aktien, Rohstoffe, Krypto | finanz adjust','Live-Kurse und 3-Monats-Verlauf für DAX, S&P 500, Nasdaq, Apple, NVIDIA, SAP, Gold, Rohöl, Bitcoin und mehr.','<div class="w"><div class="hero" style="grid-template-columns:1fr"><div class="hl"><h1>Märkte</h1><p>Kurse mit 3-Monats-Verlauf. Quellen: %s. Seite neu erstellt %s; ein gesicherter Datenstand der Kurse liegt nicht vor - Werte können verzögert oder veraltet sein. Alle Angaben ohne Gewähr.</p></div></div><div class="pn">%s</div><div class="pn"><h2 id="devisen">Devisen (EZB-Referenzkurse)</h2>%s</div></div>'%(qsrc(),NOW.strftime('%d.%m.%Y %H:%M'),tbl(Q,True),fx_rows(False)),act='/maerkte/',crumbs=[('/maerkte/','Märkte')]))
urls.append(page('/nachrichten/','Börsennews und Finanznachrichten: Archiv | finanz adjust','Börsen- und Wirtschaftsnachrichten mit Quellenkennzeichnung und Links zu den Originalmeldungen.','<div class="w"><div class="news-intro"><div><span class="news-kicker">Nachrichten · Quellen im Blick</span><h1>Was die Märkte bewegt.</h1><p>Börsennews aus externen Quellen. Die wichtigsten Schlagzeilen im Überblick, die ganze Geschichte beim Original.</p></div><div class="news-count"><b>%d</b> Meldungen im Archiv</div></div>%s<p class="news-disclosure">Gezeigt werden die neuesten %d Meldungen. Quellen-Icons sind lokal gespeichert. Grafische Quellenkarten sind keine Artikelfotos. Fremde Vorschaubilder erscheinen nur mit dokumentierter Nutzungsfreigabe und Bildnachweis. <a href="/quellen/">Mehr zu den Quellen</a></p></div>'%(len(N),news_cards(N,500),min(len(N),500)),act='/nachrichten/',crumbs=[('/nachrichten/','Nachrichten')]))
# ---------- Source-linked glossary ----------
from glossary import build_glossary
GLOSSAR=build_glossary(page,urls,ARTS,OUT,BASE)
from calculators import build_calculators
build_calculators(page,urls,OUT,BASE)
from comparisons import build_comparisons
build_comparisons(page,urls,OUT,BASE)
from lernpfade import build_lernpfade
build_lernpfade(page,urls,OUT,BASE)
# ---------- PDF-Tagesbericht ----------
today=NOW.strftime('%Y-%m-%d')
from report import build as _rep_build
def report_html(): return _rep_build(Q,ARTS,fx,N,NOW,num,sg,cls,esc,re.sub(r'<[^>]+>','',qsrc()),LOGO,adate)
open('rep.html','w').write(report_html())
pdf=OUT+'/berichte/tagesbericht-%s.pdf'%today
chrome=shutil.which('google-chrome') or shutil.which('chromium') or shutil.which('chromium-browser')
report_ok=False
if chrome:
    if os.path.exists(pdf+'.tmp'): os.remove(pdf+'.tmp')
    subprocess.run([chrome,'--headless','--no-sandbox','--disable-gpu','--no-pdf-header-footer','--print-to-pdf='+os.path.abspath(pdf+'.tmp'),'file://'+os.path.abspath('rep.html')],capture_output=True)
    import sys
    sys.path.insert(0,os.path.abspath('../tools'))
    from daily_archive import valid_pdf
    if valid_pdf(pdf+'.tmp'):
        report_ok=True
        os.replace(pdf+'.tmp',pdf)
        shutil.copy(pdf,OUT+'/berichte/aktuell.pdf')
else: print('no chrome, skip pdf')

# ---------- OG-Bilder (1200x630, FA Light-Style) ----------
os.makedirs(OUT+'/og',exist_ok=True)
def og_html(title,kicker,meta):
    return '''<!doctype html><html><head><meta charset="utf-8"><style>*{margin:0;box-sizing:border-box}body{width:1200px;height:630px;overflow:hidden;font-family:Helvetica,Arial,sans-serif;background:#f6f8fc;color:#131722;display:flex;flex-direction:column}.top{background:linear-gradient(120deg,#131722,#1A6ACD);padding:30px 48px;display:flex;align-items:center;gap:16px}.top svg{height:44px;width:auto}.wm{color:#fff;font-weight:800;font-size:26px;letter-spacing:-.01em}.wm b{color:#7cc4ff}.mid{flex:1;padding:48px 48px 0}.k{color:#0086F5;font-size:20px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;margin-bottom:16px}h1{font-size:46px;line-height:1.15;letter-spacing:-.02em;max-width:1040px}.m{margin-top:20px;color:#5a6070;font-size:20px}.ft{padding:0 48px 30px;color:#8a90a0;font-size:18px;display:flex;justify-content:space-between}.ft b{color:#0086F5}</style></head><body><div class="top">%s<span class="wm">finanz<b>adjust</b></span></div><div class="mid"><div class="k">%s</div><h1>%s</h1><div class="m">%s</div></div><div class="ft"><span>finanz-adjust.de</span><span><b>FA Redaktion</b> · Kurse · News · Einordnungen</span></div></body></html>'''%(LOGO,esc(kicker),esc(title),esc(meta))
def og_png(png,title,kicker,meta):
    if not chrome: return
    open('_og.html','w').write(og_html(title,kicker,meta))
    subprocess.run([chrome,'--headless','--no-sandbox','--disable-gpu','--hide-scrollbars','--window-size=1200,630','--screenshot='+os.path.abspath(png),'file://'+os.path.abspath('_og.html')],capture_output=True)
og_png(OUT+'/og/default.png','Märkte, Kurse und Börsennews live','finanz adjust','DAX · S&P 500 · Nasdaq · Aktien · Gold · Bitcoin · Devisen')
for a in ARTS: og_png(OUT+'/og/%s.png'%a['slug'],a['title'],a.get('section','Artikel'),'FA Redaktion · '+adate(a).strftime('%d.%m.%Y'))

from og_stocks import build_stock_ogs
build_stock_ogs(OUT, chrome, LOGO)
import sys
sys.path.insert(0,os.path.abspath('../tools'))
from daily_archive import sync, archive_html
archive_dates=sync('..',OUT+'/berichte','aktuell.pdf','tagesbericht-',NOW,archive_today=report_ok)
reps=sorted([r for r in os.listdir(OUT+'/berichte') if r.startswith('tagesbericht-')],reverse=True)
from report_landing import build as report_landing
urls.append(page('/berichte/','Tagesbericht gratis als PDF und Tagesarchiv | finanz adjust','Marktüberblick als kostenloses PDF: ohne Anmeldung und E-Mail. Mit Quellen, Druckansicht und täglichen Archiv-Ausgaben.',__import__('report_landing_fa').enhance(report_landing('..',OUT,'fa',archive_dates,'aktuell.pdf','tagesbericht-'),'..',OUT,archive_dates,'aktuell.pdf',NOW.strftime('%d.%m.%Y, %H:%M Uhr')),act='/berichte/',crumbs=[('/berichte/','Berichte')]))
# ---------- Recht & Transparenz ----------
imp='''<div class="pg"><h1>Impressum</h1><h2>Angaben gemäß § 5 DDG</h2><p>Philipp Paulik<br>Mozartstraße 1<br>53819 Neunkirchen-Seelscheid<br>Nordrhein-Westfalen</p><h2>Kontakt</h2><p>E-Mail: philipp.l.paulik@gmail.com</p><h2>Redaktion</h2><p>Die Inhalte dieser Seite erscheinen unter der Redaktionsbezeichnung "FA Redaktion".</p><h2>Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV</h2><p>Philipp Paulik, Anschrift wie oben</p><h2>Haftung für Inhalte</h2><p>Als Diensteanbieter sind wir für eigene Inhalte nach den allgemeinen Gesetzen verantwortlich. Fremde Inhalte (Kursdaten, Nachrichten-Überschriften) stammen von den genannten Quellen. Bei Bekanntwerden von Rechtsverletzungen entfernen wir Inhalte umgehend.</p><h2>Haftung für Links</h2><p>Für Inhalte verlinkter externer Seiten ist stets der jeweilige Anbieter verantwortlich.</p><h2>Keine Anlageberatung</h2><p>Siehe <a href="/risikohinweis/" style="text-decoration:underline">Risikohinweis</a>.</p></div>'''
urls.append(page('/impressum/','Impressum | finanz adjust','Impressum',imp,crumbs=[('/impressum/','Impressum')]))
risk='''<div class="pg"><h1>Risikohinweis</h1><h2>Keine Anlageberatung</h2><p>Alle Inhalte auf finanz adjust dienen ausschließlich der allgemeinen Information und Einordnung. Sie stellen keine Anlageberatung, Anlageempfehlung, Finanzanalyse und keine Kauf- oder Verkaufsempfehlung dar. Die FA Redaktion veröffentlicht keine Kursziele, keine Bewertungen einzelner Wertpapiere zum Kauf oder Verkauf und keine individuellen Handlungsaufforderungen.</p><h2>Risiken des Handels</h2><p>Der Handel mit Aktien, Derivaten, Kryptowerten und gehebelten Produkten ist mit erheblichen Risiken bis zum Totalverlust des eingesetzten Kapitals verbunden. Kursverläufe der Vergangenheit sind kein verlässlicher Indikator für die Zukunft. Treffen Sie Anlageentscheidungen nur nach eigener Prüfung und gegebenenfalls unabhängiger, individueller Beratung.</p><h2>Kursdaten und Quellen</h2><p>Kursdaten stammen aus öffentlichen Schnittstellen (%s), können verzögert, fehlerhaft oder vorübergehend nicht verfügbar sein und werden ohne Gewähr bereitgestellt. Wechselkurse stammen von der Europäischen Zentralbank (Euro-Referenzkurse). Nachrichten-Schlagzeilen werden automatisch aggregiert (GDELT Project / Yahoo Finance); für deren Inhalte sind die jeweiligen Anbieter verantwortlich.</p><h2>KI-Hinweis</h2><p>Redaktionelle Artikel und Glossar-Texte werden mit KI-Unterstützung erstellt und redaktionell geprüft. Trotz sorgfältiger Prüfung können Fehler nicht ausgeschlossen werden. Hinweise auf Fehler nehmen wir gerne über den <a href="/kontakt/" style="text-decoration:underline">Kontakt</a> entgegen.</p></div>'''%re.sub(r'<[^>]+>','',qsrc())
urls.append(page('/risikohinweis/','Risikohinweis | finanz adjust','Keine Anlageberatung: Risikohinweis, Quellen und redaktionelle Grundsätze von finanz adjust.',risk,act='/risikohinweis/',crumbs=[('/risikohinweis/','Risikohinweis')]))
quel='''<div class="pg"><h1>Quellen und Daten</h1><h2>Kursdaten</h2><p>Indizes, Aktien und Rohstoffe: <a href="https://twelvedata.com" rel="noopener" style="text-decoration:underline">Twelve Data</a> (kostenlose Schnittstelle, ggf. verzögert) sowie als Ergänzung Yahoo Finance (öffentliche Schnittstelle). Kryptowerte: <a href="https://www.coingecko.com" rel="noopener" style="text-decoration:underline">Powered by CoinGecko</a>. Wechselkurse: Europäische Zentralbank, Euro-Referenzkurse. Alle Kursdaten ohne Gewähr und möglicherweise verzögert.</p><h2>Nachrichten</h2><p>Schlagzeilen werden automatisch aus dem <a href="https://www.gdeltproject.org" rel="noopener" style="text-decoration:underline">GDELT Project</a> und aus dem vorhandenen Yahoo-Finance-Nachrichtenarchiv aggregiert. Wir zeigen ausschließlich Überschriften mit kurzen Angaben und verlinken auf die Originalquelle. Volltexte werden nicht übernommen.</p><h2>Quellen-Icons und Vorschaubilder</h2><p>Die Quellenkennzeichnung richtet sich nach der verlinkten Website, nicht nach dem Aggregator. Kleine Quellen-Icons werden lokal ausgeliefert und dienen ausschließlich der Quellenkennzeichnung; sie bedeuten keine Partnerschaft. Wo kein Icon verfügbar ist, erscheint ein Monogramm. Grafische Quellenkarten sind keine Fotos aus dem verlinkten Artikel. Fremde Vorschaubilder werden nur nach dokumentierter Prüfung der Nutzungsrechte lokal eingebunden und mit Bildnachweis versehen. Derzeit sind keine externen Artikelfotos freigegeben.</p><h2>Aktualisierung</h2><p>Die Seite wird mehrmals täglich automatisch neu erstellt (sechs Läufe zwischen ca. 7 und 22 Uhr). Der jeweilige Datenstand steht im Footer jeder Seite.</p><h2>Redaktionelle Grundsätze</h2><p>Die FA Redaktion berichtet sachlich und quellenbasiert: keine Kauf- oder Verkaufsempfehlungen, keine Kursziele, keine erfundenen Zitate, keine Politikberichterstattung. Artikel werden mit KI-Unterstützung erstellt und redaktionell geprüft; verwendete Quellen werden am Ende jedes Artikels genannt.</p></div>'''
urls.append(page('/quellen/','Quellen und Daten | finanz adjust','Woher Kurse und Nachrichten auf finanz adjust stammen: Datenquellen, Aktualisierung und redaktionelle Grundsätze der FA Redaktion.',quel,crumbs=[('/quellen/','Quellen')]))
dsg='''<div class="pg"><h1>Datenschutzerklärung</h1><h2>Verantwortlicher</h2><p>Philipp Paulik, Mozartstraße 1, 53819 Neunkirchen-Seelscheid, philipp.l.paulik@gmail.com</p><h2>Hosting</h2><p>Diese Seite wird als statische Website über GitHub Pages (GitHub Inc., USA) ausgeliefert. Dabei verarbeitet der Anbieter technisch notwendig Ihre IP-Adresse in Server-Logfiles (Art. 6 Abs. 1 lit. f DSGVO).</p><h2>Kein Tracking, keine Cookies</h2><p>Werbedienste setzen wir nicht ein. Analysedaten erheben wir nur mit Ihrer Einwilligung; Details siehe Abschnitt Google Analytics 4. Kursdaten und Nachrichten werden grundsätzlich beim Erstellen der Seite serverseitig abgerufen. Auf Aktienseiten kann bei fehlenden API-Kursen ein TradingView-Widget freiwillig per Klick geladen werden. Vor diesem Klick werden durch das Widget keine Verbindungen zu Dritten aufgebaut. Beim Klick werden IP-Adresse, Seitenadresse, Widgettyp und Symbol an TradingView übertragen; laut TradingView setzt das Widget keine Cookies. Die Einwilligung gilt nur für die aktuell geladene Seite und wird nicht gespeichert. Durch Neuladen der Seite wird das Widget wieder deaktiviert. Weitere Hinweise: <a href="https://www.tradingview.com/privacy-policy/" rel="noopener noreferrer" target="_blank">TradingView Datenschutz</a>. Quellen-Icons und gegebenenfalls freigegebene Vorschaubilder werden lokal ausgeliefert; dafür wird beim Seitenaufruf keine Verbindung zur Nachrichtenquelle aufgebaut. Beim Öffnen eines externen Nachrichtenlinks gelten die Datenschutzregeln der Zielseite. Selbst gehostete Unternehmenslogos werden ohne Anfrage an einen Logodienst ausgeliefert. Zudem speichert die Seite technisch notwendige Einstellungen ausschließlich lokal in Ihrem Browser: die gewählte Design-Ansicht (hell/dunkel) sowie eine Sitzungsmarke, damit der Hinweisdialog auf den kostenlosen Tagesbericht höchstens einmal pro Browsersitzung erscheint. Diese Angaben verlassen Ihr Gerät nicht, werden weder an uns noch an Dritte übertragen und sind für den Betrieb unbedingt erforderlich (§ 25 Abs. 2 TDDDG); die Sitzungsmarke wird automatisch gelöscht, sobald Sie den Browser-Tab schließen.</p><h2>Ihre Rechte</h2><p>Auskunft, Berichtigung, Löschung, Einschränkung, Datenübertragbarkeit, Widerspruch und Beschwerde bei einer Aufsichtsbehörde. Kontakt: philipp.l.paulik@gmail.com</p><h2>Lernpfade: lokaler Speicher</h2><p>Auf den Lernpfad-Seiten speichert Ihr Browser Ihren Lernfortschritt (welche Schritte Sie abgehakt haben) im localStorage Ihres Geräts. Die Daten verlassen Ihr Gerät nicht, werden nicht an uns oder Dritte übertragen und dienen nur der Anzeige Ihres Fortschritts. Sie können den Eintrag mit der Schaltfläche „Zurücksetzen“ oder über die Browser-Einstellungen löschen.</p></div>'''
dsg=dsg.replace('<h2>Ihre Rechte</h2>', newsletter_fa.DSG_SECTION+'<h2>Ihre Rechte</h2>')
urls.append(page('/datenschutz/','Datenschutz | finanz adjust','Datenschutzerklärung',dsg,crumbs=[('/datenschutz/','Datenschutz')]))
urls+=newsletter_fa.build(page,OUT)
urls.append(page('/kontakt/','Kontakt | finanz adjust','Kontakt zur FA Redaktion','<div class="pg"><h1>Kontakt</h1><p>FA Redaktion - E-Mail: <a href="mailto:philipp.l.paulik@gmail.com" style="text-decoration:underline">philipp.l.paulik@gmail.com</a></p></div>',crumbs=[('/kontakt/','Kontakt')]))
# ---------- Aktienverzeichnis ----------
from stocks import build_stock_pages
build_stock_pages(page,urls,ARTS,OUT,BASE)
from crypto import build_crypto_pages
build_crypto_pages(page,urls,ARTS,OUT,BASE,og_png,NOW.strftime('%d.%m.%Y %H:%M'))
from broker import build_broker
build_broker(page,urls,OUT,BASE)
# ---------- Assets, Sitemaps, Feed ----------
open(OUT+'/logo.svg','w').write(LOGO)
open(OUT+'/favicon.svg','w').write(LOGO)
red='''<div class="pg"><h1>Redaktion</h1><h2>Redaktionelle Grundsätze</h2><p>finanz adjust erscheint im Verlag von Philipp Paulik, Neunkirchen-Seelscheid. Verantwortlich im Sinne des § 18 Abs. 2 MStV ist Philipp Paulik (<a href="/impressum/" style="text-decoration:underline">Impressum</a>). Die Inhalte erscheinen unter der Redaktionsbezeichnung „FA Redaktion". Kontakt: <a href="mailto:philipp.l.paulik@gmail.com" style="text-decoration:underline">philipp.l.paulik@gmail.com</a>.</p><h2>Selbstverständnis</h2><p>finanz adjust ordnet Märkte und Börsennews auf Deutsch ein: Kurse, Schlagzeilen und Hintergründe, sachlich und quellenbasiert. Wir berichten, statt zu empfehlen: keine Anlageberatung, keine Kursziele, keine Kauf- oder Verkaufsempfehlungen.</p><h2>Unabhängigkeit und Werbung</h2><p>Die Redaktion entscheidet allein über Themen und Inhalte. Bezahlte Inhalte, Affiliate-Links oder Anzeigen würden als solche gekennzeichnet (vgl. § 6 DDG). Aktuell enthält das Angebot keine Werbung und keine Affiliate-Links.</p><h2>Einsatz von KI</h2><p>Artikel und Glossar-Texte entstehen mit KI-Unterstützung und werden vor der Veröffentlichung redaktionell geprüft. Details dazu auf der Seite <a href="/transparenz/" style="text-decoration:underline">KI-Transparenz</a>.</p><h2>Quellen und Belege</h2><p>Artikel nennen ihre Quellen am Ende des Textes. Kursdaten und Nachrichten-Schlagzeilen stammen aus den unter <a href="/quellen/" style="text-decoration:underline">Quellen und Daten</a> genannten Schnittstellen.</p><h2>Korrekturen</h2><p>Wie wir mit Fehlern umgehen, steht auf der Seite <a href="/korrekturen/" style="text-decoration:underline">Korrekturen</a>.</p></div>'''
urls.append(page('/redaktion/','Redaktion und redaktionelle Grundsätze | finanz adjust','Wer hinter finanz adjust steht und nach welchen Grundsätzen die FA Redaktion arbeitet: unabhängig, quellenbasiert, ohne Anlageberatung.',red,crumbs=[('/redaktion/','Redaktion')]))
trn='''<div class="pg"><h1>KI-Transparenz</h1><p>finanz adjust nutzt KI-Werkzeuge bei der Erstellung seiner Inhalte. Diese Seite erklärt offen, wo KI zum Einsatz kommt, wo der Mensch entscheidet und wie wir kennzeichnen. Sie gilt zusätzlich zu den Hinweisen direkt an den Beiträgen.</p><h2>Wo KI zum Einsatz kommt</h2><p>Recherche und Textentwurf: KI-Systeme unterstützen bei der Recherche und erstellen Entwürfe von Artikeln und Glossar-Texten. Titelbilder und Grafiken können mit KI-Werkzeugen erstellt sein.</p><h2>Was ohne KI läuft</h2><p>Kursdaten, Charts, Wechselkurse und Nachrichten-Schlagzeilen werden automatisch aus den genannten Schnittstellen übernommen und nicht von KI erzeugt oder interpretiert (Details: <a href="/quellen/" style="text-decoration:underline">Quellen und Daten</a>).</p><h2>Wo der Mensch entscheidet</h2><p>Themenauswahl, Quellenprüfung und Veröffentlichung verantwortet Philipp Paulik als Herausgeber. Jeder Artikel wird vor der Veröffentlichung inhaltlich geprüft: Stimmen die Quellen, stimmen die Zahlen, ist die Einordnung nachvollziehbar? Es wird nichts veröffentlicht, das nicht vorher von einem Menschen gelesen und freigegeben wurde. Die redaktionelle Verantwortung für alle Inhalte trägt Philipp Paulik (siehe <a href="/impressum/" style="text-decoration:underline">Impressum</a>).</p><h2>Wie wir kennzeichnen</h2><p>Jeder Artikel und Glossar-Eintrag trägt in der Zeile unter der Überschrift den Hinweis „mit KI-Unterstützung erstellt".</p><h2>Rechtlicher Rahmen (EU AI Act)</h2><p>Seit dem 2. August 2026 gelten die Transparenzpflichten des Artikels 50 der europäischen KI-Verordnung (Verordnung (EU) 2024/1689). Danach müssen Betreiber generativer KI-Systeme offenlegen, wenn Text zu Angelegenheiten von öffentlichem Interesse mit KI erzeugt wurde. Eine Ausnahme gilt, wenn die Inhalte einer menschlichen Überprüfung oder redaktionellen Kontrolle unterzogen wurden und eine natürliche Person die redaktionelle Verantwortung trägt. Diese Ausnahme trifft auf finanz adjust zu; wir kennzeichnen den KI-Einsatz dennoch freiwillig an jedem Beitrag.</p></div>'''
urls.append(page('/transparenz/','KI-Transparenz: So arbeitet finanz adjust mit künstlicher Intelligenz | finanz adjust','Wo finanz adjust KI einsetzt, wo der Mensch entscheidet und wie wir kennzeichnen - inklusive Hinweisen zu Artikel 50 der EU-KI-Verordnung.',trn,crumbs=[('/transparenz/','KI-Transparenz')]))
from about import build_about
build_about(page,urls,ARTS,GLOSSAR,OUT,BASE)
kor='''<div class="pg"><h1>Korrekturen und Fehlerpolitik</h1><p>Auch mit KI-Unterstützung und Prüfung bleiben Fehler möglich. Wichtig ist, wie wir damit umgehen.</p><h2>Fehler melden</h2><p>Hinweise auf Fehler bitte per E-Mail an <a href="mailto:philipp.l.paulik@gmail.com" style="text-decoration:underline">philipp.l.paulik@gmail.com</a>, Betreff „Korrektur: [Titel des Beitrags]". Wir prüfen jede Meldung, in der Regel innerhalb von zwei Werktagen.</p><h2>So korrigieren wir</h2><p>Formale Fehler (Tippfehler, Umbruch, Formatierung) korrigieren wir ohne Vermerk. Inhaltliche Fehler (Zahlen, Aussagen, Zusammenhänge) korrigieren wir im Beitrag, setzen das Aktualisierungsdatum und vermerken die Korrektur mit Datum am Ende des Textes („Korrektur, TT.MM.JJJJ: …"). Schwerwiegende Fehler, die die Aussage eines Beitrags betreffen, weisen wir zusätzlich am Anfang des Beitrags aus. Beiträge werden nicht still gelöscht. Eine Entfernung kommt nur aus rechtlichen Gründen in Betracht und wird an der ursprünglichen Stelle vermerkt.</p><h2>Kursdaten</h2><p>Kursdaten und Schlagzeilen werden automatisch aus öffentlichen Schnittstellen übernommen und können verzögert oder fehlerhaft sein; sie werden ohne Gewähr bereitgestellt. Bei Auffälligkeiten prüfen wir die Angabe gegen die Originalquelle und korrigieren die Übernahme.</p><h2>Rechtlicher Hinweis</h2><p>Diese freiwillige Fehlerpolitik lässt gesetzliche Ansprüche unberührt, insbesondere den Anspruch auf Gegendarstellung nach dem Landespressegesetz Nordrhein-Westfalen. Unsere Praxis orientiert sich an den Sorgfalts- und Richtigstellungsgrundsätzen des Pressekodex (Ziffern 1 und 3).</p></div>'''
urls.append(page('/korrekturen/','Korrekturen und Fehlerpolitik | finanz adjust','Wie die FA Redaktion mit Fehlern umgeht: Fehler melden, Korrekturvermerke, keine stillen Löschungen.',kor,crumbs=[('/korrekturen/','Korrekturen')]))
open(OUT+'/robots.txt','w').write('User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\nSitemap: %s/news-sitemap.xml\n'%(BASE,BASE))
open(OUT+'/CNAME','w').write('finanz-adjust.de\n'); open(OUT+'/.nojekyll','w').write('')
try:
    _sm_stocks=json.loads(open('stocks.json').read())
except Exception:
    _sm_stocks=[]
_sm_img={'%s/aktien/%s/'%(BASE,s['slug']):('%s/og/aktien/%s-logo.png'%(BASE,s['slug']),s['name']+' Logo auf finanz adjust') for s in _sm_stocks if s.get('logo')}
# lastmod nur wo wahr (vgl. developers.google.com/search/blog/2023/06/sitemaps-lastmod-ping):
# - Artikel: 'modified'-Feld falls gepflegt, sonst Publikationsdatum
# - / und /artikel/ aendern sich nachweislich mit jedem neuen Artikel: Datum des neuesten Artikels
# - alle anderen Seiten: kein lastmod (Render allein ist keine Inhaltsaenderung; weglassen ist laut Google ok)
_art_lm={BASE+'/artikel/%s/'%a['slug']: mdate(a)[:10] for a in ARTS}
_newest_art=mdate(ARTS[0])[:10] if ARTS else None
_list_lm={BASE+'/':_newest_art, BASE+'/artikel/':_newest_art}
def _sm_url(u):
    img=_sm_img.get(u)
    imgtag='<image:image><image:loc>%s</image:loc><image:title>%s</image:title></image:image>'%(img[0],esc(img[1])) if img else ''
    lm=_art_lm.get(u) or _list_lm.get(u)
    lmtag='<lastmod>%s</lastmod>'%lm if lm else ''
    return '<url><loc>%s</loc>%s%s</url>'%(u,lmtag,imgtag)
open(OUT+'/sitemap.xml','w').write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">'+''.join(_sm_url(u) for u in urls)+'</urlset>')
recent=[a for a in ARTS if (NOW-adate(a).astimezone()).total_seconds()<172800]
news_sm='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">'+''.join('<url><loc>%s/artikel/%s/</loc><news:news><news:publication><news:name>finanz adjust</news:name><news:language>de</news:language></news:publication><news:publication_date>%s</news:publication_date><news:title>%s</news:title></news:news></url>'%(BASE,a['slug'],pubdate(a),esc(a['title'])) for a in recent)+'</urlset>'
open(OUT+'/news-sitemap.xml','w').write(news_sm)
items=''.join('<item><title>%s</title><link>%s/artikel/%s/</link><guid>%s/artikel/%s/</guid><description>%s</description><pubDate>%s</pubDate></item>'%(esc(a['title']),BASE,a['slug'],BASE,a['slug'],esc(a.get('description','')),email.utils.format_datetime(adate(a).astimezone())) for a in ARTS[:20])
items+=''.join('<item><title>%s</title><link>%s</link><guid>%s</guid><description>%s</description><pubDate>%s</pubDate></item>'%(esc(i['title']),esc(i['url']),esc(i['url']),'',email.utils.format_datetime(datetime.datetime.fromtimestamp(i['ts']).astimezone())) for i in _feed_diverse(N,60) if i.get('ts'))
open(OUT+'/feed.xml','w').write('<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>finanz adjust</title><link>%s</link><description>Artikel der FA Redaktion und aggregierte Börsennews</description><language>de</language>%s</channel></rss>'%(BASE,items))
json.dump(Q,open(OUT+'/quotes.json','w'))
# ---------- IndexNow-Export: nur neue/geaenderte Artikel (Status: data/indexnow-state.json) ----------
# Der Push erfolgt im Deploy-Job NACH erfolgreichem Deployment; erst dann aktualisiert der
# Workflow data/indexnow-state.json. Schlaegt der Push fehl, werden die URLs beim naechsten
# Build automatisch erneut exportiert. Erstlauf: nur Artikel der letzten 48h, kein Vollpush.
try: _inow_state=json.load(open('../data/indexnow-state.json'))
except Exception: _inow_state={}
_inow_new=[]
for a in ARTS:
    _m=mdate(a)
    if _inow_state.get(a['slug'])==_m: continue
    if a['slug'] not in _inow_state and (NOW-adate(a).astimezone()).total_seconds()>=172800: continue
    _inow_new.append(BASE+'/artikel/%s/'%a['slug'])
open(OUT+'/indexnow-urls.txt','w').write('\n'.join(sorted(_inow_new))+('\n' if _inow_new else ''))
_inow_key=os.environ.get('INDEXNOW_KEY','').strip()
if _inow_key:
    open(OUT+'/%s.txt'%_inow_key,'w').write(_inow_key+'\n')
print('FA pages',len(urls),'articles',len(ARTS),'fx',len(fx),'indexnow_new',len(_inow_new))

# Rights-gated noindex sources, deliberately excluded from sitemaps and RSS.
from news_detail import build_details
build_details(page, N, OUT)
from licensed_news import archive_body, noindex
_archive_body=archive_body(licensed_archive,'finanz adjust').replace('KI-News aus externen Quellen.','Gesicherte Wirtschafts-Meldungen.').replace('Schlagzeilen und erlaubte RSS-Anrisstexte von heise online.','Schlagzeilen von FinanzNachrichten sowie erlaubte RSS-Textauszüge von Destatis und der EZB.')
page('/nachrichten/quellenarchiv/','Gesicherte Quelleninfos | finanz adjust','Dauerhaft gespeicherte Quelleninfos.',_archive_body,act='/nachrichten/')
noindex(OUT+'/nachrichten/quellenarchiv/index.html')
_p=__import__('pathlib').Path(OUT+'/nachrichten/index.html')
_p.write_text(_p.read_text().replace('<h1>Was die Märkte bewegt.</h1>','<h1>Was die Märkte bewegt.</h1><p><a href="/nachrichten/quellenarchiv/">Alle gesicherten Quelleninfos →</a></p>',1))

# Final isolated pass: advertising, consent and activation gates (no third-party code by default).
import sys
subprocess.check_call([sys.executable,'../tools/monetization.py',OUT])

# Static in-article daily-report CTA, after all article renderers and consent passes.
from report_breaker import main as add_report_breakers
add_report_breakers(OUT)
