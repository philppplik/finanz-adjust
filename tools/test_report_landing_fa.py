import json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import report_landing as rl
import report_landing_fa as fa
import share

class FaLandingTests(unittest.TestCase):
    def _root(self, t):
        r = Path(t); (r / 'data').mkdir()
        (r / 'data/quotes.json').write_text(json.dumps([{'sym': 'X', 'name': 'DAX', 'grp': 'Index', 'price': 100.0, 'pct': 1.0, 'hist': [1, 2, 3]}]))
        (r / 'data/stock-quotes.json').write_text(json.dumps({'a': {'symbol': 'AAA', 'percent_change': 2.0}, 'b': {'symbol': 'BBB', 'percent_change': -1.0}}))
        (r / 'berichte').mkdir(); return r
    def test_enhance_adds_real_sections_only(self):
        with tempfile.TemporaryDirectory() as t, patch.object(rl.shutil, 'which', return_value=None), patch.object(fa.shutil, 'which', return_value=None):
            r = self._root(t)
            base = rl.build(t, t, 'fa', ['2026-10-19'], 'aktuell.pdf', 'tagesbericht-')
            s = fa.enhance(base, r, r, ['2026-10-19'], 'aktuell.pdf', '19.10.2026')
            self.assertIn('Deine Vorteile', s); self.assertIn('Marktbreite der 2 Aktien', s); self.assertIn('AAA', s)
            self.assertIn('Ausgaben im Archiv', s)
            for bad in ('<script', '<form', 'Bewertung'): self.assertNotIn(bad, s)
            self.assertNotIn('tracking-frei', s.lower())
            self.assertIn('keine Nutzer- oder Downloadzahlen', s)
    def test_missing_data_falls_back(self):
        with tempfile.TemporaryDirectory() as t, patch.object(fa.shutil, 'which', return_value=None):
            self.assertEqual(fa.enhance('<p>x</p>', t, t, []), '<p>x</p>')
    def test_share_block(self):
        s = share.share_block('https://finanz-adjust.de/artikel/x/', 'T & "Q"', 'fa', True)
        self.assertIn('share-top', s); self.assertIn('wa.me', s); self.assertNotIn('<img', s)
        self.assertEqual(s.count('noopener noreferrer nofollow'), 6)
        self.assertEqual(s.count('class="sh-label"'), 8)
        self.assertIn('aria-label="Auf LinkedIn teilen (öffnet in neuem Tab)"', s)
        self.assertIn('aria-label="Link kopieren"', s)
        self.assertNotIn('<text ', s)
        self.assertIn('width:44px;height:44px', share.SHARE_CSS)
        self.assertIn('width:20px;height:20px', share.SHARE_CSS)

if __name__ == '__main__': unittest.main()
