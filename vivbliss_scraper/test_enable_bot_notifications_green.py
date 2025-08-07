#!/usr/bin/env python3
"""
GREEN阶段测试 - ENABLE_BOT_NOTIFICATIONS环境变量支持
验证环境变量功能正常工作
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

class TestEnableBotNotificationsEnvGreen(unittest.TestCase):
    """ENABLE_BOT_NOTIFICATIONS环境变量支持的GREEN阶段测试"""
    
    def setUp(self):
        """设置测试环境"""
        # 清除环境变量以确保测试隔离
        self.env_backup = {}
        for key in ['ENABLE_BOT_NOTIFICATIONS', 'BOT_NOTIFICATIONS_ENABLED', 'TELEGRAM_BOT_NOTIFICATIONS']:
            if key in os.environ:
                self.env_backup[key] = os.environ.pop(key)
    
    def tearDown(self):
        """恢复环境变量"""
        # 清除测试中可能设置的环境变量
        for key in ['ENABLE_BOT_NOTIFICATIONS', 'BOT_NOTIFICATIONS_ENABLED', 'TELEGRAM_BOT_NOTIFICATIONS']:
            if key in os.environ:
                os.environ.pop(key)
        # 恢复原来的环境变量
        os.environ.update(self.env_backup)
    
    def test_environment_variable_false_disables_notifications(self):
        """GREEN阶段：环境变量false值应该禁用通知"""
        from vivbliss_scraper.utils.bot_notifier import BotNotifier
        
        os.environ['ENABLE_BOT_NOTIFICATIONS'] = 'false'
        
        notifier = BotNotifier.create_from_settings({
            'TELEGRAM_NOTIFICATION_CHAT_ID': '123456'
        })
        
        # 检查配置级别的启用状态（不受Pyrogram可用性影响）
        self.assertFalse(notifier.is_config_enabled(), "环境变量'false'应该禁用通知")
    
    def test_environment_variable_true_enables_notifications(self):
        """GREEN阶段：环境变量true值应该启用通知"""
        from vivbliss_scraper.utils.bot_notifier import BotNotifier
        
        os.environ['ENABLE_BOT_NOTIFICATIONS'] = 'true'
        
        notifier = BotNotifier.create_from_settings({
            'TELEGRAM_NOTIFICATION_CHAT_ID': '123456'
        })
        
        self.assertTrue(notifier.is_config_enabled(), "环境变量'true'应该启用通知")
    
    def test_all_true_values_work(self):
        """GREEN阶段：所有形式的true值都应该工作"""
        from vivbliss_scraper.utils.bot_notifier import BotNotifier
        
        true_values = ['true', 'True', 'TRUE', '1', 'yes', 'Yes', 'YES', 'on', 'On', 'ON']
        
        for value in true_values:
            with self.subTest(value=value):
                os.environ['ENABLE_BOT_NOTIFICATIONS'] = value
                
                notifier = BotNotifier.create_from_settings({
                    'TELEGRAM_NOTIFICATION_CHAT_ID': '123456'
                })
                
                self.assertTrue(notifier.is_config_enabled(), 
                              f"环境变量值 '{value}' 应该被识别为true")
    
    def test_all_false_values_work(self):
        """GREEN阶段：所有形式的false值都应该工作"""
        from vivbliss_scraper.utils.bot_notifier import BotNotifier
        
        false_values = ['false', 'False', 'FALSE', '0', 'no', 'No', 'NO', 'off', 'Off', 'OFF', '']
        
        for value in false_values:
            with self.subTest(value=value):
                os.environ['ENABLE_BOT_NOTIFICATIONS'] = value
                
                notifier = BotNotifier.create_from_settings({
                    'TELEGRAM_NOTIFICATION_CHAT_ID': '123456'
                })
                
                self.assertFalse(notifier.is_config_enabled(), 
                               f"环境变量值 '{value}' 应该被识别为false")
    
    def test_settings_override_environment_variable(self):
        """GREEN阶段：设置应该覆盖环境变量"""
        from vivbliss_scraper.utils.bot_notifier import BotNotifier
        
        # 环境变量设为启用
        os.environ['ENABLE_BOT_NOTIFICATIONS'] = 'true'
        
        # 但设置中禁用
        settings = {
            'ENABLE_BOT_NOTIFICATIONS': False,
            'TELEGRAM_NOTIFICATION_CHAT_ID': '123456'
        }
        
        notifier = BotNotifier.create_from_settings(settings)
        
        self.assertFalse(notifier.is_config_enabled(), 
                        "设置中的显式值应该覆盖环境变量")
    
    def test_default_behavior_when_no_env_var(self):
        """GREEN阶段：没有环境变量时应该默认启用"""
        from vivbliss_scraper.utils.bot_notifier import BotNotifier
        
        # 确保环境变量不存在
        if 'ENABLE_BOT_NOTIFICATIONS' in os.environ:
            os.environ.pop('ENABLE_BOT_NOTIFICATIONS')
        
        notifier = BotNotifier.create_from_settings({
            'TELEGRAM_NOTIFICATION_CHAT_ID': '123456'
        })
        
        self.assertTrue(notifier.is_config_enabled(), 
                       "没有环境变量时应该默认启用通知")
    
    def test_invalid_values_default_to_false(self):
        """GREEN阶段：无效值应该默认为false"""
        from vivbliss_scraper.utils.bot_notifier import BotNotifier
        
        invalid_values = ['maybe', 'invalid', '2', '-1', 'null', 'undefined']
        
        for value in invalid_values:
            with self.subTest(value=value):
                os.environ['ENABLE_BOT_NOTIFICATIONS'] = value
                
                notifier = BotNotifier.create_from_settings({
                    'TELEGRAM_NOTIFICATION_CHAT_ID': '123456'
                })
                
                self.assertFalse(notifier.is_config_enabled(), 
                               f"无效环境变量值 '{value}' 应该默认为false")
    
    def test_bool_parsing_method_directly(self):
        """GREEN阶段：测试布尔值解析方法"""
        from vivbliss_scraper.utils.bot_notifier import BotNotifier
        
        # 测试true值
        true_cases = [
            ('true', True),
            ('TRUE', True), 
            ('1', True),
            ('yes', True),
            ('on', True),
            ('enabled', True)
        ]
        
        for input_val, expected in true_cases:
            with self.subTest(input_val=input_val):
                result = BotNotifier._parse_bool_value(input_val)
                self.assertEqual(result, expected, 
                               f"_parse_bool_value('{input_val}') should return {expected}")
        
        # 测试false值
        false_cases = [
            ('false', False),
            ('FALSE', False),
            ('0', False),
            ('no', False),
            ('off', False),
            ('disabled', False),
            ('', False),
            ('invalid', False)
        ]
        
        for input_val, expected in false_cases:
            with self.subTest(input_val=input_val):
                result = BotNotifier._parse_bool_value(input_val)
                self.assertEqual(result, expected, 
                               f"_parse_bool_value('{input_val}') should return {expected}")


def run_green_phase_tests():
    """运行GREEN阶段测试"""
    print("🟢 TDD GREEN阶段：验证ENABLE_BOT_NOTIFICATIONS环境变量支持正常工作")
    print("=" * 80)
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEnableBotNotificationsEnvGreen)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出结果
    print("\n" + "=" * 80)
    print("📊 GREEN阶段测试结果:")
    print(f"   运行测试: {result.testsRun}")
    print(f"   成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   失败: {len(result.failures)}")
    print(f"   错误: {len(result.errors)}")
    
    if result.failures or result.errors:
        print("\n🔴 GREEN阶段失败：实现存在问题")
        for failure in result.failures:
            print(f"   失败: {failure[0]}")
        for error in result.errors:
            print(f"   错误: {error[0]}")
        return False
    else:
        print("\n🟢 GREEN阶段成功：ENABLE_BOT_NOTIFICATIONS环境变量支持已完成！")
        print("   实现的功能:")
        print("   ✅ 从环境变量读取ENABLE_BOT_NOTIFICATIONS")
        print("   ✅ 处理各种true/false值格式")
        print("   ✅ 正确的默认值处理")
        print("   ✅ 设置参数优先级")
        print("   ✅ 无效值的安全处理")
        print("   ✅ 配置级别与运行时级别分离")
        return True


if __name__ == '__main__':
    success = run_green_phase_tests()
    exit(0 if success else 1)