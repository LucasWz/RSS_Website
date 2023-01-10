from datetime import datetime
import sqlite3
from typing import Any, Dict
from feeders import get_feeder_data
from utils import FeedDict, get_description, struct_to_datetime
import feedparser
import logging
from feeders import SELECT_FEEDERS, UPDATE_FEEDERS
from collections import defaultdict

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

CREATE_FEEDS = """
CREATE TABLE IF NOT EXISTS feeds(
    id TEXT NOT NULL PRIMARY KEY,
    url TEXT NOT NULL,
    link TEXT UNIQUE NOT NULL, 
    title TEXT UNIQUE NOT NULL, 
    description TEXT,
    published BLOB,
    FOREIGN KEY (url)
        REFERENCES feeders (url) 
            ON UPDATE CASCADE
            ON DELETE CASCADE
);
"""

INSERT_FEEDS = """INSERT INTO feeds(url, link, title, id, description, published)
VALUES (:url, :link, :title, :id, :description, :published)"""

DELETE_FEEDS_OUTDATED = "DELETE FROM feeds WHERE published <= date('now','-6 months')"

def get_published(entry:FeedDict) -> datetime:
    published = entry.get('published_parsed')
    if published:
        return struct_to_datetime(published)

def get_feed_data(entry:FeedDict, url:str) -> Dict[str,Any]:
    return {
        'url':url,
        'id':entry.id,
        'title':entry.get('title'),
        'published': get_published(entry),
        'link': entry.get('link'),
        'description': get_description(entry),
        }

        

def refresh_feed(con):
    global CREATE_FEEDS
    global SELECT_FEEDERS
    global UPDATE_FEEDERS
    global INSERT_FEEDS
    
    cur_feeders = con.cursor()
    cur_feeds = con.cursor()
    
    cur_feeds = con.execute(CREATE_FEEDS)
    feeders = cur_feeders.execute(SELECT_FEEDERS)
    
    for title, url , modified, etag in feeders:
        
        # Handle updated method checking
        if modified : 
            d = feedparser.parse(url, modified=modified)
        elif etag :
            d = feedparser.parse(url, etag=etag)
        else : 
            d = feedparser.parse(url)
        
        # Handle malformed XML
        if d.bozo == 1:
            exception = d.bozo.exception.get_message()
            logger.error(f"FEEDER:MalformedXML:{url}:{exception}.")
            logger.error(f"FEEDER:Not add into database:{url}.")
            logger.error(f"FEED:Not add into database:{url}.")
            continue
        
        status = d.status
        if status != 200:
            if status == 304: 
                # No update
                logger.info(f"FEEDER:{status}:{title}:No update found.")
                continue
            elif status == 301:
                # Permanently moved
                logger.warning(f"FEEDER:{status}:{title}:Permanently moved.")
                continue
            elif status == 410:
                # Permanently removed
                logger.warning(f"FEEDER:{status}:{title}:Permanently removed.")
                continue
            else : 
                # Unknown error
                logger.error(f"FEEDER:{status}:{title}:{d.debug_message}.")
                continue
            
        feeder = get_feeder_data(d, url)
        
        # Update 'modified', 'etag'
        cur_feeders.execute(UPDATE_FEEDERS, feeder)
        
        # Add new entries
        for e in d.entries:
            entry = get_feed_data(e, url)
            # Insert feeds if 'id' is unique or ignore 
            try : 
                cur_feeds.execute(INSERT_FEEDS, entry)
            # Handle unique contrains
            except sqlite3.IntegrityError as e:
                logger.warning(f"FEED:IntegrityError:{entry['id']}:{e}")
                continue
            
            except sqlite3.Error as e :
                logger.error(f"FEED:{url}:{entry['id']}:{e}")
                continue
            
        # Finally delete outdated feeds
        try :
            cur_feeds.execute(DELETE_FEEDS_OUTDATED)
        except sqlite3.Error as e :
            logger.error(f"FEED:{url}:{entry['id']}:{e}")
            continue    

def fetch_feeds(con):
    cur = con.cursor()
    cur.row_factory = sqlite3.Row
    cur.execute("SELECT * FROM feeds ORDER BY published DESC;")
    data_generator = cur.fetchall()
    return [{k: item[k] for k in item.keys()} for item in data_generator]


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
        date_counts[date.date().strftime('%Y-%m-%d')] += 1
    return date_counts

if __name__ == "__main__": 
    feedparser.USER_AGENT = "BioFlux/1.0 +http://flux.lucaswintz.fr/"
    db = input('>> Input database path :\n')
    with sqlite3.connect(db) as con:
        refresh_feed(con)