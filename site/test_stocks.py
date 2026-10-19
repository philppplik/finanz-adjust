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
if __name__=='__main__':unittest.main()
