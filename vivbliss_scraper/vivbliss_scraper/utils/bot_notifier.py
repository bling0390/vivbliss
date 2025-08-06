#!/usr/bin/env python3
"""
Bot消息通知器 - 用于发送产品媒体提取通知
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

try:
    from pyrogram import Client
    from ..telegram.config import TelegramConfig
    PYROGRAM_AVAILABLE = True
except ImportError:
    PYROGRAM_AVAILABLE = False
    print("⚠️  Pyrogram 未安装，Bot通知功能将被禁用")


class BotNotifier:
    """Bot消息通知器类"""
    
    def __init__(self, chat_id: Optional[str] = None, enable_notifications: bool = True):
        """
        初始化Bot通知器
        
        Args:
            chat_id: 目标聊天ID
            enable_notifications: 是否启用通知
        """
        self.logger = logging.getLogger(__name__)
        self.chat_id = chat_id
        self.enable_notifications = enable_notifications and PYROGRAM_AVAILABLE
        self.client: Optional[Client] = None
        self._client_initialized = False
        
        if not PYROGRAM_AVAILABLE:
            self.logger.warning("📵 Pyrogram不可用，Bot通知已禁用")
            self.enable_notifications = False
    
    async def initialize_client(self) -> bool:
        """
        初始化Telegram客户端
        
        Returns:
            初始化是否成功
        """
        if not self.enable_notifications:
            return False
            
        if self._client_initialized and self.client:
            return True
            
        try:
            # 从环境变量创建配置
            config = TelegramConfig.from_environment()
            self.client = await config.create_client()
            
            # 验证连接
            await self.client.start()
            connection_valid = await config.validate_client_connection(self.client)
            
            if connection_valid:
                self._client_initialized = True
                self.logger.info("🤖 Telegram Bot客户端初始化成功")
                return True
            else:
                self.logger.error("❌ Telegram Bot连接验证失败")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Telegram Bot初始化失败: {e}")
            self.enable_notifications = False
            return False
    
    def format_media_message(self, item: Dict[str, Any]) -> str:
        """
        格式化媒体通知消息
        
        Args:
            item: 包含媒体信息的项目数据
            
        Returns:
            格式化的消息字符串
        """
        # 提取基本信息
        title = item.get('title', '未知产品')
        url = item.get('url', '无URL')
        category = item.get('category', '未分类')
        
        # 提取媒体信息
        images = item.get('images', [])
        videos = item.get('videos', [])
        media_count = item.get('media_count', 0)
        
        # 构建消息
        message_parts = [
            "🛍️ **产品媒体提取完成**",
            "",
            f"📝 **产品名称**: {title}",
            f"🔗 **产品链接**: {url}",
            f"📂 **分类**: {category}",
            f"📊 **媒体统计**: 总计 {media_count} 个文件",
            ""
        ]
        
        # 添加图片信息
        if images:
            message_parts.extend([
                f"🖼️ **图片文件** ({len(images)} 个):",
                ""
            ])
            for i, img_url in enumerate(images[:5], 1):  # 限制显示前5个
                message_parts.append(f"   {i}. {img_url}")
            
            if len(images) > 5:
                message_parts.append(f"   ... 还有 {len(images) - 5} 个图片")
            message_parts.append("")
        
        # 添加视频信息
        if videos:
            message_parts.extend([
                f"🎥 **视频文件** ({len(videos)} 个):",
                ""
            ])
            for i, video_url in enumerate(videos[:3], 1):  # 限制显示前3个
                message_parts.append(f"   {i}. {video_url}")
            
            if len(videos) > 3:
                message_parts.append(f"   ... 还有 {len(videos) - 3} 个视频")
            message_parts.append("")
        
        # 添加时间戳
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message_parts.extend([
            f"⏰ **提取时间**: {timestamp}",
            "",
            "---",
            "🤖 VivBliss 爬虫自动通知"
        ])
        
        return "\n".join(message_parts)
    
    async def send_media_notification(self, item: Dict[str, Any], chat_id: Optional[str] = None) -> bool:
        """
        发送媒体提取通知
        
        Args:
            item: 包含媒体信息的项目数据
            chat_id: 目标聊天ID（可选，使用实例默认值）
            
        Returns:
            发送是否成功
        """
        if not self.enable_notifications:
            self.logger.debug("📵 Bot通知已禁用，跳过发送")
            return False
        
        # 初始化客户端（如果尚未初始化）
        if not self._client_initialized:
            init_success = await self.initialize_client()
            if not init_success:
                return False
        
        try:
            # 确定目标聊天ID
            target_chat_id = chat_id or self.chat_id
            if not target_chat_id:
                self.logger.error("❌ 未指定目标聊天ID")
                return False
            
            # 格式化消息
            message = self.format_media_message(item)
            
            # 发送消息
            await self.client.send_message(
                chat_id=target_chat_id,
                text=message,
                disable_web_page_preview=True
            )
            
            self.logger.info(f"📤 Bot通知发送成功: {item.get('title', '未知产品')}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Bot消息发送失败: {e}")
            return False
    
    def sync_send_media_notification(self, item: Dict[str, Any], chat_id: Optional[str] = None) -> bool:
        """
        同步方式发送媒体通知（适用于Scrapy环境）
        
        Args:
            item: 包含媒体信息的项目数据
            chat_id: 目标聊天ID（可选）
            
        Returns:
            发送是否成功
        """
        if not self.enable_notifications:
            return False
            
        try:
            # 获取或创建事件循环
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # 运行异步发送
            return loop.run_until_complete(
                self.send_media_notification(item, chat_id)
            )
            
        except Exception as e:
            self.logger.error(f"❌ 同步Bot消息发送失败: {e}")
            return False
    
    async def close(self):
        """关闭Bot客户端连接"""
        if self.client and self._client_initialized:
            try:
                await self.client.stop()
                self.logger.info("🔌 Telegram Bot客户端已关闭")
            except Exception as e:
                self.logger.error(f"❌ 关闭Bot客户端时出错: {e}")
            finally:
                self._client_initialized = False
    
    @classmethod
    def create_from_settings(cls, settings: Dict[str, Any]) -> 'BotNotifier':
        """
        从设置创建BotNotifier实例
        
        Args:
            settings: Scrapy设置字典
            
        Returns:
            配置好的BotNotifier实例
        """
        # 支持多种配置键名
        chat_id = (settings.get('TELEGRAM_NOTIFICATION_CHAT_ID') or 
                  settings.get('TELEGRAM_CHAT_ID') or
                  settings.get('BOT_CHAT_ID'))
        
        enable_notifications = settings.get('ENABLE_BOT_NOTIFICATIONS', True)
        
        # 如果禁用或没有chat_id，则创建禁用的通知器
        if not enable_notifications or not chat_id:
            enable_notifications = False
        
        return cls(
            chat_id=chat_id,
            enable_notifications=enable_notifications
        )
    
    def is_enabled(self) -> bool:
        """检查通知是否启用"""
        return self.enable_notifications
    
    def get_status(self) -> Dict[str, Any]:
        """获取通知器状态"""
        return {
            'enabled': self.enable_notifications,
            'pyrogram_available': PYROGRAM_AVAILABLE,
            'client_initialized': self._client_initialized,
            'chat_id_configured': bool(self.chat_id)
        }