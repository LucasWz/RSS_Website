from time import struct_time, mktime
from datetime import datetime
import feedparser
import re

FeedDict = feedparser.FeedParserDict

def get_description(entry_or_feeder:FeedDict):
    description = entry_or_feeder.get('description')
    summary = entry_or_feeder.get('summary')
    if description:
        return clean_html(description)
    elif summary:
        return clean_html(summary)
    
def struct_to_datetime(o:struct_time) -> datetime:
    return datetime.fromtimestamp(mktime(o))

def clean_html(raw_html):
    CLEANR = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    cleantext = re.sub(CLEANR, '', raw_html)
    return cleantext


