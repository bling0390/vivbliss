"""
爬虫配置管理模块
"""
import os
from typing import Dict, Any, Optional


class SpiderConfig:
    """爬虫配置管理类"""
    
    # 默认配置
    DEFAULT_CONFIG = {
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS': 4,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 2.0,
        'RETRY_TIMES': 3,
        'LOG_LEVEL': 'INFO',
        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
        'COOKIES_ENABLED': True,
        'HTTPCACHE_ENABLED': False
    }
    
    @classmethod
    def get_scrapy_settings(cls) -> Dict[str, Any]:
        """
        获取 Scrapy 配置字典
        
        Returns:
            Dict[str, Any]: Scrapy 配置字典
        """
        config = {}
        
        # 基础配置
        config['ROBOTSTXT_OBEY'] = cls._get_bool_env('ROBOTSTXT_OBEY', 
                                                     cls.DEFAULT_CONFIG['ROBOTSTXT_OBEY'])
        
        # 速率控制配置
        config['DOWNLOAD_DELAY'] = cls._get_int_env('DOWNLOAD_DELAY', 
                                                   cls.DEFAULT_CONFIG['DOWNLOAD_DELAY'])
        config['CONCURRENT_REQUESTS'] = cls._get_int_env('CONCURRENT_REQUESTS', 
                                                        cls.DEFAULT_CONFIG['CONCURRENT_REQUESTS'])
        
        # 自动限速配置
        config['AUTOTHROTTLE_ENABLED'] = cls._get_bool_env('AUTOTHROTTLE_ENABLED', 
                                                          cls.DEFAULT_CONFIG['AUTOTHROTTLE_ENABLED'])
        config['AUTOTHROTTLE_START_DELAY'] = cls._get_int_env('AUTOTHROTTLE_START_DELAY', 
                                                             cls.DEFAULT_CONFIG['AUTOTHROTTLE_START_DELAY'])
        config['AUTOTHROTTLE_MAX_DELAY'] = cls._get_int_env('AUTOTHROTTLE_MAX_DELAY', 
                                                           cls.DEFAULT_CONFIG['AUTOTHROTTLE_MAX_DELAY'])
        config['AUTOTHROTTLE_TARGET_CONCURRENCY'] = cls._get_float_env('AUTOTHROTTLE_TARGET_CONCURRENCY', 
                                                                      cls.DEFAULT_CONFIG['AUTOTHROTTLE_TARGET_CONCURRENCY'])
        config['AUTOTHROTTLE_DEBUG'] = cls._get_bool_env('AUTOTHROTTLE_DEBUG', False)
        
        # 重试配置
        config['RETRY_TIMES'] = cls._get_int_env('RETRY_TIMES', 
                                                cls.DEFAULT_CONFIG['RETRY_TIMES'])
        config['RETRY_HTTP_CODES'] = [500, 502, 503, 504, 408, 429]
        
        # 日志配置
        config['LOG_LEVEL'] = os.getenv('LOG_LEVEL', cls.DEFAULT_CONFIG['LOG_LEVEL'])
        config['LOG_ENABLED'] = True
        
        # 随机延迟配置
        config['RANDOMIZE_DOWNLOAD_DELAY'] = cls._get_float_env('RANDOMIZE_DOWNLOAD_DELAY', 
                                                               cls.DEFAULT_CONFIG['RANDOMIZE_DOWNLOAD_DELAY'])
        
        # Cookie 配置
        config['COOKIES_ENABLED'] = cls._get_bool_env('COOKIES_ENABLED', 
                                                     cls.DEFAULT_CONFIG['COOKIES_ENABLED'])
        config['COOKIES_DEBUG'] = cls._get_bool_env('COOKIES_DEBUG', False)
        
        # HTTP 缓存配置
        config['HTTPCACHE_ENABLED'] = cls._get_bool_env('HTTPCACHE_ENABLED', 
                                                       cls.DEFAULT_CONFIG['HTTPCACHE_ENABLED'])
        config['HTTPCACHE_EXPIRATION_SECS'] = cls._get_int_env('HTTPCACHE_EXPIRATION_SECS', 3600)
        config['HTTPCACHE_DIR'] = 'httpcache'
        config['HTTPCACHE_IGNORE_HTTP_CODES'] = [429, 503, 504, 500, 403, 404]
        
        return config
    
    @classmethod
    def get_spider_custom_settings(cls) -> Dict[str, Any]:
        """
        获取爬虫自定义配置
        
        Returns:
            Dict[str, Any]: 爬虫自定义配置字典
        """
        return {
            'DOWNLOAD_DELAY': cls._get_int_env('SPIDER_DOWNLOAD_DELAY', 2),
            'CONCURRENT_REQUESTS': cls._get_int_env('SPIDER_CONCURRENT_REQUESTS', 2),
            'AUTOTHROTTLE_ENABLED': True,
            'AUTOTHROTTLE_TARGET_CONCURRENCY': cls._get_float_env('SPIDER_AUTOTHROTTLE_TARGET_CONCURRENCY', 1.5),
            'AUTOTHROTTLE_MAX_DELAY': cls._get_int_env('SPIDER_AUTOTHROTTLE_MAX_DELAY', 10),
            'RANDOMIZE_DOWNLOAD_DELAY': cls._get_float_env('SPIDER_RANDOMIZE_DOWNLOAD_DELAY', 0.5),
            'LOG_LEVEL': os.getenv('SPIDER_LOG_LEVEL', 'INFO'),
        }
    
    @classmethod
    def get_middlewares_config(cls) -> Dict[str, int]:
        """
        获取中间件配置
        
        Returns:
            Dict[str, int]: 中间件配置字典
        """
        return {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        }
    
    @classmethod
    def validate_config(cls, config: Dict[str, Any]) -> Dict[str, str]:
        """
        验证配置有效性
        
        Args:
            config: 配置字典
            
        Returns:
            Dict[str, str]: 验证错误信息，空字典表示验证通过
        """
        errors = {}
        
        # 验证下载延迟
        if config.get('DOWNLOAD_DELAY', 0) < 1:
            errors['DOWNLOAD_DELAY'] = '下载延迟应至少为 1 秒'
        
        # 验证并发请求数
        if config.get('CONCURRENT_REQUESTS', 0) > 16:
            errors['CONCURRENT_REQUESTS'] = '并发请求数不应超过 16'
        
        # 验证自动限速配置
        if config.get('AUTOTHROTTLE_TARGET_CONCURRENCY', 0) <= 0:
            errors['AUTOTHROTTLE_TARGET_CONCURRENCY'] = '自动限速目标并发数应大于 0'
        
        # 验证重试次数
        if config.get('RETRY_TIMES', 0) < 0:
            errors['RETRY_TIMES'] = '重试次数不能为负数'
        
        return errors
    
    @staticmethod
    def _get_int_env(key: str, default: int) -> int:
        """获取整数类型的环境变量"""
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            return default
    
    @staticmethod
    def _get_float_env(key: str, default: float) -> float:
        """获取浮点数类型的环境变量"""
        try:
            return float(os.getenv(key, str(default)))
        except ValueError:
            return default
    
    @staticmethod
    def _get_bool_env(key: str, default: bool) -> bool:
        """获取布尔类型的环境变量"""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')
    
    @classmethod
    def print_config_summary(cls, config: Dict[str, Any]) -> None:
        """
        打印配置摘要
        
        Args:
            config: 配置字典
        """
        print("=== Scrapy 配置摘要 ===")
        print(f"ROBOTSTXT_OBEY: {config.get('ROBOTSTXT_OBEY')}")
        print(f"DOWNLOAD_DELAY: {config.get('DOWNLOAD_DELAY')} 秒")
        print(f"CONCURRENT_REQUESTS: {config.get('CONCURRENT_REQUESTS')}")
        print(f"AUTOTHROTTLE_ENABLED: {config.get('AUTOTHROTTLE_ENABLED')}")
        print(f"RETRY_TIMES: {config.get('RETRY_TIMES')}")
        print(f"LOG_LEVEL: {config.get('LOG_LEVEL')}")
        print("=" * 25)