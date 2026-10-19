import json, os, tempfile, time, unittest
from pathlib import Path
from unittest.mock import patch
from stock_data import parse_quote, refresh, render_quote
from stocks import related
class StocksTest(unittest.TestCase):
    def setUp(self):
        self.s=dict(slug='apple',name='Apple',ticker='AAPL',exchange='Nasdaq',currency='USD',aliases=['Apple Inc.'])
        self.raw=dict(symbol='AAPL',exchange='NASDAQ',currency='USD',close='123.45',timestamp=int(time.time()),change='1',percent_change='0.8')
    def test_quote(self):
        q=parse_quote(self.raw,self.s);self.assertEqual(q['price'],123.45);self.assertIn('123,45 USD',render_quote(q,self.s))
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
    def test_catalogue(self):
        rows=json.loads(Path('stocks.json').read_text());self.assertEqual(len(rows),34)
        self.assertEqual(len({r['slug'] for r in rows}),len(rows))
if __name__=='__main__':unittest.main()
