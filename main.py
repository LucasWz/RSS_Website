import json
import sqlite3
from flask import Flask, request, render_template
from feeders import fetch_feeders
from feeds import create_date_counts, fetch_publication_date, refresh_feed, fetch_feeds
from search import fuzzy_search
import logging 

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Flask(__name__)
DB = 'bio-flux.db'


def get_db():
  global DB
  if 'db' not in g:
          g.db = sqlite3.connect(DB)
  return g.db


@app.teardown_appcontext
def close_db(error):
        db = g.pop('db', None)
        if db is not None:
                db.close()

@app.route("/")
def home():
    con = get_db()
    refresh_feed(con)
    feed_data = fetch_feeds(con)
    return render_template("home.html", entries=feed_data)


@app.route("/search")
def search():
    con = get_db()
    feed_data = fetch_feeds(con)
    query = request.args.get("search")
    results = fuzzy_search(query, feed_data)
    return render_template("home.html", entries=results)


@app.route("/feeders")
def feeders():
    con = get_db()
    feeders = fetch_feeders(con)
    return render_template("feeders.html", entries=feeders)


@app.route("/refresh")
def refresh():
    con = get_db()
    refresh_feed(con)
    feed_data = fetch_feeds(con)
    return render_template("home.html", entries=feed_data)


@app.route('/calendar')
def calendar():
    con = get_db()
    dates = fetch_publication_date(con)
    date_counts = create_date_counts(dates)
    data = json.dumps(date_counts)
    return render_template('calendar.html', data=data)


if __name__ == "__main__":
    app.run()
