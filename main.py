import sqlite3
from flask import Flask, request, render_template
from feeders import fetch_feeders
from feeds import refresh_feed, fetch_feeds
from search import fuzzy_search
from feeds import refresh_feed
import logging 

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Flask(__name__)

DB = 'bio-flux.db'

@app.route("/")
def home():
  with sqlite3.connect(DB) as con:
      feed_data = fetch_feeds(con)
  return render_template("home.html", entries=feed_data)

@app.route("/search")
def search():
  with sqlite3.connect(DB) as con:
      feed_data = fetch_feeds(con)
  query = request.args.get("search")
  results = fuzzy_search(query, feed_data)
  return render_template("home.html", entries=results)

@app.route("/feeders")
def feeders():
  with sqlite3.connect(DB) as con:
    feeders = fetch_feeders(con)
    return render_template("feeders.html", entries=feeders)

@app.route("/refresh")
def refresh():
  with sqlite3.connect(DB) as con:
    refresh_feed(con)
    feed_data = fetch_feeds(con)
  return render_template("home.html", entries=feed_data)
  
if __name__ == "__main__":
  app.run()