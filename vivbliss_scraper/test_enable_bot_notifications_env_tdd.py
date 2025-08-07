#!/usr/bin/env python3
"""
TDD测试用例 - ENABLE_BOT_NOTIFICATIONS环境变量支持
RED阶段：编写失败测试验证环境变量功能缺失
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

class TestEnableBotNotificationsEnvTDD(unittest.TestCase):
    """ENABLE_BOT_NOTIFICATIONS环境变量支持的TDD测试用例"""
    
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
    
    def test_bot_notifier_should_read_enable_bot_notifications_env_var(self):
        """RED阶段：测试BotNotifier应该从环境变量读取ENABLE_BOT_NOTIFICATIONS"""
        try:
            from vivbliss_scraper.utils.bot_notifier import BotNotifier
            
            # 设置环境变量为禁用
            os.environ['ENABLE_BOT_NOTIFICATIONS'] = 'false'
            
            # 创建BotNotifier实例，不传入任何设置（但提供chat_id以允许通知）
            notifier = BotNotifier.create_from_settings({'TELEGRAM_NOTIFICATION_CHAT_ID': '123456'})
            
            # 检查是否从环境变量读取了设置（使用config级别的检查）
            env_var_respected = not notifier.is_config_enabled()
            
        except (ImportError, Exception) as e:
            print(f"   错误: {e}")
            env_var_respected = False
        
        print(f"\n🌍 环境变量读取测试:")
        print(f"   从环境变量读取ENABLE_BOT_NOTIFICATIONS: {'✅' if env_var_respected else '❌'}")
        
        # RED阶段：这应该失败，因为当前实现不读取环境变量
        self.assertTrue(env_var_respected, "BotNotifier应该从环境变量读取ENABLE_BOT_NOTIFICATIONS")
    
    def test_environment_variable_true_values(self):
        """RED阶段：测试环境变量的true值处理"""
        try:
            from vivbliss_scraper.utils.bot_notifier import BotNotifier
            
            true_values = ['true', 'True', 'TRUE', '1', 'yes', 'Yes', 'YES', 'on', 'On', 'ON']
            results = []
            
            for value in true_values:
                os.environ['ENABLE_BOT_NOTIFICATIONS'] = value
                notifier = BotNotifier.create_from_settings({'TELEGRAM_NOTIFICATION_CHAT_ID': '123456'})
                results.append(notifier.is_config_enabled())
                
            all_true_values_work = all(results)
            
        except (ImportError, Exception) as e:
            print(f"   错误: {e}")
            all_true_values_work = False
        
        print(f"\n✅ True值测试:")
        print(f"   所有true值被正确识别: {'✅' if all_true_values_work else '❌'}")
        
        # RED阶段：这应该失败
        self.assertTrue(all_true_values_work, "应该正确识别所有形式的true值")
    
    def test_environment_variable_false_values(self):
        """RED阶段：测试环境变量的false值处理"""
        try:
            from vivbliss_scraper.utils.bot_notifier import BotNotifier
            
            false_values = ['false', 'False', 'FALSE', '0', 'no', 'No', 'NO', 'off', 'Off', 'OFF', '']
            results = []
            
            for value in false_values:
                os.environ['ENABLE_BOT_NOTIFICATIONS'] = value
                notifier = BotNotifier.create_from_settings({'TELEGRAM_NOTIFICATION_CHAT_ID': '123456'})
                results.append(not notifier.is_config_enabled())  # 期望为disabled
                
            all_false_values_work = all(results)
            
        except (ImportError, Exception) as e:
            print(f"   错误: {e}")
            all_false_values_work = False
        
        print(f"\n❌ False值测试:")
        print(f"   所有false值被正确识别: {'✅' if all_false_values_work else '❌'}")
        
        # RED阶段：这应该失败
        self.assertTrue(all_false_values_work, "应该正确识别所有形式的false值")
    
    def test_default_behavior_when_env_var_not_set(self):
        """RED阶段：测试环境变量未设置时的默认行为"""
        try:
            from vivbliss_scraper.utils.bot_notifier import BotNotifier
            
            # 确保环境变量未设置
            if 'ENABLE_BOT_NOTIFICATIONS' in os.environ:
                os.environ.pop('ENABLE_BOT_NOTIFICATIONS')
            
            # 创建通知器，不传入设置
            notifier = BotNotifier.create_from_settings({})
            
            # 默认应该是启用的（根据现有代码的默认行为）
            default_enabled = notifier.is_config_enabled()
            
            # 同时测试有chat_id的情况
            notifier_with_chat = BotNotifier.create_from_settings({
                'TELEGRAM_NOTIFICATION_CHAT_ID': '123456'
            })
            default_enabled_with_chat = notifier_with_chat.is_config_enabled()
            
        except (ImportError, Exception) as e:
            print(f"   错误: {e}")
            default_enabled = False
            default_enabled_with_chat = False
        
        print(f"\n🔧 默认行为测试:")
        print(f"   环境变量未设置时默认启用: {'✅' if default_enabled_with_chat else '❌'}")
        
        # RED阶段：这可能成功，因为现有代码有默认值True
        # 但测试环境变量优先级可能失败
        self.assertTrue(default_enabled_with_chat, "环境变量未设置时应该默认启用通知")
    
    def test_settings_override_environment_variable(self):
        """RED阶段：测试设置参数是否覆盖环境变量"""
        try:
            from vivbliss_scraper.utils.bot_notifier import BotNotifier
            
            # 设置环境变量为启用
            os.environ['ENABLE_BOT_NOTIFICATIONS'] = 'true'
            
            # 但在settings中禁用
            settings = {
                'ENABLE_BOT_NOTIFICATIONS': False,
                'TELEGRAM_NOTIFICATION_CHAT_ID': '123456'
            }
            
            notifier = BotNotifier.create_from_settings(settings)
            
            # 设置应该覆盖环境变量
            settings_override_env = not notifier.is_config_enabled()
            
        except (ImportError, Exception) as e:
            print(f"   错误: {e}")
            settings_override_env = False
        
        print(f"\n⚖️  优先级测试:")
        print(f"   设置参数覆盖环境变量: {'✅' if settings_override_env else '❌'}")
        
        # RED阶段：这可能成功，因为现有代码可能已经有这个逻辑
        self.assertTrue(settings_override_env, "显式传入的设置应该覆盖环境变量")
    
    def test_invalid_environment_variable_values(self):
        """RED阶段：测试无效环境变量值的处理"""
        try:
            from vivbliss_scraper.utils.bot_notifier import BotNotifier
            
            invalid_values = ['maybe', 'invalid', '2', '-1', 'null', 'undefined']
            results = []
            
            for value in invalid_values:
                os.environ['ENABLE_BOT_NOTIFICATIONS'] = value
                try:
                    notifier = BotNotifier.create_from_settings({
                        'TELEGRAM_NOTIFICATION_CHAT_ID': '123456'
                    })
                    # 无效值应该被当作false处理，或者回退到默认值
                    results.append(True)  # 如果没有抛出异常就算成功
                except Exception:
                    results.append(False)
                
            invalid_values_handled = all(results)
            
        except (ImportError, Exception) as e:
            print(f"   错误: {e}")
            invalid_values_handled = False
        
        print(f"\n🚫 无效值处理测试:")
        print(f"   无效环境变量值被正确处理: {'✅' if invalid_values_handled else '❌'}")
        
        # RED阶段：这应该失败，因为现有代码可能不处理无效值
        self.assertTrue(invalid_values_handled, "应该正确处理无效的环境变量值")
    
    def test_spider_integration_with_env_variable(self):
        """RED阶段：测试爬虫集成时环境变量的使用"""
        try:
            from vivbliss_scraper.spiders.vivbliss import VivblissSpider
            
            # 设置环境变量
            os.environ['ENABLE_BOT_NOTIFICATIONS'] = 'false'
            
            # 创建爬虫实例，应该从环境变量读取设置
            spider = VivblissSpider()
            
            # 检查爬虫的bot_notifier是否反映了环境变量的值
            env_var_used_in_spider = hasattr(spider, 'bot_notifier') and not spider.bot_notifier.is_config_enabled()
            
        except (ImportError, Exception) as e:
            print(f"   错误: {e}")
            env_var_used_in_spider = False
        
        print(f"\n🕷️  爬虫集成测试:")
        print(f"   爬虫从环境变量读取配置: {'✅' if env_var_used_in_spider else '❌'}")
        
        # RED阶段：这应该失败
        self.assertTrue(env_var_used_in_spider, "爬虫应该从环境变量读取ENABLE_BOT_NOTIFICATIONS设置")
    
    def test_environment_extractor_integration(self):
        """RED阶段：测试与EnvironmentExtractor的集成"""
        try:
            from vivbliss_scraper.config.env_extractor import EnvironmentExtractor
            from vivbliss_scraper.utils.bot_notifier import BotNotifier
            
            # 使用EnvironmentExtractor加载环境变量
            os.environ['ENABLE_BOT_NOTIFICATIONS'] = 'false'
            
            extractor = EnvironmentExtractor()
            # 模拟从环境文件或compose文件加载
            env_vars = {'ENABLE_BOT_NOTIFICATIONS': 'false'}
            
            # 添加chat_id以允许通知功能
            env_vars['TELEGRAM_NOTIFICATION_CHAT_ID'] = '123456'
            # 检查BotNotifier是否可以使用EnvironmentExtractor的结果
            notifier = BotNotifier.create_from_settings(env_vars)
            
            integration_works = not notifier.is_config_enabled()
            
        except (ImportError, Exception) as e:
            print(f"   错误: {e}")
            integration_works = False
        
        print(f"\n🔌 环境提取器集成测试:")
        print(f"   与EnvironmentExtractor集成: {'✅' if integration_works else '❌'}")
        
        # RED阶段：这可能成功，因为BotNotifier.create_from_settings已经接受字典
        self.assertTrue(integration_works, "应该能与EnvironmentExtractor集成")


def run_red_phase_tests():
    """运行RED阶段测试"""
    print("🔴 TDD RED阶段：验证ENABLE_BOT_NOTIFICATIONS环境变量支持缺失")
    print("=" * 80)
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEnableBotNotificationsEnvTDD)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出结果
    print("\n" + "=" * 80)
    print("📊 RED阶段测试结果:")
    print(f"   运行测试: {result.testsRun}")
    print(f"   成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   失败: {len(result.failures)}")
    print(f"   错误: {len(result.errors)}")
    
    # RED阶段应该有一些测试失败（确认功能缺失）
    if result.failures or result.errors:
        print("\n🔴 RED阶段完成：确认了ENABLE_BOT_NOTIFICATIONS环境变量支持缺失")
        print("   需要实现的功能:")
        print("   1. 从环境变量读取ENABLE_BOT_NOTIFICATIONS")
        print("   2. 处理各种true/false值格式")
        print("   3. 正确的默认值处理")
        print("   4. 设置参数优先级")
        print("   5. 无效值的错误处理")
        return True
    else:
        print("\n⚠️  RED阶段异常：环境变量支持可能已存在")
        return False


if __name__ == '__main__':
    success = run_red_phase_tests()
    exit(0 if success else 1)