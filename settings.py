from scrapy.item import Item, Field

class WikipediaItem(Item):  # Rename BritannicaItem to WikipediaItem
    url = Field()
    text = Field()

# Spider settings
CUSTOM_SETTINGS = {
    'DEPTH_LIMIT': 2,
    'CONCURRENT_REQUESTS': 8,
    'AUTOTHROTTLE_ENABLED': True,
    'AUTOTHROTTLE_START_DELAY': 5,
    'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
    'AUTOTHROTTLE_DEBUG': True,
    'LOG_LEVEL': 'INFO',
    'FEEDS': {
        'wikipedia_items.json': {  # Change 'britannica_items.json' to 'wikipedia_items.json' if you prefer
            'format': 'json',
            'encoding': 'utf8',
        }
    }
}

MAX_PAGES = 100000
