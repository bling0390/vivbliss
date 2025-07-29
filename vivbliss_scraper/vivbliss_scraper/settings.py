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
    'vivbliss_scraper.telegram.pipeline.TelegramUploadPipeline': 400,
}

# MongoDB Configuration
MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
MONGO_PORT = int(os.getenv('MONGO_PORT', '27017'))
MONGO_USERNAME = os.getenv('MONGO_USERNAME')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
MONGO_DATABASE = os.getenv('MONGO_DATABASE', 'vivbliss_db')

# Build MongoDB URI with optional authentication
if MONGO_USERNAME and MONGO_PASSWORD:
    MONGO_URI = f'mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DATABASE}?authSource=admin'
else:
    MONGO_URI = f'mongodb://{MONGO_HOST}:{MONGO_PORT}'

# Allow direct URI override
MONGO_URI = os.getenv('MONGO_URI', MONGO_URI)

# Telegram Configuration
TELEGRAM_API_ID = os.getenv('TELEGRAM_API_ID')
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH')
TELEGRAM_SESSION_NAME = os.getenv('TELEGRAM_SESSION_NAME', 'vivbliss_bot')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')  # Optional: For bot authentication
TELEGRAM_CHAT_ID = int(os.getenv('TELEGRAM_CHAT_ID', '0'))
TELEGRAM_ENABLE_UPLOAD = os.getenv('TELEGRAM_ENABLE_UPLOAD', 'True').lower() == 'true'

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
}