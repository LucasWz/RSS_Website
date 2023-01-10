from collections import defaultdict
import sqlite3
import feedparser
from pprint import pprint
from datetime import datetime
# FEEDER = {
#     "mediapart": "https://www.mediapart.fr/articles/feed",
#     "le monde": "https://www.lemonde.fr/rss/une.xml",
#     "le figaro": "https://www.lefigaro.fr/rss/figaro_actualites.xml"
# }

# pprint(feedparser.parse(FEEDER['le monde']).keys())

def fetch_publication_date(con):
    cur = con.cursor()
    cur.execute("SELECT published FROM feeds")
    dates = [row[0] for row in cur.fetchall()]
    cur.close()
    return dates

def create_date_counts(dates):
    date_counts = defaultdict(int)
    for date in dates:
        date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        date_counts[date.date()] += 1
    return date_counts

with sqlite3.connect('bio-flux.db') as con:
    dates = fetch_publication_date(con)
    print(create_date_counts(dates))
    

