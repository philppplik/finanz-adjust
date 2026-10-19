import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import news_detail as d

class DetailTests(unittest.TestCase):
    def item(self, url='https://www.finanznachrichten.de/nachrichten/2026-10/a.htm', **kw):
        return dict(url=url,title='DAX und Inflation: <Test> & Zinsen',ts=1792400790,sum='DO NOT REPRINT THIS TEASER',src='GDELT',**kw)
    def test_no_teasers(self):
        self.assertFalse(d.TEASER_SOURCES)
        self.assertNotIn('DO NOT REPRINT',d.content(self.item(),[]))
    def test_block_sources(self):
        for host in ('cnn.com','fool.com','tagesschau.de','www.tagesschau.de','unknown.example','finanznachrichten.de.evil.example'):
            with self.assertRaises(ValueError):d.content(self.item('https://'+host+'/a'),[])
        with self.assertRaises(ValueError):d.content(self.item('javascript:alert(1)'),[])
    def test_safe_path(self):
        a=self.item();b=dict(a,url=a['url']+'?another=1')
        self.assertRegex(d.detail_path(a),r'^/nachrichten/[a-z0-9-]+-[a-f0-9]{12}/$')
        self.assertNotEqual(d.detail_path(a),d.detail_path(b))
        self.assertEqual(d.detail_path(a),d.detail_path(a))
    def test_escape_and_external_link(self):
        s=d.content(self.item(),[])
        self.assertIn('&lt;Test&gt; &amp;',s)
        self.assertNotIn('<Test>',s)
        self.assertIn('rel="noopener noreferrer nofollow"',s)
        self.assertIn('target="_blank"',s)
        self.assertLess(s.index('Original bei'),s.index('nd-report'))
        self.assertLess(s.index('Original bei'),s.index('nd-ad'))
        self.assertEqual(s.count('Original bei'),2)
        self.assertNotIn('<script',s)
        self.assertNotIn('<iframe',s)
    def test_external_notice_without_permission_copy(self):
        s=d.content(self.item(),[])
        self.assertIn('nd-leaving',s)
        self.assertIn('Beim Klick auf den Original-Link verlässt du finanz adjust',s)
        self.assertIn('<strong>finanznachrichten.de</strong>',s)
        self.assertIn('neuen Tab',s)
        self.assertNotIn('Hier zeigen wir nur die Überschrift',s)
        self.assertNotIn('Nutzungsfreigabe',s)
        self.assertLess(s.index('nd-leaving'),s.index('class="nd-original"'))
        self.assertEqual(s.count('nd-leaving'),1)
        self.assertNotIn('DO NOT REPRINT',s)

    def test_ad_placeholder_only(self):
        s=d.content(self.item(),[])
        self.assertIn('Anzeige · Platzhalter',s)
        self.assertIn('Hier wird keine Werbung geladen.',s)
        self.assertNotIn('adsbygoogle',s)
    def test_related_terms(self):
        g=[dict(term='DAX',slug='dax',short='Index',aliases=[]),dict(term='Aktie',slug='aktie',short='Anteil',aliases=[])]
        self.assertEqual(d.related_terms(self.item(),g),g[:1])
        self.assertIn('/glossar/dax/',d.content(self.item(),g))
    def test_routing(self):
        from news_policy import destination, has_detail
        a=self.item();self.assertTrue(has_detail(a));self.assertEqual(destination(a),d.detail_path(a))
        for host in ('cnn.com','fool.com','finanzen.net','deutschlandfunk.de'):
            a=self.item('https://'+host+'/x');self.assertFalse(has_detail(a));self.assertEqual(destination(a),a['url'])
    def test_build_output(self):
        root=Path('out')
        if not (root/'sitemap.xml').is_file():self.skipTest('Run build.py first')
        n=json.loads(Path('../data/fin_archive.json').read_text())
        pages=[i for i in n if d.has_detail(i)]
        self.assertTrue(pages)
        for i in pages:
            path=d.detail_path(i);s=(root/path.strip('/')/'index.html').read_text()
            self.assertIn('noindex,follow',s);self.assertNotIn('rel="canonical"',s)
            self.assertIn('data-fa-consent-open',s)
            self.assertNotIn('NewsArticle',s)
            self.assertIn('nd-ad" hidden',s)
            self.assertIn('nd-leaving',s)
            self.assertNotIn('Nutzungsfreigabe',s)
            for f in ('sitemap.xml','news-sitemap.xml','feed.xml'):
                self.assertNotIn(path,(root/f).read_text())
        archive=(root/'nachrichten/index.html').read_text()
        self.assertIn(d.detail_path(pages[0]),archive)
        self.assertNotIn('href="/nachrichten/cnn',archive)
    def test_preview_noindex_no_sitemap(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);(p/'nachrichten').mkdir();(p/'nachrichten/index.html').write_text('<html><head><title>x</title><link rel="canonical" href="https://fa.example/"><meta name="robots" content="index,follow"><meta name="description" content="x"><meta property="og:title" content="x"><script type="application/ld+json">{}</script></head><body><div class="w"><div class="news-intro">old</div></div><footer>f</footer></body></html>')
            path=d.render_preview(p);s=(p/path.strip('/')/'index.html').read_text()
            self.assertIn('noindex,follow',s);self.assertNotIn('rel="canonical"',s)
            self.assertNotIn('application/ld+json',s);self.assertNotIn('og:title',s)
            self.assertFalse((p/'sitemap.xml').exists())
            self.assertIn('old',(p/'nachrichten/index.html').read_text())

if __name__=='__main__':unittest.main()
