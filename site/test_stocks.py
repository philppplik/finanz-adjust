import json, os, tempfile, time, unittest
from pathlib import Path
from unittest.mock import patch
from stock_data import parse_quote, refresh, render_quote, format_number
from stocks import related
class StocksTest(unittest.TestCase):
    def setUp(self):
        self.s=dict(slug='apple',name='Apple',ticker='AAPL',exchange='Nasdaq',currency='USD',aliases=['Apple Inc.'])
        self.raw=dict(symbol='AAPL',exchange='NASDAQ',currency='USD',close='123.45',timestamp=int(time.time()),change='1',percent_change='0.8')
    def test_quote(self):
        q=parse_quote(self.raw,self.s);self.assertEqual(q['price'],123.45);self.assertIn('123,45 USD',render_quote(q,self.s))
    def test_german_numbers(self):
        self.assertEqual(format_number(346.089996),'346,09')
        self.assertEqual(format_number(1234567.899),'1.234.567,90')
        self.assertEqual(format_number(1234567,0),'1.234.567')
        self.assertEqual(format_number(-1234.567),'-1.234,57')
    def test_all_rendered_fields(self):
        q=parse_quote({**self.raw,'open':'346.089996','high':'1500.456','low':'320.1234','previous_close':'340.999','volume':'1234567'},self.s)
        html=render_quote(q,self.s)
        for value in ['123,45 USD','346,09','1.500,46','320,12','341,00','1.234.567']:
            self.assertIn(value,html)
        q['open']='NaN';q['high']='invalid';q['low']=None
        html=render_quote(q,self.s)
        self.assertNotIn('NaN',html);self.assertNotIn('invalid',html)
    def test_reject_bad_data(self):
        for field,value in [('symbol','MSFT'),('exchange','XETRA'),('currency','EUR'),('close','NaN'),('close','0'),('timestamp',0),('timestamp',time.time()+99999)]:
            self.assertIsNone(parse_quote({**self.raw,field:value},self.s))
    def test_default_off(self):
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ,{},clear=True):
            p=Path(d)/'cache.json';p.write_text(json.dumps({'apple':parse_quote(self.raw,self.s)}))
            self.assertEqual(refresh([self.s],p),{})
    def test_cache_and_failed_fetch(self):
        class Provider:
            calls=0
            def quote(self,s):self.calls+=1;return None
        pvd=Provider()
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ,{'STOCK_QUOTES_ENABLED':'1'}):
            p=Path(d)/'cache.json';old=parse_quote(self.raw,self.s);p.write_text(json.dumps({'apple':old}))
            self.assertEqual(refresh([self.s],p,pvd)['apple']['price'],123.45);self.assertEqual(pvd.calls,0)
            self.assertEqual(refresh([self.s],p,pvd,now=int(time.time())+20000)['apple']['price'],123.45);self.assertEqual(pvd.calls,1)
    def test_budget(self):
        class Provider:
            calls=0
            def quote(self,s):self.calls+=1;return None
        pvd=Provider()
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ,{'STOCK_QUOTES_ENABLED':'1'}):
            refresh([{**self.s,'slug':str(n)} for n in range(50)],Path(d)/'q',pvd,max_calls=3)
            self.assertEqual(pvd.calls,3)
    def test_article_boundaries(self):
        self.assertEqual(len(related(self.s,[{'title':'Apple Aktie'},{'title':'Pineapple test'}])),1)
    def test_widget_consent_and_mapping(self):
        from stock_fallback import fallback
        html=fallback({**self.s,'tv_symbol':'NASDAQ:AAPL'})
        self.assertIn('data-tv-load',html)
        self.assertNotIn('<iframe',html)
        self.assertNotIn('s3.tradingview.com',html)
        self.assertEqual(fallback({**self.s,'tv_symbol':'bad<script>'}),'')
    def test_failed_attempt_rotation(self):
        class Provider:
            symbols=[]
            def quote(self,s):self.symbols.append(s['slug']);return None
        pvd=Provider()
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ,{'STOCK_QUOTES_ENABLED':'1'}):
            stocks=[{**self.s,'slug':str(n)} for n in range(4)]
            path=Path(d)/'quotes.json'
            refresh(stocks,path,pvd,now=100000,max_calls=2)
            refresh(stocks,path,pvd,now=100001,max_calls=2)
            self.assertEqual(pvd.symbols,['0','1','2','3'])
    def test_catalogue(self):
        rows=json.loads(Path('stocks.json').read_text());self.assertGreaterEqual(len(rows),190)
        self.assertEqual(len({r['slug'] for r in rows}),len(rows))
        self.assertEqual(len({(r['ticker'],r['exchange']) for r in rows}),len(rows))
        self.assertTrue(all(r.get('tv_symbol') for r in rows))

    def xetra(self):
        return dict(slug='sap',name='SAP',ticker='SAP',exchange='Xetra',currency='EUR',aliases=['SAP'],api_enabled=False)
    def yahoo_raw(self, **meta):
        m=dict(symbol='SAP.DE',exchangeName='GER',currency='EUR',instrumentType='EQUITY',
               regularMarketPrice=213.15,regularMarketTime=int(time.time()),
               regularMarketDayHigh=215.25,regularMarketDayLow=211.7,chartPreviousClose=212.0,
               regularMarketVolume=1762,regularMarketChangePercent=0.54)
        m.update(meta)
        return {'chart':{'result':[{'meta':m,'indicators':{'quote':[{'open':[212.75]}]}}]}}
    def test_yahoo_parse(self):
        from stock_data import parse_yahoo, yahoo_symbol
        s=self.xetra()
        q=parse_yahoo(self.yahoo_raw(),s,yahoo_symbol(s))
        self.assertEqual(q['price'],213.15);self.assertEqual(q['source'],'Yahoo Finance')
        self.assertEqual(q['exchange'],'Xetra');self.assertEqual(q['currency'],'EUR')
        self.assertEqual(q['delay'],'15 Minuten (Anbieterangabe)')
        self.assertAlmostEqual(q['change'],1.15)
        html=render_quote(q,s)
        self.assertIn('213,15 EUR',html);self.assertIn('finance.yahoo.com',html)
        self.assertIn('Kursdaten: Yahoo Finance',html);self.assertNotIn('Twelve Data',html)
        self.assertIn('15 Minuten (Anbieterangabe)',html)
    def test_yahoo_reject_wrong_exchange_currency_symbol(self):
        from stock_data import parse_yahoo, yahoo_symbol
        s=self.xetra();sym=yahoo_symbol(s)
        for meta in [dict(exchangeName='NYQ'),dict(currency='USD'),dict(symbol='SAP'),
                     dict(regularMarketPrice=0),dict(regularMarketPrice=float('nan')),
                     dict(regularMarketTime=0),dict(regularMarketTime=int(time.time())+99999),
                     dict(instrumentType='ETF')]:
            self.assertIsNone(parse_yahoo(self.yahoo_raw(**meta),s,sym),meta)
    def test_yahoo_symbol_mapping(self):
        from stock_data import yahoo_symbol
        self.assertEqual(yahoo_symbol(self.xetra()),'SAP.DE')
        self.assertEqual(yahoo_symbol(self.s),'AAPL')
        self.assertEqual(yahoo_symbol(dict(ticker='BRK-B',exchange='NYSE')),'BRK-B')
    def test_fallback_chain_and_api_gate(self):
        from stock_data import TwelveData, Yahoo
        class TD(TwelveData):
            def __init__(self): self.seen=[]
            def quote(self,s): self.seen.append(s['slug']); return None
        raw=self.raw; base=self.s
        class YF(Yahoo):
            def __init__(self): self.seen=[]
            def quote(self,s):
                self.seen.append(s['slug'])
                return parse_quote(raw,{**base,'slug':s['slug']})
        td,yf=TD(),YF()
        xetra=self.xetra()
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ,{'STOCK_QUOTES_ENABLED':'1'}):
            cache=refresh([self.s,xetra],Path(d)/'q',[td,yf])
            self.assertEqual(td.seen,['apple'])       # Twelve Data ueberspringt api_enabled=False
            self.assertEqual(sorted(yf.seen),['apple','sap'])  # Yahoo faengt beide auf
            self.assertEqual(cache['sap']['price'],123.45)
            self.assertIn('apple',cache)
    def test_yahoo_budget_separate(self):
        from stock_data import Yahoo
        class YF(Yahoo):
            calls=0
            def quote(self,s): self.calls+=1; return None
        class TD2:
            calls=0
            def quote(self,s): self.calls+=1; return None
        yf,td=YF(),TD2()
        stocks=[{**self.s,'slug':str(n)} for n in range(10)]
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ,{'STOCK_QUOTES_ENABLED':'1'}):
            refresh(stocks,Path(d)/'q',[td,yf],max_calls=3,max_fallback_calls=2)
            self.assertEqual(td.calls,3);self.assertEqual(yf.calls,2)
    def test_catalogue_xetra_stays_api_disabled(self):
        rows=json.loads(Path('stocks.json').read_text())
        xe=[r for r in rows if r['exchange']=='Xetra']
        self.assertGreaterEqual(len(xe),60)
        self.assertTrue(all(r.get('api_enabled') is False for r in xe))
if __name__=='__main__':unittest.main()
