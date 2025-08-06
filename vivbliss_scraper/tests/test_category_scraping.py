#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试分类爬取功能的测试用例
包含分类发现、分类层级、分类数据提取等功能测试
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import scrapy
from scrapy.http import HtmlResponse, Request
from scrapy.utils.test import get_crawler
import sys
import os

# 添加项目路径到 sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from vivbliss_scraper.spiders.vivbliss import VivblissSpider
    from vivbliss_scraper.items import CategoryItem
except ImportError:
    # 如果导入失败，创建模拟对象
    class VivblissSpider:
        name = 'vivbliss'
        allowed_domains = ['vivbliss.com']
        start_urls = ['https://vivbliss.com']
        
        def parse_categories(self, response):
            pass
    
    class CategoryItem:
        def __init__(self):
            self.fields = {}


class TestCategoryScrapingFunctionality(unittest.TestCase):
    """测试分类爬取功能"""
    
    def setUp(self):
        """测试前准备"""
        self.spider = VivblissSpider()
        self.spider.logger = Mock()
        
        # 模拟分类页面 HTML 内容
        self.category_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>VivBliss - 商品分类</title>
            <meta name="description" content="探索 VivBliss 的全部商品分类">
        </head>
        <body>
            <nav class="main-navigation">
                <ul class="category-menu">
                    <li class="category-item level-1">
                        <a href="/category/clothing" class="category-link" data-category-id="1">
                            服装 <span class="product-count">(156)</span>
                        </a>
                        <ul class="subcategory-menu">
                            <li class="category-item level-2">
                                <a href="/category/clothing/mens" data-category-id="2">
                                    男装 <span class="product-count">(78)</span>
                                </a>
                                <ul class="subcategory-menu">
                                    <li class="category-item level-3">
                                        <a href="/category/clothing/mens/shirts" data-category-id="3">
                                            衬衫 <span class="product-count">(25)</span>
                                        </a>
                                    </li>
                                    <li class="category-item level-3">
                                        <a href="/category/clothing/mens/pants" data-category-id="4">
                                            裤子 <span class="product-count">(30)</span>
                                        </a>
                                    </li>
                                </ul>
                            </li>
                            <li class="category-item level-2">
                                <a href="/category/clothing/womens" data-category-id="5">
                                    女装 <span class="product-count">(78)</span>
                                </a>
                            </li>
                        </ul>
                    </li>
                    <li class="category-item level-1">
                        <a href="/category/accessories" class="category-link" data-category-id="6">
                            配饰 <span class="product-count">(89)</span>
                        </a>
                        <ul class="subcategory-menu">
                            <li class="category-item level-2">
                                <a href="/category/accessories/bags" data-category-id="7">
                                    包包 <span class="product-count">(45)</span>
                                </a>
                            </li>
                            <li class="category-item level-2">
                                <a href="/category/accessories/jewelry" data-category-id="8">
                                    珠宝 <span class="product-count">(44)</span>
                                </a>
                            </li>
                        </ul>
                    </li>
                </ul>
            </nav>
            
            <!-- 分类页面内容 -->
            <div class="category-content">
                <div class="category-header">
                    <h1 class="category-title">所有分类</h1>
                    <p class="category-description">浏览我们的完整产品分类</p>
                    <img src="/images/categories-banner.jpg" alt="分类横幅" class="category-image">
                </div>
                
                <div class="category-grid">
                    <div class="category-card" data-category="clothing">
                        <img src="/images/clothing-category.jpg" alt="服装分类">
                        <h3>服装</h3>
                        <p>时尚服装收藏</p>
                        <span class="item-count">156 件商品</span>
                    </div>
                    <div class="category-card" data-category="accessories">
                        <img src="/images/accessories-category.jpg" alt="配饰分类">
                        <h3>配饰</h3>
                        <p>精美配饰选择</p>
                        <span class="item-count">89 件商品</span>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 创建模拟响应对象
        self.response = HtmlResponse(
            url='https://vivbliss.com/categories',
            body=self.category_html.encode('utf-8'),
            encoding='utf-8'
        )
    
    def test_category_navigation_discovery(self):
        """测试分类导航发现功能"""
        # 检查是否能发现主要分类链接
        category_links = self.response.css('.category-menu .category-link::attr(href)').getall()
        
        self.assertGreater(len(category_links), 0, "应该发现至少一个分类链接")
        self.assertIn('/category/clothing', category_links, "应该发现服装分类链接")
        self.assertIn('/category/accessories', category_links, "应该发现配饰分类链接")
    
    def test_category_hierarchy_extraction(self):
        """测试分类层级提取功能"""
        # 测试一级分类
        level_1_categories = self.response.css('.category-item.level-1 > .category-link')
        self.assertEqual(len(level_1_categories), 2, "应该发现2个一级分类")
        
        # 测试二级分类
        level_2_categories = self.response.css('.category-item.level-2 > a')
        self.assertGreater(len(level_2_categories), 2, "应该发现多个二级分类")
        
        # 测试三级分类
        level_3_categories = self.response.css('.category-item.level-3 > a')
        self.assertGreater(len(level_3_categories), 0, "应该发现至少一个三级分类")
    
    def test_category_data_extraction(self):
        """测试分类数据提取功能"""
        # 提取第一个分类的详细信息
        first_category = self.response.css('.category-item.level-1').get()
        
        if first_category:
            category_selector = scrapy.Selector(text=first_category)
            
            # 提取分类名称
            name = category_selector.css('.category-link::text').get()
            self.assertIsNotNone(name, "应该能提取到分类名称")
            self.assertIn('服装', name, "分类名称应该包含'服装'")
            
            # 提取分类链接
            url = category_selector.css('.category-link::attr(href)').get()
            self.assertIsNotNone(url, "应该能提取到分类链接")
            self.assertTrue(url.startswith('/category/'), "链接应该以'/category/'开头")
            
            # 提取产品数量
            product_count_text = category_selector.css('.product-count::text').get()
            if product_count_text:
                # 从 "(156)" 中提取数字
                import re
                numbers = re.findall(r'\d+', product_count_text)
                self.assertGreater(len(numbers), 0, "应该能从产品数量文本中提取到数字")
    
    def test_category_path_construction(self):
        """测试分类路径构建功能"""
        # 测试构建分类路径的逻辑
        test_cases = [
            {
                'category': '服装',
                'parent': None,
                'expected_path': '服装'
            },
            {
                'category': '男装',
                'parent': '服装',
                'expected_path': '服装/男装'
            },
            {
                'category': '衬衫',
                'parent': '服装/男装',
                'expected_path': '服装/男装/衬衫'
            }
        ]
        
        def build_category_path(category_name, parent_path=None):
            """构建分类路径的辅助函数"""
            if parent_path:
                return f"{parent_path}/{category_name}"
            return category_name
        
        for case in test_cases:
            result = build_category_path(case['category'], case['parent'])
            self.assertEqual(result, case['expected_path'], 
                           f"分类路径构建错误: {case}")
    
    def test_category_item_creation(self):
        """测试 CategoryItem 对象创建"""
        # 创建一个测试用的 CategoryItem
        try:
            category = CategoryItem()
            
            # 测试设置基础字段
            test_data = {
                'name': '服装',
                'url': 'https://vivbliss.com/category/clothing',
                'slug': 'clothing',
                'level': 1,
                'path': '服装',
                'product_count': 156,
                'description': '时尚服装收藏',
                'parent_category': None
            }
            
            # 验证可以设置所有字段
            for field_name, value in test_data.items():
                category[field_name] = value
                self.assertEqual(category[field_name], value, 
                               f"字段 {field_name} 设置失败")
            
        except Exception as e:
            self.fail(f"创建 CategoryItem 对象失败: {e}")
    
    def test_subcategory_relationship_tracking(self):
        """测试子分类关系追踪"""
        # 从 HTML 中提取分类层级关系
        categories_data = []
        
        # 提取一级分类
        level_1_items = self.response.css('.category-item.level-1')
        for item in level_1_items:
            category_link = item.css('> .category-link')
            if category_link:
                name = category_link.css('::text').re_first(r'^([^(]+)')
                if name:
                    name = name.strip()
                    url = category_link.css('::attr(href)').get()
                    categories_data.append({
                        'name': name,
                        'url': url,
                        'level': 1,
                        'parent': None
                    })
                    
                    # 提取子分类
                    level_2_items = item.css('.subcategory-menu .category-item.level-2')
                    for sub_item in level_2_items:
                        sub_link = sub_item.css('> a')
                        if sub_link:
                            sub_name = sub_link.css('::text').re_first(r'^([^(]+)')
                            if sub_name:
                                sub_name = sub_name.strip()
                                sub_url = sub_link.css('::attr(href)').get()
                                categories_data.append({
                                    'name': sub_name,
                                    'url': sub_url,
                                    'level': 2,
                                    'parent': name
                                })
        
        # 验证提取的分类数据
        self.assertGreater(len(categories_data), 0, "应该提取到分类数据")
        
        # 验证层级关系
        parent_categories = [c for c in categories_data if c['level'] == 1]
        child_categories = [c for c in categories_data if c['level'] == 2]
        
        self.assertGreater(len(parent_categories), 0, "应该有父分类")
        self.assertGreater(len(child_categories), 0, "应该有子分类")
        
        # 验证每个子分类都有对应的父分类
        parent_names = {c['name'] for c in parent_categories}
        for child in child_categories:
            self.assertIn(child['parent'], parent_names, 
                         f"子分类 {child['name']} 的父分类 {child['parent']} 不存在")
    
    def test_category_url_pattern_validation(self):
        """测试分类 URL 模式验证"""
        # 提取所有分类 URL
        category_urls = self.response.css('.category-item a::attr(href)').getall()
        
        # 验证 URL 模式
        import re
        url_pattern = re.compile(r'^/category/[\w\-/]+$')
        
        valid_urls = []
        invalid_urls = []
        
        for url in category_urls:
            if url and url_pattern.match(url):
                valid_urls.append(url)
            else:
                invalid_urls.append(url)
        
        self.assertGreater(len(valid_urls), 0, "应该有有效的分类 URL")
        self.assertEqual(len(invalid_urls), 0, f"发现无效的 URL: {invalid_urls}")
    
    def test_category_metadata_extraction(self):
        """测试分类元数据提取"""
        # 测试页面级别的元数据
        page_title = self.response.css('title::text').get()
        self.assertIsNotNone(page_title, "应该能提取到页面标题")
        
        meta_description = self.response.css('meta[name="description"]::attr(content)').get()
        self.assertIsNotNone(meta_description, "应该能提取到页面描述")
        
        # 测试分类特定的元数据
        category_title = self.response.css('.category-title::text').get()
        if category_title:
            self.assertIn('分类', category_title, "分类标题应该包含'分类'")
        
        category_description = self.response.css('.category-description::text').get()
        if category_description:
            self.assertIsInstance(category_description, str, "分类描述应该是字符串")
        
        category_image = self.response.css('.category-image::attr(src)').get()
        if category_image:
            self.assertTrue(category_image.startswith('/'), "分类图片路径应该以'/'开头")


class TestCategoryScrapingEdgeCases(unittest.TestCase):
    """测试分类爬取的边缘情况"""
    
    def setUp(self):
        """测试前准备"""
        self.spider = VivblissSpider()
        self.spider.logger = Mock()
    
    def test_empty_category_page(self):
        """测试空分类页面处理"""
        empty_html = """
        <!DOCTYPE html>
        <html>
        <head><title>Empty Categories</title></head>
        <body>
            <div class="no-categories">暂无分类</div>
        </body>
        </html>
        """
        
        response = HtmlResponse(
            url='https://vivbliss.com/categories',
            body=empty_html.encode('utf-8'),
            encoding='utf-8'
        )
        
        # 验证处理空页面不会崩溃
        category_links = response.css('.category-menu .category-link::attr(href)').getall()
        self.assertEqual(len(category_links), 0, "空页面应该没有分类链接")
    
    def test_malformed_html_handling(self):
        """测试畸形 HTML 处理"""
        malformed_html = """
        <html>
        <body>
            <div class="category-item">
                <a href="/category/test">测试分类
                <!-- 没有关闭的链接标签 -->
                <span class="product-count">(10)
                <!-- 没有关闭的 span 标签 -->
            </div>
        </body>
        </html>
        """
        
        response = HtmlResponse(
            url='https://vivbliss.com/categories',
            body=malformed_html.encode('utf-8'),
            encoding='utf-8'
        )
        
        # 验证能从畸形 HTML 中提取数据
        category_links = response.css('a::attr(href)').getall()
        self.assertGreater(len(category_links), 0, "应该能从畸形 HTML 中提取链接")
    
    def test_unicode_category_names(self):
        """测试 Unicode 分类名称处理"""
        unicode_html = """
        <html>
        <body>
            <div class="category-menu">
                <a href="/category/chinese">中文分类 🇨🇳</a>
                <a href="/category/japanese">日本語カテゴリ 🇯🇵</a>
                <a href="/category/korean">한국어 카테고리 🇰🇷</a>
                <a href="/category/emoji">Emoji分类 🎉✨🌟</a>
            </div>
        </body>
        </html>
        """
        
        response = HtmlResponse(
            url='https://vivbliss.com/categories',
            body=unicode_html.encode('utf-8'),
            encoding='utf-8'
        )
        
        # 验证能正确处理 Unicode 字符
        category_names = response.css('.category-menu a::text').getall()
        self.assertGreater(len(category_names), 0, "应该能提取 Unicode 分类名称")
        
        # 验证包含多种语言和 emoji
        all_text = ' '.join(category_names)
        self.assertIn('中文', all_text, "应该包含中文")
        self.assertIn('日本語', all_text, "应该包含日文")
        self.assertIn('한국어', all_text, "应该包含韩文")
        self.assertIn('🎉', all_text, "应该包含 emoji")


if __name__ == '__main__':
    # 运行所有测试
    unittest.main(verbosity=2)