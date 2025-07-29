import os
from dotenv import load_dotenv

load_dotenv()

BOT_NAME = 'vivbliss_scraper'

SPIDER_MODULES = ['vivbliss_scraper.spiders']
NEWSPIDER_MODULE = 'vivbliss_scraper.spiders'

USER_AGENT = 'vivbliss_scraper (+https://vivbliss.com)'

# Robot.txt obey setting - set to False to bypass robots.txt restrictions
ROBOTSTXT_OBEY = False

# Download delay - increased to reduce server load and avoid rate limiting
DOWNLOAD_DELAY = int(os.getenv('DOWNLOAD_DELAY', '3'))  # Default 3 seconds

# Concurrent requests - reduced to be more respectful to servers
CONCURRENT_REQUESTS = int(os.getenv('CONCURRENT_REQUESTS', '4'))  # Default 4

# Enable and configure AutoThrottle for automatic delay adjustment
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0
AUTOTHROTTLE_DEBUG = os.getenv('AUTOTHROTTLE_DEBUG', 'False').lower() == 'true'

# Retry settings
RETRY_TIMES = int(os.getenv('RETRY_TIMES', '3'))
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_ENABLED = True

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
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
}

# Random delay between requests (0.5 * to 1.5 * DOWNLOAD_DELAY)
RANDOMIZE_DOWNLOAD_DELAY = 0.5

# Cookies settings
COOKIES_ENABLED = True
COOKIES_DEBUG = os.getenv('COOKIES_DEBUG', 'False').lower() == 'true'

# HTTP cache settings for development
HTTPCACHE_ENABLED = os.getenv('HTTPCACHE_ENABLED', 'False').lower() == 'true'
HTTPCACHE_EXPIRATION_SECS = 3600  # 1 hour
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = [429, 503, 504, 500, 403, 404]