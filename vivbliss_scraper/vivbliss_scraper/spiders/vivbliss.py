import scrapy
from vivbliss_scraper.items import VivblissItem, CategoryItem, ProductItem
import logging
import time
from urllib.parse import urljoin
import re
from datetime import datetime

# 导入辅助工具
from vivbliss_scraper.utils.extraction_helpers import (
    CategoryExtractor, ProductExtractor, LinkDiscovery, DataValidator
)
from vivbliss_scraper.utils.spider_helpers import (
    SpiderStats, RequestBuilder, ResponseAnalyzer, LoggingHelper,
    timing_decorator, error_handler
)
from vivbliss_scraper.utils.media_extractor import MediaExtractor, MediaValidator


class VivblissSpider(scrapy.Spider):
    name = 'vivbliss'
    allowed_domains = ['vivbliss.com']
    start_urls = ['https://vivbliss.com']
    
    def __init__(self, *args, **kwargs):
        super(VivblissSpider, self).__init__(*args, **kwargs)
        self.total_items = 0
        self.start_time = time.time()
        
        # 初始化统计管理器
        self.stats_manager = SpiderStats()
        
        # 初始化提取器
        self.category_extractor = CategoryExtractor()
        self.product_extractor = ProductExtractor()
        self.link_discovery = LinkDiscovery()
        self.media_extractor = MediaExtractor()
        self.media_validator = MediaValidator()
    
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
        # 使用日志辅助工具记录启动信息
        config = {
            'allowed_domains': self.allowed_domains,
            'start_urls': self.start_urls,
            'ROBOTSTXT_OBEY': getattr(self.settings, 'ROBOTSTXT_OBEY', '未设置'),
            'DOWNLOAD_DELAY': getattr(self.settings, 'DOWNLOAD_DELAY', '未设置'),
            'CONCURRENT_REQUESTS': getattr(self.settings, 'CONCURRENT_REQUESTS', '未设置'),
            'AUTOTHROTTLE_ENABLED': getattr(self.settings, 'AUTOTHROTTLE_ENABLED', '未设置')
        }
        
        LoggingHelper.log_spider_start(self.logger, self.name, config)
        
        for url in self.start_urls:
            self.logger.info(f'📤 发送请求到: {url}')
            self.stats_manager.increment('requests_sent')
            yield scrapy.Request(url, self.parse)
            
    def closed(self, reason):
        """Called when the spider is closed"""
        # 使用日志辅助工具记录结束信息
        LoggingHelper.log_spider_end(self.logger, self.name, self.stats_manager)
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
        
        # 🎯 优先发现和爬取分类
        self.logger.info(f'🔍 开始搜索产品分类...')
        for request in self.discover_categories(response):
            yield request
        
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
                
                # 🖼️ 提取媒体内容
                media_content = self.extract_media_from_article(article, response)
                item['images'] = media_content.get('images', [])
                item['videos'] = media_content.get('videos', [])
                item['media_files'] = item['images'] + item['videos']
                item['media_count'] = len(item['media_files'])
                
                # Log extracted item details
                self.logger.info(f'✅ 提取文章 #{i}:')
                self.logger.info(f'   标题: {item["title"][:50]}...' if len(item['title']) > 50 else f'   标题: {item["title"]}')
                self.logger.info(f'   URL: {item["url"]}')
                self.logger.info(f'   分类: {item["category"]}')
                self.logger.info(f'   日期: {item["date"]}')
                self.logger.info(f'   内容长度: {len(item["content"])} 字符')
                self.logger.info(f'   📷 图片数量: {len(item["images"])}')
                self.logger.info(f'   🎥 视频数量: {len(item["videos"])}')
                self.logger.info(f'   📁 媒体总数: {item["media_count"]}')
                
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
    
    @timing_decorator
    @error_handler(default_return=[])
    def discover_categories(self, response):
        """发现并爬取网站分类"""
        self.logger.info(f'🔍 正在分析页面结构，寻找分类导航...')
        
        # 使用链接发现工具
        discovered_links = self.link_discovery.discover_category_links(response)
        
        # 记录发现结果
        LoggingHelper.log_discovery_results(self.logger, '分类', discovered_links)
        
        # 更新统计
        self.stats_manager.increment('categories_discovered', len(discovered_links))
        
        if not discovered_links:
            self.logger.warning(f'⚠️  未发现任何分类链接，将尝试通用产品发现')
            # 如果没有发现分类，尝试直接寻找产品
            for request in self.discover_products(response):
                yield request
        else:
            # 为每个发现的分类生成请求
            for link_info in discovered_links:
                full_url = response.urljoin(link_info['url'])
                
                # 使用请求构建器创建请求
                request = RequestBuilder.build_category_request(
                    url=full_url,
                    category_info=link_info,
                    callback=self.parse_category
                )
                
                self.stats_manager.increment('requests_sent')
                yield request
    
    @timing_decorator
    @error_handler(default_return=[])
    def parse_category(self, response):
        """解析分类页面"""
        category_name = response.meta.get('category_name', '未知分类')
        level = response.meta.get('level', 1)
        
        # 记录页面处理开始
        LoggingHelper.log_page_processing(self.logger, response, f"分类页面: {category_name}")
        
        # 记录调度器状态
        self.log_scheduler_status()
        
        # 更新统计
        self.stats_manager.increment('responses_received')
        
        # 创建分类数据项
        category_item = CategoryItem()
        
        # 使用分类提取器提取数据
        category_item['name'] = self.category_extractor.extract_category_name(response) or category_name
        category_item['url'] = response.url
        category_item['level'] = level
        category_item['created_at'] = datetime.now().isoformat()
        
        # 提取其他分类信息
        category_item['description'] = self.category_extractor.extract_category_description(response)
        category_item['product_count'] = self.category_extractor.extract_product_count(response)
        category_item['image_url'] = self.category_extractor.extract_category_image(response)
        
        # 构建分类路径
        parent_category = response.meta.get('parent_category')
        category_item['path'] = self.category_extractor.build_category_path(
            category_item['name'], parent_category
        )
        category_item['parent_category'] = parent_category
        
        # 提取URL slug
        from vivbliss_scraper.utils.spider_helpers import UrlPatternMatcher
        category_item['slug'] = UrlPatternMatcher.extract_category_slug(response.url)
        
        # SEO元数据
        category_item['meta_title'] = response.css('title::text').get()
        category_item['meta_description'] = response.css('meta[name="description"]::attr(content)').get()
        
        # 记录提取的分类信息
        LoggingHelper.log_item_extraction(self.logger, '分类', category_item)
        
        # 更新统计
        self.stats_manager.add_category_stat({
            'name': category_item['name'],
            'url': category_item['url'],
            'level': category_item['level'],
            'product_count': category_item.get('product_count')
        })
        
        yield category_item
        
        # 🔍 寻找子分类
        self.logger.info(f'🔍 在分类 "{category_name}" 中搜索子分类...')
        subcategory_selectors = [
            '.subcategory a',
            '.sub-category a',
            '.category-children a',
            '.nested-category a',
            'ul.subcategories a'
        ]
        
        subcategories_found = 0
        for selector in subcategory_selectors:
            subcategory_links = response.css(selector)
            for link in subcategory_links:
                href = link.css('::attr(href)').get()
                text = link.css('::text').get()
                
                if href and text:
                    subcategories_found += 1
                    full_url = response.urljoin(href)
                    
                    self.logger.info(f'🔗 发现子分类: "{text}" -> {full_url}')
                    
                    yield scrapy.Request(
                        url=full_url,
                        callback=self.parse_category,
                        meta={
                            'category_name': text.strip(),
                            'category_url': href,
                            'level': level + 1,
                            'parent_category': category_item['path']
                        }
                    )
        
        if subcategories_found > 0:
            self.logger.info(f'✅ 在分类 "{category_name}" 中发现 {subcategories_found} 个子分类')
        
        # 🛍️  在当前分类页面中寻找产品
        self.logger.info(f'🛍️  在分类 "{category_name}" 中搜索产品...')
        
        # 获取调度器控制的产品请求
        for request in self.discover_products_with_priority(response, category_path):
            yield request
        
        # 🔄 处理分类页面分页
        pagination_selectors = [
            '.pagination a.next::attr(href)',
            'a.next-page::attr(href)',
            'a[rel="next"]::attr(href)',
            '.pager a.next::attr(href)'
        ]
        
        for selector in pagination_selectors:
            next_page = response.css(selector).get()
            if next_page:
                self.logger.info(f'📄 分类 "{category_name}" 发现下一页: {next_page}')
                yield scrapy.Request(
                    url=response.urljoin(next_page),
                    callback=self.parse_category,
                    meta=response.meta  # 传递相同的元数据
                )
                break
    
    @timing_decorator
    @error_handler(default_return=[])
    def discover_products(self, response, category_path=None):
        """在页面中发现产品链接"""
        self.logger.info(f'🛍️  开始搜索产品链接...')
        
        # 使用链接发现工具
        discovered_links = self.link_discovery.discover_product_links(response)
        
        # 记录发现结果
        LoggingHelper.log_discovery_results(self.logger, '产品', discovered_links)
        
        # 更新统计
        self.stats_manager.increment('products_discovered', len(discovered_links))
        
        if discovered_links:
            # 为每个发现的产品生成请求
            for link_info in discovered_links:
                full_url = response.urljoin(link_info['url'])
                
                # 使用请求构建器创建请求
                request = RequestBuilder.build_product_request(
                    url=full_url,
                    product_info=link_info,
                    callback=self.parse_product,
                    category_path=category_path
                )
                
                self.stats_manager.increment('requests_sent')
                yield request
        else:
            self.logger.warning(f'⚠️  未发现任何产品链接')
    
    @timing_decorator
    @error_handler(default_return=[])
    def parse_product(self, response):
        """解析产品详情页面"""
        category_path = response.meta.get('category_path', '未分类')
        
        # 记录页面处理开始
        LoggingHelper.log_page_processing(self.logger, response, f"产品页面")
        
        # 记录调度器状态
        self.log_scheduler_status()
        
        # 更新统计
        self.stats_manager.increment('responses_received')
        
        product_item = ProductItem()
        
        # 基础信息
        product_item['url'] = response.url
        product_item['category_path'] = category_path
        product_item['created_at'] = datetime.now().isoformat()
        
        # 使用产品提取器提取数据
        product_item['name'] = self.product_extractor.extract_product_name(response)
        product_item['brand'] = self.product_extractor.extract_brand(response)
        product_item['sku'] = self.product_extractor.extract_sku(response)
        
        # 提取价格信息
        price_info = self.product_extractor.extract_price_info(response)
        product_item['price'] = price_info['current_price']
        product_item['original_price'] = price_info['original_price']
        product_item['discount'] = price_info['discount']
        
        # 提取库存信息
        stock_info = self.product_extractor.extract_stock_info(response)
        product_item['stock_status'] = stock_info['stock_status']
        product_item['stock_quantity'] = stock_info['stock_quantity']
        
        # 提取描述和图片
        product_item['description'] = self.product_extractor.extract_description(response)
        product_item['image_urls'] = self.product_extractor.extract_images(response)
        if product_item['image_urls']:
            product_item['thumbnail_url'] = product_item['image_urls'][0]
        
        # 提取评分信息
        rating_info = self.product_extractor.extract_rating_info(response)
        product_item['rating'] = rating_info['rating']
        product_item['review_count'] = rating_info['review_count']
        
        # SEO 元数据
        product_item['meta_title'] = response.css('title::text').get()
        product_item['meta_description'] = response.css('meta[name="description"]::attr(content)').get()
        product_item['meta_keywords'] = response.css('meta[name="keywords"]::attr(content)').get()
        
        # 记录提取的产品信息
        LoggingHelper.log_item_extraction(self.logger, '产品', product_item)
        
        # 更新统计
        self.stats_manager.add_product_stat({
            'name': product_item['name'],
            'url': product_item['url'],
            'price': product_item.get('price'),
            'category_path': category_path
        })
        
        yield product_item
    
    def extract_media_from_article(self, article_selector, response):
        """从文章选择器中提取媒体内容"""
        try:
            # 创建一个临时响应对象用于媒体提取
            article_html = article_selector.get()
            if not article_html:
                return {'images': [], 'videos': []}
            
            # 使用媒体提取器提取内容
            from scrapy.http import HtmlResponse
            article_response = HtmlResponse(
                url=response.url,
                body=article_html.encode('utf-8'),
                encoding='utf-8'
            )
            
            # 提取图片和视频
            images = self.extract_images_from_article(article_response)
            videos = self.extract_videos_from_article(article_response)
            
            # 验证媒体URLs
            validated_images = self.validate_media_urls(images, response)
            validated_videos = self.validate_media_urls(videos, response)
            
            self.logger.debug(f"从文章中提取: {len(validated_images)} 张图片, {len(validated_videos)} 个视频")
            
            return {
                'images': validated_images,
                'videos': validated_videos
            }
            
        except Exception as e:
            self.logger.error(f"提取媒体内容时出错: {e}")
            return {'images': [], 'videos': []}
    
    def extract_images_from_article(self, response):
        """从文章中提取图片URLs"""
        return self.media_extractor.extract_images_from_response(response)
    
    def extract_videos_from_article(self, response):
        """从文章中提取视频URLs"""
        return self.media_extractor.extract_videos_from_response(response)
    
    def validate_media_urls(self, urls, response):
        """验证媒体URLs的有效性"""
        if not urls:
            return []
        
        validated_urls = []
        for url in urls:
            try:
                # 转换为绝对URL
                absolute_url = response.urljoin(url.strip())
                
                # 验证URL格式和类型
                if (self.media_validator.is_valid_image_url(absolute_url) or 
                    self.media_validator.is_valid_video_url(absolute_url)):
                    validated_urls.append(absolute_url)
                    
            except Exception as e:
                self.logger.debug(f"验证媒体URL时出错: {url}, 错误: {e}")
                continue
        
        return validated_urls
    
    def get_next_priority_request(self):
        """获取下一个优先级请求"""
        try:
            return self.priority_scheduler.get_next_request()
        except Exception as e:
            self.logger.error(f"获取优先级请求时出错: {e}")
            return None
    
    def log_scheduler_status(self):
        """记录调度器状态"""
        try:
            stats = self.priority_scheduler.get_scheduler_stats()
            self.logger.info(f"🎯 当前优先目录: {stats.get('current_priority_directory', '无')}")
            
            # 显示活跃目录
            active_dirs = stats.get('active_directories', [])
            if active_dirs:
                self.logger.info(f"📁 活跃目录 ({len(active_dirs)}): {', '.join(active_dirs[:3])}{'...' if len(active_dirs) > 3 else ''}")
                
        except Exception as e:
            self.logger.error(f"记录调度器状态时出错: {e}")
    
    @timing_decorator
    @error_handler(default_return=[])
    def parse_product_with_error_handling(self, response):
        """带有错误处理的产品解析方法"""
        try:
            # 调用原有的产品解析方法
            for item in self.parse_product(response):
                yield item
                
        except Exception as e:
            # 处理错误情况
            self.logger.error(f'❌ 产品页面解析失败: {response.url}, 错误: {e}')
            
            # 通知调度器产品处理失败
            self.priority_scheduler.mark_product_failed(response.url)
            
            # 更新统计
            self.stats_manager.increment('products_failed')