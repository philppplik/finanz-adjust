from html import escape
import re
from share import share_block

SHARE_SECTIONS = ('/aktien/', '/broker/', '/lernpfade/')

def add_page_sharing(path, title, body, base):
    """One canonical, passive sharing group per supported directory/detail page."""
    if not path.startswith(SHARE_SECTIONS):
        return body
    # Insert after the complete introductory header where available, never inside h1.
    marker = re.search(r'<header class="stock-title">.*?</header>|<div class="stock-hero">.*?</div>(?=<section)|<div class="cmp-offer-head">.*?<h1\b[^>]*>.*?</h1></div>|<h1\b[^>]*>.*?</h1>', body, re.S)
    if not marker:
        return body
    block = share_block(base + path, title.split(' | ')[0], 'fa', top=True, label='Seite teilen')
    return body[:marker.end()] + block + body[marker.end():]
