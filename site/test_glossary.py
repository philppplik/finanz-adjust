import json, re, tempfile, unittest
from pathlib import Path
from glossary import load_entries, matching_articles, normalize, schemas, build_glossary

class GlossaryTest(unittest.TestCase):
    def test_curated_data_and_old_urls(self):
        entries=load_entries()
        self.assertGreaterEqual(len(entries),50)
        slugs={g['slug'] for g in entries}
        for s in ['was-ist-der-dax','was-ist-ein-etf','was-ist-eine-aktie','was-ist-eine-dividende','was-bedeutet-volatilitaet','was-ist-ein-wechselkurs']:
            self.assertIn(s,slugs)
        self.assertEqual(len({g['category'] for g in entries}),7)
    def test_normalization(self):
        for a,b in [('Börse','Boerse'),('Fälligkeit','Faelligkeit'),('Ausschüttung','Ausschuettung'),('Straße','Strasse')]:
            self.assertEqual(normalize(a),normalize(b))
    def test_schema_matches_visible_faq_and_sources(self):
        for g in load_entries():
            term,web,faq=schemas(g,'https://finanz-adjust.de')
            self.assertEqual(term['description'],g['short'])
            self.assertEqual(web['author']['name'],'FA Redaktion')
            self.assertEqual(web['citation'],[s['url'] for s in g['sources']])
            self.assertEqual([q['acceptedAnswer']['text'] for q in faq['mainEntity']],[f['a'] for f in g['faq']])
            json.dumps([term,web,faq],allow_nan=False)
    def test_article_matching_and_word_boundaries(self):
        g=next(g for g in load_entries() if g['slug']=='zew-index')
        self.assertEqual(len(matching_articles(g,[dict(title='Was ist der ZEW-Index?',description='') ])),1)
        g=next(g for g in load_entries() if g['slug']=='was-ist-ein-etf')
        self.assertFalse(matching_articles(g,[dict(title='Netfilter',description='')]))
    def test_build_is_static_and_escape_safe(self):
        with tempfile.TemporaryDirectory() as d:
            pages={};urls=[]
            def page(path,title,desc,body,ld=None,**kwargs):
                pages[path]=(body,ld);return 'https://finanz-adjust.de'+path
            build_glossary(page,urls,[],d,'https://finanz-adjust.de')
            self.assertEqual(len(pages),len(load_entries())+1)
            self.assertIn('DefinedTermSet',json.dumps(pages['/glossar/'][1]))
            self.assertIn('58 Begriffe',pages['/glossar/'][0])
            for g in load_entries():
                html=pages['/glossar/'+g['slug']+'/'][0]
                self.assertIn('FA Redaktion',html)
                self.assertIn('Quellen &amp; Prüfstand',html)
                self.assertNotIn('target="_blank"',html)
            js=(Path(d)/'glossary.js').read_text()
            for token in ('fetch(', 'XMLHttpRequest', 'document.cookie', 'localStorage'):
                self.assertNotIn(token,js)
    def test_built_internal_links(self):
        out=Path('out')
        if not out.exists():self.skipTest('Run build.py first')
        for page in out.glob('glossar/**/index.html'):
            html=page.read_text()
            for href in re.findall(r'href="(/[^"#?]*)"',html):
                path=out/href.lstrip('/')
                if href.endswith('/'):path/='index.html'
                self.assertTrue(path.exists(),str(page)+' -> '+href)
            for payload in re.findall(r'<script type="application/ld\+json">(.*?)</script>',html,re.S):json.loads(payload)
        for slug in ['glossar-zew-index','glossar-einkaufsmanagerindex']:
            html=(out/'artikel'/slug/'index.html').read_text()
            self.assertIn('Begriffe zum Weiterlesen',html)
            self.assertIn('/glossar/',html)

if __name__=='__main__':unittest.main()
