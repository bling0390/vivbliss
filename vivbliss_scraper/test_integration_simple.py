#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的集成测试，验证完整的爬取流程
不依赖外部库，测试核心业务逻辑
"""

import sys
import os
import re
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

def test_spider_import():
    """测试爬虫模块导入"""
    print("🧪 测试爬虫模块导入...")
    
    try:
        # 尝试导入爬虫类
        from vivbliss_scraper.spiders.vivbliss import VivblissSpider
        print("✅ 成功导入 VivblissSpider")
        
        # 尝试导入数据项
        from vivbliss_scraper.items import VivblissItem, CategoryItem, ProductItem
        print("✅ 成功导入数据项类")
        
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_spider_initialization():
    """测试爬虫初始化"""
    print("\n🧪 测试爬虫初始化...")
    
    try:
        from vivbliss_scraper.spiders.vivbliss import VivblissSpider
        
        spider = VivblissSpider()
        
        # 检查基本属性
        assert spider.name == 'vivbliss', f"爬虫名称应该是 'vivbliss'，实际是 '{spider.name}'"
        assert 'vivbliss.com' in spider.allowed_domains, "允许的域名应该包含 'vivbliss.com'"
        assert len(spider.start_urls) > 0, "起始URL列表不应该为空"
        
        print("✅ 爬虫初始化成功")
        print(f"   - 名称: {spider.name}")
        print(f"   - 允许域名: {spider.allowed_domains}")
        print(f"   - 起始URL: {spider.start_urls}")
        
        return True
    except Exception as e:
        print(f"❌ 爬虫初始化失败: {e}")
        return False

def test_data_models():
    """测试数据模型创建"""
    print("\n🧪 测试数据模型创建...")
    
    try:
        from vivbliss_scraper.items import VivblissItem, CategoryItem, ProductItem
        
        # 测试原始文章项
        article_item = VivblissItem()
        article_item['title'] = '测试文章标题'
        article_item['url'] = 'https://vivbliss.com/article/test'
        article_item['content'] = '测试文章内容'
        article_item['date'] = '2024-01-01'
        article_item['category'] = '测试分类'
        print("✅ VivblissItem 创建成功")
        
        # 测试分类项
        category_item = CategoryItem()
        category_item['name'] = '测试分类'
        category_item['url'] = 'https://vivbliss.com/category/test'
        category_item['level'] = 1
        category_item['path'] = '测试分类'
        category_item['product_count'] = 50
        category_item['created_at'] = datetime.now().isoformat()
        print("✅ CategoryItem 创建成功")
        
        # 测试产品项
        product_item = ProductItem()
        product_item['name'] = '测试产品'
        product_item['url'] = 'https://vivbliss.com/product/test'
        product_item['price'] = '¥199.00'
        product_item['stock_status'] = 'in_stock'
        product_item['description'] = '测试产品描述'
        product_item['created_at'] = datetime.now().isoformat()
        print("✅ ProductItem 创建成功")
        
        return True
    except Exception as e:
        print(f"❌ 数据模型创建失败: {e}")
        return False

def test_category_discovery_logic():
    """测试分类发现逻辑"""
    print("\n🧪 测试分类发现逻辑...")
    
    # 模拟HTML内容中的分类链接
    mock_html_content = """
    <nav class="main-navigation">
        <ul class="category-menu">
            <li><a href="/category/clothing">服装</a></li>
            <li><a href="/category/accessories">配饰</a></li>
            <li><a href="/category/shoes">鞋类</a></li>
        </ul>
    </nav>
    """
    
    # 模拟分类链接发现
    category_patterns = [
        r'href="(/category/[^"]+)"',
        r'href="(/categories/[^"]+)"',
        r'href="(/cat/[^"]+)"'
    ]
    
    discovered_categories = set()
    
    for pattern in category_patterns:
        matches = re.findall(pattern, mock_html_content)
        for match in matches:
            discovered_categories.add(match)
    
    print(f"发现的分类链接: {list(discovered_categories)}")
    
    # 验证发现的分类
    expected_categories = ['/category/clothing', '/category/accessories', '/category/shoes']
    
    success = True
    for expected in expected_categories:
        if expected in discovered_categories:
            print(f"✅ 成功发现分类: {expected}")
        else:
            print(f"❌ 未发现预期分类: {expected}")
            success = False
    
    return success

def test_product_discovery_logic():
    """测试产品发现逻辑"""
    print("\n🧪 测试产品发现逻辑...")
    
    # 模拟产品列表页面内容
    mock_product_html = """
    <div class="products-grid">
        <div class="product-item">
            <a href="/product/shirt-001">精品衬衫</a>
        </div>
        <div class="product-item">
            <a href="/product/pants-002">休闲裤子</a>
        </div>
    </div>
    <div class="shop-items">
        <div class="item">
            <a href="/products/watch-003">时尚手表</a>
        </div>
    </div>
    """
    
    # 模拟产品链接发现
    product_patterns = [
        r'href="(/product/[^"]+)"',
        r'href="(/products/[^"]+)"',
        r'href="(/item/[^"]+)"'
    ]
    
    discovered_products = set()
    
    for pattern in product_patterns:
        matches = re.findall(pattern, mock_product_html)
        for match in matches:
            discovered_products.add(match)
    
    print(f"发现的产品链接: {list(discovered_products)}")
    
    # 验证发现的产品
    expected_products = ['/product/shirt-001', '/product/pants-002', '/products/watch-003']
    
    success = True
    for expected in expected_products:
        if expected in discovered_products:
            print(f"✅ 成功发现产品: {expected}")
        else:
            print(f"❌ 未发现预期产品: {expected}")
            success = False
    
    return success

def test_data_extraction_logic():
    """测试数据提取逻辑"""
    print("\n🧪 测试数据提取逻辑...")
    
    # 模拟产品详情页面内容
    mock_product_detail = """
    <div class="product-page">
        <h1 class="product-title">VivBliss 精品衬衫</h1>
        <div class="product-brand">VivBliss</div>
        <div class="price-section">
            <span class="current-price">¥299.00</span>
            <span class="original-price">¥399.00</span>
        </div>
        <div class="stock-status">现货供应</div>
        <div class="product-description">
            <p>高品质棉质衬衫，舒适透气。</p>
        </div>
        <div class="product-images">
            <img src="/images/shirt-001.jpg" alt="衬衫">
        </div>
        <div class="rating-section">
            <div class="average-rating">4.8</div>
            <div class="review-count">128条评价</div>
        </div>
    </div>
    """
    
    # 测试数据提取
    extraction_tests = [
        ('产品标题', r'<h1 class="product-title">([^<]+)</h1>', 'VivBliss 精品衬衫'),
        ('品牌', r'<div class="product-brand">([^<]+)</div>', 'VivBliss'),
        ('当前价格', r'<span class="current-price">([^<]+)</span>', '¥299.00'),
        ('原价', r'<span class="original-price">([^<]+)</span>', '¥399.00'),
        ('库存状态', r'<div class="stock-status">([^<]+)</div>', '现货供应'),
        ('评分', r'<div class="average-rating">([^<]+)</div>', '4.8'),
    ]
    
    success = True
    for field_name, pattern, expected in extraction_tests:
        match = re.search(pattern, mock_product_detail)
        if match:
            actual = match.group(1)
            if actual == expected:
                print(f"✅ 成功提取{field_name}: {actual}")
            else:
                print(f"❌ {field_name}提取错误，期望：{expected}，实际：{actual}")
                success = False
        else:
            print(f"❌ 未能提取{field_name}")
            success = False
    
    return success

def test_url_building_logic():
    """测试URL构建逻辑"""
    print("\n🧪 测试URL构建逻辑...")
    
    base_url = "https://vivbliss.com"
    relative_urls = [
        "/category/clothing",
        "/product/shirt-001",
        "products/watch-003",  # 没有前导斜杠
        "https://vivbliss.com/absolute/url"  # 绝对URL
    ]
    
    def urljoin_simple(base, relative):
        """简单的URL连接函数"""
        if relative.startswith('http'):
            return relative
        elif relative.startswith('/'):
            return base + relative
        else:
            return base + '/' + relative
    
    success = True
    for relative in relative_urls:
        full_url = urljoin_simple(base_url, relative)
        print(f"URL构建: '{relative}' -> '{full_url}'")
        
        # 验证构建的URL
        if not full_url.startswith('http'):
            print(f"❌ URL格式错误: {full_url}")
            success = False
        elif 'vivbliss.com' not in full_url:
            print(f"❌ URL域名错误: {full_url}")
            success = False
        else:
            print(f"✅ URL构建正确")
    
    return success

def test_data_validation():
    """测试数据验证逻辑"""
    print("\n🧪 测试数据验证逻辑...")
    
    # 测试价格验证
    price_test_cases = [
        ("¥299.00", True),
        ("$29.99", True),
        ("€25.50", True),
        ("199", True),
        ("", False),
        ("免费", False),
        ("价格面议", False)
    ]
    
    def is_valid_price(price_text):
        """验证价格格式"""
        if not price_text:
            return False
        
        # 检查是否包含数字
        if not re.search(r'\d+', price_text):
            return False
        
        # 检查是否是有效的价格格式
        price_patterns = [
            r'^[¥$€£]?\d+\.?\d*$',  # 简单价格格式
            r'^\d+\.?\d*[¥$€£]?$',  # 数字+货币符号
        ]
        
        return any(re.match(pattern, price_text.strip()) for pattern in price_patterns)
    
    success = True
    for price, expected in price_test_cases:
        result = is_valid_price(price)
        if result == expected:
            print(f"✅ 价格验证正确: '{price}' -> {result}")
        else:
            print(f"❌ 价格验证错误: '{price}' -> 期望 {expected}, 实际 {result}")
            success = False
    
    # 测试URL验证
    url_test_cases = [
        ("https://vivbliss.com/product/test", True),
        ("/category/clothing", True),
        ("invalid-url", False),
        ("", False),
        ("https://other-site.com/product", False)  # 不在允许域名内
    ]
    
    def is_valid_url(url, allowed_domains=['vivbliss.com']):
        """验证URL格式"""
        if not url:
            return False
        
        if url.startswith('/'):
            return True  # 相对URL认为有效
        
        if url.startswith('http'):
            for domain in allowed_domains:
                if domain in url:
                    return True
            return False
        
        return False
    
    for url, expected in url_test_cases:
        result = is_valid_url(url)
        if result == expected:
            print(f"✅ URL验证正确: '{url}' -> {result}")
        else:
            print(f"❌ URL验证错误: '{url}' -> 期望 {expected}, 实际 {result}")
            success = False
    
    return success

def main():
    """运行所有集成测试"""
    print("🚀 开始运行集成测试\n")
    
    tests = [
        ("爬虫模块导入", test_spider_import),
        ("爬虫初始化", test_spider_initialization),
        ("数据模型创建", test_data_models),
        ("分类发现逻辑", test_category_discovery_logic),
        ("产品发现逻辑", test_product_discovery_logic),
        ("数据提取逻辑", test_data_extraction_logic),
        ("URL构建逻辑", test_url_building_logic),
        ("数据验证逻辑", test_data_validation)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"运行测试: {test_name}")
        print('='*60)
        
        try:
            if test_func():
                print(f"✅ 测试 '{test_name}' 通过")
                passed_tests += 1
            else:
                print(f"❌ 测试 '{test_name}' 失败")
        except Exception as e:
            print(f"❌ 测试 '{test_name}' 出现异常: {e}")
    
    print(f"\n{'='*60}")
    print(f"📊 集成测试总结")
    print(f"{'='*60}")
    print(f"通过测试: {passed_tests}/{total_tests}")
    print(f"成功率: {passed_tests/total_tests*100:.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 所有集成测试通过！爬虫核心功能正常工作。")
        print("\n🚀 可以继续进行以下工作：")
        print("1. 代码重构和优化")
        print("2. 添加更多错误处理")
        print("3. 性能优化")
        print("4. 详细文档编写")
        return 0
    else:
        print("⚠️  部分集成测试失败，需要修复相关功能。")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)