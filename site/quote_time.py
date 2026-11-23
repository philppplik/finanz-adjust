"""Provider quote time is distinct from capture and document creation time."""
import datetime
import math
from zoneinfo import ZoneInfo

ZONE = ZoneInfo('Europe/Berlin')

def epoch(value):
    try:
        value = float(value)
        return int(value) if math.isfinite(value) and 0 < value <= datetime.datetime.now(datetime.timezone.utc).timestamp() + 300 else None
    except (TypeError, ValueError, OverflowError):
        return None

def label(q):
    ts = epoch(q.get('timestamp'))
    if ts:
        return 'Kurszeit: ' + datetime.datetime.fromtimestamp(ts, ZONE).strftime('%d.%m.%Y %H:%M %Z')
    return 'Kurszeit nicht ausgewiesen'

def capture(q):
    value = q.get('fetched_at')
    ts = epoch(value)
    if ts:
        return datetime.datetime.fromtimestamp(ts, ZONE).strftime('%d.%m.%Y %H:%M %Z')
    return str(value) if value else 'nicht ausgewiesen'

def summary(rows):
    times = [epoch(q.get('timestamp')) for q in rows]
    known = [t for t in times if t]
    if not known:
        return 'Kurszeiten nicht ausgewiesen. Abruf- und Erstellungszeit sind keine Kurszeit.'
    fmt = lambda t: datetime.datetime.fromtimestamp(t, ZONE).strftime('%d.%m.%Y %H:%M %Z')
    span = fmt(min(known)) if min(known) == max(known) else fmt(min(known)) + ' bis ' + fmt(max(known))
    missing = ' Bei %d Werten fehlt die Kurszeit.' % (len(times)-len(known)) if len(known)<len(times) else ''
    return 'Kurszeiten: ' + span + '. Unterschiedliche Handelszeiten; keine Echtzeitzusage.' + missing

def yahoo_time(meta):
    return epoch(meta.get('regularMarketTime'))

def td_time(row):
    # timestamp is Unix UTC per provider. A bare date/datetime without a
    # provider timezone is not silently interpreted in the build timezone.
    return epoch(row.get('timestamp'))
