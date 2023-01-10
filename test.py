import feedparser
from pprint import pprint

FEEDER = {
    "mediapart": "https://www.mediapart.fr/articles/feed",
    "le monde": "https://www.lemonde.fr/rss/une.xml",
    "le figaro": "https://www.lefigaro.fr/rss/figaro_actualites.xml"
}

pprint(feedparser.parse(FEEDER['le monde']).keys())