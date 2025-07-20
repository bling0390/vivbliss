import scrapy


class VivblissItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    content = scrapy.Field()
    date = scrapy.Field()
    category = scrapy.Field()