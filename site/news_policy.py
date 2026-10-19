"""Conservative routing policy. No foreign excerpts are approved for republication."""
import hashlib
import re
import unicodedata
from news_media import domain, permitted_news

HEADLINE_SOURCES = frozenset({'finanznachrichten.de'})
TEASER_SOURCES = frozenset()

def detail_path(item):
    title = unicodedata.normalize('NFKD', item['title']).encode('ascii', 'ignore').decode().lower()
    slug = re.sub('[^a-z0-9]+', '-', title).strip('-')[:76].rstrip('-') or 'meldung'
    return '/nachrichten/%s-%s/' % (slug, hashlib.sha256(item['url'].encode()).hexdigest()[:12])

def has_detail(item):
    return bool(permitted_news([item])) and domain(item.get('url','')) in HEADLINE_SOURCES

def destination(item):
    return detail_path(item) if has_detail(item) else item['url']
