"""Local-only news presentation. Publisher photos are deny-by-default."""
import datetime
import hashlib
import html
import json
from pathlib import Path
from urllib.parse import urlsplit

ASSETS = Path(__file__).resolve().parent / 'news-assets'

def domain(url):
    try:
        p = urlsplit(url)
        return (p.hostname or '').lower().removeprefix('www.') if p.scheme in ('http', 'https') else ''
    except ValueError:
        return ''

def permitted_news(items):
    return [i for i in items if domain(i.get('url', '')) and
            not (domain(i.get('url', '')) == 'tagesschau.de' or
                 domain(i.get('url', '')).endswith('.tagesschau.de') or
                 'tagesschau' in i.get('src', '').lower())]

def identity(item):
    host = domain(item.get('url', ''))
    label = host or 'Quelle'
    # Source is the linked publisher, NOT the aggregator Yahoo/GDELT.
    mono = ''.join(x[0] for x in host.split('.')[:-1])[:2].upper() or '?'
    color = int(hashlib.sha256(host.encode()).hexdigest()[:4], 16) % 360
    icon = ASSETS / 'icons' / (host + '.png')
    return host, label, mono, color, ('/news-assets/icons/' + host + '.png') if icon.is_file() else None

def approved_thumbnail(item):
    """Only exact URL matches with locally verified assets and rights evidence."""
    try:
        entries = json.loads((ASSETS / 'thumbnails.json').read_text())
        entry = entries.get(item['url'], {})
        if not all(entry.get(k) for k in ('file', 'credit', 'rights_url', 'reviewed', 'source_url')):
            return None
        datetime.date.fromisoformat(entry['reviewed'])
        rel = Path(entry['file'])
        if rel.is_absolute() or '..' in rel.parts or rel.parts[0] != 'thumbnails':
            return None
        path = ASSETS / rel
        if path.suffix.lower() not in ('.jpg', '.jpeg', '.png', '.webp') or not path.is_file():
            return None
        if not entry['rights_url'].startswith('https://'):
            return None
        return entry
    except (OSError, ValueError, KeyError, IndexError, TypeError):
        return None

def source_badge(item):
    host, label, mono, color, icon = identity(item)
    e = html.escape
    mark = ('<img src="%s" width="20" height="20" alt="" loading="lazy" decoding="async">' % e(icon, quote=True)
            if icon else '<span class="source-mono" aria-hidden="true">%s</span>' % e(mono))
    return '<span class="source-badge">%s<span>%s</span></span>' % (mark, e(label))

def news_cards(items, limit=500):
    e = lambda s: html.escape(str(s), quote=True)
    cards = []
    for item in permitted_news(items)[:limit]:
        host, label, mono, color, icon = identity(item)
        thumb = approved_thumbnail(item)
        if thumb:
            media = '<figure class="news-photo"><img src="/news-assets/%s" width="320" height="200" alt="" loading="lazy" decoding="async"><figcaption>%s</figcaption></figure>' % (e(thumb['file']), e(thumb['credit']))
        else:
            mark = '<img src="%s" width="40" height="40" alt="" loading="lazy" decoding="async">' % e(icon) if icon else '<b>%s</b>' % e(mono)
            media = '<div class="news-art" style="--source-hue:%d" aria-hidden="true"><span>%s</span><svg viewBox="0 0 160 56" focusable="false"><path d="M0 42H28L45 22L68 33L91 10L116 25L139 5H160"/></svg><small>QUELLEN-LINK</small></div>' % (color, mark)
        try:
            dt = datetime.datetime.fromtimestamp(item['ts']).astimezone()
            when = '<time datetime="%s">%s</time>' % (dt.isoformat(), dt.strftime('%d.%m.%Y · %H:%M')) if item['ts'] else ''
        except (KeyError, TypeError, ValueError, OSError):
            when = ''
        cards.append('<li class="news-card">%s<div class="news-copy">%s<h2><a href="%s" target="_blank" rel="noopener noreferrer nofollow">%s<span class="news-arrow" aria-hidden="true"> ↗</span></a></h2><div class="news-meta">%s<span>Original lesen ↗</span></div></div></li>' % (media, source_badge(item), e(item['url']), e(item['title']), when))
    return '<ul class="news-grid">' + ''.join(cards) + '</ul>' if cards else '<p class="note">Aktuell sind keine Meldungen verfügbar. Neue Schlagzeilen folgen mit dem nächsten Datenlauf.</p>'
