from typing import Any
from flask import Flask, request, render_template
import feedparser
from fuzzywuzzy import fuzz

app = Flask(__name__)

feed_data = []
FEEDER = {
    "Médiapart": "https://www.mediapart.fr/articles/feed",
    "Le Monde": "https://www.lemonde.fr/rss/une.xml",
}

def parse_feed(feed_url:str) -> dict:
  return feedparser.parse(feed_url)

def fuzzy_search(query:str, entries) -> list:
  query = query.lower()
  matching_entries = []
  for entry in entries:
    title = entry.title.lower()
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

@app.route("/refresh")
def refresh():
  global feed_data
  feed_data
  
if __name__ == "__main__":
  app.run()