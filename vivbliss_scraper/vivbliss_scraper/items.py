import scrapy


class VivblissItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    content = scrapy.Field()
    date = scrapy.Field()
    category = scrapy.Field()


class VivblissMediaItem(scrapy.Item):
    title = scrapy.Field()
    source_url = scrapy.Field()
    image_urls = scrapy.Field()
    video_urls = scrapy.Field()
    images = scrapy.Field()  # For downloaded images info
    videos = scrapy.Field()  # For downloaded videos info
    category = scrapy.Field()
    date = scrapy.Field()
    download_errors = scrapy.Field()  # For tracking failed downloads
    telegram_upload_status = scrapy.Field()  # For tracking upload status