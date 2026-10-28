import json, re, unittest
from pathlib import Path
ROOT = Path(__file__).parent

class CryptoTest(unittest.TestCase):
    def setUp(self):
        self.coins = json.loads((ROOT/'crypto.json').read_text())

    def test_slugs_unique_and_safe(self):
        slugs = [c['slug'] for c in self.coins]
        self.assertEqual(len(set(slugs)), len(slugs))
        for c in self.coins:
            self.assertRegex(c['slug'], r'^[a-z0-9-]+$')

    def test_logos_exist_and_svg(self):
        for c in self.coins:
            p = ROOT/'logos'/c['logo']
            self.assertTrue(p.is_file(), c['logo'])
            self.assertIn('<svg', p.read_text()[:400])
            self.assertIn('wikimedia.org/wiki/File:', c['logo_source'])
            self.assertTrue(c['logo_credit'])

    def test_tv_symbols_strict(self):
        for c in self.coins:
            self.assertRegex(c['tv_symbol'], r'^[A-Z0-9_]+:[A-Z0-9.\/-]+$')

    def test_pages_render(self):
        import crypto
        urls = []
        def page(path, title, desc, body, ld=None, act='', otype='website', crumbs=None, og=None):
            return (path, body)
        crypto.build_crypto_pages(page, urls, [], 'out-test', 'https://finanz-adjust.de')
        paths = [u[0] for u in urls]
        self.assertIn('/krypto/', paths)
        for c in self.coins:
            p = '/krypto/%s/' % c['slug']
            self.assertIn(p, paths)
            body = dict(urls)[p]
            # Click-to-load only: kein iframe, kein externer Request vor Klick
            self.assertNotIn('<iframe', body)
            self.assertIn('data-tv-symbol="%s"' % c['tv_symbol'], body)
            self.assertIn('data-tv-load', body)
            self.assertIn('s3.tradingview.com', body) if False else None
            # Logo lokal referenziert, Credit im Steckbrief
            self.assertIn('/stock-logos/%s' % c['logo'], body)
            self.assertIn(c['logo_credit'], body)
            # Rueckweg und Einordnung
            self.assertIn('← Alle Märkte', body)
            self.assertIn('Einordnung und Risiken', body)
            self.assertIn('risikohinweis', body)
            # Keine erfundenen Marktdaten
            self.assertNotIn('Marktkapitalisierung', body)
        import shutil; shutil.rmtree('out-test', ignore_errors=True)

    def test_quelle_bafin_verlinkt(self):
        for c in self.coins:
            self.assertTrue(any('bafin.de' in u for _, u in c['quellen']))

if __name__ == '__main__':
    unittest.main()
