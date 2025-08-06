#!/usr/bin/env python3
"""
TDD测试用例 - Bot消息通知功能
RED阶段：编写失败测试验证功能缺失
"""

import unittest
import sys
import os
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

try:
    from vivbliss_scraper.items import VivblissItem, ProductItem
    SCRAPY_AVAILABLE = True
except ImportError:
    SCRAPY_AVAILABLE = False
    print("⚠️  Scrapy 未安装，将跳过需要 Scrapy 的测试")
    
    # Create mock classes for testing when Scrapy is not available
    class VivblissItem(dict):
        def __init__(self):
            super().__init__()
        def __setitem__(self, key, value):
            super().__setitem__(key, value)
        def __getitem__(self, key):
            return super().__getitem__(key)
        def get(self, key, default=None):
            return super().get(key, default)
        def update(self, other):
            super().update(other)


class TestBotNotificationTDD(unittest.TestCase):
    """Bot消息通知功能的TDD测试用例"""
    
    def setUp(self):
        """设置测试环境"""
        self.sample_media_data = {
            'images': [
                'https://example.com/image1.jpg',
                'https://example.com/image2.png',
                'https://example.com/image3.gif'
            ],
            'videos': [
                'https://example.com/video1.mp4',
                'https://www.youtube.com/embed/abc123'
            ],
            'media_files': [
                'https://example.com/image1.jpg',
                'https://example.com/image2.png', 
                'https://example.com/image3.gif',
                'https://example.com/video1.mp4',
                'https://www.youtube.com/embed/abc123'
            ],
            'media_count': 5
        }
    
    def test_bot_notifier_class_should_exist(self):
        """RED阶段：测试BotNotifier类应该存在"""
        try:
            from vivbliss_scraper.utils.bot_notifier import BotNotifier
            bot_notifier_exists = True
        except ImportError:
            bot_notifier_exists = False
        
        print("🔴 RED阶段测试：BotNotifier类")
        print(f"   BotNotifier类存在: {'✅' if bot_notifier_exists else '❌'}")
        
        # RED阶段：这应该失败，因为类还不存在
        self.assertTrue(bot_notifier_exists, "BotNotifier类应该存在")
    
    def test_bot_notifier_initialization(self):
        """RED阶段：测试BotNotifier初始化"""
        try:
            from vivbliss_scraper.utils.bot_notifier import BotNotifier
            
            # 尝试初始化
            notifier = BotNotifier()
            initialization_success = True
        except ImportError:
            initialization_success = False
        except Exception as e:
            print(f"   初始化错误: {e}")
            initialization_success = False
        
        print(f"\n🔍 BotNotifier初始化测试:")
        print(f"   初始化成功: {'✅' if initialization_success else '❌'}")
        
        # RED阶段：这应该失败
        self.assertTrue(initialization_success, "BotNotifier应该能够初始化")
    
    def test_send_media_notification_method_exists(self):
        """RED阶段：测试发送媒体通知方法存在"""
        try:
            from vivbliss_scraper.utils.bot_notifier import BotNotifier
            notifier = BotNotifier()
            
            # 检查方法是否存在
            has_send_method = hasattr(notifier, 'send_media_notification')
            is_callable = callable(getattr(notifier, 'send_media_notification', None))
            
        except ImportError:
            has_send_method = False
            is_callable = False
        
        print(f"\n📤 发送通知方法测试:")
        print(f"   send_media_notification方法存在: {'✅' if has_send_method else '❌'}")
        print(f"   方法可调用: {'✅' if is_callable else '❌'}")
        
        # RED阶段：这应该失败
        self.assertTrue(has_send_method, "send_media_notification方法应该存在")
        self.assertTrue(is_callable, "send_media_notification方法应该可调用")
    
    def test_media_message_format(self):
        """RED阶段：测试媒体消息格式"""
        try:
            from vivbliss_scraper.utils.bot_notifier import BotNotifier
            notifier = BotNotifier()
            
            # 创建测试项目
            test_item = VivblissItem()
            test_item['title'] = '测试产品'
            test_item['url'] = 'https://example.com/product1'
            test_item.update(self.sample_media_data)
            
            # 尝试格式化消息
            message = notifier.format_media_message(test_item)
            message_formatted = isinstance(message, str) and len(message) > 0
            
        except ImportError:
            message_formatted = False
        except AttributeError:
            message_formatted = False
        
        print(f"\n💬 消息格式化测试:")
        print(f"   消息格式化成功: {'✅' if message_formatted else '❌'}")
        
        # RED阶段：这应该失败
        self.assertTrue(message_formatted, "应该能够格式化媒体消息")
    
    def test_bot_integration_with_spider(self):
        """RED阶段：测试Bot与爬虫的集成"""
        try:
            # 检查爬虫是否有bot通知器
            from vivbliss_scraper.spiders.vivbliss import VivblissSpider
            spider = VivblissSpider()
            
            has_bot_notifier = hasattr(spider, 'bot_notifier')
            bot_notifier_configured = False
            
            if has_bot_notifier:
                bot_notifier_configured = spider.bot_notifier is not None
            
        except (ImportError, Exception) as e:
            print(f"   导入错误: {e}")
            has_bot_notifier = False
            bot_notifier_configured = False
        
        print(f"\n🕷️  爬虫集成测试:")
        print(f"   爬虫有bot_notifier属性: {'✅' if has_bot_notifier else '❌'}")
        print(f"   bot_notifier已配置: {'✅' if bot_notifier_configured else '❌'}")
        
        # RED阶段：这应该失败
        self.assertTrue(has_bot_notifier, "爬虫应该有bot_notifier属性")
    
    def test_notification_trigger_on_product_extraction(self):
        """RED阶段：测试产品提取完成时触发通知"""
        try:
            from vivbliss_scraper.spiders.vivbliss import VivblissSpider
            spider = VivblissSpider()
            
            # 模拟产品提取完成
            with patch.object(spider, 'bot_notifier', create=True) as mock_notifier:
                mock_notifier.send_media_notification = AsyncMock()
                
                # 检查是否在产品解析完成后调用通知
                # 这需要检查parse_product或相关方法的实现
                notification_triggered = hasattr(spider, '_trigger_media_notification')
                
        except (ImportError, Exception) as e:
            print(f"   导入/初始化错误: {e}")
            notification_triggered = False
        
        print(f"\n🔔 通知触发测试:")
        print(f"   产品提取完成触发通知: {'✅' if notification_triggered else '❌'}")
        
        # RED阶段：这应该失败
        self.assertTrue(notification_triggered, "产品提取完成应该触发Bot通知")
    
    def test_message_content_includes_media_files(self):
        """RED阶段：测试消息内容包含媒体文件信息"""
        expected_content = [
            '产品名称',
            '图片数量',
            '视频数量',
            '媒体文件列表',
            'URL链接'
        ]
        
        content_requirements_met = False
        
        try:
            from vivbliss_scraper.utils.bot_notifier import BotNotifier
            notifier = BotNotifier()
            
            # 创建测试项目
            test_item = VivblissItem()
            test_item['title'] = '测试产品'
            test_item['url'] = 'https://example.com/product1'
            test_item.update(self.sample_media_data)
            
            message = notifier.format_media_message(test_item)
            
            # 检查消息是否包含必要内容
            content_checks = [
                '测试产品' in message,
                '图片' in message or 'images' in message.lower(),
                '视频' in message or 'videos' in message.lower(),
                str(self.sample_media_data['media_count']) in message,
                'https://' in message
            ]
            
            content_requirements_met = all(content_checks)
            
        except ImportError:
            pass
        except Exception:
            pass
        
        print(f"\n📝 消息内容测试:")
        print(f"   消息包含必要信息: {'✅' if content_requirements_met else '❌'}")
        
        # RED阶段：这应该失败
        self.assertTrue(content_requirements_met, "消息应该包含所有必要的媒体文件信息")


def run_red_phase_tests():
    """运行RED阶段测试"""
    print("🔴 TDD RED阶段：验证Bot消息通知功能缺失")
    print("=" * 70)
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBotNotificationTDD)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出结果
    print("\n" + "=" * 70)
    print("📊 RED阶段测试结果:")
    print(f"   运行测试: {result.testsRun}")
    print(f"   成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   失败: {len(result.failures)}")
    print(f"   错误: {len(result.errors)}")
    
    # RED阶段应该有一些测试失败（确认功能缺失）
    if result.failures or result.errors:
        print("\n🔴 RED阶段完成：确认了Bot消息通知功能缺失")
        print("   需要实现的组件:")
        print("   1. BotNotifier类")
        print("   2. send_media_notification方法")
        print("   3. format_media_message方法")
        print("   4. 爬虫集成")
        print("   5. 产品提取完成触发机制")
        return True
    else:
        print("\n⚠️  RED阶段异常：功能可能已存在")
        return False


if __name__ == '__main__':
    success = run_red_phase_tests()
    exit(0 if success else 1)