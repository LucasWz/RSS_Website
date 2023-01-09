from flask import Flask, render_template
import feedparser
from fuzzywuzzy import fuzz

app = Flask(__name__)

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

@app.route("/")
def home():
  feed_url = "https://www.mediapart.fr/articles/feed"
  feed = parse_feed(feed_url)
  sorted_entries = sort_feed_entries_by_date(feed)
  return render_template("home.html", entries=sorted_entries)


if __name__ == "__main__":
  app.run()
