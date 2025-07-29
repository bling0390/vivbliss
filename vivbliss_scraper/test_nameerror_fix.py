#!/usr/bin/env python3
"""
TDD测试用例 - 验证NameError: category_path未定义错误
RED阶段：编写失败测试确认错误存在
"""

import unittest
import sys
import os
import ast

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

class TestNameErrorTDD(unittest.TestCase):
    """测试NameError的TDD测试用例"""
    
    def test_category_path_variable_usage(self):
        """RED阶段：测试category_path变量使用情况"""
        # 读取源代码
        file_path = "/root/ideas/vivbliss/vivbliss_scraper/vivbliss_scraper/spiders/vivbliss.py"
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # 查找parse_category方法
        lines = source_code.split('\n')
        parse_category_start = None
        parse_category_end = None
        
        for i, line in enumerate(lines):
            if 'def parse_category' in line:
                parse_category_start = i
            elif parse_category_start is not None and line.strip().startswith('def ') and i > parse_category_start:
                parse_category_end = i
                break
        
        if parse_category_end is None:
            parse_category_end = len(lines)
        
        # 提取parse_category方法内容
        method_lines = lines[parse_category_start:parse_category_end]
        method_content = '\n'.join(method_lines)
        
        # 检查category_path的定义和使用
        category_path_defined = False
        category_path_used = False
        
        for line in method_lines:
            # 检查定义（赋值）
            if 'category_path =' in line and not line.strip().startswith('#'):
                category_path_defined = True
            # 检查使用
            if 'category_path)' in line and 'discover_products_with_priority' in line:
                category_path_used = True
        
        # RED阶段：我们期望category_path被使用但未定义
        self.assertTrue(category_path_used, "category_path应该在discover_products_with_priority调用中被使用")
        self.assertFalse(category_path_defined, "category_path不应该被定义（这是错误的原因）")
        
        # 这将导致NameError
        print(f"🔴 RED阶段确认：category_path被使用但未定义")
        print(f"   使用位置：discover_products_with_priority(response, category_path)")
        print(f"   定义状态：{'已定义' if category_path_defined else '未定义'}")
    
    def test_available_variables_in_parse_category(self):
        """RED阶段：测试parse_category中可用的变量"""
        file_path = "/root/ideas/vivbliss/vivbliss_scraper/vivbliss_scraper/spiders/vivbliss.py"
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # 使用AST解析
        tree = ast.parse(source_code)
        
        # 找到parse_category方法
        parse_category_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == 'parse_category':
                parse_category_node = node
                break
        
        self.assertIsNotNone(parse_category_node, "应该找到parse_category方法")
        
        # 收集方法中的所有赋值
        assigned_vars = set()
        for node in ast.walk(parse_category_node):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        assigned_vars.add(target.id)
                    elif isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name):
                        # 处理 category_item['path'] 这样的赋值
                        assigned_vars.add(target.value.id)
        
        print(f"\n🔍 parse_category中定义的变量：")
        for var in sorted(assigned_vars):
            print(f"   - {var}")
        
        # 检查是否有category_item
        self.assertIn('category_item', assigned_vars, "应该有category_item变量")
        
        # 检查是否没有category_path
        self.assertNotIn('category_path', assigned_vars, "不应该有category_path变量（错误原因）")
    
    def test_correct_variable_should_be_used(self):
        """RED阶段：测试应该使用的正确变量"""
        file_path = "/root/ideas/vivbliss/vivbliss_scraper/vivbliss_scraper/spiders/vivbliss.py"
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # 检查category_item['path']是否存在
        category_item_path_assigned = "category_item['path'] =" in source_code
        
        # 检查错误的使用
        wrong_usage = "discover_products_with_priority(response, category_path)" in source_code
        
        print(f"\n📊 变量使用分析：")
        print(f"   category_item['path'] 已赋值: {'✅' if category_item_path_assigned else '❌'}")
        print(f"   错误使用 category_path: {'⚠️ 是' if wrong_usage else '✅ 否'}")
        
        self.assertTrue(category_item_path_assigned, "category_item['path']应该被赋值")
        self.assertTrue(wrong_usage, "确认存在错误的category_path使用")
        
        print(f"\n💡 建议修复：将 category_path 替换为 category_item['path']")


def run_red_phase_tests():
    """运行RED阶段测试"""
    print("🔴 TDD RED阶段：验证NameError错误")
    print("=" * 60)
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestNameErrorTDD)
    
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
    
    # RED阶段应该有一些测试通过（确认错误存在）
    if result.testsRun > 0 and len(result.errors) == 0:
        print("\n🔴 RED阶段完成：确认了NameError的存在")
        print("   问题：category_path 未定义")
        print("   位置：parse_category方法中调用discover_products_with_priority时")
        print("   修复：应该使用 category_item['path'] 替代 category_path")
        return True
    else:
        print("\n⚠️  RED阶段异常：无法确认错误")
        return False


if __name__ == '__main__':
    success = run_red_phase_tests()
    exit(0 if success else 1)