"""Time-bounded own-article RSS pool for the weekly newsletter.

Keep fourteen elapsed days, not a fixed item count. A weekly Berlin window is at
most 169 hours across DST; the extra week buffers delayed reads. External
headline selection and rights stay with the existing feed builder.
"""
from datetime import timedelta

RETENTION_DAYS = 14


def editorial_feed_articles(articles, date_of, now):
    """Preserve input order and every published own article in the retention span."""
    end = now.timestamp()
    start = end - timedelta(days=RETENTION_DAYS).total_seconds()
    return [article for article in articles
            if start <= date_of(article).timestamp() <= end]
