from flask import Flask, request, render_template
import feedparser
import time
from fuzzywuzzy import fuzz

app = Flask(__name__)

# global variable to store the RSS feed data
feed_data = None

def parse_feed(feed_url):
  feed = feedparser.parse(feed_url)
  return feed

def sort_feed_entries_by_date(feed):
  sorted_entries = sorted(feed.entries, key=lambda entry: entry.published_parsed, reverse=True)
  return sorted_entries

def fuzzy_search(query, entries):
  query = query.lower()
  matching_entries = []
  for entry in entries:
    title = entry.title.lower()
    if fuzz.token_set_ratio(query, title) >= 90:
      matching_entries.append(entry)
  return matching_entries

def refresh_feed():
  global feed_data
  feed_url = "https://www.mediapart.fr/articles/feed"
  feed_data = parse_feed(feed_url)

@app.route("/")
def home():
  global feed_data
  if feed_data is None:
    refresh_feed()
  sorted_entries = sort_feed_entries_by_date(feed_data)
  return render_template("home.html", entries=sorted_entries)

@app.route("/search")
def search():
  global feed_data
  query = request.args.get("search")
  results = fuzzy_search(query, feed_data.entries)
  return render_template("home.html", entries=results)

@app.route("/refresh")
def refresh():
  refresh_feed()

if __name__ == "__main__":
  app.run()