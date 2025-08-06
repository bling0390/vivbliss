"""
Scrapy pipeline for integrating Telegram file uploads with the scraping process.
"""
import asyncio
import logging
import os
from typing import Optional, Dict, Any
from scrapy import signals
from itemadapter import ItemAdapter
from .config import TelegramConfig
from .file_uploader import FileUploader
from .file_validator import FileValidator
from vivbliss_scraper.items import VivblissMediaItem


class TelegramUploadPipeline:
    """Scrapy pipeline for uploading extracted media files to Telegram."""
    
    def __init__(self, 
                 api_id: str, 
                 api_hash: str, 
                 session_name: str,
                 chat_id: int,
                 enable_upload: bool = True,
                 bot_token: Optional[str] = None,
                 images_store: str = 'images',
                 files_store: str = 'videos'):
        """
        Initialize Telegram upload pipeline.
        
        Args:
            api_id: Telegram API ID
            api_hash: Telegram API hash
            session_name: Pyrogram session name
            chat_id: Telegram chat ID to upload files to
            enable_upload: Whether to enable actual uploads (useful for testing)
            bot_token: Optional bot token for bot authentication
            images_store: Path to images store directory
            files_store: Path to files/videos store directory
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.chat_id = chat_id
        self.enable_upload = enable_upload
        self.bot_token = bot_token
        self.images_store = images_store
        self.files_store = files_store
        
        self.config: Optional[TelegramConfig] = None
        self.client = None
        self.uploader: Optional[FileUploader] = None
        self.validator = FileValidator()
        self.stats = {
            'files_processed': 0,
            'files_uploaded': 0,
            'files_failed': 0,
            'files_skipped': 0
        }
    
    @classmethod
    def from_crawler(cls, crawler):
        """Create pipeline instance from Scrapy crawler settings."""
        return cls(
            api_id=crawler.settings.get('TELEGRAM_API_ID'),
            api_hash=crawler.settings.get('TELEGRAM_API_HASH'),
            session_name=crawler.settings.get('TELEGRAM_SESSION_NAME', 'vivbliss_bot'),
            chat_id=crawler.settings.get('TELEGRAM_CHAT_ID'),
            enable_upload=crawler.settings.get('TELEGRAM_ENABLE_UPLOAD', True),
            bot_token=crawler.settings.get('TELEGRAM_BOT_TOKEN'),
            images_store=crawler.settings.get('IMAGES_STORE', 'images'),
            files_store=crawler.settings.get('FILES_STORE', 'videos')
        )
    
    async def open_spider(self, spider):
        """Initialize Telegram client when spider opens."""
        if not self.enable_upload:
            spider.logger.info("Telegram upload disabled in settings")
            return
        
        try:
            # Initialize Telegram configuration
            self.config = TelegramConfig(
                api_id=self.api_id,
                api_hash=self.api_hash,
                session_name=self.session_name,
                bot_token=self.bot_token
            )
            
            # Create and start client
            self.client = await self.config.create_client()
            await self.client.start()
            
            # Validate connection
            if await self.config.validate_client_connection(self.client):
                self.uploader = FileUploader(self.client)
                spider.logger.info("Telegram client initialized successfully")
            else:
                spider.logger.error("Failed to validate Telegram client connection")
                self.enable_upload = False
                
        except Exception as e:
            spider.logger.error(f"Failed to initialize Telegram client: {e}")
            self.enable_upload = False
    
    async def close_spider(self, spider):
        """Close Telegram client and log statistics when spider closes."""
        if self.client:
            await self.client.stop()
        
        spider.logger.info(f"Telegram upload statistics: {self.stats}")
    
    def process_item(self, item, spider):
        """Process scraped item and upload any media files found."""
        if not self.enable_upload:
            return item
        
        adapter = ItemAdapter(item)
        
        # Extract media files from item (you may need to customize based on your item structure)
        media_files = self._extract_media_files(adapter)
        
        if media_files:
            # Run upload in event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self._upload_media_files(media_files, spider, item))
            finally:
                loop.close()
        
        return item
    
    def _extract_media_files(self, adapter: ItemAdapter) -> list:
        """
        Extract media file paths from scraped item.
        Handles both regular items and VivblissMediaItem.
        """
        media_files = []
        
        # Handle VivblissMediaItem specifically
        if adapter.item.__class__.__name__ == 'VivblissMediaItem':
            # Extract downloaded images
            if 'images' in adapter and adapter['images']:
                for img_info in adapter['images']:
                    if isinstance(img_info, dict) and 'path' in img_info:
                        # Convert relative path to absolute if needed
                        path = img_info['path']
                        if not os.path.isabs(path):
                            # Assume path is relative to IMAGES_STORE
                            path = os.path.join(self.images_store, path)
                        media_files.append(path)
            
            # Extract downloaded videos
            if 'videos' in adapter and adapter['videos']:
                for video_info in adapter['videos']:
                    if isinstance(video_info, dict) and 'path' in video_info:
                        # Convert relative path to absolute if needed
                        path = video_info['path']
                        if not os.path.isabs(path):
                            # Assume path is relative to FILES_STORE
                            path = os.path.join(self.files_store, path)
                        media_files.append(path)
        else:
            # Handle regular items - look for common field names
            for field_name in ['images', 'videos', 'media_files', 'attachments']:
                if field_name in adapter:
                    files = adapter[field_name]
                    if isinstance(files, list):
                        for f in files:
                            if isinstance(f, str):
                                media_files.append(f)
                            elif isinstance(f, dict) and 'path' in f:
                                media_files.append(f['path'])
                    elif isinstance(files, str):
                        media_files.append(files)
        
        return [f for f in media_files if f and os.path.exists(f)]
    
    async def _upload_media_files(self, media_files: list, spider, item=None):
        """Upload media files to Telegram."""
        for file_path in media_files:
            self.stats['files_processed'] += 1
            
            try:
                # Validate file
                validation_result = self.validator.validate_file(file_path)
                
                if not validation_result['is_valid']:
                    spider.logger.warning(
                        f"Skipping invalid file {file_path}: {validation_result['errors']}"
                    )
                    self.stats['files_skipped'] += 1
                    continue
                
                # Generate caption with item information if available
                caption = self._generate_caption(file_path, item)
                
                # Upload file
                result = await self.uploader.upload_file(
                    chat_id=self.chat_id,
                    file_path=file_path,
                    caption=caption
                )
                
                if result['success']:
                    spider.logger.info(
                        f"Successfully uploaded {file_path} (Message ID: {result['message_id']})"
                    )
                    self.stats['files_uploaded'] += 1
                else:
                    spider.logger.error(
                        f"Failed to upload {file_path}: {result['error']}"
                    )
                    self.stats['files_failed'] += 1
                    
            except Exception as e:
                spider.logger.error(f"Error processing file {file_path}: {e}")
                self.stats['files_failed'] += 1
    
    def _generate_caption(self, file_path: str, item=None) -> str:
        """Generate caption for uploaded media file."""
        filename = os.path.basename(file_path)
        
        # If we have a VivblissMediaItem with product info
        if item and hasattr(item, '__class__') and item.__class__.__name__ == 'VivblissMediaItem':
            adapter = ItemAdapter(item)
            caption_parts = ["🛍️ 产品介绍"]
            
            if 'title' in adapter and adapter['title']:
                caption_parts.append(f"📌 {adapter['title']}")
            
            if 'category' in adapter and adapter['category']:
                caption_parts.append(f"📂 分类: {adapter['category']}")
            
            if 'date' in adapter and adapter['date']:
                caption_parts.append(f"📅 日期: {adapter['date']}")
            
            caption_parts.append(f"📄 文件: {filename}")
            
            if 'source_url' in adapter and adapter['source_url']:
                caption_parts.append(f"🔗 来源: {adapter['source_url']}")
            
            return "\n".join(caption_parts)
        else:
            # Default caption
            return f"📁 File from VivBliss scraper\n📄 {filename}"
    
    def extract_media_files(self, item) -> list:
        """Public method to extract media files from item."""
        adapter = ItemAdapter(item)
        return self._extract_media_files(adapter)
    
    def build_media_caption(self, item) -> str:
        """Build caption for media uploads."""
        return self._generate_caption("", item)
    
    def group_media_by_type(self, media_files: list) -> tuple:
        """Group media files by type (images and videos)."""
        images = []
        videos = []
        
        for file_path in media_files:
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']:
                images.append(file_path)
            elif ext in ['.mp4', '.avi', '.mkv', '.mov', '.webm', '.flv']:
                videos.append(file_path)
        
        return images, videos
    
    async def process_item_async(self, item, spider):
        """Async version of process_item for testing."""
        if not self.enable_upload:
            return item
        
        adapter = ItemAdapter(item)
        media_files = self._extract_media_files(adapter)
        
        if media_files:
            await self._upload_media_files(media_files, spider, item)
        
        return item
    
    async def upload_media_album(self, item, spider):
        """Upload multiple media files as an album."""
        adapter = ItemAdapter(item)
        media_files = self._extract_media_files(adapter)
        
        if not media_files:
            return {'successful': 0, 'failed': 0}
        
        # For now, upload individually
        # In a real implementation, you'd use Telegram's media group feature
        await self._upload_media_files(media_files, spider, item)
        
        return {
            'successful': self.stats['files_uploaded'],
            'failed': self.stats['files_failed'],
            'album_id': f'album_{id(item)}'
        }
    
    async def process_item_with_retry(self, item, spider, max_retries=3):
        """Process item with retry logic."""
        for attempt in range(max_retries):
            try:
                return await self.process_item_async(item, spider)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return item