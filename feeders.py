from typing import Any, Dict, List
import feedparser
from utils import FeedDict, get_description
import sqlite3 
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

CREATE_FEEDERS = """
CREATE TABLE IF NOT EXISTS feeders(
    url TEXT NOT NULL PRIMARY KEY,
    link TEXT NOT NULL, 
    title TEXT NOT NULL,
    image TEXT, 
    description TEXT,
    etag TEXT,
    modified TEXT    
);
"""

INSERT_FEEDERS = """INSERT INTO feeders(url, link, title, image, description, etag, modified)
VALUES (:url, :link, :title, :image, :description, :etag, :modified)"""

UPDATE_FEEDERS ="""UPDATE feeders 
SET etag = :etag,
    modified = :modified
WHERE url = :url;
"""

SELECT_FEEDERS = 'SELECT title, url , modified, etag FROM feeders;'


def get_feeders(text_file:str='static/txt/feeders.txt') -> List[str]:
    with open(text_file, 'r') as f: 
        feeders = [row.strip() for row in f.read().split('\n')]
    return feeders

def get_image_href(feeder:FeedDict) -> str: 
    if feeder.get('image'):
        image = feeder.get('image')
        if image.get('href'): 
            return image.get('href')
        

def get_feeder_data(data:FeedDict, url:str) -> Dict[str,Any]:
    feeder = data.feed
    return {
        'url':url,
        'image': get_image_href(feeder),
        'title': feeder.get('title'),
        'link': feeder.get('link'),
        'description': get_description(feeder),
        'etag': feeder.get('etag'),
        'modified': feeder.get('modified'),
        }
    
    

def add_feeders(urls:List[str], con) -> None:
    cur = con.cursor()        
    cur = con.execute(CREATE_FEEDERS)
    for url in urls:
        
        logger.info(f"FEEDER:Adding feeder data to DB:{url}")
        d = feedparser.parse(url)
        
        # Handle malformed XML
        if d.bozo == 1:
            exception = d.bozo_exception
            logger.error(f"FEEDER:MalformedXML:{url}:{exception}.")
            logger.error(f"FEEDER:Not add into database:{url}.")
            continue
        
        feeder = get_feeder_data(d, url)
        # Reset `etag` and `modified` to enable feeds
        feeder['etag'] = None
        feeder['modified'] = None
        
        try : 
            cur.execute(INSERT_FEEDERS, feeder)
            
        # Handle unique contrains
        except sqlite3.IntegrityError as e:
            logger.warning(f"FEEDER:IntegrityError:{url}:{e}")
            continue
        
        except sqlite3.Error as e :
            logger.error(f"FEEDER:{url}:{e}")
            continue
            
        
    cur.close()
    
def fetch_feeders(con):
    cur = con.cursor()
    cur.row_factory = sqlite3.Row
    cur.execute("SELECT * FROM feeders ORDER BY title DESC;")
    data_generator = cur.fetchall()
    return [{k: item[k] for k in item.keys()} for item in data_generator]
    
if __name__ == "__main__":
    feedparser.USER_AGENT = "BioFlux/1.0 +http://flux.lucaswintz.fr/"
    db = input('>> Input database path :\n')
    with sqlite3.connect(db) as con:
        feeders = get_feeders()
        add_feeders(feeders, con)