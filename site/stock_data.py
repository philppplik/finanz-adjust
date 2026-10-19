"""Provider boundary for equity quotes. Server-side only; never exposes API keys.

The build opts in through STOCK_QUOTES_ENABLED=1. This is an owner deployment
choice, not a claim that the provider granted redistribution rights.
"""
import datetime as dt
import json
import math
import os
from pathlib import Path
import time
import urllib.parse
import urllib.request

class TwelveData:
    name = 'Twelve Data'
    source_url = 'https://twelvedata.com/'
    def __init__(self, key):
        self.key = key
        self.calls = 0
        self.window = time.monotonic()
    def quote(self, stock):
        if self.calls >= 8:
            time.sleep(max(0, 61-(time.monotonic()-self.window)))
            self.calls, self.window = 0, time.monotonic()
        params = urllib.parse.urlencode({'symbol':stock['ticker'], 'exchange':stock['exchange'], 'apikey':self.key})
        self.calls += 1
        try:
            req=urllib.request.Request('https://api.twelvedata.com/quote?'+params,headers={'User-Agent':'FinanzAdjust/1.0'})
            with urllib.request.urlopen(req,timeout=15) as response: raw=json.load(response)
        except Exception:
            # Never log request URLs: they contain the key.
            return None
        return parse_quote(raw, stock)

def parse_quote(raw, stock):
    """Reject provider errors, cross-exchange matches, currency mismatches, bad timestamps."""
    try:
        if raw.get('status') == 'error': return None
        if raw['symbol'].upper() != stock['ticker'].upper(): return None
        if raw['exchange'].lower() != stock['exchange'].lower(): return None
        if raw['currency'] != stock['currency']: return None
        price=float(raw['close'])
        if not math.isfinite(price) or price<=0: return None
        timestamp=int(raw['timestamp'])
        now=int(time.time())
        if timestamp<=0 or timestamp>now+300: return None
        quote={'price':price,'currency':raw['currency'],'exchange':raw['exchange'],
               'timestamp':timestamp,'source':'Twelve Data','source_url':'https://twelvedata.com/',
               'fetched_at':now,'delay':'Vom Anbieter nicht ausgewiesen; kein Echtzeitversprechen',
               'symbol':stock['ticker']}
        for field in ('change','percent_change','open','high','low','previous_close','volume'):
            try:
                value=float(raw[field])
                if math.isfinite(value): quote[field]=value
            except (KeyError,ValueError,TypeError): pass
        return quote
    except (KeyError,ValueError,TypeError): return None

def refresh(stocks, cache_path, provider=None, now=None, ttl=10800, max_calls=16):
    """Bounded build-time refresh; no traffic-dependent API calls. Preserve dated stale data."""
    now=int(time.time()) if now is None else now
    path=Path(cache_path)
    if os.getenv('STOCK_QUOTES_ENABLED') != '1':
        return {}  # Explicit operational kill switch, including cached output.
    try: cache=json.loads(path.read_text())
    except (OSError,ValueError): cache={}
    if provider is None:
        key=os.getenv('TWELVEDATA_API_KEY','').strip()
        if not key: return cache
        provider=TwelveData(key)
    candidates=sorted(stocks,key=lambda s:cache.get(s['slug'],{}).get('fetched_at',0))
    calls=0
    for stock in candidates:
        old=cache.get(stock['slug'],{})
        if now-old.get('fetched_at',0)<ttl:continue
        if calls>=max_calls: break
        calls+=1
        result=provider.quote(stock)
        if result: cache[stock['slug']]=result
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(cache,ensure_ascii=False));tmp.replace(path)
    return cache

def render_quote(quote, stock):
    from html import escape as e
    if not quote:return None
    # Cache is data, not authority: validate the fields again before display.
    if quote.get('exchange','').lower()!=stock['exchange'].lower() or quote.get('currency')!=stock['currency'] or quote.get('symbol')!=stock['ticker']:return None
    try:
        price=float(quote['price']);timestamp=int(quote['timestamp']);fetched=int(quote['fetched_at'])
        if not math.isfinite(price) or price<=0 or timestamp<=0 or timestamp>time.time()+300:return None
    except (KeyError,ValueError,TypeError): return None
    formatted=f'{price:,.2f}'.replace(',','X').replace('.',',').replace('X','.')
    stamp=dt.datetime.fromtimestamp(timestamp,dt.timezone.utc).strftime('%d.%m.%Y %H:%M UTC')
    fetched_stamp=dt.datetime.fromtimestamp(fetched,dt.timezone.utc).strftime('%d.%m.%Y %H:%M UTC')
    stale=time.time()-fetched>21600
    details=''
    for key,label in [('open','Eröffnung'),('high','Tageshoch'),('low','Tagestief'),('previous_close','Vortagesschluss'),('volume','Volumen')]:
        if key in quote:details+='<div><dt>'+label+'</dt><dd>'+e(str(quote[key]))+'</dd></div>'
    return '<section id="kurs" class="stock-quote"><p class="stock-kicker">LETZTER VERFÜGBARER KURS'+(' · ÄLTERER CACHE' if stale else '')+'</p><h2>'+formatted+' '+e(quote['currency'])+'</h2><dl><div><dt>Kurszeit</dt><dd>'+stamp+'</dd></div><div><dt>Handelsplatz</dt><dd>'+e(stock['exchange'])+'</dd></div></dl><p class="stock-note">Verzögerung: '+e(quote.get('delay','Nicht ausgewiesen'))+'. Abruf: '+fetched_stamp+'. Keine Live-Aktualisierung im Browser.</p><dl class="stock-facts">'+details+'</dl><p><a class="stock-source" href="https://twelvedata.com/" rel="noopener" target="_blank">Kursdaten: Twelve Data</a></p></section>'
