import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import news_media as m

class MediaTests(unittest.TestCase):
    def item(self, url='https://www.finanzen.net/a', **kw):
        return dict(url=url, title='<b>Aktie & Börse</b>', src='GDELT', ts=1792400790, **kw)
    def test_blocked_source_and_domain(self):
        for u in ('https://tagesschau.de/a','https://www.tagesschau.de/a','https://sub.tagesschau.de/a','javascript:alert(1)'):
            self.assertEqual(m.permitted_news([self.item(u)]), [])
        self.assertEqual(m.permitted_news([dict(self.item(),src='tagesschau Finanzen')]), [])
        self.assertEqual(len(m.permitted_news([self.item('https://not-tagesschau.de/a')])),1)
    def test_source_not_aggregator(self):
        self.assertEqual(m.identity(self.item())[1], 'finanzen.net')
        self.assertIn('/news-assets/icons/finanzen.net.png',m.source_badge(self.item()))
    def test_monogram(self):
        self.assertIn('source-mono',m.source_badge(self.item('https://unknown.invalid/x')))
    def test_escaping_local_assets(self):
        out=m.news_cards([self.item()]);self.assertIn('&lt;b&gt;',out)
        self.assertNotIn('<b>Aktie',out);self.assertNotIn('<img src="https://',out)
        self.assertIn('noreferrer nofollow',out);self.assertIn('QUELLEN-LINK',out)
    def test_remote_thumbnail_denied(self):
        self.assertIsNone(m.approved_thumbnail(dict(self.item(),thumbnail='https://bad.example/x.jpg')))
    def test_approved_local_thumbnail_and_traversal(self):
        with tempfile.TemporaryDirectory() as t, patch.object(m,'ASSETS',Path(t)):
            p=Path(t);(p/'thumbnails').mkdir();(p/'thumbnails/a.png').write_bytes(b'fixture')
            e=dict(file='thumbnails/a.png',credit='Credit',rights_url='https://license.example',reviewed='2026-10-19',source_url='https://source.example/a.png')
            (p/'thumbnails.json').write_text(json.dumps({self.item()['url']:e}));self.assertIsNotNone(m.approved_thumbnail(self.item()))
            e['file']='../a.png';(p/'thumbnails.json').write_text(json.dumps({self.item()['url']:e}));self.assertIsNone(m.approved_thumbnail(self.item()))
    def test_empty(self):
        self.assertIn('keine Meldungen',m.news_cards([]))
    def test_archive_clean(self):
        n=json.loads(Path('../data/fin_archive.json').read_text());self.assertEqual(n,m.permitted_news(n))

if __name__=='__main__': unittest.main()
