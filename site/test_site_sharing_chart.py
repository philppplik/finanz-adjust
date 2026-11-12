import sys,unittest,json,tempfile,re
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'tools'))
from page_sharing import add_page_sharing
from share import share_block
from stock_fallback import chart
from broker import build_broker
from stocks import build_stock_pages
from lernpfade import build_lernpfade

class FeatureTests(unittest.TestCase):
    def test_passive_canonical_sharing(self):
        for path in ['/broker/','/broker/comdirect/','/aktien/','/aktien/ttwo/','/lernpfade/','/lernpfade/test/']:
            h=add_page_sharing(path,'Title & test | finanz adjust','<main><h1>Title</h1><p>Intro</p></main>','https://finanz-adjust.de')
            self.assertEqual(h.count('aria-label="Seite teilen"'),1)
            self.assertIn('data-copy="https://finanz-adjust.de'+path+'"',h)
            self.assertNotIn('<iframe',h);self.assertNotIn('src="https:',h)
            self.assertIn('rel="noopener noreferrer nofollow"',h)
        self.assertEqual(add_page_sharing('/artikel/x/','x','<h1>x</h1>','https://a'),'<h1>x</h1>')
        self.assertIn('Artikel teilen',share_block('https://example.com','A & "B"','fa'))
        self.assertIn('A &amp; &quot;B&quot;',share_block('https://example.com','A & "B"','fa'))
    def test_chart_consent_and_validation(self):
        s=dict(tv_symbol='NASDAQ:TTWO',exchange='Nasdaq',currency='USD')
        h=chart(s)
        for x in ['id="chart"','data-tv-widget="advanced-chart"','data-tv-symbol="NASDAQ:TTWO"','data-tv-load','Noch nicht geladen']:
            self.assertIn(x,h)
        for x in ['<script','<iframe','s3.tradingview.com','preconnect']:self.assertNotIn(x,h)
        self.assertEqual(chart({**s,'tv_symbol':'BAD<script>'}),'')
    def test_broker_links_only_details(self):
        pages={}
        def page(path,title,desc,body,*a,**kw):pages[path]=body;return path
        with tempfile.TemporaryDirectory() as d:build_broker(page,[],d,'https://finanz-adjust.de')
        from html.parser import HTMLParser
        class Links(HTMLParser):
            def __init__(self):super().__init__();self.hrefs=[]
            def handle_starttag(self,t,a):
                if t=='a':self.hrefs.append(dict(a).get('href',''))
        p=Links();p.feed(pages['/broker/'])
        self.assertFalse(any(x.startswith('https:') for x in p.hrefs))
        self.assertIn('Anbieter-Seite',pages['/broker/comdirect/'])
        self.assertIn('Preise und Konditionen',pages['/broker/comdirect/'])
        self.assertIn('<h1>comdirect</h1>',pages['/broker/comdirect/'])
    def test_yahoo_range_baseline_not_prior_close(self):
        import time
        from stock_data import parse_yahoo,render_quote
        s=dict(slug='ttwo',ticker='TTWO',exchange='Nasdaq',currency='USD')
        meta=dict(symbol='TTWO',exchangeName='NMS',currency='USD',regularMarketPrice=231.31,regularMarketTime=int(time.time()),chartPreviousClose=208.90,regularMarketChangePercent=2.969)
        q=parse_yahoo({'chart':{'result':[{'meta':meta}]}},s,'TTWO')
        self.assertNotIn('previous_close',q);self.assertNotIn('change',q)
        legacy={**q,'previous_close':208.90,'change':22.41}
        self.assertNotIn('Vortagesschluss',render_quote(legacy,s))
        meta['previousClose']=224.64
        q=parse_yahoo({'chart':{'result':[{'meta':meta}]}},s,'TTWO')
        self.assertEqual(q['previous_close'],224.64)
        self.assertAlmostEqual(q['change'],6.67)
        self.assertIn('Vortagesschluss',render_quote(q,s))
    def test_ttwp_chart_even_with_valid_quote(self):
        pages={}
        def page(path,title,desc,body,*a,**kw):pages[path]=body;return path
        with tempfile.TemporaryDirectory() as d, patch('stock_data.refresh',return_value={'ttwo':{'x':1}}),patch('stock_data.render_quote',return_value='<section id="kurs">Sourced valid quote</section>'):
            build_stock_pages(page,[],[],d,'https://finanz-adjust.de')
        self.assertIn('Sourced valid quote',pages['/aktien/ttwo/'])
        self.assertIn('data-tv-widget="advanced-chart"',pages['/aktien/ttwo/'])
        self.assertIn('NASDAQ:TTWO',pages['/aktien/ttwo/'])

if __name__=='__main__':unittest.main()
