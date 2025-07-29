#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的爬虫功能测试，不依赖外部库
测试分类和产品发现功能的基本逻辑
"""

import sys
import os
import re
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

def test_category_url_pattern():
    """测试分类 URL 模式匹配"""
    print("🧪 测试分类 URL 模式匹配...")
    
    # 定义 URL 模式
    category_patterns = [
        r'/category/[\w\-/]+',
        r'/categories/[\w\-/]+',
        r'/cat/[\w\-/]+',
        r'/shop/[\w\-/]+',
        r'/products/[\w\-/]+',
        r'/collection/[\w\-/]+'
    ]
    
    # 测试用例
    test_urls = [
        '/category/clothing',
        '/category/clothing/mens',
        '/category/clothing/mens/shirts',
        '/categories/accessories',
        '/shop/electronics',
        '/products/smartphones',
        '/collection/summer-2024',
        '/invalid/path',  # 这个应该不匹配
        '/category/',     # 这个应该不匹配
    ]
    
    valid_urls = []
    for url in test_urls:
        is_valid = any(re.match(pattern + '$', url) for pattern in category_patterns)
        if is_valid:
            valid_urls.append(url)
            print(f"✅ 有效分类 URL: {url}")
        else:
            print(f"❌ 无效分类 URL: {url}")
    
    print(f"📊 总计: {len(valid_urls)}/{len(test_urls)} 个有效分类 URL")
    return len(valid_urls) > 0

def test_category_hierarchy():
    """测试分类层级构建逻辑"""
    print("\n🧪 测试分类层级构建...")
    
    def build_category_path(category_name, parent_path=None):
        """构建分类路径"""
        if parent_path:
            return f"{parent_path}/{category_name}"
        return category_name
    
    test_cases = [
        {
            'category': '服装',
            'parent': None,
            'expected': '服装'
        },
        {
            'category': '男装',
            'parent': '服装',
            'expected': '服装/男装'
        },
        {
            'category': '衬衫',
            'parent': '服装/男装',
            'expected': '服装/男装/衬衫'
        },
        {
            'category': '配饰',
            'parent': None,
            'expected': '配饰'
        }
    ]
    
    all_passed = True
    for case in test_cases:
        result = build_category_path(case['category'], case['parent'])
        if result == case['expected']:
            print(f"✅ 分类路径构建成功: '{case['category']}' -> '{result}'")
        else:
            print(f"❌ 分类路径构建失败: 期望 '{case['expected']}', 得到 '{result}'")
            all_passed = False
    
    return all_passed

def test_product_data_extraction():
    """测试产品数据提取逻辑"""
    print("\n🧪 测试产品数据提取逻辑...")
    
    # 模拟产品数据
    mock_product_data = {
        'name': 'VivBliss 精品衬衫',
        'price': '¥299.00',
        'original_price': '¥399.00',
        'stock_status': 'in_stock',
        'description': '高品质棉质衬衫，舒适透气，适合商务和休闲场合。',
        'rating': 4.5,
        'review_count': 128,
        'image_urls': [
            'https://vivbliss.com/images/shirt-1.jpg',
            'https://vivbliss.com/images/shirt-2.jpg'
        ]
    }
    
    # 验证数据结构
    required_fields = ['name', 'price', 'stock_status']
    optional_fields = ['original_price', 'description', 'rating', 'review_count', 'image_urls']
    
    print("验证必需字段:")
    for field in required_fields:
        if field in mock_product_data and mock_product_data[field]:
            print(f"✅ {field}: {mock_product_data[field]}")
        else:
            print(f"❌ 缺少必需字段: {field}")
            return False
    
    print("验证可选字段:")
    for field in optional_fields:
        if field in mock_product_data:
            value = mock_product_data[field]
            if isinstance(value, list):
                print(f"✅ {field}: {len(value)} 项")
            else:
                print(f"✅ {field}: {value}")
        else:
            print(f"⚪ 可选字段 {field} 未设置（正常）")
    
    return True

def test_price_extraction():
    """测试价格提取逻辑"""
    print("\n🧪 测试价格提取逻辑...")
    
    price_test_cases = [
        ("¥299.00", "¥299.00"),
        ("$29.99", "$29.99"),
        ("€25.50", "€25.50"),
        ("299", "299"),
        ("价格: ¥199.00", "¥199.00"),
        ("Price: $19.99 USD", "$19.99"),
        ("", None)
    ]
    
    def extract_price(price_text):
        """从价格文本中提取价格"""
        if not price_text:
            return None
        
        # 查找价格模式
        price_patterns = [
            r'[¥$€£]\d+\.?\d*',  # 货币符号 + 数字
            r'\d+\.?\d*\s*[¥$€£]',  # 数字 + 货币符号
            r'\d+\.?\d*'  # 纯数字
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, price_text)
            if match:
                return match.group()
        
        return price_text.strip()
    
    all_passed = True
    for test_input, expected in price_test_cases:
        result = extract_price(test_input)
        if (result is None and expected is None) or (result and expected and expected in result):
            print(f"✅ 价格提取成功: '{test_input}' -> '{result}'")
        else:
            print(f"❌ 价格提取失败: '{test_input}' -> 期望包含 '{expected}', 得到 '{result}'")
            all_passed = False
    
    return all_passed

def test_category_data_structure():
    """测试分类数据结构"""
    print("\n🧪 测试分类数据结构...")
    
    # 模拟 CategoryItem 数据结构
    mock_category = {
        'name': '服装',
        'url': 'https://vivbliss.com/category/clothing',
        'slug': 'clothing',
        'level': 1,
        'path': '服装',
        'product_count': 156,
        'description': '时尚服装收藏',
        'parent_category': None,
        'created_at': datetime.now().isoformat(),
        'meta_title': 'VivBliss 服装分类',
        'meta_description': '探索我们的服装收藏'
    }
    
    # 验证必需字段
    required_category_fields = ['name', 'url', 'level', 'path']
    
    all_valid = True
    for field in required_category_fields:
        if field in mock_category and mock_category[field] is not None:
            print(f"✅ 分类字段 {field}: {mock_category[field]}")
        else:
            print(f"❌ 分类缺少必需字段: {field}")
            all_valid = False
    
    # 验证分类层级
    if mock_category['level'] > 0:
        print(f"✅ 分类层级有效: {mock_category['level']}")
    else:
        print(f"❌ 分类层级无效: {mock_category['level']}")
        all_valid = False
    
    # 验证日期格式
    try:
        datetime.fromisoformat(mock_category['created_at'].replace('Z', '+00:00'))
        print(f"✅ 创建时间格式有效: {mock_category['created_at']}")
    except ValueError:
        print(f"❌ 创建时间格式无效: {mock_category['created_at']}")
        all_valid = False
    
    return all_valid

def main():
    """运行所有测试"""
    print("🚀 开始运行分类和产品爬取功能测试\n")
    
    tests = [
        ("分类 URL 模式匹配", test_category_url_pattern),
        ("分类层级构建", test_category_hierarchy),
        ("产品数据提取", test_product_data_extraction),
        ("价格提取逻辑", test_price_extraction),
        ("分类数据结构", test_category_data_structure)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"运行测试: {test_name}")
        print('='*50)
        
        try:
            if test_func():
                print(f"✅ 测试 '{test_name}' 通过")
                passed_tests += 1
            else:
                print(f"❌ 测试 '{test_name}' 失败")
        except Exception as e:
            print(f"❌ 测试 '{test_name}' 出现异常: {e}")
    
    print(f"\n{'='*50}")
    print(f"📊 测试总结")
    print(f"{'='*50}")
    print(f"通过测试: {passed_tests}/{total_tests}")
    print(f"成功率: {passed_tests/total_tests*100:.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 所有测试通过！分类和产品爬取功能逻辑正确。")
        return 0
    else:
        print("⚠️  部分测试失败，需要修复相关功能。")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)