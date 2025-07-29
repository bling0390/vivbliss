#!/usr/bin/env python3
"""
TDD测试用例 - 验证discover_products_with_priority方法缺失错误
RED阶段：编写失败测试确认错误存在
"""

import unittest
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

try:
    from scrapy.http import HtmlResponse
    from vivbliss_scraper.spiders.vivbliss import VivblissSpider
    SCRAPY_AVAILABLE = True
except ImportError:
    SCRAPY_AVAILABLE = False
    print("⚠️  Scrapy 未安装，将跳过需要 Scrapy 的测试")


class TestMissingMethodTDD(unittest.TestCase):
    """测试缺失方法的TDD测试用例"""
    
    def setUp(self):
        """设置测试环境"""
        if SCRAPY_AVAILABLE:
            self.spider = VivblissSpider()
    
    @unittest.skipUnless(SCRAPY_AVAILABLE, "需要 Scrapy")
    def test_discover_products_with_priority_method_exists(self):
        """RED阶段：测试discover_products_with_priority方法是否存在"""
        # 这个测试应该失败，因为方法不存在
        self.assertTrue(
            hasattr(self.spider, 'discover_products_with_priority'),
            "VivblissSpider应该有discover_products_with_priority方法"
        )
    
    @unittest.skipUnless(SCRAPY_AVAILABLE, "需要 Scrapy")
    def test_discover_products_with_priority_method_callable(self):
        """RED阶段：测试方法是否可调用"""
        # 这个测试应该失败，因为方法不存在
        self.assertTrue(
            callable(getattr(self.spider, 'discover_products_with_priority', None)),
            "discover_products_with_priority应该是可调用的方法"
        )
    
    @unittest.skipUnless(SCRAPY_AVAILABLE, "需要 Scrapy")
    def test_discover_products_with_priority_method_signature(self):
        """RED阶段：测试方法签名"""
        # 创建模拟响应
        html_content = """
        <html>
            <body>
                <article>
                    <h2><a href="/product1">Product 1</a></h2>
                    <p>Description</p>
                </article>
            </body>
        </html>
        """
        
        response = HtmlResponse(
            url="https://vivbliss.com/category",
            body=html_content.encode('utf-8'),
            encoding='utf-8'
        )
        
        try:
            # 尝试调用方法 - 这应该失败
            result = list(self.spider.discover_products_with_priority(response, "/category"))
            self.assertIsInstance(result, list, "方法应该返回一个列表")
        except AttributeError as e:
            # 预期的错误 - 测试会失败（RED阶段的目标）
            self.fail(f"方法不存在: {e}")
    
    @unittest.skipUnless(SCRAPY_AVAILABLE, "需要 Scrapy")
    def test_spider_can_call_method_without_error(self):
        """RED阶段：测试爬虫调用方法不会出错"""
        # 模拟parse_category方法中的调用场景
        html_content = """
        <html>
            <body>
                <div class="category">
                    <h1>Electronics</h1>
                    <div class="products">
                        <a href="/product1">Product 1</a>
                        <a href="/product2">Product 2</a>
                    </div>
                </div>
            </body>
        </html>
        """
        
        response = HtmlResponse(
            url="https://vivbliss.com/electronics",
            body=html_content.encode('utf-8'),
            encoding='utf-8'
        )
        
        # 设置meta数据模拟parse_category调用
        response.meta = {
            'category_name': 'Electronics',
            'level': 1,
            'parent_category': None
        }
        
        try:
            # 这应该不会抛出AttributeError
            # 但在RED阶段，我们期望它失败
            requests = list(self.spider.discover_products_with_priority(response, "/electronics"))
            self.assertIsInstance(requests, list, "应该返回请求列表")
            
        except AttributeError as e:
            # 这是我们期望在RED阶段看到的错误
            self.assertIn("discover_products_with_priority", str(e), 
                         "错误应该提到缺失的方法名")
            # 在RED阶段，我们让测试失败以确认错误存在
            raise e


def run_failing_tests():
    """运行失败测试（RED阶段）"""
    print("🔴 TDD RED阶段：运行失败测试验证错误")
    print("=" * 60)
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMissingMethodTDD)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出结果
    print("\n" + "=" * 60)
    print("📊 RED阶段测试结果:")
    print(f"   运行测试: {result.testsRun}")
    print(f"   成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   失败: {len(result.failures)}")
    print(f"   错误: {len(result.errors)}")
    
    if result.failures or result.errors:
        print("\n🔴 预期的失败（RED阶段目标）:")
        for test, traceback in result.failures + result.errors:
            print(f"   - {test}")
            # 显示最后几行错误信息
            error_lines = traceback.strip().split('\n')[-3:]
            for line in error_lines:
                print(f"     {line}")
    
    print(f"\n🎯 RED阶段状态: {'✅ 测试按预期失败' if (result.failures or result.errors) else '❌ 测试意外通过'}")
    
    return result.failures or result.errors


if __name__ == '__main__':
    has_failures = run_failing_tests()
    
    if has_failures:
        print("\n🔴 RED阶段完成：测试按预期失败，现在需要实现功能")
        exit(0)  # RED阶段成功（测试失败是预期的）
    else:
        print("\n⚠️  意外：测试没有失败，可能方法已经存在")
        exit(1)  # RED阶段失败（测试应该失败但没有）