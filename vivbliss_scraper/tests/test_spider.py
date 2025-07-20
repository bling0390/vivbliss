import pytest
from scrapy.http import Request, HtmlResponse
from vivbliss_scraper.spiders.vivbliss import VivblissSpider


class TestVivblissSpider:
    @pytest.fixture
    def spider(self):
        return VivblissSpider()
    
    def test_spider_name(self, spider):
        assert spider.name == 'vivbliss'
    
    def test_spider_allowed_domains(self, spider):
        assert 'vivbliss.com' in spider.allowed_domains
    
    def test_spider_start_urls(self, spider):
        assert len(spider.start_urls) > 0
        assert all(url.startswith('https://vivbliss.com') for url in spider.start_urls)
    
    def test_parse_method_exists(self, spider):
        assert hasattr(spider, 'parse')
        assert callable(spider.parse)
    
    def test_parse_extracts_items(self, spider):
        html = '''
        <html>
            <body>
                <article>
                    <h2><a href="/post/1">Test Article</a></h2>
                    <div class="content">Test content here</div>
                    <time>2024-01-01</time>
                    <span class="category">Technology</span>
                </article>
            </body>
        </html>
        '''
        response = HtmlResponse(
            url='https://vivbliss.com',
            body=html.encode('utf-8')
        )
        
        items = list(spider.parse(response))
        assert len(items) > 0
        
        first_item = items[0]
        assert 'title' in first_item
        assert 'url' in first_item
        assert 'content' in first_item
        assert 'date' in first_item
        assert 'category' in first_item
    
    def test_follow_pagination(self, spider):
        html = '''
        <html>
            <body>
                <article>
                    <h2><a href="/post/1">Dummy Article</a></h2>
                    <div class="content">Some content</div>
                </article>
                <div class="pagination">
                    <a href="/page/2" class="next">Next</a>
                </div>
            </body>
        </html>
        '''
        response = HtmlResponse(
            url='https://vivbliss.com',
            body=html.encode('utf-8')
        )
        
        results = list(spider.parse(response))
        requests = [r for r in results if isinstance(r, Request)]
        
        assert len(requests) > 0
        assert any('page/2' in r.url for r in requests)