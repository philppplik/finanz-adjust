import json,os,re,time,urllib.parse
from zoneinfo import ZoneInfo
from common import *
from news_media import permitted_news
os.makedirs('../data',exist_ok=True)
TD_KEY=os.environ.get('TWELVEDATA_API_KEY','').strip()
# ---------- Nachrichten: GDELT (aggregiert, keine Volltexte) ----------
fin=[]
# GDELT DOC 2.0 API (100% free & open, kein Key): aggregierte Boersen-Schlagzeilen, deutsch + international
GDELT_STATUS=[]
import urllib.error
def gget(u,q):
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=15)
        GDELT_STATUS.append({'query':q,'status':r.status})
        return r.read()
    except urllib.error.HTTPError as e:
        # Throttling respektieren: Status + Retry-After nur protokollieren, kein Retry/Umgehung
        GDELT_STATUS.append({'query':q,'status':e.code,'retry_after':e.headers.get('Retry-After') or ''})
        print('GDELT HTTP',e.code,'retry-after',e.headers.get('Retry-After'))
        return None
    except Exception as e:
        GDELT_STATUS.append({'query':q,'status':'ERR','error':str(e)[:120]})
        print('GDELT',e); return None
for qi,(q,src) in enumerate([('(dax OR aktie OR börse OR aktienmarkt) sourcelang:german','GDELT'),
              ('(nasdaq OR "s&p 500" OR dow jones OR nvidia OR bitcoin) sourcelang:german','GDELT'),
              ('(federal reserve OR ezb OR zinsen) sourcelang:german','GDELT')]):
    b=gget('https://api.gdeltproject.org/api/v2/doc/doc?query=%s&mode=artlist&maxrecords=40&format=json&sort=hybridrel'%urllib.parse.quote(q),q)
    if qi<2: time.sleep(6)  # GDELT-Limit: max 1 Request / 5s
    if not b: continue
    try:
        arts=json.loads(b).get('articles',[])
        for a in arts:
            sd=a.get('seendate','')
            try: ts=datetime.datetime.strptime(sd,'%Y%m%dT%H%M%SZ').replace(tzinfo=datetime.timezone.utc).timestamp()
            except: ts=0
            dom=a.get('domain','')
            fin.append(dict(title=strip(a.get('title','')),url=(a.get('url') or '').strip(),sum='',ts=ts,src='%s · %s'%(src,dom)))
    except Exception as e: print('GDELT',e)
fin=[f for f in fin if f['title'] and f['url']]
# Fetch-Fehler sichtbar machen: Status ins Archiv-Verzeichnis schreiben (wird vom Workflow mitcommittet)
json.dump({'ts':int(time.time()),'archive_newest':max([f['ts'] for f in json.load(open('../data/fin_archive.json'))] or [0]) if os.path.exists('../data/fin_archive.json') else 0,'queries':GDELT_STATUS},open('../data/gdelt-status.json','w'),ensure_ascii=False)
json.dump(permitted_news(merge_archive('../data/fin_archive.json',permitted_news(fin))),open('../data/fin_archive.json','w'),ensure_ascii=False)
# ---------- Kurse ----------
# sym, name, gruppe, twelvedata-symbol (None = kein TD), td-exchange, coingecko-id
SYM=[('^GDAXI','DAX','Index',None,None,None),('^GSPC','S&P 500','Index',None,None,None),('^IXIC','Nasdaq','Index',None,None,None),('^STOXX50E','Euro Stoxx 50','Index',None,None,None),
('AAPL','Apple','US','AAPL',None,None),('MSFT','Microsoft','US','MSFT',None,None),('NVDA','NVIDIA','US','NVDA',None,None),('TSLA','Tesla','US','TSLA',None,None),('AMZN','Amazon','US','AMZN',None,None),('GOOGL','Alphabet','US','GOOGL',None,None),('META','Meta','US','META',None,None),
('SAP.DE','SAP','DE',None,None,None),('SIE.DE','Siemens','DE',None,None,None),('ALV.DE','Allianz','DE',None,None,None),('DTE.DE','Dt. Telekom','DE',None,None,None),('BMW.DE','BMW','DE',None,None,None),
('EURUSD=X','EUR/USD','FX','EUR/USD',None,None),('GC=F','Gold','Rohstoff','XAU/USD',None,None),('CL=F','Rohöl WTI','Rohstoff',None,None,None),
('BTC-USD','Bitcoin','Krypto',None,None,'bitcoin'),('ETH-USD','Ethereum','Krypto',None,None,'ethereum')]
def yahoo(sym):
    b=get('https://query1.finance.yahoo.com/v8/finance/chart/%s?range=3mo&interval=1d'%sym.replace('^','%5E'))
    if not b: return None
    try:
        r=json.loads(b)['chart']['result'][0]; m=r['meta']
        cl=[c for c in r['indicators']['quote'][0]['close'] if c is not None]
        px=m['regularMarketPrice']; prev=cl[-2] if len(cl)>1 else px
        return dict(price=px,chg=px-prev,pct=(px-prev)/prev*100 if prev else 0,hist=cl[-60:],cur=m.get('currency',''),src='Yahoo Finance')
    except Exception as e: print('YF',sym,e); return None
def coingecko(cid):
    p=get('https://api.coingecko.com/api/v3/simple/price?ids=%s&vs_currencies=usd&include_24hr_change=true'%cid)
    h=get('https://api.coingecko.com/api/v3/coins/%s/market_chart?vs_currency=usd&days=90&interval=daily'%cid)
    try:
        d=json.loads(p)[cid]; px=d['usd']; pct=d.get('usd_24h_change',0)
        hist=[x[1] for x in json.loads(h).get('prices',[])][-60:] if h else []
        prev=px/(1+pct/100) if pct else (hist[-2] if len(hist)>1 else px)
        return dict(price=px,chg=px-prev,pct=pct,hist=hist,cur='USD',src='CoinGecko')
    except Exception as e: print('CG',cid,e); return None
_tdwin=[0.0,0]  # [Fenster-Start, verbrauchte Credits] - Free-Tier: 8 Credits/Minute
def td_batch(kind,params,credits):
    """kind: 'quote' oder 'time_series'; wartet bis das Credit-Fenster Platz hat"""
    now=time.time()
    if now-_tdwin[0]>=60: _tdwin[0]=now; _tdwin[1]=0
    if _tdwin[1]+credits>8:
        w=61-(time.time()-_tdwin[0])
        if w>0: time.sleep(w)
        _tdwin[0]=time.time(); _tdwin[1]=0
    b=get('https://api.twelvedata.com/%s?apikey=%s&%s'%(kind,TD_KEY,params))
    _tdwin[1]+=credits
    if not b: return {}
    try: return json.loads(b)
    except Exception as e: print('TD',kind,e); return {}
q=[]; srcs=set()
if TD_KEY:
    # Twelve Data: Quotes und Tageshistorie gebuendelt (Batch), Rest faellt auf Yahoo zurueck
    tdmap={s[3]:(s[0],s[4]) for s in SYM if s[3]}
    syms=list(tdmap)
    quotes={}
    for i in range(0,len(syms),8):
        chunk=syms[i:i+8]
        params='symbol=%s'%','.join(chunk)
        # Exchange pro Symbol einzeln noetig; XETRA-Titel separat
        de=[c for c in chunk if tdmap[c][1]]; other=[c for c in chunk if not tdmap[c][1]]
        if other:
            r=td_batch('quote','symbol=%s'%','.join(other),len(other))
            if isinstance(r,dict):
                if 'close' in r: quotes[r.get('symbol')]=r
                else:
                    for k,v in r.items():
                        if isinstance(v,dict) and 'close' in v: quotes[k]=v
        for c in de:
            r=td_batch('quote','symbol=%s&exchange=%s'%(c,tdmap[c][1]),1)
            if isinstance(r,dict) and 'close' in r: quotes[c]=r
    for i in range(0,len(syms),8):
        chunk=syms[i:i+8]
        de=[c for c in chunk if tdmap[c][1]]; other=[c for c in chunk if not tdmap[c][1]]
        groups=[('symbol=%s&interval=1day&outputsize=60&order=ASC'%','.join(other),other)] if other else []
        groups+=[('symbol=%s&exchange=%s&interval=1day&outputsize=60&order=ASC'%(c,tdmap[c][1]),[c]) for c in de]
        for params,members in groups:
            r=td_batch('time_series',params,len(members))
            if not isinstance(r,dict): continue
            def hist_of(v):
                try: return [float(x['close']) for x in v['values']][-60:]
                except: return []
            if 'values' in r:
                key=r.get('meta',{}).get('symbol',members[0])
                h=hist_of(r)
                if key in quotes and h: quotes[key]['_hist']=h
            else:
                for k,v in r.items():
                    if isinstance(v,dict) and 'values' in v:
                        h=hist_of(v)
                        if k in quotes and h: quotes[k]['_hist']=h
    for sym,name,grp,tds,ex,cg in SYM:
        if cg: continue
        d=None
        if tds and tds in quotes:
            r=quotes[tds]
            try:
                px=float(r['close']); prev=float(r.get('previous_close') or px)
                h=r.get('_hist') or []
                d=dict(price=px,chg=px-prev,pct=(px-prev)/prev*100 if prev else 0,hist=h,cur=r.get('currency',''),src='Twelve Data')
            except Exception as e: print('TD parse',tds,e)
        if not d or not d['hist']:
            y=yahoo(sym)
            if y:
                if d and not d['hist'] and y['hist']: d['hist']=y['hist']
                elif not d: d=y
        if d:
            srcs.add(d['src']); q.append(dict(sym=sym,name=name,grp=grp,cur=d['cur'],price=d['price'],chg=d['chg'],pct=d['pct'],hist=d['hist'],src=d['src'],fetched_at=datetime.datetime.now(ZoneInfo('Europe/Berlin')).strftime('%d.%m.%Y %H:%M')))
else:
    for sym,name,grp,tds,ex,cg in SYM:
        if cg: continue
        d=yahoo(sym)
        if d: srcs.add('Yahoo Finance'); q.append(dict(sym=sym,name=name,grp=grp,cur=d['cur'],price=d['price'],chg=d['chg'],pct=d['pct'],hist=d['hist'],src=d['src'],fetched_at=datetime.datetime.now(ZoneInfo('Europe/Berlin')).strftime('%d.%m.%Y %H:%M')))
# Krypto: CoinGecko primaer (oeffentliche Anzeige mit Attribution erlaubt), Yahoo als Fallback
for sym,name,grp,tds,ex,cg in SYM:
    if not cg: continue
    d=coingecko(cg) or yahoo(sym)
    if d:
        srcs.add(d['src']); q.append(dict(sym=sym,name=name,grp=grp,cur=d['cur'],price=d['price'],chg=d['chg'],pct=d['pct'],hist=d['hist'],src=d['src'],fetched_at=datetime.datetime.now(ZoneInfo('Europe/Berlin')).strftime('%d.%m.%Y %H:%M')))
json.dump(q,open('../data/quotes.json','w'))
print(len(fin),'news;',len(q),'quotes;',sorted(srcs))
