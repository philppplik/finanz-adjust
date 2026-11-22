"""No network, no full site build: RSS retention and builder wiring regressions."""
import ast
from datetime import datetime, timedelta
from pathlib import Path
import unittest
from zoneinfo import ZoneInfo
from rss_editorial import editorial_feed_articles

BERLIN = ZoneInfo('Europe/Berlin')


class EditorialFeedTests(unittest.TestCase):
    def test_high_volume_has_no_twenty_item_cap(self):
        now = datetime(2026, 11, 27, 9, tzinfo=BERLIN)
        rows = [{'n': i, 'date': now - timedelta(minutes=i)} for i in range(2000)]
        self.assertEqual(editorial_feed_articles(rows, lambda a: a['date'], now), rows)

    def test_fourteen_day_boundaries_and_future_are_exact(self):
        now = datetime(2026, 11, 27, 9, tzinfo=BERLIN)
        times = [now + timedelta(seconds=1), now, now - timedelta(days=14),
                 now - timedelta(days=14, seconds=1)]
        self.assertEqual(editorial_feed_articles(times, lambda d: d, now), times[1:3])

    def test_every_weekly_slot_item_survives_both_dst_directions(self):
        for end in [datetime(2026, 3, 29, 9, tzinfo=BERLIN),
                    datetime(2026, 10, 25, 9, tzinfo=BERLIN)]:
            start = end - timedelta(days=7)
            rows = [start, start + timedelta(seconds=1), end - timedelta(seconds=1)]
            self.assertEqual(editorial_feed_articles(rows, lambda d: d, end), rows)

    def test_empty_pool_stays_empty(self):
        self.assertEqual(editorial_feed_articles([], lambda a: a, datetime.now(BERLIN)), [])

    def test_builder_uses_retention_for_own_articles_only(self):
        source = Path(__file__).with_name('build.py').read_text()
        tree = ast.parse(source)
        imports = [x for x in ast.walk(tree) if isinstance(x, ast.ImportFrom)]
        self.assertTrue(any(x.module == 'rss_editorial' for x in imports))
        calls = [ast.unparse(x) for x in ast.walk(tree) if isinstance(x, ast.Call)]
        self.assertIn('editorial_feed_articles(ARTS, adate, NOW)', calls)
        self.assertNotIn('ARTS[:20]', source)
        self.assertIn('_feed_diverse(N, 60)', calls)
        self.assertIn('if i.get(\'ts\')', source)


if __name__ == '__main__':
    unittest.main()
