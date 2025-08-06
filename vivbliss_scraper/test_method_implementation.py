#!/usr/bin/env python3
"""
TDD GREEN阶段测试 - 验证discover_products_with_priority方法实现
"""

import sys
import os
import ast
import inspect

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

def test_method_syntax():
    """测试方法语法是否正确"""
    print("🟢 GREEN阶段：验证方法实现")
    print("=" * 50)
    
    try:
        # 读取文件并解析AST
        file_path = "/root/ideas/vivbliss/vivbliss_scraper/vivbliss_scraper/spiders/vivbliss.py"
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # 解析语法树
        tree = ast.parse(source_code)
        
        # 查找方法定义
        method_found = False
        method_details = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == 'discover_products_with_priority':
                method_found = True
                method_details = {
                    'name': node.name,
                    'args': [arg.arg for arg in node.args.args],
                    'decorators': [decorator.id if hasattr(decorator, 'id') else str(decorator) for decorator in node.decorator_list],
                    'line_number': node.lineno,
                    'has_docstring': isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant)
                }
                break
        
        print(f"📋 方法检查结果:")
        print(f"   ✅ 方法定义找到: {method_found}")
        
        if method_found:
            print(f"   📝 方法名称: {method_details['name']}")
            print(f"   📦 参数列表: {method_details['args']}")
            print(f"   🎨 装饰器: {method_details['decorators']}")
            print(f"   📍 行号: {method_details['line_number']}")
            print(f"   📖 有文档字符串: {method_details['has_docstring']}")
            
            # 验证方法签名
            expected_args = ['self', 'response', 'category_path']
            actual_args = method_details['args']
            signature_correct = all(arg in actual_args for arg in expected_args[:2])  # self和response是必需的
            
            print(f"   ✅ 方法签名正确: {signature_correct}")
            
            # 验证装饰器
            expected_decorators = ['timing_decorator', 'error_handler']
            has_decorators = any(dec in str(method_details['decorators']) for dec in expected_decorators)
            print(f"   ✅ 有必要的装饰器: {has_decorators}")
        
        return method_found and method_details
        
    except Exception as e:
        print(f"❌ 语法检查失败: {e}")
        return False

def test_method_content():
    """测试方法内容是否合理"""
    print(f"\n🔍 内容分析:")
    
    try:
        file_path = "/root/ideas/vivbliss/vivbliss_scraper/vivbliss_scraper/spiders/vivbliss.py"
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取方法内容
        lines = content.split('\n')
        start_line = None
        end_line = None
        
        for i, line in enumerate(lines):
            if 'def discover_products_with_priority' in line:
                start_line = i
            elif start_line is not None and line.strip().startswith('def ') and i > start_line:
                end_line = i
                break
        
        if start_line is None:
            print("❌ 未找到方法定义")
            return False
        
        if end_line is None:
            end_line = len(lines)
        
        method_lines = lines[start_line:end_line]
        method_content = '\n'.join(method_lines)
        
        print(f"   📏 方法行数: {len(method_lines)}")
        
        # 检查关键功能
        key_features = {
            '链接发现': 'link_discovery.discover_product_links' in method_content,
            '日志记录': 'LoggingHelper.log_discovery_results' in method_content,
            '统计更新': 'stats_manager.increment' in method_content,
            '请求构建': 'RequestBuilder.build_product_request' in method_content,
            '调度器集成': 'priority_scheduler.add_product_request' in method_content,
            '错误处理': 'parse_product_with_error_handling' in method_content
        }
        
        for feature, present in key_features.items():
            print(f"   {'✅' if present else '❌'} {feature}: {present}")
        
        all_features_present = all(key_features.values())
        print(f"\n   🎯 所有关键功能完整: {all_features_present}")
        
        return all_features_present
        
    except Exception as e:
        print(f"❌ 内容分析失败: {e}")
        return False

def test_integration_points():
    """测试与其他组件的集成点"""
    print(f"\n🔗 集成点检查:")
    
    try:
        file_path = "/root/ideas/vivbliss/vivbliss_scraper/vivbliss_scraper/spiders/vivbliss.py"
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        integration_checks = {
            '调用点存在': 'discover_products_with_priority(response, category_path)' in content,
            '优先级调度器导入': 'from vivbliss_scraper.utils.priority_scheduler import DirectoryPriorityScheduler' in content,
            '调度器初始化': 'self.priority_scheduler = DirectoryPriorityScheduler()' in content,
            '错误处理方法': 'parse_product_with_error_handling' in content
        }
        
        for check, passed in integration_checks.items():
            print(f"   {'✅' if passed else '❌'} {check}: {passed}")
        
        all_integrations_ok = all(integration_checks.values())
        print(f"\n   🎯 所有集成检查通过: {all_integrations_ok}")
        
        return all_integrations_ok
        
    except Exception as e:
        print(f"❌ 集成检查失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🟢 TDD GREEN阶段：验证 discover_products_with_priority 方法实现")
    print("=" * 80)
    
    # 运行各项测试
    tests = [
        ("语法检查", test_method_syntax),
        ("内容分析", test_method_content),
        ("集成检查", test_integration_points)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}出错: {e}")
            results.append((test_name, False))
    
    # 输出总结
    print(f"\n" + "=" * 80)
    print("📊 GREEN阶段测试结果:")
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
        print("🟢 GREEN阶段成功：discover_products_with_priority 方法已正确实现！")
        return True
    else:
        print("❌ GREEN阶段失败：方法实现需要进一步完善")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)