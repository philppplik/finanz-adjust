"""Select the prior completed daily close for a timestamped Yahoo quote.

The daily history may include today's partial bar or may end before the quote's
session. Positional indexing alone therefore cannot establish the baseline.
"""
import datetime
import math
from zoneinfo import ZoneInfo

def prior_session_close(result):
    meta = result['meta']
    zone = ZoneInfo(meta['exchangeTimezoneName'])
    quote_day = datetime.datetime.fromtimestamp(meta['regularMarketTime'], zone).date()
    timestamps = result['timestamp']
    closes = result['indicators']['quote'][0]['close']
    candidates = []
    for ts, close in zip(timestamps, closes):
        if ts is None:
            continue
        day = datetime.datetime.fromtimestamp(ts, zone).date()
        if day < quote_day:
            candidates.append((ts, close))
    if not candidates:
        raise ValueError('No timestamped prior-session close for Yahoo quote')
    close = max(candidates)[1]
    if not isinstance(close, (int, float)) or not math.isfinite(close) or close <= 0:
        raise ValueError('Latest prior-session close is missing or invalid')
    return close
