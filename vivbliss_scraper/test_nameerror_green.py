#!/usr/bin/env python3
"""
TDD GREEN阶段测试 - 验证NameError修复
"""

import unittest
import sys
import os
import ast

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

class TestNameErrorFixTDD(unittest.TestCase):
    """测试NameError修复的TDD测试用例"""
    
    def test_category_path_fixed(self):
        """GREEN阶段：测试category_path错误已修复"""
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
        
        # 检查修复
        category_path_used = False
        category_item_path_used = False
        problematic_line = None
        fixed_line = None
        
        for i, line in enumerate(method_lines):
            if 'discover_products_with_priority' in line:
                if 'category_path)' in line:
                    category_path_used = True
                    problematic_line = line.strip()
                if "category_item['path'])" in line:
                    category_item_path_used = True
                    fixed_line = line.strip()
        
        print(f"🟢 GREEN阶段验证：")
        print(f"   错误的 category_path 使用: {'❌ 仍存在' if category_path_used else '✅ 已移除'}")
        print(f"   正确的 category_item['path'] 使用: {'✅ 已应用' if category_item_path_used else '❌ 未应用'}")
        
        if fixed_line:
            print(f"   修复后的代码: {fixed_line}")
        
        # GREEN阶段：错误应该被修复
        self.assertFalse(category_path_used, "category_path不应该再被使用")
        self.assertTrue(category_item_path_used, "应该使用category_item['path']")
    
    def test_syntax_correctness(self):
        """GREEN阶段：测试语法正确性"""
        file_path = "/root/ideas/vivbliss/vivbliss_scraper/vivbliss_scraper/spiders/vivbliss.py"
        
        try:
            # 尝试编译文件以检查语法
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # 编译代码（不执行）
            compile(source_code, file_path, 'exec')
            syntax_valid = True
            error_msg = None
        except SyntaxError as e:
            syntax_valid = False
            error_msg = str(e)
        except Exception as e:
            # 其他错误（如NameError）在编译时不会出现
            syntax_valid = True
            error_msg = f"编译通过，但可能有运行时错误: {type(e).__name__}"
        
        print(f"\n📋 语法检查：")
        print(f"   语法有效: {'✅' if syntax_valid else '❌'}")
        if error_msg:
            print(f"   错误信息: {error_msg}")
        
        self.assertTrue(syntax_valid, "代码应该没有语法错误")
    
    def test_variable_consistency(self):
        """GREEN阶段：测试变量使用一致性"""
        file_path = "/root/ideas/vivbliss/vivbliss_scraper/vivbliss_scraper/spiders/vivbliss.py"
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # 解析AST
        tree = ast.parse(source_code)
        
        # 找到parse_category方法
        parse_category_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == 'parse_category':
                parse_category_node = node
                break
        
        self.assertIsNotNone(parse_category_node, "应该找到parse_category方法")
        
        # 检查category_item是否被正确定义和使用
        category_item_defined = False
        category_item_path_assigned = False
        category_item_path_used = False
        
        for node in ast.walk(parse_category_node):
            # 检查category_item定义
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == 'category_item':
                        category_item_defined = True
                    # 检查category_item['path']赋值
                    elif (isinstance(target, ast.Subscript) and 
                          isinstance(target.value, ast.Name) and 
                          target.value.id == 'category_item' and
                          isinstance(target.slice, ast.Constant) and
                          target.slice.value == 'path'):
                        category_item_path_assigned = True
            
            # 检查在函数调用中使用category_item['path']
            if isinstance(node, ast.Call):
                for arg in node.args:
                    if (isinstance(arg, ast.Subscript) and
                        isinstance(arg.value, ast.Name) and
                        arg.value.id == 'category_item' and
                        isinstance(arg.slice, ast.Constant) and
                        arg.slice.value == 'path'):
                        category_item_path_used = True
        
        print(f"\n🔍 变量一致性检查：")
        print(f"   category_item 已定义: {'✅' if category_item_defined else '❌'}")
        print(f"   category_item['path'] 已赋值: {'✅' if category_item_path_assigned else '❌'}")
        print(f"   category_item['path'] 在函数调用中使用: {'✅' if category_item_path_used else '❌'}")
        
        self.assertTrue(category_item_defined, "category_item应该被定义")
        self.assertTrue(category_item_path_assigned, "category_item['path']应该被赋值")
        self.assertTrue(category_item_path_used, "category_item['path']应该在函数调用中使用")
    
    def test_fix_completeness(self):
        """GREEN阶段：测试修复的完整性"""
        file_path = "/root/ideas/vivbliss/vivbliss_scraper/vivbliss_scraper/spiders/vivbliss.py"
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # 检查是否还有其他地方使用了未定义的category_path
        # 排除注释和字符串
        lines = source_code.split('\n')
        other_category_path_usage = []
        
        for i, line in enumerate(lines, 1):
            # 跳过注释
            if line.strip().startswith('#'):
                continue
            # 跳过字符串中的category_path
            if 'category_path' in line and not ('"category_path"' in line or "'category_path'" in line):
                # 检查是否是函数参数定义
                if 'def ' in line and 'category_path' in line:
                    continue  # 这是合法的参数定义
                # 检查是否是response.meta.get('category_path'
                if "response.meta.get('category_path'" in line:
                    continue  # 这是合法的meta获取
                # 检查是否是参数传递
                if 'category_path=' in line:
                    continue  # 这是合法的参数传递
                    
                # 如果不是上述情况，可能是问题
                if 'category_path' in line and 'category_item' not in line:
                    other_category_path_usage.append((i, line.strip()))
        
        print(f"\n🔎 完整性检查：")
        if other_category_path_usage:
            print(f"   ⚠️  发现其他可能的category_path使用：")
            for line_no, line in other_category_path_usage[:5]:  # 只显示前5个
                print(f"      行 {line_no}: {line}")
        else:
            print(f"   ✅ 没有发现其他未处理的category_path使用")
        
        # 修复应该是完整的
        self.assertEqual(len(other_category_path_usage), 0, 
                        f"不应该有其他未处理的category_path使用，发现{len(other_category_path_usage)}处")


def run_green_phase_tests():
    """运行GREEN阶段测试"""
    print("🟢 TDD GREEN阶段：验证NameError修复")
    print("=" * 60)
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestNameErrorFixTDD)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出结果
    print("\n" + "=" * 60)
    print("📊 GREEN阶段测试结果:")
    print(f"   运行测试: {result.testsRun}")
    print(f"   成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   失败: {len(result.failures)}")
    print(f"   错误: {len(result.errors)}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print("\n🟢 GREEN阶段成功：NameError已修复！")
        print("   ✅ category_path 替换为 category_item['path']")
        print("   ✅ 语法检查通过")
        print("   ✅ 变量使用一致")
        print("   ✅ 修复完整")
    else:
        print("\n❌ GREEN阶段失败：修复可能不完整")
    
    return success


if __name__ == '__main__':
    success = run_green_phase_tests()
    exit(0 if success else 1)