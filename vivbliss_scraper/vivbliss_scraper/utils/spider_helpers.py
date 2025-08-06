#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫辅助工具
提供爬虫开发中常用的工具函数和装饰器
"""

import time
import functools
from typing import Callable, Any, Dict, List, Optional
from datetime import datetime
import logging


def timing_decorator(func: Callable) -> Callable:
    """
    计时装饰器，用于测量函数执行时间
    
    Args:
        func: 要装饰的函数
        
    Returns:
        装饰后的函数
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        start_time = time.time()
        result = func(self, *args, **kwargs)
        end_time = time.time()
        
        duration = end_time - start_time
        if hasattr(self, 'logger'):
            self.logger.info(f"⏱️  {func.__name__} 执行耗时: {duration:.2f} 秒")
        
        return result
    return wrapper


def error_handler(default_return=None, log_error=True):
    """
    错误处理装饰器
    
    Args:
        default_return: 出错时的默认返回值
        log_error: 是否记录错误日志
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                if log_error and hasattr(self, 'logger'):
                    self.logger.error(f"❌ {func.__name__} 出现错误: {e}")
                return default_return
        return wrapper
    return decorator


class SpiderStats:
    """爬虫统计信息管理器"""
    
    def __init__(self):
        self.start_time = time.time()
        self.stats = {
            'categories_discovered': 0,
            'categories_processed': 0,
            'products_discovered': 0,
            'products_processed': 0,
            'errors': 0,
            'requests_sent': 0,
            'responses_received': 0
        }
        self.detailed_stats = {
            'categories': [],
            'products': [],
            'errors': []
        }
    
    def increment(self, stat_name: str, count: int = 1):
        """增加统计计数"""
        if stat_name in self.stats:
            self.stats[stat_name] += count
    
    def add_category_stat(self, category_info: Dict[str, Any]):
        """添加分类统计信息"""
        category_info['processed_at'] = datetime.now().isoformat()
        self.detailed_stats['categories'].append(category_info)
        self.increment('categories_processed')
    
    def add_product_stat(self, product_info: Dict[str, Any]):
        """添加产品统计信息"""
        product_info['processed_at'] = datetime.now().isoformat()
        self.detailed_stats['products'].append(product_info)
        self.increment('products_processed')
    
    def add_error_stat(self, error_info: Dict[str, Any]):
        """添加错误统计信息"""
        error_info['occurred_at'] = datetime.now().isoformat()
        self.detailed_stats['errors'].append(error_info)
        self.increment('errors')
    
    def get_runtime(self) -> float:
        """获取运行时间"""
        return time.time() - self.start_time
    
    def get_summary(self) -> Dict[str, Any]:
        """获取统计摘要"""
        runtime = self.get_runtime()
        
        summary = {
            'runtime_seconds': runtime,
            'total_categories': self.stats['categories_processed'],
            'total_products': self.stats['products_processed'],
            'total_errors': self.stats['errors'],
            'success_rate': self._calculate_success_rate(),
            'processing_speed': {
                'categories_per_second': self.stats['categories_processed'] / runtime if runtime > 0 else 0,
                'products_per_second': self.stats['products_processed'] / runtime if runtime > 0 else 0
            }
        }
        
        return summary
    
    def _calculate_success_rate(self) -> float:
        """计算成功率"""
        total_items = self.stats['categories_processed'] + self.stats['products_processed']
        if total_items == 0:
            return 0.0
        
        success_items = total_items - self.stats['errors']
        return (success_items / total_items) * 100


class RequestBuilder:
    """请求构建工具"""
    
    @staticmethod
    def build_category_request(url: str, category_info: Dict[str, Any], callback: Callable):
        """构建分类请求"""
        try:
            import scrapy
            return scrapy.Request(
                url=url,
                callback=callback,
                meta={
                    'category_name': category_info.get('text', '未知分类'),
                    'category_url': category_info.get('url'),
                    'level': category_info.get('level', 1),
                    'parent_category': category_info.get('parent_category'),
                    'request_type': 'category'
                }
            )
        except ImportError:
            # 如果没有scrapy，返回模拟对象
            class MockRequest:
                def __init__(self, url, callback, meta):
                    self.url = url
                    self.callback = callback
                    self.meta = meta
            
            return MockRequest(url, callback, {
                'category_name': category_info.get('text', '未知分类'),
                'category_url': category_info.get('url'),
                'level': category_info.get('level', 1),
                'parent_category': category_info.get('parent_category'),
                'request_type': 'category'
            })
    
    @staticmethod
    def build_product_request(url: str, product_info: Dict[str, Any], callback: Callable, category_path: str = None):
        """构建产品请求"""
        try:
            import scrapy
            return scrapy.Request(
                url=url,
                callback=callback,
                meta={
                    'product_name': product_info.get('text', '未知产品'),
                    'product_url': product_info.get('url'),
                    'category_path': category_path or '未分类',
                    'request_type': 'product'
                }
            )
        except ImportError:
            # 如果没有scrapy，返回模拟对象
            class MockRequest:
                def __init__(self, url, callback, meta):
                    self.url = url
                    self.callback = callback
                    self.meta = meta
            
            return MockRequest(url, callback, {
                'product_name': product_info.get('text', '未知产品'),
                'product_url': product_info.get('url'),
                'category_path': category_path or '未分类',
                'request_type': 'product'
            })


class ResponseAnalyzer:
    """响应分析工具"""
    
    @staticmethod
    def analyze_page_structure(response) -> Dict[str, Any]:
        """
        分析页面结构
        
        Args:
            response: Scrapy响应对象
            
        Returns:
            页面结构分析结果
        """
        try:
            analysis = {
                'url': response.url,
                'status_code': response.status,
                'content_length': len(response.body),
                'content_type': response.headers.get('Content-Type', b'unknown').decode(),
                'page_structure': {
                    'title_count': len(response.css('title')),
                    'h1_count': len(response.css('h1')),
                    'h2_count': len(response.css('h2')),
                    'div_count': len(response.css('div')),
                    'link_count': len(response.css('a')),
                    'image_count': len(response.css('img')),
                    'form_count': len(response.css('form')),
                },
                'potential_categories': ResponseAnalyzer._count_potential_categories(response),
                'potential_products': ResponseAnalyzer._count_potential_products(response)
            }
            
            return analysis
        except Exception as e:
            return {
                'error': str(e),
                'url': getattr(response, 'url', 'unknown'),
                'analysis_failed': True
            }
    
    @staticmethod
    def _count_potential_categories(response) -> int:
        """计算潜在分类数量"""
        category_selectors = [
            'a[href*="category"]',
            'a[href*="categories"]',
            '.category-link',
            '.nav-menu a'
        ]
        
        total_count = 0
        for selector in category_selectors:
            try:
                count = len(response.css(selector))
                total_count += count
            except Exception:
                continue
        
        return total_count
    
    @staticmethod
    def _count_potential_products(response) -> int:
        """计算潜在产品数量"""
        product_selectors = [
            'a[href*="product"]',
            '.product-item',
            '.product-card',
            '.shop-item'
        ]
        
        total_count = 0
        for selector in product_selectors:
            try:
                count = len(response.css(selector))
                total_count += count
            except Exception:
                continue
        
        return total_count


class LoggingHelper:
    """日志辅助工具"""
    
    @staticmethod
    def log_spider_start(logger, spider_name: str, config: Dict[str, Any]):
        """记录爬虫启动日志"""
        logger.info(f'\n🚀 开始爬取 {spider_name} 爬虫')
        logger.info(f'🎯 目标域名: {config.get("allowed_domains", [])}')
        logger.info(f'📋 起始URL数量: {len(config.get("start_urls", []))}')
        logger.info(f'⚙️  爬虫配置:')
        for key, value in config.items():
            if key not in ['allowed_domains', 'start_urls']:
                logger.info(f'   {key}: {value}')
    
    @staticmethod
    def log_spider_end(logger, spider_name: str, stats: SpiderStats):
        """记录爬虫结束日志"""
        summary = stats.get_summary()
        
        logger.info(f'\n🏁 爬虫 {spider_name} 结束运行')
        logger.info(f'📊 爬取统计:')
        logger.info(f'   总处理分类: {summary["total_categories"]} 个')
        logger.info(f'   总处理产品: {summary["total_products"]} 个')
        logger.info(f'   总耗时: {summary["runtime_seconds"]:.2f} 秒')
        logger.info(f'   成功率: {summary["success_rate"]:.1f}%')
        logger.info(f'   处理速度: {summary["processing_speed"]["products_per_second"]:.2f} 产品/秒')
    
    @staticmethod
    def log_page_processing(logger, response, processing_type: str = "页面"):
        """记录页面处理日志"""
        logger.info(f'\n=== 开始解析{processing_type} ===')
        logger.info(f'URL: {response.url}')
        logger.info(f'状态码: {response.status}')
        logger.info(f'响应大小: {len(response.body)} bytes')
        
        try:
            content_type = response.headers.get('Content-Type', b'unknown').decode()
            logger.info(f'Content-Type: {content_type}')
        except Exception:
            logger.info(f'Content-Type: unknown')
    
    @staticmethod
    def log_item_extraction(logger, item_type: str, item_data: Dict[str, Any], index: int = None):
        """记录数据项提取日志"""
        prefix = f"#{index}" if index is not None else ""
        logger.info(f'✅ 提取{item_type} {prefix}:')
        
        # 只记录关键字段，避免日志过长
        key_fields = {
            '分类': ['name', 'url', 'level', 'product_count'],
            '产品': ['name', 'url', 'price', 'stock_status', 'rating']
        }
        
        fields_to_log = key_fields.get(item_type, list(item_data.keys())[:5])
        
        for field in fields_to_log:
            if field in item_data and item_data[field] is not None:
                value = item_data[field]
                if isinstance(value, str) and len(value) > 50:
                    value = value[:47] + '...'
                logger.info(f'   {field}: {value}')
    
    @staticmethod
    def log_discovery_results(logger, discovery_type: str, discovered_items: List[Dict[str, Any]]):
        """记录发现结果日志"""
        logger.info(f'🔍 {discovery_type}发现结果:')
        logger.info(f'   总计发现: {len(discovered_items)} 个{discovery_type}')
        
        # 记录前几个发现的项目
        for i, item in enumerate(discovered_items[:5], 1):
            text = item.get('text', '未知')
            url = item.get('url', '未知')
            logger.info(f'   {i}. {text} -> {url}')
        
        if len(discovered_items) > 5:
            logger.info(f'   ... 还有 {len(discovered_items) - 5} 个{discovery_type}')


class RateLimiter:
    """速率限制器"""
    
    def __init__(self, max_requests_per_second: int = 1):
        self.max_requests_per_second = max_requests_per_second
        self.last_request_time = 0
        self.request_interval = 1.0 / max_requests_per_second
    
    def wait_if_needed(self):
        """如果需要，等待以限制请求速率"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.request_interval:
            wait_time = self.request_interval - time_since_last_request
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    def can_make_request(self) -> bool:
        """检查是否可以发出请求"""
        current_time = time.time()
        return (current_time - self.last_request_time) >= self.request_interval


class UrlPatternMatcher:
    """URL模式匹配器"""
    
    # 预定义的URL模式
    CATEGORY_PATTERNS = [
        r'/category/[\w\-/]+',
        r'/categories/[\w\-/]+',
        r'/cat/[\w\-/]+',
        r'/shop/[\w\-/]+',
        r'/collection/[\w\-/]+'
    ]
    
    PRODUCT_PATTERNS = [
        r'/product/[\w\-/]+',
        r'/products/[\w\-/]+',
        r'/item/[\w\-/]+',
        r'/shop/.+/product/.+'
    ]
    
    @classmethod
    def is_category_url(cls, url: str) -> bool:
        """判断是否是分类URL"""
        if not url:
            return False
        
        import re
        return any(re.search(pattern, url) for pattern in cls.CATEGORY_PATTERNS)
    
    @classmethod
    def is_product_url(cls, url: str) -> bool:
        """判断是否是产品URL"""
        if not url:
            return False
        
        import re
        return any(re.search(pattern, url) for pattern in cls.PRODUCT_PATTERNS)
    
    @classmethod
    def extract_category_slug(cls, url: str) -> Optional[str]:
        """从分类URL中提取slug"""
        if not cls.is_category_url(url):
            return None
        
        # 提取最后一个路径段作为slug
        parts = url.strip('/').split('/')
        return parts[-1] if parts else None
    
    @classmethod
    def extract_product_slug(cls, url: str) -> Optional[str]:
        """从产品URL中提取slug"""
        if not cls.is_product_url(url):
            return None
        
        # 提取最后一个路径段作为slug
        parts = url.strip('/').split('/')
        return parts[-1] if parts else None