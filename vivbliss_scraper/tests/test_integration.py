import pytest
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from vivbliss_scraper.spiders.vivbliss import VivblissSpider
import mongomock


class TestSpiderIntegration:
    @pytest.fixture
    def crawler_process(self):
        settings = get_project_settings()
        settings.set('MONGO_URI', 'mongodb://localhost:27017')
        settings.set('MONGO_DATABASE', 'test_vivbliss')
        settings.set('CONCURRENT_REQUESTS', 1)
        settings.set('DOWNLOAD_DELAY', 0)
        return CrawlerProcess(settings)
    
    def test_spider_can_be_instantiated(self):
        spider = VivblissSpider()
        assert spider.name == 'vivbliss'
        assert 'vivbliss.com' in spider.allowed_domains
    
    @mongomock.patch(servers=(('localhost', 27017),))
    def test_spider_crawl_process(self, crawler_process):
        # This test verifies the spider can be initialized within the Scrapy framework
        spider = VivblissSpider()
        assert spider is not None
        assert hasattr(spider, 'parse')