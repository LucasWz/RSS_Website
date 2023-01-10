from typing import Any
from flask import Flask, request, render_template
import feedparser
from fuzzywuzzy import fuzz

app = Flask(__name__)

feed_data = []
FEEDER = {
    "Ministère de l'Agriculture et de la Souveraineté alimentaire":"https://agriculture.gouv.fr/rss.xml",
    "Agence Bio": "https://www.agencebio.org/feed/",
    "ABioDoc - Abeille": "https://abiodoc.docressources.fr/rss.php?id=3",
    # "ABioDoc - Agroécologie": "https://abiodoc.docressources.fr/rss.php?id=26",
    # "ABioDoc - Bovin": "https://abiodoc.docressources.fr/rss.php?id=5",
    # "ABioDoc - Caprin": "https://abiodoc.docressources.fr/rss.php?id=6",
    # "ABioDoc - Ovin": "https://abiodoc.docressources.fr/rss.php?id=13",
    # "ABioDoc - Changement climatique": "https://abiodoc.docressources.fr/rss.php?id=24",
    # "ABioDoc - Eau": "https://abiodoc.docressources.fr/rss.php?id=8",
    # "ABioDoc - Filière": "https://abiodoc.docressources.fr/rss.php?id=9",
    # "ABioDoc - Fruit": "https://abiodoc.docressources.fr/rss.php?id=11", 
    # "ABioDoc - Réglementation": "https://abiodoc.docressources.fr/rss.php?id=18", 
    # "ABioDoc - PPAM": "https://abiodoc.docressources.fr/rss.php?id=17", 
    # "ABioDoc - Restauration collective": "https://abiodoc.docressources.fr/rss.php?id=33",
    # "ABioDoc - Territoire et Société": "https://abiodoc.docressources.fr/rss.php?id=25",  
    # "ABioDoc - Volailles": "https://abiodoc.docressources.fr/rss.php?id=22", 
    # "ABioDoc - Maraîchage": "https://abiodoc.docressources.fr/rss.php?id=31", 
}

def parse_feed(feed_url:str) -> dict:
  return feedparser.parse(feed_url)

def fuzzy_search(query:str, entries) -> list:
  query = query.lower()
  matching_entries = []
  for entry in entries:
    title = entry['title'].lower()
    if fuzz.token_set_ratio(query, title) >= 80:
      matching_entries.append(entry)
  return matching_entries

def refresh_feed() -> list:
  global feed_data
  feed_data = []
  for name, url in FEEDER.items():
    feed = parse_feed(url)
    update = {'name':name}
    updated_feed = [{**d,**update} for d in feed.entries]
    feed_data.extend(updated_feed)
  return feed_data

@app.route("/")
def home():
  global feed_data
  if len(feed_data) == 0:
    refresh_feed()
  return render_template("home.html", entries=feed_data)

@app.route("/search")
def search():
  global feed_data
  query = request.args.get("search")
  results = fuzzy_search(query, feed_data)
  return render_template("home.html", entries=results)

@app.route("/feeders")
def feeders():
  global FEEDER
  return render_template("feeders.html", entries=FEEDER)

@app.route("/refresh")
def refresh():
  global feed_data
  feed_data
  
if __name__ == "__main__":
  app.run()