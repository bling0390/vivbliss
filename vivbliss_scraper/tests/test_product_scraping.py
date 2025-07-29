#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试产品爬取功能的测试用例
包含产品发现、产品详情提取、价格解析等功能测试
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import re
from datetime import datetime

# 添加项目路径到 sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 尝试导入 scrapy 模块，如果失败则创建模拟对象
try:
    import scrapy
    from scrapy.http import HtmlResponse, Request
    from scrapy.utils.test import get_crawler
    SCRAPY_AVAILABLE = True
except ImportError:
    SCRAPY_AVAILABLE = False
    
    # 创建模拟 scrapy 对象
    class scrapy:
        class Item:
            def __init__(self):
                self.fields = {}
            
            def __getitem__(self, key):
                return self.fields.get(key)
            
            def __setitem__(self, key, value):
                self.fields[key] = value
        
        class Field:
            pass
        
        class Request:
            def __init__(self, url, callback=None, meta=None):
                self.url = url
                self.callback = callback
                self.meta = meta or {}
    
    class HtmlResponse:
        def __init__(self, url, body, encoding='utf-8'):
            self.url = url
            self.body = body
            self.encoding = encoding
            self.status = 200
            self.text = body.decode(encoding) if isinstance(body, bytes) else body
        
        def css(self, selector):
            return MockSelector()
        
        def urljoin(self, url):
            return f"https://vivbliss.com{url}" if url.startswith('/') else url

    class MockSelector:
        def get(self):
            return None
        
        def getall(self):
            return []

try:
    from vivbliss_scraper.spiders.vivbliss import VivblissSpider
    from vivbliss_scraper.items import ProductItem
except ImportError:
    # 如果导入失败，创建模拟对象
    class VivblissSpider:
        name = 'vivbliss'
        allowed_domains = ['vivbliss.com']
        start_urls = ['https://vivbliss.com']
        
        def __init__(self):
            self.logger = Mock()
        
        def parse_product(self, response):
            pass
        
        def discover_products(self, response, category_path=None):
            pass
    
    class ProductItem:
        def __init__(self):
            self.fields = {}
        
        def __getitem__(self, key):
            return self.fields.get(key)
        
        def __setitem__(self, key, value):
            self.fields[key] = value


class TestProductScrapingFunctionality(unittest.TestCase):
    """测试产品爬取功能"""
    
    def setUp(self):
        """测试前准备"""
        self.spider = VivblissSpider()
        if hasattr(self.spider, 'logger'):
            self.spider.logger = Mock()
        
        # 模拟产品页面 HTML 内容
        self.product_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>VivBliss 精品衬衫 - 高品质男装</title>
            <meta name="description" content="VivBliss 精品衬衫，采用高品质棉质面料，舒适透气，适合商务和休闲场合。">
            <meta name="keywords" content="衬衫,男装,商务,休闲,VivBliss">
        </head>
        <body>
            <div class="product-page">
                <!-- 产品标题 -->
                <h1 class="product-title">VivBliss 精品商务衬衫</h1>
                
                <!-- 品牌信息 -->
                <div class="product-brand">VivBliss</div>
                <div class="product-sku">VB-SHIRT-001</div>
                
                <!-- 价格信息 -->
                <div class="price-section">
                    <span class="current-price">¥299.00</span>
                    <span class="original-price">¥399.00</span>
                    <span class="discount">25% OFF</span>
                </div>
                
                <!-- 库存状态 -->
                <div class="stock-status in-stock">现货供应</div>
                <div class="stock-quantity">库存：58件</div>
                
                <!-- 产品描述 -->
                <div class="product-description">
                    <p>这款精品商务衬衫采用高品质100%纯棉面料制作，手感柔软，透气性佳。</p>
                    <p>经典版型设计，适合商务场合和日常穿着。精致的做工和细节处理彰显品质。</p>
                </div>
                
                <!-- 产品规格 -->
                <div class="specifications">
                    <h3>产品规格</h3>
                    <ul>
                        <li>材质：100%纯棉</li>
                        <li>版型：修身</li>
                        <li>领型：标准领</li>
                        <li>袖长：长袖</li>
                    </ul>
                </div>
                
                <!-- 产品图片 -->
                <div class="product-images">
                    <img src="/images/products/shirt-001-main.jpg" alt="VivBliss 精品衬衫 主图" class="main-image">
                    <div class="gallery">
                        <img src="/images/products/shirt-001-detail1.jpg" alt="细节图1">
                        <img src="/images/products/shirt-001-detail2.jpg" alt="细节图2">
                        <img src="/images/products/shirt-001-model.jpg" alt="模特图">
                    </div>
                </div>
                
                <!-- 评分和评价 -->
                <div class="rating-section">
                    <div class="average-rating">4.8</div>
                    <div class="review-count">128条评价</div>
                    <div class="rating-stars">★★★★★</div>
                </div>
                
                <!-- 产品变体 -->
                <div class="product-variants">
                    <div class="color-options">
                        <h4>颜色</h4>
                        <button class="color-option" data-color="white">白色</button>
                        <button class="color-option" data-color="blue">蓝色</button>
                        <button class="color-option" data-color="black">黑色</button>
                    </div>
                    <div class="size-options">
                        <h4>尺码</h4>
                        <button class="size-option" data-size="S">S</button>
                        <button class="size-option" data-size="M">M</button>
                        <button class="size-option" data-size="L">L</button>
                        <button class="size-option" data-size="XL">XL</button>
                    </div>
                </div>
                
                <!-- 运输信息 -->
                <div class="shipping-info">
                    <p>免费配送：订单满199元</p>
                    <p>预计送达：3-5个工作日</p>
                </div>
                
                <!-- 保修信息 -->
                <div class="warranty">
                    <p>30天无理由退换</p>
                    <p>质量保证</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 创建模拟响应对象
        if SCRAPY_AVAILABLE:
            self.response = HtmlResponse(
                url='https://vivbliss.com/product/vivbliss-business-shirt-001',
                body=self.product_html.encode('utf-8'),
                encoding='utf-8'
            )
        else:
            self.response = HtmlResponse(
                url='https://vivbliss.com/product/vivbliss-business-shirt-001',
                body=self.product_html.encode('utf-8')
            )
    
    def test_product_basic_info_extraction(self):
        """测试产品基础信息提取"""
        # 提取产品标题
        title = self.response.css('h1.product-title::text').get()
        self.assertIsNotNone(title, "应该能提取到产品标题")
        self.assertIn('VivBliss', title, "产品标题应该包含品牌名")
        self.assertIn('衬衫', title, "产品标题应该包含产品类型")
        
        # 提取品牌信息
        brand = self.response.css('.product-brand::text').get()
        self.assertIsNotNone(brand, "应该能提取到品牌信息")
        self.assertEqual(brand, 'VivBliss', "品牌应该是 VivBliss")
        
        # 提取 SKU
        sku = self.response.css('.product-sku::text').get()
        self.assertIsNotNone(sku, "应该能提取到产品 SKU")
        self.assertTrue(sku.startswith('VB-'), "SKU 应该以 VB- 开头")
    
    def test_product_price_extraction(self):
        """测试产品价格信息提取"""
        # 提取当前价格
        current_price = self.response.css('.current-price::text').get()
        self.assertIsNotNone(current_price, "应该能提取到当前价格")
        self.assertIn('¥', current_price, "价格应该包含货币符号")
        self.assertIn('299', current_price, "价格应该包含正确的数值")
        
        # 提取原价
        original_price = self.response.css('.original-price::text').get()
        self.assertIsNotNone(original_price, "应该能提取到原价")
        self.assertIn('399', original_price, "原价应该包含正确的数值")
        
        # 提取折扣信息
        discount = self.response.css('.discount::text').get()
        self.assertIsNotNone(discount, "应该能提取到折扣信息")
        self.assertIn('%', discount, "折扣应该包含百分号")
    
    def test_product_stock_status_extraction(self):
        """测试产品库存状态提取"""
        # 提取库存状态
        stock_status = self.response.css('.stock-status::text').get()
        self.assertIsNotNone(stock_status, "应该能提取到库存状态")
        
        # 验证库存状态包含相关信息
        stock_keywords = ['现货', '有库存', '供应', 'in-stock', 'available']
        has_stock_keyword = any(keyword in stock_status for keyword in stock_keywords)
        self.assertTrue(has_stock_keyword, f"库存状态应该包含相关关键词，实际值：{stock_status}")
        
        # 提取库存数量
        stock_quantity = self.response.css('.stock-quantity::text').get()
        if stock_quantity:
            # 从库存文本中提取数字
            numbers = re.findall(r'\d+', stock_quantity)
            self.assertGreater(len(numbers), 0, "应该能从库存文本中提取到数字")
    
    def test_product_description_extraction(self):
        """测试产品描述提取"""
        # 提取产品描述段落
        description_paragraphs = self.response.css('.product-description p::text').getall()
        self.assertGreater(len(description_paragraphs), 0, "应该能提取到产品描述段落")
        
        # 组合描述文本
        full_description = ' '.join(description_paragraphs)
        self.assertGreater(len(full_description), 50, "产品描述应该有足够的长度")
        self.assertIn('棉', full_description, "产品描述应该包含材质信息")
        self.assertIn('商务', full_description, "产品描述应该包含用途信息")
    
    def test_product_images_extraction(self):
        """测试产品图片提取"""
        # 提取主图
        main_image = self.response.css('.product-images .main-image::attr(src)').get()
        self.assertIsNotNone(main_image, "应该能提取到主图")
        self.assertTrue(main_image.startswith('/images/'), "图片路径应该以 /images/ 开头")
        
        # 提取所有产品图片
        all_images = self.response.css('.product-images img::attr(src)').getall()
        self.assertGreater(len(all_images), 1, "应该有多张产品图片")
        
        # 验证图片路径格式
        for image in all_images:
            self.assertTrue(
                image.startswith('/images/') or image.startswith('http'),
                f"图片路径格式应该正确: {image}"
            )
    
    def test_product_rating_extraction(self):
        """测试产品评分和评价提取"""
        # 提取平均评分
        rating = self.response.css('.average-rating::text').get()
        self.assertIsNotNone(rating, "应该能提取到平均评分")
        
        # 验证评分格式
        try:
            rating_value = float(rating)
            self.assertGreaterEqual(rating_value, 0, "评分应该大于等于0")
            self.assertLessEqual(rating_value, 5, "评分应该小于等于5")
        except ValueError:
            self.fail(f"评分应该是有效的数字: {rating}")
        
        # 提取评价数量
        review_count = self.response.css('.review-count::text').get()
        self.assertIsNotNone(review_count, "应该能提取到评价数量")
        
        # 从评价数量文本中提取数字
        review_numbers = re.findall(r'\d+', review_count)
        self.assertGreater(len(review_numbers), 0, "应该能从评价数量文本中提取到数字")
    
    def test_product_variants_extraction(self):
        """测试产品变体信息提取"""
        # 提取颜色选项
        color_options = self.response.css('.color-option::text').getall()
        self.assertGreater(len(color_options), 1, "应该有多个颜色选项")
        
        expected_colors = ['白色', '蓝色', '黑色']
        for color in expected_colors:
            self.assertIn(color, color_options, f"应该包含颜色选项: {color}")
        
        # 提取尺码选项
        size_options = self.response.css('.size-option::text').getall()
        self.assertGreater(len(size_options), 1, "应该有多个尺码选项")
        
        expected_sizes = ['S', 'M', 'L', 'XL']
        for size in expected_sizes:
            self.assertIn(size, size_options, f"应该包含尺码选项: {size}")
    
    def test_product_seo_metadata_extraction(self):
        """测试产品 SEO 元数据提取"""
        # 提取页面标题
        page_title = self.response.css('title::text').get()
        self.assertIsNotNone(page_title, "应该能提取到页面标题")
        self.assertIn('VivBliss', page_title, "页面标题应该包含品牌名")
        
        # 提取 meta description
        meta_description = self.response.css('meta[name="description"]::attr(content)').get()
        self.assertIsNotNone(meta_description, "应该能提取到 meta description")
        self.assertGreater(len(meta_description), 50, "meta description 应该有足够长度")
        
        # 提取 meta keywords
        meta_keywords = self.response.css('meta[name="keywords"]::attr(content)').get()
        self.assertIsNotNone(meta_keywords, "应该能提取到 meta keywords")
        self.assertIn('衬衫', meta_keywords, "meta keywords 应该包含产品相关关键词")
    
    def test_product_shipping_and_warranty_info(self):
        """测试产品运输和保修信息提取"""
        # 提取运输信息
        shipping_info = self.response.css('.shipping-info p::text').getall()
        self.assertGreater(len(shipping_info), 0, "应该能提取到运输信息")
        
        shipping_text = ' '.join(shipping_info)
        self.assertIn('配送', shipping_text, "运输信息应该包含配送相关内容")
        
        # 提取保修信息
        warranty_info = self.response.css('.warranty p::text').getall()
        self.assertGreater(len(warranty_info), 0, "应该能提取到保修信息")
        
        warranty_text = ' '.join(warranty_info)
        self.assertIn('退换', warranty_text, "保修信息应该包含退换相关内容")


class TestProductDiscoveryFunctionality(unittest.TestCase):
    """测试产品发现功能"""
    
    def setUp(self):
        """测试前准备"""
        # 模拟产品列表页面 HTML
        self.product_list_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>VivBliss 产品列表</title>
        </head>
        <body>
            <div class="products-grid">
                <div class="product-item">
                    <a href="/product/shirt-001" class="product-link">
                        <img src="/images/shirt-001-thumb.jpg" alt="衬衫">
                        <h3>精品商务衬衫</h3>
                        <span class="price">¥299.00</span>
                    </a>
                </div>
                <div class="product-item">
                    <a href="/product/pants-002" class="product-link">
                        <img src="/images/pants-002-thumb.jpg" alt="裤子">
                        <h3>休闲长裤</h3>
                        <span class="price">¥199.00</span>
                    </a>
                </div>
                <div class="product-item">
                    <a href="/product/jacket-003" class="product-link">
                        <img src="/images/jacket-003-thumb.jpg" alt="外套">
                        <h3>时尚外套</h3>
                        <span class="price">¥399.00</span>
                    </a>
                </div>
            </div>
            
            <!-- 另一种产品布局 -->
            <div class="shop-items">
                <div class="item">
                    <a href="/products/accessory-001">
                        <h4>精美手表</h4>
                        <div class="item-price">¥899.00</div>
                    </a>
                </div>
                <div class="item">
                    <a href="/products/accessory-002">
                        <h4>皮质钱包</h4>
                        <div class="item-price">¥159.00</div>
                    </a>
                </div>
            </div>
        </body>
        </html>
        """
        
        if SCRAPY_AVAILABLE:
            self.response = HtmlResponse(
                url='https://vivbliss.com/category/clothing',
                body=self.product_list_html.encode('utf-8'),
                encoding='utf-8'
            )
        else:
            self.response = HtmlResponse(
                url='https://vivbliss.com/category/clothing',
                body=self.product_list_html.encode('utf-8')
            )
    
    def test_product_links_discovery(self):
        """测试产品链接发现"""
        # 使用多种选择器查找产品链接
        product_selectors = [
            '.product-item a[href*="product"]',
            '.shop-items .item a[href*="products"]',
            'a[href*="/product/"]',
            'a[href*="/products/"]'
        ]
        
        all_product_links = set()
        
        for selector in product_selectors:
            links = self.response.css(selector + '::attr(href)').getall()
            for link in links:
                all_product_links.add(link)
        
        self.assertGreater(len(all_product_links), 3, "应该发现多个产品链接")
        
        # 验证链接格式
        for link in all_product_links:
            self.assertTrue(
                '/product/' in link or '/products/' in link,
                f"产品链接应该包含产品路径: {link}"
            )
    
    def test_product_preview_info_extraction(self):
        """测试产品预览信息提取"""
        # 提取产品预览信息（产品列表页面中的基本信息）
        product_items = self.response.css('.product-item')
        
        self.assertGreater(len(product_items), 0, "应该发现产品项目")
        
        for i, item in enumerate(product_items):
            # 提取产品名称
            product_name = item.css('h3::text').get()
            self.assertIsNotNone(product_name, f"产品 {i+1} 应该有名称")
            
            # 提取产品链接
            product_link = item.css('a::attr(href)').get()
            self.assertIsNotNone(product_link, f"产品 {i+1} 应该有链接")
            
            # 提取产品价格
            product_price = item.css('.price::text').get()
            self.assertIsNotNone(product_price, f"产品 {i+1} 应该有价格")
            self.assertIn('¥', product_price, f"产品 {i+1} 价格应该包含货币符号")
    
    def test_product_url_validation(self):
        """测试产品 URL 有效性验证"""
        # 提取所有产品链接
        all_links = self.response.css('a[href*="product"]::attr(href)').getall()
        all_links.extend(self.response.css('a[href*="products"]::attr(href)').getall())
        
        # 验证 URL 格式
        url_pattern = re.compile(r'^/products?/[\w\-]+$')
        
        valid_urls = []
        invalid_urls = []
        
        for url in all_links:
            if url_pattern.match(url):
                valid_urls.append(url)
            else:
                invalid_urls.append(url)
        
        self.assertGreater(len(valid_urls), 0, "应该有有效的产品 URL")
        self.assertEqual(len(invalid_urls), 0, f"不应该有无效的 URL: {invalid_urls}")


class TestProductDataStructure(unittest.TestCase):
    """测试产品数据结构"""
    
    def test_product_item_fields(self):
        """测试 ProductItem 字段结构"""
        product = ProductItem()
        
        # 测试必需字段
        required_fields = ['name', 'url', 'price', 'stock_status']
        for field in required_fields:
            try:
                product[field] = f"test_{field}_value"
                self.assertEqual(product[field], f"test_{field}_value", 
                               f"应该能设置和获取字段: {field}")
            except Exception as e:
                self.fail(f"设置字段 {field} 时出错: {e}")
        
        # 测试可选字段
        optional_fields = [
            'original_price', 'discount', 'currency', 'stock_quantity',
            'description', 'brand', 'sku', 'rating', 'review_count',
            'image_urls', 'variants', 'created_at'
        ]
        
        for field in optional_fields:
            try:
                product[field] = f"test_{field}_value"
                self.assertEqual(product[field], f"test_{field}_value",
                               f"应该能设置和获取可选字段: {field}")
            except Exception as e:
                self.fail(f"设置可选字段 {field} 时出错: {e}")
    
    def test_product_data_types(self):
        """测试产品数据类型"""
        product = ProductItem()
        
        # 测试字符串字段
        string_fields = ['name', 'url', 'description', 'brand', 'sku']
        for field in string_fields:
            product[field] = "测试字符串"
            self.assertIsInstance(product[field], str, f"字段 {field} 应该是字符串类型")
        
        # 测试数字字段
        product['rating'] = 4.5
        self.assertIsInstance(product['rating'], (int, float), "评分应该是数字类型")
        
        product['review_count'] = 100
        self.assertIsInstance(product['review_count'], int, "评价数量应该是整数类型")
        
        # 测试列表字段
        product['image_urls'] = ['url1', 'url2', 'url3']
        self.assertIsInstance(product['image_urls'], list, "图片URL应该是列表类型")
        
        # 测试日期字段
        product['created_at'] = datetime.now().isoformat()
        try:
            datetime.fromisoformat(product['created_at'].replace('Z', '+00:00'))
        except ValueError:
            self.fail("创建时间应该是有效的ISO格式")


if __name__ == '__main__':
    # 运行所有测试
    unittest.main(verbosity=2)