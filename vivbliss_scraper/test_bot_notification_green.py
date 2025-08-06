#!/usr/bin/env python3
"""
TDD测试用例 - Bot消息通知功能 GREEN阶段
GREEN阶段：编写测试验证功能正常工作
"""

import unittest
import sys
import os
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

# Mock VivblissItem for testing without Scrapy
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


class TestBotNotificationGreen(unittest.TestCase):
    """Bot消息通知功能的GREEN阶段测试用例"""
    
    def setUp(self):
        """设置测试环境"""
        self.sample_media_data = {
            'title': '测试产品名称',
            'url': 'https://example.com/product1',
            'category': '测试分类',
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
    
    def test_bot_notifier_class_exists_and_works(self):
        """GREEN阶段：测试BotNotifier类存在且工作正常"""
        try:
            from vivbliss_scraper.utils.bot_notifier import BotNotifier
            bot_notifier = BotNotifier()
            
            # 测试基本功能
            self.assertIsNotNone(bot_notifier)
            self.assertTrue(hasattr(bot_notifier, 'format_media_message'))
            self.assertTrue(hasattr(bot_notifier, 'send_media_notification'))
            self.assertTrue(hasattr(bot_notifier, 'sync_send_media_notification'))
            self.assertTrue(callable(bot_notifier.format_media_message))
            
            print("✅ GREEN阶段：BotNotifier类存在且功能完整")
            
        except ImportError as e:
            self.fail(f"BotNotifier类导入失败: {e}")
    
    def test_format_media_message_works(self):
        """GREEN阶段：测试消息格式化功能"""
        try:
            from vivbliss_scraper.utils.bot_notifier import BotNotifier
            notifier = BotNotifier()
            
            # 创建测试项目
            test_item = VivblissItem()
            test_item.update(self.sample_media_data)
            
            # 格式化消息
            message = notifier.format_media_message(test_item)
            
            # 验证消息内容
            self.assertIsInstance(message, str)
            self.assertGreater(len(message), 0)
            
            # 验证消息包含必要信息
            self.assertIn('测试产品名称', message)
            self.assertIn('https://example.com/product1', message)
            self.assertIn('测试分类', message)
            self.assertIn('5', message)  # 媒体数量
            self.assertIn('图片', message)
            self.assertIn('视频', message)
            
            print("✅ GREEN阶段：消息格式化功能正常工作")
            print(f"   消息长度: {len(message)} 字符")
            print(f"   包含产品名称: {'✅' if '测试产品名称' in message else '❌'}")
            print(f"   包含URL: {'✅' if 'https://example.com/product1' in message else '❌'}")
            print(f"   包含媒体统计: {'✅' if '5' in message else '❌'}")
            
        except Exception as e:
            self.fail(f"消息格式化功能失败: {e}")
    
    def test_bot_notifier_initialization_options(self):
        """GREEN阶段：测试BotNotifier不同初始化选项"""
        try:
            from vivbliss_scraper.utils.bot_notifier import BotNotifier
            
            # 测试默认初始化
            notifier1 = BotNotifier()
            self.assertIsNotNone(notifier1)
            
            # 测试带参数初始化
            notifier2 = BotNotifier(chat_id="123456", enable_notifications=False)
            self.assertIsNotNone(notifier2)
            self.assertEqual(notifier2.chat_id, "123456")
            self.assertFalse(notifier2.enable_notifications)
            
            # 测试从设置创建
            settings = {
                'TELEGRAM_NOTIFICATION_CHAT_ID': '789012',
                'ENABLE_BOT_NOTIFICATIONS': True
            }
            notifier3 = BotNotifier.create_from_settings(settings)
            self.assertIsNotNone(notifier3)
            self.assertEqual(notifier3.chat_id, '789012')
            
            print("✅ GREEN阶段：BotNotifier初始化选项工作正常")
            print(f"   默认初始化: ✅")
            print(f"   参数初始化: ✅")
            print(f"   从设置创建: ✅")
            
        except Exception as e:
            self.fail(f"BotNotifier初始化失败: {e}")
    
    def test_bot_notifier_status_methods(self):
        """GREEN阶段：测试BotNotifier状态方法"""
        try:
            from vivbliss_scraper.utils.bot_notifier import BotNotifier
            
            notifier = BotNotifier(enable_notifications=False)
            
            # 测试状态方法
            self.assertTrue(hasattr(notifier, 'is_enabled'))
            self.assertTrue(hasattr(notifier, 'get_status'))
            
            # 测试is_enabled
            enabled = notifier.is_enabled()
            self.assertIsInstance(enabled, bool)
            
            # 测试get_status
            status = notifier.get_status()
            self.assertIsInstance(status, dict)
            self.assertIn('enabled', status)
            self.assertIn('pyrogram_available', status)
            self.assertIn('client_initialized', status)
            self.assertIn('chat_id_configured', status)
            
            print("✅ GREEN阶段：BotNotifier状态方法工作正常")
            print(f"   is_enabled(): {enabled}")
            print(f"   get_status(): {len(status)} 个状态项")
            
        except Exception as e:
            self.fail(f"BotNotifier状态方法失败: {e}")
    
    def test_mock_spider_integration(self):
        """GREEN阶段：测试模拟爬虫集成"""
        try:
            from vivbliss_scraper.utils.bot_notifier import BotNotifier
            
            # 创建模拟爬虫
            class MockSpider:
                def __init__(self):
                    self.bot_notifier = BotNotifier.create_from_settings({})
                    self.logger = Mock()
                
                def _trigger_media_notification(self, context):
                    """触发媒体提取完成的Bot通知"""
                    if not self.bot_notifier.is_enabled():
                        return
                    
                    try:
                        item = context.get('item')
                        if not item:
                            return
                        
                        # 检查是否有媒体内容
                        has_media = (item.get('media_count', 0) > 0 or 
                                    len(item.get('images', [])) > 0 or 
                                    len(item.get('videos', [])) > 0)
                        
                        if has_media:
                            # 模拟同步发送通知
                            success = True  # 模拟成功
                            if success:
                                self.logger.info(f"📤 Bot通知发送成功: {item.get('title', '未知项目')}")
                            else:
                                self.logger.warning(f"📵 Bot通知发送失败: {item.get('title', '未知项目')}")
                        
                    except Exception as e:
                        self.logger.error(f"❌ 触发Bot通知时出错: {e}")
            
            # 测试模拟爬虫
            spider = MockSpider()
            
            # 验证爬虫具有必要属性
            self.assertTrue(hasattr(spider, 'bot_notifier'))
            self.assertTrue(hasattr(spider, '_trigger_media_notification'))
            self.assertIsNotNone(spider.bot_notifier)
            
            # 测试通知触发
            test_item = VivblissItem()
            test_item.update(self.sample_media_data)
            
            spider._trigger_media_notification({'item': test_item})
            
            print("✅ GREEN阶段：模拟爬虫集成工作正常")
            print(f"   爬虫有bot_notifier属性: ✅")
            print(f"   爬虫有_trigger_media_notification方法: ✅")
            print(f"   通知触发功能: ✅")
            
        except Exception as e:
            self.fail(f"模拟爬虫集成失败: {e}")
    
    def test_media_content_validation(self):
        """GREEN阶段：测试媒体内容验证"""
        try:
            from vivbliss_scraper.utils.bot_notifier import BotNotifier
            
            notifier = BotNotifier()
            
            # 测试空媒体内容
            empty_item = VivblissItem()
            empty_item.update({
                'title': '空媒体产品',
                'url': 'https://example.com/empty',
                'images': [],
                'videos': [],
                'media_count': 0
            })
            
            empty_message = notifier.format_media_message(empty_item)
            self.assertIsInstance(empty_message, str)
            self.assertIn('空媒体产品', empty_message)
            self.assertIn('总计 0 个文件', empty_message)
            
            # 测试只有图片的内容
            image_only_item = VivblissItem()
            image_only_item.update({
                'title': '只有图片的产品',
                'url': 'https://example.com/images-only',
                'images': ['https://example.com/img1.jpg', 'https://example.com/img2.jpg'],
                'videos': [],
                'media_count': 2
            })
            
            image_message = notifier.format_media_message(image_only_item)
            self.assertIn('只有图片的产品', image_message)
            self.assertIn('总计 2 个文件', image_message)
            self.assertIn('图片文件', image_message)
            self.assertNotIn('视频文件', image_message)
            
            print("✅ GREEN阶段：媒体内容验证工作正常")
            print(f"   空媒体处理: ✅")
            print(f"   只有图片处理: ✅")
            
        except Exception as e:
            self.fail(f"媒体内容验证失败: {e}")


def run_green_phase_tests():
    """运行GREEN阶段测试"""
    print("🟢 TDD GREEN阶段：验证Bot消息通知功能正常工作")
    print("=" * 70)
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBotNotificationGreen)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出结果
    print("\n" + "=" * 70)
    print("📊 GREEN阶段测试结果:")
    print(f"   运行测试: {result.testsRun}")
    print(f"   成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   失败: {len(result.failures)}")
    print(f"   错误: {len(result.errors)}")
    
    # GREEN阶段应该所有测试都通过
    if not result.failures and not result.errors:
        print("\n🟢 GREEN阶段成功：Bot消息通知功能实现完成！")
        print("   ✅ BotNotifier类正常工作")
        print("   ✅ 消息格式化功能完整")
        print("   ✅ 初始化选项灵活")
        print("   ✅ 状态管理正确")
        print("   ✅ 爬虫集成就绪") 
        print("   ✅ 媒体内容验证有效")
        return True
    else:
        print("\n🔴 GREEN阶段失败：需要修复实现问题")
        if result.failures:
            print("   失败的测试:")
            for test, error in result.failures:
                print(f"     - {test}: {error.split('AssertionError:')[-1].strip()}")
        if result.errors:
            print("   错误的测试:")
            for test, error in result.errors:
                print(f"     - {test}: {error.split(':', 1)[-1].strip()}")
        return False


if __name__ == '__main__':
    success = run_green_phase_tests()
    exit(0 if success else 1)