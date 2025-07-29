"""
目录优先级调度器的TDD测试用例
测试先完成当前目录所有商品，再进入下一目录的逻辑
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from scrapy import Request
    from vivbliss_scraper.utils.priority_scheduler import (
        DirectoryTracker, PriorityRequestQueue, DirectoryPriorityScheduler
    )
    SCRAPY_AVAILABLE = True
except ImportError:
    SCRAPY_AVAILABLE = False
    print("⚠️  Scrapy 未安装，将跳过需要 Scrapy 的测试")


class TestDirectoryTrackingTDD(unittest.TestCase):
    """目录跟踪器TDD测试"""
    
    def setUp(self):
        """设置测试环境"""
        if SCRAPY_AVAILABLE:
            self.tracker = DirectoryTracker()
    
    # ============ RED Phase Tests (应该失败) ============
    
    @unittest.skipUnless(SCRAPY_AVAILABLE, "需要 Scrapy")
    def test_directory_completion_tracking_should_work(self):
        """测试目录完成度跟踪功能"""
        # 添加目录和产品
        self.tracker.add_directory("/electronics", {"level": 1})
        self.tracker.add_product_to_directory("/electronics", "product1.html")
        self.tracker.add_product_to_directory("/electronics", "product2.html")
        
        # 目录应该未完成
        self.assertFalse(self.tracker.is_directory_completed("/electronics"))
        
        # 完成一个产品
        self.tracker.mark_product_completed("product1.html")
        self.assertFalse(self.tracker.is_directory_completed("/electronics"))
        
        # 完成第二个产品，目录应该完成
        self.tracker.mark_product_completed("product2.html")
        self.assertTrue(self.tracker.is_directory_completed("/electronics"))
    
    @unittest.skipUnless(SCRAPY_AVAILABLE, "需要 Scrapy")
    def test_priority_directory_selection(self):
        """测试优先目录选择逻辑"""
        # 添加不同级别的目录
        self.tracker.add_directory("/level1", {"level": 1})
        self.tracker.add_directory("/level2", {"level": 2})
        self.tracker.add_directory("/level3", {"level": 3})
        
        # 应该优先选择级别最低的目录
        priority_dir = self.tracker.get_next_priority_directory()
        self.assertEqual(priority_dir, "/level1")
        
        # 完成级别1目录后，应该选择级别2
        self.tracker.completed_directories.add("/level1")
        priority_dir = self.tracker.get_next_priority_directory()
        self.assertEqual(priority_dir, "/level2")


class TestPriorityRequestQueueTDD(unittest.TestCase):
    """优先级请求队列TDD测试"""
    
    def setUp(self):
        """设置测试环境"""
        if SCRAPY_AVAILABLE:
            self.queue = PriorityRequestQueue()
    
    @unittest.skipUnless(SCRAPY_AVAILABLE, "需要 Scrapy")
    def test_request_priority_ordering(self):
        """测试请求优先级排序"""
        # 创建不同类型的请求
        category_req = Request("https://example.com/category1")
        product_req1 = Request("https://example.com/product1")
        product_req2 = Request("https://example.com/product2")
        other_req = Request("https://example.com/other")
        
        # 添加请求（故意打乱顺序）
        self.queue.add_other_request(other_req)
        self.queue.add_product_request(product_req1, "/category1")
        self.queue.add_category_request(category_req)
        self.queue.add_product_request(product_req2, "/category1")
        
        # 应该优先返回指定目录的产品请求
        next_req = self.queue.get_next_request(priority_directory="/category1")
        self.assertEqual(next_req, product_req1)
        
        # 第二个产品请求
        next_req = self.queue.get_next_request(priority_directory="/category1")
        self.assertEqual(next_req, product_req2)
        
        # 然后是分类请求
        next_req = self.queue.get_next_request(priority_directory="/category1")
        self.assertEqual(next_req, category_req)
        
        # 最后是其他请求
        next_req = self.queue.get_next_request(priority_directory="/category1")
        self.assertEqual(next_req, other_req)
    
    @unittest.skipUnless(SCRAPY_AVAILABLE, "需要 Scrapy")
    def test_request_deduplication(self):
        """测试请求去重功能"""
        # 创建相同的请求
        req1 = Request("https://example.com/same-url")
        req2 = Request("https://example.com/same-url")
        
        # 第一个应该成功添加
        result1 = self.queue.add_product_request(req1, "/category1")
        self.assertTrue(result1)
        
        # 第二个应该被去重
        result2 = self.queue.add_product_request(req2, "/category1")
        self.assertFalse(result2)
        
        # 队列中应该只有一个请求
        stats = self.queue.get_queue_stats()
        self.assertEqual(stats["total_product_requests"], 1)


class TestSchedulerIntegrationTDD(unittest.TestCase):
    """调度器集成TDD测试"""
    
    def setUp(self):
        """设置测试环境"""
        if SCRAPY_AVAILABLE:
            self.scheduler = DirectoryPriorityScheduler()
    
    @unittest.skipUnless(SCRAPY_AVAILABLE, "需要 Scrapy")
    def test_complete_directory_before_next_workflow(self):
        """测试完整的'完成当前目录再进入下一目录'工作流"""
        # 场景：有两个目录，每个目录有两个产品
        
        # 1. 发现目录和产品
        self.scheduler.discover_category("/electronics", {"level": 1})
        self.scheduler.discover_category("/books", {"level": 2})
        
        # 添加产品请求
        electronics_req1 = Request("https://example.com/phone1")
        electronics_req2 = Request("https://example.com/phone2")
        books_req1 = Request("https://example.com/book1")
        books_req2 = Request("https://example.com/book2")
        
        self.scheduler.add_product_request(electronics_req1, "/electronics")
        self.scheduler.add_product_request(electronics_req2, "/electronics")
        self.scheduler.add_product_request(books_req1, "/books")
        self.scheduler.add_product_request(books_req2, "/books")
        
        # 2. 验证请求调度顺序
        
        # 应该首先处理electronics目录（级别更低）
        req1 = self.scheduler.get_next_request()
        self.assertIn(req1.url, ["https://example.com/phone1", "https://example.com/phone2"])
        
        req2 = self.scheduler.get_next_request() 
        self.assertIn(req2.url, ["https://example.com/phone1", "https://example.com/phone2"])
        self.assertNotEqual(req1.url, req2.url)  # 应该是不同的产品
        
        # 在electronics目录完成之前，不应该处理books目录
        # 完成第一个electronics产品
        self.scheduler.mark_product_completed(req1.url)
        
        # 下一个请求仍应该是electronics目录的剩余产品
        req3 = self.scheduler.get_next_request()
        # 如果还有electronics产品未完成，应该继续处理electronics
        # 如果electronics完成了，才开始books
        
        # 完成第二个electronics产品
        self.scheduler.mark_product_completed(req2.url)
        
        # 现在electronics目录应该完成，开始处理books
        req4 = self.scheduler.get_next_request()
        self.assertIn(req4.url, ["https://example.com/book1", "https://example.com/book2"])
        
        req5 = self.scheduler.get_next_request()
        self.assertIn(req5.url, ["https://example.com/book1", "https://example.com/book2"])
        self.assertNotEqual(req4.url, req5.url)
    
    @unittest.skipUnless(SCRAPY_AVAILABLE, "需要 Scrapy")
    def test_directory_progress_tracking(self):
        """测试目录进度跟踪"""
        # 添加目录和产品
        self.scheduler.discover_category("/test-category", {"level": 1})
        
        req1 = Request("https://example.com/product1")
        req2 = Request("https://example.com/product2") 
        req3 = Request("https://example.com/product3")
        
        self.scheduler.add_product_request(req1, "/test-category")
        self.scheduler.add_product_request(req2, "/test-category")
        self.scheduler.add_product_request(req3, "/test-category")
        
        # 检查初始进度
        progress = self.scheduler.directory_tracker.get_directory_progress("/test-category")
        self.assertEqual(progress["total_products"], 3)
        self.assertEqual(progress["completed_products"], 0)
        self.assertEqual(progress["completion_rate"], 0.0)
        
        # 完成一个产品
        self.scheduler.mark_product_completed("https://example.com/product1")
        progress = self.scheduler.directory_tracker.get_directory_progress("/test-category")
        self.assertEqual(progress["completed_products"], 1)
        self.assertAlmostEqual(progress["completion_rate"], 1/3)
        
        # 完成所有产品
        self.scheduler.mark_product_completed("https://example.com/product2")
        self.scheduler.mark_product_completed("https://example.com/product3")
        
        progress = self.scheduler.directory_tracker.get_directory_progress("/test-category")
        self.assertEqual(progress["completed_products"], 3)
        self.assertEqual(progress["completion_rate"], 1.0)
        self.assertTrue(self.scheduler.directory_tracker.is_directory_completed("/test-category"))
    
    @unittest.skipUnless(SCRAPY_AVAILABLE, "需要 Scrapy")
    def test_failed_products_handling(self):
        """测试失败产品的处理"""
        self.scheduler.discover_category("/test-category", {"level": 1})
        
        req1 = Request("https://example.com/product1")
        req2 = Request("https://example.com/product2")
        
        self.scheduler.add_product_request(req1, "/test-category")
        self.scheduler.add_product_request(req2, "/test-category")
        
        # 一个产品成功，一个产品失败
        self.scheduler.mark_product_completed("https://example.com/product1")
        self.scheduler.mark_product_failed("https://example.com/product2")
        
        # 目录应该被标记为完成（包括失败的产品）
        progress = self.scheduler.directory_tracker.get_directory_progress("/test-category")
        self.assertEqual(progress["completed_products"], 1)
        self.assertEqual(progress["failed_products"], 1)
        self.assertEqual(progress["completion_rate"], 1.0)  # (1成功 + 1失败) / 2总数 = 1.0
        
        self.assertTrue(self.scheduler.directory_tracker.is_directory_completed("/test-category"))
    
    @unittest.skipUnless(SCRAPY_AVAILABLE, "需要 Scrapy")
    def test_multi_level_directory_priority(self):
        """测试多级目录的优先级处理"""
        # 添加不同级别的目录
        self.scheduler.discover_category("/level1", {"level": 1})
        self.scheduler.discover_category("/level1/sublevel2", {"level": 2, "parent": "/level1"})
        self.scheduler.discover_category("/level1/sublevel2/sublevel3", {"level": 3, "parent": "/level1/sublevel2"})
        
        # 为每个级别添加产品
        req_l1 = Request("https://example.com/l1-product")
        req_l2 = Request("https://example.com/l2-product")
        req_l3 = Request("https://example.com/l3-product")
        
        self.scheduler.add_product_request(req_l3, "/level1/sublevel2/sublevel3")  # 添加顺序故意打乱
        self.scheduler.add_product_request(req_l1, "/level1")
        self.scheduler.add_product_request(req_l2, "/level1/sublevel2")
        
        # 应该按级别顺序处理：level1 -> level2 -> level3
        req1 = self.scheduler.get_next_request()
        self.assertEqual(req1.url, "https://example.com/l1-product")
        
        # 完成level1目录
        self.scheduler.mark_product_completed("https://example.com/l1-product")
        
        # 然后处理level2
        req2 = self.scheduler.get_next_request()
        self.assertEqual(req2.url, "https://example.com/l2-product")
        
        # 完成level2目录
        self.scheduler.mark_product_completed("https://example.com/l2-product")
        
        # 最后处理level3
        req3 = self.scheduler.get_next_request()
        self.assertEqual(req3.url, "https://example.com/l3-product")


class TestSchedulerPerformanceTDD(unittest.TestCase):
    """调度器性能测试"""
    
    def setUp(self):
        """设置测试环境"""
        if SCRAPY_AVAILABLE:
            self.scheduler = DirectoryPriorityScheduler()
    
    @unittest.skipUnless(SCRAPY_AVAILABLE, "需要 Scrapy")
    def test_large_scale_scheduling_performance(self):
        """测试大规模调度性能"""
        import time
        
        # 创建大量目录和产品
        num_categories = 10
        products_per_category = 100
        
        start_time = time.time()
        
        # 添加目录和产品
        for cat_i in range(num_categories):
            category_path = f"/category_{cat_i}"
            self.scheduler.discover_category(category_path, {"level": cat_i + 1})
            
            for prod_i in range(products_per_category):
                product_url = f"https://example.com/cat{cat_i}_prod{prod_i}"
                req = Request(product_url)
                self.scheduler.add_product_request(req, category_path)
        
        setup_time = time.time() - start_time
        
        # 测试调度性能
        start_time = time.time()
        requests_processed = 0
        
        # 处理前100个请求
        for _ in range(100):
            req = self.scheduler.get_next_request()
            if req:
                requests_processed += 1
                # 模拟产品处理完成
                self.scheduler.mark_product_completed(req.url)
        
        scheduling_time = time.time() - start_time
        
        # 性能要求
        self.assertLess(setup_time, 5.0, f"设置时间过长: {setup_time:.2f}s")
        self.assertLess(scheduling_time, 1.0, f"调度时间过长: {scheduling_time:.2f}s")
        self.assertEqual(requests_processed, 100, "应该处理100个请求")
        
        # 验证调度顺序正确性（应该先处理category_0的所有产品）
        stats = self.scheduler.get_scheduler_stats()
        self.assertGreater(stats["directory_stats"]["directories_completed"], 0, "应该有目录被完成")


class TestSchedulerEdgeCasesTDD(unittest.TestCase):
    """调度器边缘情况测试"""
    
    def setUp(self):
        """设置测试环境"""
        if SCRAPY_AVAILABLE:
            self.scheduler = DirectoryPriorityScheduler()
    
    @unittest.skipUnless(SCRAPY_AVAILABLE, "需要 Scrapy")
    def test_empty_directory_handling(self):
        """测试空目录处理"""
        # 添加空目录
        self.scheduler.discover_category("/empty-category", {"level": 1})
        
        # 空目录应该被自动标记为完成
        # 或者在没有产品时不影响调度
        req = self.scheduler.get_next_request()
        self.assertIsNone(req, "空目录不应该产生请求")
    
    @unittest.skipUnless(SCRAPY_AVAILABLE, "需要 Scrapy")
    def test_scheduler_disable_enable(self):
        """测试调度器启用/禁用功能"""
        # 添加一些请求
        self.scheduler.discover_category("/test", {"level": 1})
        req = Request("https://example.com/product")
        self.scheduler.add_product_request(req, "/test")
        
        # 禁用调度器
        self.scheduler.disable_scheduler()
        
        # 应该仍能获取请求，但不按优先级
        next_req = self.scheduler.get_next_request()
        self.assertIsNotNone(next_req)
        
        # 重新启用
        self.scheduler.enable_scheduler()
        stats = self.scheduler.get_scheduler_stats()
        self.assertTrue(stats["scheduler_enabled"])


def run_priority_tests():
    """运行所有优先级调度测试"""
    print("🧪 开始运行目录优先级调度TDD测试")
    print("=" * 60)
    
    test_classes = [
        TestDirectoryTrackingTDD,
        TestPriorityRequestQueueTDD,
        TestSchedulerIntegrationTDD,
        TestSchedulerPerformanceTDD,
        TestSchedulerEdgeCasesTDD
    ]
    
    suite = unittest.TestSuite()
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出结果
    print("\n" + "=" * 60)
    print("📊 TDD测试结果:")
    print(f"   运行测试: {result.testsRun}")
    print(f"   成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   失败: {len(result.failures)}")
    print(f"   错误: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ 失败的测试 (RED阶段 - 预期的):")
        for test, traceback in result.failures:
            print(f"   - {test}")
    
    if result.errors:
        print("\n💥 错误的测试:")
        for test, traceback in result.errors:
            print(f"   - {test}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if not success:
        print("\n🔴 TDD红灯阶段：测试失败是预期的，现在需要实现功能使测试通过")
    else:
        print("\n🟢 TDD绿灯阶段：所有测试通过！")
    
    return success


if __name__ == '__main__':
    run_priority_tests()