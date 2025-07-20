import os
from dotenv import load_dotenv

load_dotenv()

BOT_NAME = 'vivbliss_scraper'

SPIDER_MODULES = ['vivbliss_scraper.spiders']
NEWSPIDER_MODULE = 'vivbliss_scraper.spiders'

USER_AGENT = 'vivbliss_scraper (+https://vivbliss.com)'

ROBOTSTXT_OBEY = True

DOWNLOAD_DELAY = 1

CONCURRENT_REQUESTS = 16

ITEM_PIPELINES = {
    'vivbliss_scraper.pipelines.MongoDBPipeline': 300,
}

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
MONGO_DATABASE = os.getenv('MONGO_DATABASE', 'vivbliss_db')

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
}