"""Build-output regression: external archive remains, foreign RSS excerpts do not."""
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

class RssRightsTests(unittest.TestCase):
    def test_external_descriptions_empty_but_links_preserved(self):
        path=Path('out/feed.xml')
        self.assertTrue(path.is_file(), 'Run build.py before this regression test')
        archive=json.loads(Path('../data/fin_archive.json').read_text())
        by_url={x['url']:x for x in archive}
        rows=ET.parse(path).findall('.//item')
        external=[x for x in rows if x.findtext('link') in by_url]
        self.assertTrue(external)
        for item in external:
            self.assertFalse(item.findtext('description'), item.findtext('link'))
            self.assertEqual(item.findtext('guid'),item.findtext('link'))
            self.assertTrue(item.findtext('title'))
        self.assertTrue(any(x.get('sum') for x in archive), 'Archive snippets must remain untouched')
        editorial=[x for x in rows if x.findtext('link') not in by_url]
        self.assertTrue(editorial)
        self.assertTrue(any(x.findtext('description') for x in editorial), 'Own article descriptions must remain')

if __name__=='__main__': unittest.main()
