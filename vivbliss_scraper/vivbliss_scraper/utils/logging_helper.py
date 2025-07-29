"""
日志辅助工具模块
"""
import time
import logging
from typing import Dict, Any, Optional, List
from scrapy import Spider


class SpiderLoggingHelper:
    """爬虫日志辅助类"""
    
    def __init__(self, spider: Spider):
        """
        初始化日志助手
        
        Args:
            spider: Scrapy 爬虫实例
        """
        self.spider = spider
        self.logger = spider.logger
        
    def log_spider_start(self) -> None:
        """记录爬虫启动信息"""
        self.logger.info(f'\n🚀 开始爬取 {self.spider.name} 爬虫')
        self.logger.info(f'🎯 目标域名: {", ".join(self.spider.allowed_domains)}')
        self.logger.info(f'📋 起始URL数量: {len(self.spider.start_urls)}')
        
        # 记录配置信息
        self._log_spider_settings()
        
        # 记录起始URL
        for url in self.spider.start_urls:
            self.logger.info(f'📤 发送请求到: {url}')
    
    def log_spider_end(self, reason: str, total_items: int, start_time: float) -> None:
        """
        记录爬虫结束信息
        
        Args:
            reason: 结束原因
            total_items: 总提取项目数
            start_time: 开始时间戳
        """
        end_time = time.time()
        duration = end_time - start_time
        
        self.logger.info(f'\n🏁 爬虫 {self.spider.name} 结束运行')
        self.logger.info(f'📊 爬取统计:')
        self.logger.info(f'   总提取文章: {total_items} 篇')
        self.logger.info(f'   总耗时: {duration:.2f} 秒')
        self.logger.info(f'   平均速度: {total_items/duration:.2f} 文章/秒' if duration > 0 else '   平均速度: N/A')
        self.logger.info(f'   结束原因: {reason}')
    
    def log_response_info(self, response) -> None:
        """
        记录响应信息
        
        Args:
            response: Scrapy 响应对象
        """
        self.logger.info(f'\n=== 开始解析页面 ===')
        self.logger.info(f'URL: {response.url}')
        self.logger.info(f'状态码: {response.status}')
        self.logger.info(f'响应大小: {len(response.body)} bytes')
        self.logger.info(f'Content-Type: {response.headers.get("Content-Type", b"unknown").decode()}')
        
        # 记录请求延迟信息
        download_delay = getattr(self.spider.settings, 'DOWNLOAD_DELAY', 1)
        self.logger.info(f'当前下载延迟: {download_delay} 秒')
    
    def log_articles_found(self, articles: List, selector_used: str) -> None:
        """
        记录找到的文章信息
        
        Args:
            articles: 文章列表
            selector_used: 使用的选择器
        """
        if articles:
            self.logger.info(f'Found {len(articles)} articles using selector: {selector_used}')
            self.logger.info(f'🔄 开始处理 {len(articles)} 篇文章...')
        else:
            self.logger.warning(f'❌ 未找到任何文章')
    
    def log_no_articles_found(self, response) -> None:
        """
        记录未找到文章的调试信息
        
        Args:
            response: Scrapy 响应对象
        """
        self.logger.warning(f'❌ 在页面 {response.url} 上未找到任何文章')
        self.logger.warning(f'页面内容长度: {len(response.text)} 字符')
        
        # 记录页面结构用于调试
        self.logger.debug(f'页面标题: {response.css("title::text").get()}')
        self.logger.debug(f'页面主要标签数量: h1={len(response.css("h1"))}, h2={len(response.css("h2"))}, div={len(response.css("div"))}')
    
    def log_item_extracted(self, item: Dict[str, Any], index: int) -> None:
        """
        记录提取的项目信息
        
        Args:
            item: 提取的项目
            index: 项目索引
        """
        self.logger.info(f'✅ 提取文章 #{index}:')
        title = item.get('title', '')
        self.logger.info(f'   标题: {title[:50]}...' if len(title) > 50 else f'   标题: {title}')
        self.logger.info(f'   URL: {item.get("url", "")}')
        self.logger.info(f'   分类: {item.get("category", "")}')
        self.logger.info(f'   日期: {item.get("date", "")}')
        self.logger.info(f'   内容长度: {len(item.get("content", ""))} 字符')
    
    def log_item_skipped(self, title: Optional[str], url: Optional[str], index: int) -> None:
        """
        记录跳过的项目信息
        
        Args:
            title: 标题
            url: URL
            index: 项目索引
        """
        self.logger.warning(f'❌ 跳过第 {index} 篇文章 - 缺少标题或URL')
        self.logger.warning(f'   标题: {title or "(空)"}  URL: {url or "(空)"}')
    
    def log_processing_summary(self, extracted_items: int, skipped_items: int, 
                             processing_time: float) -> None:
        """
        记录处理摘要
        
        Args:
            extracted_items: 提取的项目数
            skipped_items: 跳过的项目数  
            processing_time: 处理时间
        """
        self.logger.info(f'\n=== 页面处理完成 ===')
        self.logger.info(f'✅ 成功提取: {extracted_items} 篇文章')
        self.logger.info(f'❌ 跳过文章: {skipped_items} 篇')
        self.logger.info(f'⏱️  处理耗时: {processing_time:.2f} 秒')
        self.logger.info(f'📊 提取效率: {extracted_items/processing_time:.1f} 文章/秒' if processing_time > 0 else '📊 提取效率: N/A')
    
    def log_pagination_info(self, next_page: Optional[str], selector_index: int, 
                           full_url: str, extracted_items: int) -> None:
        """
        记录分页信息
        
        Args:
            next_page: 下一页链接
            selector_index: 选择器索引
            full_url: 完整URL
            extracted_items: 提取的项目数
        """
        if next_page:
            self.logger.info(f'🔗 发现下一页链接 (选择器 #{selector_index}): {next_page}')
            self.logger.info(f'🔗 完整下一页URL: {full_url}')
            
            if extracted_items > 0:
                self.logger.info(f'➡️  继续爬取下一页...')
            else:
                self.logger.warning(f'⚠️  本页未提取到文章，停止分页爬取')
        else:
            self.logger.info(f'🏁 未找到下一页链接，可能已到达最后一页')
    
    def _log_spider_settings(self) -> None:
        """记录爬虫设置信息"""
        self.logger.info(f'⚙️  爬虫配置:')
        self.logger.info(f'   ROBOTSTXT_OBEY: {getattr(self.spider.settings, "ROBOTSTXT_OBEY", "未设置")}')
        self.logger.info(f'   DOWNLOAD_DELAY: {getattr(self.spider.settings, "DOWNLOAD_DELAY", "未设置")} 秒')
        self.logger.info(f'   CONCURRENT_REQUESTS: {getattr(self.spider.settings, "CONCURRENT_REQUESTS", "未设置")}')
        self.logger.info(f'   AUTOTHROTTLE_ENABLED: {getattr(self.spider.settings, "AUTOTHROTTLE_ENABLED", "未设置")}')


class LoggingMixin:
    """日志记录混入类"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logging_helper = None
        
    def setup_logging_helper(self):
        """设置日志助手"""
        if hasattr(self, 'logger'):
            self.logging_helper = SpiderLoggingHelper(self)
    
    def log_debug_info(self, message: str, extra_data: Optional[Dict] = None) -> None:
        """记录调试信息"""
        if hasattr(self, 'logger'):
            self.logger.debug(message)
            if extra_data:
                for key, value in extra_data.items():
                    self.logger.debug(f'  {key}: {value}')
    
    def log_performance_metric(self, metric_name: str, value: float, unit: str = '') -> None:
        """记录性能指标"""
        if hasattr(self, 'logger'):
            self.logger.info(f'📈 {metric_name}: {value:.2f} {unit}')
    
    def log_error_with_context(self, error: Exception, context: Dict[str, Any]) -> None:
        """记录带上下文的错误信息"""
        if hasattr(self, 'logger'):
            self.logger.error(f'❌ 错误: {str(error)}')
            self.logger.error(f'📍 错误上下文:')
            for key, value in context.items():
                self.logger.error(f'  {key}: {value}')