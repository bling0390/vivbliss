import scrapy
from vivbliss_scraper.items import VivblissItem
import logging
import time
from urllib.parse import urljoin


class VivblissSpider(scrapy.Spider):
    name = 'vivbliss'
    allowed_domains = ['vivbliss.com']
    start_urls = ['https://vivbliss.com']
    
    def __init__(self, *args, **kwargs):
        super(VivblissSpider, self).__init__(*args, **kwargs)
        self.total_items = 0
        self.start_time = time.time()
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2,  # Increased from 1 to 2 seconds
        'CONCURRENT_REQUESTS': 2,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.5,  # Reduced for gentler crawling
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
        'LOG_LEVEL': 'INFO',
    }
    
    def start_requests(self):
        """Override start_requests to add initial logging"""
        self.logger.info(f'\n🚀 开始爬取 {self.name} 爬虫')
        self.logger.info(f'🎯 目标域名: {", ".join(self.allowed_domains)}')
        self.logger.info(f'📋 起始URL数量: {len(self.start_urls)}')
        
        # Log current settings
        self.logger.info(f'⚙️  爬虫配置:')
        self.logger.info(f'   ROBOTSTXT_OBEY: {getattr(self.settings, "ROBOTSTXT_OBEY", "未设置")}')
        self.logger.info(f'   DOWNLOAD_DELAY: {getattr(self.settings, "DOWNLOAD_DELAY", "未设置")} 秒')
        self.logger.info(f'   CONCURRENT_REQUESTS: {getattr(self.settings, "CONCURRENT_REQUESTS", "未设置")}')
        self.logger.info(f'   AUTOTHROTTLE_ENABLED: {getattr(self.settings, "AUTOTHROTTLE_ENABLED", "未设置")}')
        
        for url in self.start_urls:
            self.logger.info(f'📤 发送请求到: {url}')
            yield scrapy.Request(url, self.parse)
            
    def closed(self, reason):
        """Called when the spider is closed"""
        end_time = time.time()
        duration = end_time - self.start_time
        
        self.logger.info(f'\n🏁 爬虫 {self.name} 结束运行')
        self.logger.info(f'📊 爬取统计:')
        self.logger.info(f'   总提取文章: {self.total_items} 篇')
        self.logger.info(f'   总耗时: {duration:.2f} 秒')
        self.logger.info(f'   平均速度: {self.total_items/duration:.2f} 文章/秒' if duration > 0 else '   平均速度: N/A')
        self.logger.info(f'   结束原因: {reason}')

    def parse(self, response):
        # Log detailed response information
        self.logger.info(f'\n=== 开始解析页面 ===')
        self.logger.info(f'URL: {response.url}')
        self.logger.info(f'状态码: {response.status}')
        self.logger.info(f'响应大小: {len(response.body)} bytes')
        self.logger.info(f'Content-Type: {response.headers.get("Content-Type", b"unknown").decode()}')
        
        # Log request delay information
        download_delay = getattr(self.settings, 'DOWNLOAD_DELAY', 1)
        self.logger.info(f'当前下载延迟: {download_delay} 秒')
        
        # Start processing time
        start_time = time.time()
        
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
            self.logger.warning(f'❌ 在页面 {response.url} 上未找到任何文章')
            self.logger.warning(f'页面内容长度: {len(response.text)} 字符')
            
            # Log page structure for debugging
            self.logger.debug(f'页面标题: {response.css("title::text").get()}')
            self.logger.debug(f'页面主要标签数量: h1={len(response.css("h1"))}, h2={len(response.css("h2"))}, div={len(response.css("div"))}')
            return
        
        extracted_items = 0
        skipped_items = 0
        
        self.logger.info(f'🔄 开始处理 {len(articles)} 篇文章...')
        
        for i, article in enumerate(articles, 1):
            self.logger.debug(f'处理第 {i}/{len(articles)} 篇文章')
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
                
                # Log extracted item details
                self.logger.info(f'✅ 提取文章 #{i}:')
                self.logger.info(f'   标题: {item["title"][:50]}...' if len(item['title']) > 50 else f'   标题: {item["title"]}')
                self.logger.info(f'   URL: {item["url"]}')
                self.logger.info(f'   分类: {item["category"]}')
                self.logger.info(f'   日期: {item["date"]}')
                self.logger.info(f'   内容长度: {len(item["content"])} 字符')
                
                extracted_items += 1
                self.total_items += 1
                yield item
            else:
                self.logger.warning(f'❌ 跳过第 {i} 篇文章 - 缺少标题或URL')
                self.logger.warning(f'   标题: {title or "(空)"}  URL: {url or "(空)"}')
                skipped_items += 1

        # Multiple pagination selectors
        pagination_selectors = [
            'div.pagination a.next::attr(href)',
            'a.next::attr(href)',
            'a[rel="next"]::attr(href)',
            '.pagination a[aria-label="Next"]::attr(href)',
            'a:contains("Next")::attr(href)'
        ]
        
        # Log processing summary
        processing_time = time.time() - start_time
        self.logger.info(f'\n=== 页面处理完成 ===')
        self.logger.info(f'✅ 成功提取: {extracted_items} 篇文章')
        self.logger.info(f'❌ 跳过文章: {skipped_items} 篇')
        self.logger.info(f'⏱️  处理耗时: {processing_time:.2f} 秒')
        self.logger.info(f'📊 提取效率: {extracted_items/processing_time:.1f} 文章/秒' if processing_time > 0 else '📊 提取效率: N/A')
        
        # Enhanced pagination handling
        next_page = None
        for i, selector in enumerate(pagination_selectors, 1):
            next_page = response.css(selector).get()
            if next_page:
                self.logger.info(f'🔗 发现下一页链接 (选择器 #{i}): {next_page}')
                full_next_url = response.urljoin(next_page)
                self.logger.info(f'🔗 完整下一页URL: {full_next_url}')
                
                # Check if we should continue pagination
                if extracted_items > 0:  # Only continue if we found articles
                    self.logger.info(f'➡️  继续爬取下一页...')
                    yield response.follow(next_page, self.parse)
                else:
                    self.logger.warning(f'⚠️  本页未提取到文章，停止分页爬取')
                break
        
        if not next_page:
            self.logger.info(f'🏁 未找到下一页链接，可能已到达最后一页')
            self.logger.debug(f'尝试的分页选择器: {", ".join(pagination_selectors)}')