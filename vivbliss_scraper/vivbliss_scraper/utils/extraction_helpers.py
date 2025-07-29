#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据提取辅助工具
提供可重用的数据提取、验证和格式化功能
"""

import re
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from urllib.parse import urljoin as urllib_urljoin


class DataExtractor:
    """数据提取器，包含各种通用的数据提取方法"""
    
    @staticmethod
    def extract_text_with_fallback(response, selectors: List[str]) -> Optional[str]:
        """
        使用多个选择器提取文本，返回第一个成功的结果
        
        Args:
            response: Scrapy响应对象
            selectors: CSS选择器列表
            
        Returns:
            提取到的文本，如果都失败则返回None
        """
        for selector in selectors:
            try:
                text = response.css(selector).get()
                if text and text.strip():
                    return text.strip()
            except Exception:
                continue
        return None
    
    @staticmethod
    def extract_all_text_with_fallback(response, selectors: List[str]) -> List[str]:
        """
        使用多个选择器提取所有文本，返回第一个成功的结果列表
        
        Args:
            response: Scrapy响应对象
            selectors: CSS选择器列表
            
        Returns:
            提取到的文本列表，如果都失败则返回空列表
        """
        for selector in selectors:
            try:
                texts = response.css(selector).getall()
                if texts:
                    return [text.strip() for text in texts if text.strip()]
            except Exception:
                continue
        return []
    
    @staticmethod
    def extract_price_from_text(text: str) -> Optional[str]:
        """
        从文本中提取价格信息
        
        Args:
            text: 包含价格的文本
            
        Returns:
            提取到的价格字符串，如果失败则返回None
        """
        if not text:
            return None
        
        # 价格模式匹配
        price_patterns = [
            r'[¥$€£]\d+\.?\d*',  # 货币符号 + 数字
            r'\d+\.?\d*\s*[¥$€£]',  # 数字 + 货币符号
            r'\d+\.?\d*'  # 纯数字
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group().strip()
        
        return text.strip()
    
    @staticmethod
    def extract_numbers_from_text(text: str) -> List[str]:
        """
        从文本中提取所有数字
        
        Args:
            text: 输入文本
            
        Returns:
            数字字符串列表
        """
        if not text:
            return []
        
        return re.findall(r'\d+\.?\d*', text)
    
    @staticmethod
    def clean_description_text(text: Union[str, List[str]]) -> str:
        """
        清理产品描述文本
        
        Args:
            text: 文本字符串或文本列表
            
        Returns:
            清理后的文本
        """
        if isinstance(text, list):
            text = ' '.join(text)
        
        if not text:
            return ''
        
        # 去除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 去除HTML标签（如果有）
        text = re.sub(r'<[^>]+>', '', text)
        
        return text.strip()
    
    @staticmethod
    def build_category_path(category_name: str, parent_path: Optional[str] = None) -> str:
        """
        构建分类路径
        
        Args:
            category_name: 分类名称
            parent_path: 父分类路径
            
        Returns:
            完整的分类路径
        """
        if parent_path:
            return f"{parent_path}/{category_name}"
        return category_name
    
    @staticmethod
    def validate_url(url: str, allowed_domains: List[str] = None) -> bool:
        """
        验证URL有效性
        
        Args:
            url: 要验证的URL
            allowed_domains: 允许的域名列表
            
        Returns:
            URL是否有效
        """
        if not url:
            return False
        
        # 相对URL被认为是有效的
        if url.startswith('/'):
            return True
        
        # 绝对URL需要检查域名
        if url.startswith('http'):
            if allowed_domains:
                return any(domain in url for domain in allowed_domains)
            return True
        
        return False
    
    @staticmethod
    def safe_urljoin(base_url: str, relative_url: str) -> str:
        """
        安全的URL连接
        
        Args:
            base_url: 基础URL
            relative_url: 相对URL
            
        Returns:
            完整的URL
        """
        try:
            return urllib_urljoin(base_url, relative_url)
        except Exception:
            # 如果urllib_urljoin失败，使用简单的字符串连接
            if relative_url.startswith('http'):
                return relative_url
            elif relative_url.startswith('/'):
                return base_url.rstrip('/') + relative_url
            else:
                return base_url.rstrip('/') + '/' + relative_url


class CategoryExtractor(DataExtractor):
    """分类数据提取器"""
    
    @classmethod
    def extract_category_name(cls, response) -> Optional[str]:
        """提取分类名称"""
        selectors = [
            '.category-title::text',
            '.category-name::text',
            'h1::text',
            'title::text'
        ]
        
        name = cls.extract_text_with_fallback(response, selectors)
        if name:
            # 清理分类名称，去除多余的文字
            name = re.sub(r'\s*-\s*.*$', '', name)  # 去除标题中的网站名等
            name = re.sub(r'\s*\|\s*.*$', '', name)  # 去除管道符后的内容
        
        return name
    
    @classmethod
    def extract_category_description(cls, response) -> Optional[str]:
        """提取分类描述"""
        selectors = [
            '.category-description::text',
            '.category-intro::text',
            'meta[name="description"]::attr(content)',
            '.description::text'
        ]
        
        return cls.extract_text_with_fallback(response, selectors)
    
    @classmethod
    def extract_product_count(cls, response) -> Optional[int]:
        """提取产品数量"""
        selectors = [
            '.product-count::text',
            '.results-count::text',
            '.total-products::text',
            '.items-count::text'
        ]
        
        for selector in selectors:
            text = response.css(selector).get()
            if text:
                numbers = cls.extract_numbers_from_text(text)
                if numbers:
                    try:
                        return int(numbers[0])
                    except (ValueError, IndexError):
                        continue
        
        return None
    
    @classmethod
    def extract_category_image(cls, response) -> Optional[str]:
        """提取分类图片"""
        selectors = [
            '.category-image img::attr(src)',
            '.category-banner img::attr(src)',
            '.category-hero img::attr(src)',
            '.banner-image::attr(src)'
        ]
        
        return cls.extract_text_with_fallback(response, selectors)


class ProductExtractor(DataExtractor):
    """产品数据提取器"""
    
    @classmethod
    def extract_product_name(cls, response) -> Optional[str]:
        """提取产品名称"""
        selectors = [
            'h1.product-title::text',
            '.product-name::text',
            'h1::text',
            '.title::text'
        ]
        
        return cls.extract_text_with_fallback(response, selectors)
    
    @classmethod
    def extract_brand(cls, response) -> Optional[str]:
        """提取品牌信息"""
        selectors = [
            '.brand::text',
            '.product-brand::text',
            '[class*="brand"]::text',
            '.manufacturer::text'
        ]
        
        return cls.extract_text_with_fallback(response, selectors)
    
    @classmethod
    def extract_sku(cls, response) -> Optional[str]:
        """提取SKU"""
        selectors = [
            '.sku::text',
            '.product-sku::text',
            '[class*="sku"]::text',
            '.product-id::text'
        ]
        
        return cls.extract_text_with_fallback(response, selectors)
    
    @classmethod
    def extract_price_info(cls, response) -> Dict[str, Optional[str]]:
        """提取价格信息"""
        price_info = {
            'current_price': None,
            'original_price': None,
            'discount': None
        }
        
        # 当前价格
        current_price_selectors = [
            '.price .current-price::text',
            '.product-price::text',
            '.price::text',
            '[class*="price"]:not([class*="original"]):not([class*="old"])::text'
        ]
        
        price_info['current_price'] = cls.extract_text_with_fallback(
            response, current_price_selectors
        )
        
        # 原价
        original_price_selectors = [
            '.price .original-price::text',
            '.old-price::text',
            '.was-price::text',
            '[class*="original-price"]::text'
        ]
        
        price_info['original_price'] = cls.extract_text_with_fallback(
            response, original_price_selectors
        )
        
        # 折扣信息
        discount_selectors = [
            '.discount::text',
            '.sale-percentage::text',
            '.off::text',
            '[class*="discount"]::text'
        ]
        
        price_info['discount'] = cls.extract_text_with_fallback(
            response, discount_selectors
        )
        
        return price_info
    
    @classmethod
    def extract_stock_info(cls, response) -> Dict[str, Optional[Union[str, int]]]:
        """提取库存信息"""
        stock_info = {
            'stock_status': None,
            'stock_quantity': None
        }
        
        # 库存状态
        status_selectors = [
            '.stock-status::text',
            '.availability::text',
            '.in-stock::text',
            '.out-of-stock::text',
            '[class*="stock"]::text'
        ]
        
        stock_info['stock_status'] = cls.extract_text_with_fallback(
            response, status_selectors
        )
        
        # 库存数量
        quantity_selectors = [
            '.stock-quantity::text',
            '.quantity-available::text',
            '.inventory-count::text'
        ]
        
        quantity_text = cls.extract_text_with_fallback(response, quantity_selectors)
        if quantity_text:
            numbers = cls.extract_numbers_from_text(quantity_text)
            if numbers:
                try:
                    stock_info['stock_quantity'] = int(numbers[0])
                except (ValueError, IndexError):
                    pass
        
        return stock_info
    
    @classmethod
    def extract_description(cls, response) -> Optional[str]:
        """提取产品描述"""
        selectors = [
            '.product-description::text',
            '.description::text',
            '.product-content::text',
            '.product-details::text'
        ]
        
        # 尝试提取单个描述
        description = cls.extract_text_with_fallback(response, selectors)
        if not description:
            # 尝试提取多段描述
            multi_selectors = [
                '.product-description p::text',
                '.description p::text',
                '.product-content p::text'
            ]
            
            for selector in multi_selectors:
                texts = response.css(selector).getall()
                if texts:
                    description = ' '.join(texts)
                    break
        
        return cls.clean_description_text(description) if description else None
    
    @classmethod
    def extract_images(cls, response) -> List[str]:
        """提取产品图片"""
        selectors = [
            '.product-images img::attr(src)',
            '.product-gallery img::attr(src)',
            '.product-image img::attr(src)',
            'img[alt*="product"]::attr(src)',
            '.gallery img::attr(src)'
        ]
        
        images = []
        for selector in selectors:
            found_images = response.css(selector).getall()
            for img in found_images:
                if img and img not in images:
                    # 转换为绝对URL
                    full_url = cls.safe_urljoin(response.url, img)
                    images.append(full_url)
        
        return images
    
    @classmethod
    def extract_rating_info(cls, response) -> Dict[str, Optional[Union[str, int, float]]]:
        """提取评分信息"""
        rating_info = {
            'rating': None,
            'review_count': None
        }
        
        # 评分
        rating_selectors = [
            '.rating::text',
            '.average-rating::text',
            '[class*="rating"]:not([class*="count"])::text',
            '.stars-rating::attr(data-rating)'
        ]
        
        rating_text = cls.extract_text_with_fallback(response, rating_selectors)
        if rating_text:
            numbers = re.findall(r'\d+\.?\d*', rating_text)
            if numbers:
                try:
                    rating_info['rating'] = float(numbers[0])
                except (ValueError, IndexError):
                    pass
        
        # 评价数量
        review_selectors = [
            '.review-count::text',
            '.reviews-count::text',
            '[class*="review"][class*="count"]::text',
            '.rating-count::text'
        ]
        
        review_text = cls.extract_text_with_fallback(response, review_selectors)
        if review_text:
            numbers = cls.extract_numbers_from_text(review_text)
            if numbers:
                try:
                    rating_info['review_count'] = int(numbers[0])
                except (ValueError, IndexError):
                    pass
        
        return rating_info


class LinkDiscovery:
    """链接发现工具"""
    
    @staticmethod
    def discover_category_links(response) -> List[Dict[str, str]]:
        """
        发现分类链接
        
        Returns:
            包含链接信息的字典列表，每个字典包含 'url', 'text', 'level' 等字段
        """
        category_selectors = [
            # 导航菜单分类
            'nav ul li a[href*="category"]',
            'nav .menu li a[href*="category"]',
            '.navigation li a[href*="category"]',
            '.nav-menu li a[href*="category"]',
            
            # 分类页面链接
            'a[href*="/category/"]',
            'a[href*="/categories/"]',
            'a[href*="/cat/"]',
            
            # 产品分类链接
            '.category-link',
            '.category-item a',
            '.product-category a',
            '.category-menu a',
            
            # 通用分类模式
            'a[href*="shop"]',
            'a[href*="products"]',
            'a[href*="collection"]'
        ]
        
        discovered_links = []
        seen_urls = set()
        
        for selector in category_selectors:
            try:
                links = response.css(selector)
                for link in links:
                    href = link.css('::attr(href)').get()
                    text = link.css('::text').get()
                    
                    if href and href not in seen_urls:
                        seen_urls.add(href)
                        
                        # 判断分类层级
                        level = LinkDiscovery._determine_category_level(href)
                        
                        discovered_links.append({
                            'url': href,
                            'text': text.strip() if text else '未知分类',
                            'level': level,
                            'selector': selector
                        })
            except Exception:
                continue
        
        return discovered_links
    
    @staticmethod
    def discover_product_links(response) -> List[Dict[str, str]]:
        """
        发现产品链接
        
        Returns:
            包含产品链接信息的字典列表
        """
        product_selectors = [
            # 产品卡片和链接
            '.product-item a[href*="product"]',
            '.product-card a',
            '.product a',
            'a[href*="/product/"]',
            'a[href*="/products/"]',
            'a[href*="/item/"]',
            
            # 商品列表
            '.product-list .product a',
            '.products-grid .product a',
            '.shop-items .item a',
            
            # 通用产品链接模式
            'a[href*="shop"][href*="product"]'
        ]
        
        discovered_links = []
        seen_urls = set()
        
        for selector in product_selectors:
            try:
                links = response.css(selector)
                for link in links:
                    href = link.css('::attr(href)').get()
                    text = link.css('::text').get()
                    
                    if href and href not in seen_urls:
                        seen_urls.add(href)
                        
                        discovered_links.append({
                            'url': href,
                            'text': text.strip() if text else '未知产品',
                            'selector': selector
                        })
            except Exception:
                continue
        
        return discovered_links
    
    @staticmethod
    def _determine_category_level(url: str) -> int:
        """
        根据URL确定分类层级
        
        Args:
            url: 分类URL
            
        Returns:
            分类层级（1为顶级分类）
        """
        if not url:
            return 1
        
        # 计算URL中的路径段数来估算层级
        path_segments = [segment for segment in url.split('/') if segment and segment != 'category' and segment != 'categories']
        
        # 至少是1级分类
        return max(1, len(path_segments))


class DataValidator:
    """数据验证工具"""
    
    @staticmethod
    def validate_price(price: str) -> bool:
        """验证价格格式"""
        if not price:
            return False
        
        # 检查是否包含数字
        if not re.search(r'\d+', price):
            return False
        
        # 排除无效价格文本
        invalid_patterns = [
            r'免费',
            r'面议',
            r'咨询',
            r'询价',
            r'contact',
            r'call'
        ]
        
        price_lower = price.lower()
        for pattern in invalid_patterns:
            if re.search(pattern, price_lower):
                return False
        
        return True
    
    @staticmethod
    def validate_url(url: str, allowed_domains: List[str] = None) -> bool:
        """验证URL格式"""
        if not url:
            return False
        
        # 相对URL
        if url.startswith('/'):
            return True
        
        # 绝对URL
        if url.startswith('http'):
            if allowed_domains:
                return any(domain in url for domain in allowed_domains)
            return True
        
        return False
    
    @staticmethod
    def validate_rating(rating: Union[str, int, float]) -> bool:
        """验证评分"""
        try:
            rating_value = float(rating)
            return 0 <= rating_value <= 5
        except (ValueError, TypeError):
            return False