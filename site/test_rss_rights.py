"""Build-output regression: external archive remains, foreign RSS excerpts do not.

Quellenmix seit dem FinanzNachrichten-Umbau: externe Feed-Schlagzeilen stammen aus
data/news-pages.json (lizenzierte Quellen, headline-only mit rights_checked/license_key);
data/fin_archive.json bleibt das historische GDELT/Yahoo-Archiv mit unangetasteten Snippets.
"""
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

BASE='https://finanz-adjust.de'

class RssRightsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path=Path('out/feed.xml')
        assert path.is_file(), 'Run build.py before this regression test'
        cls.rows=ET.parse(path).findall('.//item')
        cls.external=[x for x in cls.rows if not x.findtext('link').startswith(BASE)]
        cls.editorial=[x for x in cls.rows if x.findtext('link').startswith(BASE)]
        cls.licensed=json.loads(Path('../data/news-pages.json').read_text())
        cls.licensed_urls={x['url'] for x in cls.licensed if x.get('url','').startswith('http')}
        cls.legacy=json.loads(Path('../data/fin_archive.json').read_text())
        cls.legacy_urls={x['url'] for x in cls.legacy}

    def test_external_items_headline_only_and_attributed(self):
        # Positivnachweis: externe Schlagzeilen sind im Feed vorhanden.
        self.assertTrue(self.external)
        known=self.licensed_urls|self.legacy_urls
        for item in self.external:
            link=item.findtext('link')
            # Negativprobe: keine unerlaubten Fremd-Descriptions (nur Schlagzeile+Link).
            self.assertFalse(item.findtext('description'), link)
            self.assertEqual(item.findtext('guid'),link)
            self.assertTrue(item.findtext('title'))
            # Negativprobe: keine falsche Quellzuordnung - nur bekannte archivierte Quell-URLs.
            self.assertIn(link, known, link)

    def test_licensed_items_carry_rights_markers(self):
        fn=[x for x in self.licensed if 'finanznachrichten.de' in x.get('url','')]
        self.assertTrue(fn)
        for x in fn:
            self.assertTrue(x.get('rights_checked'), x['url'])
            self.assertTrue(x.get('license_key'), x['url'])
            # Headline-only: lizenzierte Uebernahme erlaubt keine Fremdtexte.
            self.assertFalse(x.get('sum'), x['url'])
            self.assertFalse(x.get('teaser'), x['url'])

    def test_archive_snippets_untouched(self):
        self.assertTrue(any(x.get('sum') for x in self.legacy), 'Archive snippets must remain untouched')

    def test_editorial_descriptions_remain(self):
        self.assertTrue(self.editorial)
        self.assertTrue(any(x.findtext('description') for x in self.editorial), 'Own article descriptions must remain')

if __name__=='__main__': unittest.main()
