import datetime, unittest
import quote_time as q
class QuoteTimeTests(unittest.TestCase):
 def test_weekend_build_never_becomes_friday_quote(self):
  ts=int(datetime.datetime(2026,11,20,17,tzinfo=datetime.timezone.utc).timestamp())
  self.assertIn('20.11.2026 18:00 CET',q.label({'timestamp':ts,'fetched_at':'23.11.2026 09:00'}))
  self.assertNotIn('23.11',q.summary([{'timestamp':ts}]))
 def test_missing_invalid_future_not_inferred(self):
  for ts in (None,0,-1,'bad',float('nan'),99999999999):
   self.assertEqual(q.label({'timestamp':ts,'fetched_at':'23.11.2026 09:00'}),'Kurszeit nicht ausgewiesen')
 def test_mixed_times_and_absent(self):
  s=q.summary([{'timestamp':1795194000},{'timestamp':1795197600},{}])
  self.assertIn(' bis ',s);self.assertIn('Bei 1 Werten fehlt',s)
 def test_provider_extraction_no_timezone_guess(self):
  self.assertEqual(q.yahoo_time({'regularMarketTime':1795194000}),1795194000)
  self.assertIsNone(q.td_time({'datetime':'2026-11-20'}))
