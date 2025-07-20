import scrapy
from vivbliss_scraper.items import VivblissItem
import logging


class VivblissSpider(scrapy.Spider):
    name = 'vivbliss'
    allowed_domains = ['vivbliss.com']
    start_urls = ['https://vivbliss.com']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 2,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 2.0,
    }

    def parse(self, response):
        # Log the response status
        self.logger.info(f'Parsing page: {response.url}')
        
        # Multiple possible selectors for articles
        article_selectors = [
            'article',
            'div.post',
            'div.article',
            'div.blog-post',
            'div.entry'
        ]
        
        articles = None
        for selector in article_selectors:
            articles = response.css(selector)
            if articles:
                self.logger.info(f'Found {len(articles)} articles using selector: {selector}')
                break
        
        if not articles:
            self.logger.warning(f'No articles found on {response.url}')
            return
        
        for article in articles:
            item = VivblissItem()
            
            # Try multiple selectors for title
            title = (article.css('h2 a::text').get() or 
                    article.css('h2::text').get() or
                    article.css('h3 a::text').get() or
                    article.css('.title::text').get())
            
            # Try multiple selectors for URL
            url = (article.css('h2 a::attr(href)').get() or
                  article.css('h3 a::attr(href)').get() or
                  article.css('a::attr(href)').get())
            
            # Try multiple selectors for content
            content = (article.css('div.content::text').get() or
                      article.css('div.excerpt::text').get() or
                      article.css('p::text').get() or
                      article.css('::text').getall())
            
            if isinstance(content, list):
                content = ' '.join(content).strip()
            
            # Try multiple selectors for date
            date = (article.css('time::text').get() or
                   article.css('time::attr(datetime)').get() or
                   article.css('.date::text').get() or
                   article.css('.published::text').get())
            
            # Try multiple selectors for category
            category = (article.css('span.category::text').get() or
                       article.css('.category a::text').get() or
                       article.css('.tag::text').get() or
                       'Uncategorized')
            
            # Only yield item if we have at least title and URL
            if title and url:
                item['title'] = title.strip()
                item['url'] = response.urljoin(url)
                item['content'] = content.strip() if content else ''
                item['date'] = date.strip() if date else ''
                item['category'] = category.strip()
                
                yield item
            else:
                self.logger.warning(f'Skipping article without title or URL')

        # Multiple pagination selectors
        pagination_selectors = [
            'div.pagination a.next::attr(href)',
            'a.next::attr(href)',
            'a[rel="next"]::attr(href)',
            '.pagination a[aria-label="Next"]::attr(href)',
            'a:contains("Next")::attr(href)'
        ]
        
        next_page = None
        for selector in pagination_selectors:
            next_page = response.css(selector).get()
            if next_page:
                self.logger.info(f'Found next page: {next_page}')
                yield response.follow(next_page, self.parse)
                break