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


# Yahoo-Finance-Boersencodes, die zu unseren Stammdaten-Handelsplaetzen passen.
# Kein stiller Handelsplatz- oder Waehrungswechsel: alles andere wird verworfen.
YAHOO_EXCHANGE = {'Xetra': ('GER',), 'Nasdaq': ('NMS',), 'NYSE': ('NYQ',)}

def yahoo_symbol(stock):
    """Yahoo-Notation: US-Ticker unveraendert, Xetra mit .DE-Suffix."""
    if stock['exchange'] == 'Xetra':
        return stock['ticker'] + '.DE'
    return stock['ticker']

# Anbieterauskunft zur Verzoegerung (Yahoo-Hilfeseite, geprueft 28.10.2026):
# Xetra/GER 15 Minuten. US-Notierungen: nicht pauschal ausgewiesen.
YAHOO_DELAY = {'Xetra': '15 Minuten (Anbieterangabe)'}

class Yahoo:
    """Yahoo Finance chart-Schnittstelle ohne Schluessel, als Fallback hinter Twelve Data.

    Vom Eigentuemer am 18.10.2026 ausdruecklich als Fallback gewuenscht und am
    19.10.2026 trotz bekannter Anzeigebeschraenkungen freigegeben (siehe STOCKS.md).
    Oeffentliche Anzeige bleibt vertraglich ungeklaert; das ist eine bewusste
    Eigentuemer-Entscheidung, keine erteilte Lizenz.
    """
    name = 'Yahoo Finance'
    source_url = 'https://finance.yahoo.com/'
    def __init__(self, min_interval=0.5):
        self.min_interval = min_interval
        self.last = 0.0
        self.blocked = False
    def quote(self, stock):
        if self.blocked or stock['exchange'] not in YAHOO_EXCHANGE:
            return None
        wait = self.min_interval - (time.monotonic() - self.last)
        if wait > 0:
            time.sleep(wait)
        self.last = time.monotonic()
        symbol = yahoo_symbol(stock)
        url = ('https://query1.finance.yahoo.com/v8/finance/chart/'
               + urllib.parse.quote(symbol) + '?range=5d&interval=1d')
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; FinanzAdjust/1.0)'})
            with urllib.request.urlopen(req, timeout=15) as response:
                raw = json.load(response)
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 999):
                self.blocked = True  # Rate-Limit: fuer diesen Build keine weiteren Yahoo-Abrufe
            return None
        except Exception:
            return None
        return parse_yahoo(raw, stock, symbol)

def parse_yahoo(raw, stock, symbol):
    """Gleiche Strenge wie parse_quote: Symbol-, Handelsplatz- und Waehrungsabgleich."""
    try:
        meta = raw['chart']['result'][0]['meta']
        if meta.get('symbol', '').upper() != symbol.upper(): return None
        if meta.get('exchangeName') not in YAHOO_EXCHANGE[stock['exchange']]: return None
        if meta.get('currency') != stock['currency']: return None
        if meta.get('instrumentType', 'EQUITY') != 'EQUITY': return None
        price = float(meta['regularMarketPrice'])
        if not math.isfinite(price) or price <= 0: return None
        timestamp = int(meta['regularMarketTime'])
        now = int(time.time())
        if timestamp <= 0 or timestamp > now + 300: return None
        quote = {'price': price, 'currency': meta['currency'], 'exchange': stock['exchange'],
                 'timestamp': timestamp, 'source': 'Yahoo Finance',
                 'source_url': 'https://finance.yahoo.com/',
                 'fetched_at': now,
                 'delay': YAHOO_DELAY.get(stock['exchange'], 'Vom Anbieter nicht ausgewiesen; kein Echtzeitversprechen'),
                 'symbol': stock['ticker']}
        optional = {'high': 'regularMarketDayHigh', 'low': 'regularMarketDayLow',
                    'previous_close': 'chartPreviousClose', 'volume': 'regularMarketVolume',
                    'percent_change': 'regularMarketChangePercent'}
        for field, key in optional.items():
            try:
                value = float(meta[key])
                if math.isfinite(value): quote[field] = value
            except (KeyError, ValueError, TypeError): pass
        try:
            value = float(raw['chart']['result'][0]['indicators']['quote'][0]['open'][-1])
            if math.isfinite(value): quote['open'] = value
        except (KeyError, ValueError, TypeError, IndexError): pass
        if 'previous_close' in quote:
            quote['change'] = price - quote['previous_close']
        return quote
    except (KeyError, ValueError, TypeError, IndexError): return None

def refresh(stocks, cache_path, provider=None, now=None, ttl=10800, max_calls=16, max_fallback_calls=48):
    """Bounded build-time refresh; no traffic-dependent API calls. Preserve dated stale data.

    Provider-Kette: Twelve Data (nur api_enabled-Titel, Credit-Budget max_calls),
    danach Yahoo Finance als kostenloser Fallback (eigenes Budget max_fallback_calls).
    """
    now=int(time.time()) if now is None else now
    path=Path(cache_path)
    if os.getenv('STOCK_QUOTES_ENABLED') != '1':
        return {}  # Explicit operational kill switch, including cached output.
    try: cache=json.loads(path.read_text())
    except (OSError,ValueError): cache={}
    if provider is None:
        providers=[]
        key=os.getenv('TWELVEDATA_API_KEY','').strip()
        if key: providers.append(TwelveData(key))
        providers.append(Yahoo())
    elif isinstance(provider,(list,tuple)):
        providers=list(provider)
    else:
        providers=[provider]
    if not providers: return cache
    attempt_path=path.with_name('stock-quote-attempts.json')
    try: attempts=json.loads(attempt_path.read_text())
    except (OSError,ValueError): attempts={}
    candidates=sorted([s for s in stocks if s.get('api_enabled', True) or any(not isinstance(p, TwelveData) for p in providers)],key=lambda s:max(cache.get(s['slug'],{}).get('fetched_at',0),attempts.get(s['slug'],0)))
    calls={}
    def budget(p):
        return max_fallback_calls if isinstance(p, Yahoo) else max_calls
    def usable(p, stock):
        if isinstance(p, TwelveData) and not stock.get('api_enabled', True): return False
        return calls.get(id(p),0) < budget(p)
    for stock in candidates:
        old=cache.get(stock['slug'],{})
        if now-old.get('fetched_at',0)<ttl:continue
        available=[p for p in providers if usable(p,stock)]
        if not available: continue  # getrennte Budgets: erschöpfter Fallback blockiert nicht die Primaer-API
        attempts[stock['slug']]=now
        for p in available:
            calls[id(p)]=calls.get(id(p),0)+1
            result=p.quote(stock)
            if result:
                cache[stock['slug']]=result
                break
    path.parent.mkdir(parents=True,exist_ok=True)
    attempt_path.write_text(json.dumps(attempts))
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(cache,ensure_ascii=False));tmp.replace(path)
    return cache

def format_number(value, decimals=2):
    """German display format, independent of the build machine locale."""
    number=float(value)
    if not math.isfinite(number): raise ValueError("non-finite quote field")
    return f"{number:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")

def render_quote(quote, stock):
    from html import escape as e
    if not quote:return None
    # Cache is data, not authority: validate the fields again before display.
    if quote.get('exchange','').lower()!=stock['exchange'].lower() or quote.get('currency')!=stock['currency'] or quote.get('symbol')!=stock['ticker']:return None
    try:
        price=float(quote['price']);timestamp=int(quote['timestamp']);fetched=int(quote['fetched_at'])
        if not math.isfinite(price) or price<=0 or timestamp<=0 or timestamp>time.time()+300:return None
    except (KeyError,ValueError,TypeError): return None
    formatted=format_number(price)
    stamp=dt.datetime.fromtimestamp(timestamp,dt.timezone.utc).strftime('%d.%m.%Y %H:%M UTC')
    fetched_stamp=dt.datetime.fromtimestamp(fetched,dt.timezone.utc).strftime('%d.%m.%Y %H:%M UTC')
    stale=time.time()-fetched>21600
    details=''
    for key,label in [('open','Eröffnung'),('high','Tageshoch'),('low','Tagestief'),('previous_close','Vortagesschluss'),('volume','Volumen')]:
        if key not in quote: continue
        try: value=format_number(quote[key],0 if key=='volume' else 2)
        except (ValueError,TypeError,OverflowError): continue
        details+='<div><dt>'+label+'</dt><dd>'+e(value)+'</dd></div>'
    return '<section id="kurs" class="stock-quote"><p class="stock-kicker">LETZTER VERFÜGBARER KURS'+(' · ÄLTERER CACHE' if stale else '')+'</p><h2>'+formatted+' '+e(quote['currency'])+'</h2><dl><div><dt>Kurszeit</dt><dd>'+stamp+'</dd></div><div><dt>Handelsplatz</dt><dd>'+e(stock['exchange'])+'</dd></div></dl><p class="stock-note">Verzögerung: '+e(quote.get('delay','Nicht ausgewiesen'))+'. Abruf: '+fetched_stamp+'. Keine Live-Aktualisierung im Browser.</p><dl class="stock-facts">'+details+'</dl><p><a class="stock-source" href="'+e(quote.get('source_url','https://twelvedata.com/'),quote=True)+'" rel="noopener" target="_blank">Kursdaten: '+e(quote.get('source','Twelve Data'))+'</a></p></section>'
