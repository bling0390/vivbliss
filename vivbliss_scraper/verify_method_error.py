#!/usr/bin/env python3
"""
简单验证脚本 - 确认discover_products_with_priority方法缺失错误
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

def test_method_exists():
    """测试方法是否存在"""
    try:
        from vivbliss_scraper.spiders.vivbliss import VivblissSpider
        spider = VivblissSpider()
        
        # 检查方法是否存在
        has_method = hasattr(spider, 'discover_products_with_priority')
        is_callable = callable(getattr(spider, 'discover_products_with_priority', None))
        
        print(f"🔍 VivblissSpider 类检查:")
        print(f"   - 有 discover_products_with_priority 方法: {'✅' if has_method else '❌'}")
        print(f"   - 方法可调用: {'✅' if is_callable else '❌'}")
        
        if not has_method:
            print(f"\n🔴 确认错误: AttributeError: 'VivblissSpider' object has no attribute 'discover_products_with_priority'")
            return False
        else:
            print(f"\n✅ 方法存在，错误可能已修复")
            return True
            
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

def check_spider_methods():
    """检查爬虫中的所有方法"""
    try:
        from vivbliss_scraper.spiders.vivbliss import VivblissSpider
        spider = VivblissSpider()
        
        # 获取所有方法
        methods = [method for method in dir(spider) if method.startswith('discover')]
        
        print(f"\n📋 VivblissSpider 中的 discover 方法:")
        for method in methods:
            is_callable = callable(getattr(spider, method))
            print(f"   - {method}: {'✅ 可调用' if is_callable else '❌ 不可调用'}")
        
        return methods
        
    except Exception as e:
        print(f"❌ 检查方法时出错: {e}")
        return []

def main():
    """主测试函数"""
    print("🔴 TDD RED阶段：验证 discover_products_with_priority 方法缺失")
    print("=" * 70)
    
    # 测试方法是否存在
    method_exists = test_method_exists()
    
    # 检查现有的discover方法
    existing_methods = check_spider_methods()
    
    print(f"\n" + "=" * 70)
    print("📊 验证结果:")
    print(f"   - 目标方法存在: {'✅' if method_exists else '❌'}")
    print(f"   - 现有discover方法数量: {len(existing_methods)}")
    
    if not method_exists:
        print(f"\n🎯 结论: 需要实现 discover_products_with_priority 方法")
        print(f"💡 建议: 基于现有的 discover_products 方法进行扩展")
        return False
    else:
        print(f"\n✅ 方法已存在，无需修复")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)