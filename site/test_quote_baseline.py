import datetime
import unittest
from zoneinfo import ZoneInfo
from quote_baseline import prior_session_close


def stamp(day, hour=9):
    return int(datetime.datetime.fromisoformat(day).replace(hour=hour, tzinfo=ZoneInfo('Europe/Berlin')).timestamp())


def result(quote_day, days, closes):
    return {'meta': {'regularMarketTime': stamp(quote_day, 17), 'exchangeTimezoneName': 'Europe/Berlin'},
            'timestamp': [stamp(day) for day in days], 'indicators': {'quote': [{'close': closes}]}}


class BaselineTests(unittest.TestCase):
    def test_completed_session_with_same_day_bar(self):
        r = result('2026-11-17', ['2026-11-13', '2026-11-16', '2026-11-17'], [26749.95, 26598.64, 26045.37])
        self.assertEqual(prior_session_close(r), 26598.64)

    def test_overnight_history_lacks_quote_session_bar(self):
        r = result('2026-11-17', ['2026-11-13', '2026-11-16'], [26749.95, 26598.64])
        prev = prior_session_close(r)
        self.assertEqual(prev, 26598.64)
        self.assertEqual(round(26045.37-prev, 2), -553.27)
        self.assertEqual(round((26045.37-prev)/prev*100, 2), -2.08)

    def test_intraday_and_weekend(self):
        r = result('2026-11-18', ['2026-11-16', '2026-11-17', '2026-11-18'], [26598.64, 26045.37, 26091.65])
        self.assertEqual(prior_session_close(r), 26045.37)
        self.assertEqual(prior_session_close(result('2026-11-16', ['2026-11-13', '2026-11-16'], [26749.95, 26598.64])), 26749.95)

    def test_future_null_and_invalid_values_are_not_baselines(self):
        r = result('2026-11-18', ['2026-11-13', '2026-11-16', '2026-11-17', '2026-11-19'], [26749.95, 26598.64, None, 27000])
        with self.assertRaises(ValueError): prior_session_close(r)
        r['indicators']['quote'][0]['close'] = [None, 0, float('nan'), 27000]
        with self.assertRaises(ValueError): prior_session_close(r)

    def test_missing_timestamp_fails_closed(self):
        r = result('2026-11-18', ['2026-11-18'], [26091.65])
        with self.assertRaises(ValueError): prior_session_close(r)
        del r['meta']['regularMarketTime']
        with self.assertRaises(KeyError): prior_session_close(r)


if __name__ == '__main__': unittest.main()
