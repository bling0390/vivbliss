#!/usr/bin/env python3
"""
目录优先级调度器验证脚本
验证目录优先级和产品提取顺序逻辑
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from vivbliss_scraper.utils.priority_scheduler import (
    DirectoryTracker, PriorityRequestQueue, DirectoryPriorityScheduler
)

def test_basic_functionality():
    """测试基本功能"""
    print("🧪 测试基本目录优先级功能")
    print("=" * 50)
    
    # 创建调度器
    scheduler = DirectoryPriorityScheduler()
    
    # 模拟发现目录
    print("📁 发现目录:")
    scheduler.discover_category("/electronics", {"level": 1})
    scheduler.discover_category("/books", {"level": 2}) 
    scheduler.discover_category("/electronics/phones", {"level": 2, "parent": "/electronics"})
    
    # 模拟发现产品
    print("\n🛍️  发现产品:")
    scheduler.discover_product("https://example.com/phone1", "/electronics")
    scheduler.discover_product("https://example.com/phone2", "/electronics")
    scheduler.discover_product("https://example.com/smartphone", "/electronics/phones")
    scheduler.discover_product("https://example.com/book1", "/books")
    scheduler.discover_product("https://example.com/book2", "/books")
    
    # 检查调度器状态
    stats = scheduler.get_scheduler_stats()
    print(f"\n📊 调度器状态:")
    print(f"   发现目录: {stats['directory_stats']['directories_discovered']}")
    print(f"   发现产品: {stats['directory_stats']['products_discovered']}")
    print(f"   当前优先目录: {stats['current_priority_directory']}")
    
    # 获取目录进度报告
    progress_report = scheduler.get_directory_progress_report()
    print(f"\n📈 目录进度报告:")
    for progress in progress_report:
        print(f"   📁 {progress['path']} (级别{progress['level']}): "
              f"{progress['completed_products']}/{progress['total_products']} "
              f"({progress['completion_rate']*100:.1f}%)")
    
    print("\n✅ 基本功能测试完成")
    return True

def test_directory_priority_order():
    """测试目录优先级顺序"""
    print("\n🧪 测试目录优先级顺序")
    print("=" * 50)
    
    tracker = DirectoryTracker()
    
    # 添加不同级别的目录
    print("📁 添加目录 (不按顺序):")
    tracker.add_directory("/level3", {"level": 3})
    tracker.add_directory("/level1", {"level": 1})
    tracker.add_directory("/level2", {"level": 2})
    
    # 测试优先级选择
    print("\n🎯 测试优先级选择:")
    priority_dir1 = tracker.get_next_priority_directory()
    print(f"   第1优先: {priority_dir1} (应该是 /level1)")
    
    # 模拟完成第一个目录
    tracker.completed_directories.add("/level1")
    priority_dir2 = tracker.get_next_priority_directory()
    print(f"   第2优先: {priority_dir2} (应该是 /level2)")
    
    # 模拟完成第二个目录
    tracker.completed_directories.add("/level2")
    priority_dir3 = tracker.get_next_priority_directory()
    print(f"   第3优先: {priority_dir3} (应该是 /level3)")
    
    success = (priority_dir1 == "/level1" and 
               priority_dir2 == "/level2" and 
               priority_dir3 == "/level3")
    
    print(f"\n{'✅ 优先级测试通过' if success else '❌ 优先级测试失败'}")
    return success

def test_product_completion_tracking():
    """测试产品完成度跟踪"""
    print("\n🧪 测试产品完成度跟踪")
    print("=" * 50)
    
    tracker = DirectoryTracker()
    
    # 添加目录和产品
    tracker.add_directory("/test-category", {"level": 1})
    tracker.add_product_to_directory("/test-category", "product1.html")
    tracker.add_product_to_directory("/test-category", "product2.html")
    tracker.add_product_to_directory("/test-category", "product3.html")
    
    # 检查初始状态
    progress = tracker.get_directory_progress("/test-category")
    print(f"📊 初始进度: {progress['completed_products']}/{progress['total_products']}")
    
    # 完成产品
    print("\n✅ 完成产品:")
    tracker.mark_product_completed("product1.html")
    progress = tracker.get_directory_progress("/test-category")
    print(f"   完成 product1: {progress['completed_products']}/{progress['total_products']} ({progress['completion_rate']*100:.1f}%)")
    
    tracker.mark_product_completed("product2.html")
    progress = tracker.get_directory_progress("/test-category")
    print(f"   完成 product2: {progress['completed_products']}/{progress['total_products']} ({progress['completion_rate']*100:.1f}%)")
    
    # 一个产品失败
    tracker.mark_product_failed("product3.html")
    progress = tracker.get_directory_progress("/test-category")
    print(f"   失败 product3: {progress['completed_products']}/{progress['total_products']} ({progress['completion_rate']*100:.1f}%)")
    
    # 检查目录是否完成
    is_completed = tracker.is_directory_completed("/test-category")
    print(f"\n🎯 目录完成状态: {'✅ 已完成' if is_completed else '❌ 未完成'}")
    
    return is_completed

def test_queue_statistics():
    """测试队列统计功能"""
    print("\n🧪 测试队列统计功能")
    print("=" * 50)
    
    queue = PriorityRequestQueue()
    
    # 模拟添加不同类型的请求
    print("➕ 添加模拟请求:")
    
    # 创建模拟请求对象
    class MockRequest:
        def __init__(self, url):
            self.url = url
            self.meta = {}
    
    # 添加请求
    queue.add_category_request(MockRequest("https://example.com/category1"))
    queue.add_product_request(MockRequest("https://example.com/product1"), "/category1")
    queue.add_product_request(MockRequest("https://example.com/product2"), "/category1")
    queue.add_product_request(MockRequest("https://example.com/product3"), "/category2")
    queue.add_other_request(MockRequest("https://example.com/other"))
    
    # 获取统计信息
    stats = queue.get_queue_stats()
    print(f"📊 队列统计:")
    print(f"   分类请求: {stats['category_requests']}")
    print(f"   产品请求总数: {stats['total_product_requests']}")
    print(f"   其他请求: {stats['other_requests']}")
    print(f"   总请求数: {stats['total_requests']}")
    print(f"   按目录分组的产品请求: {stats['product_requests_by_directory']}")
    
    success = (stats['total_requests'] == 5 and 
               stats['total_product_requests'] == 3 and
               stats['category_requests'] == 1)
    
    print(f"\n{'✅ 统计测试通过' if success else '❌ 统计测试失败'}")
    return success

def main():
    """主测试函数"""
    print("🚀 VivBliss 目录优先级调度器验证")
    print("=" * 60)
    
    tests = [
        ("基本功能测试", test_basic_functionality),
        ("目录优先级顺序", test_directory_priority_order),
        ("产品完成度跟踪", test_product_completion_tracking),
        ("队列统计功能", test_queue_statistics)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试出错: {e}")
            results.append((test_name, False))
    
    # 输出总结
    print("\n" + "=" * 60)
    print("📋 测试结果总结:")
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    total = len(results)
    success_rate = (passed / total) * 100 if total > 0 else 0
    
    print(f"\n🎯 总体结果: {passed}/{total} 测试通过 ({success_rate:.1f}%)")
    
    if passed == total:
        print("🎉 所有测试通过！目录优先级调度器工作正常")
        return True
    else:
        print("⚠️  部分测试失败，需要进一步调试")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)