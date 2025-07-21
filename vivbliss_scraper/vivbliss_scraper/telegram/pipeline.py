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


class TelegramUploadPipeline:
    """Scrapy pipeline for uploading extracted media files to Telegram."""
    
    def __init__(self, 
                 api_id: str, 
                 api_hash: str, 
                 session_name: str,
                 chat_id: int,
                 enable_upload: bool = True,
                 bot_token: Optional[str] = None):
        """
        Initialize Telegram upload pipeline.
        
        Args:
            api_id: Telegram API ID
            api_hash: Telegram API hash
            session_name: Pyrogram session name
            chat_id: Telegram chat ID to upload files to
            enable_upload: Whether to enable actual uploads (useful for testing)
            bot_token: Optional bot token for bot authentication
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.chat_id = chat_id
        self.enable_upload = enable_upload
        self.bot_token = bot_token
        
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
            bot_token=crawler.settings.get('TELEGRAM_BOT_TOKEN')
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
                loop.run_until_complete(self._upload_media_files(media_files, spider))
            finally:
                loop.close()
        
        return item
    
    def _extract_media_files(self, adapter: ItemAdapter) -> list:
        """
        Extract media file paths from scraped item.
        Override this method based on your item structure.
        """
        media_files = []
        
        # Example: Look for common field names that might contain file paths
        for field_name in ['images', 'videos', 'media_files', 'attachments']:
            if field_name in adapter:
                files = adapter[field_name]
                if isinstance(files, list):
                    media_files.extend(files)
                elif isinstance(files, str):
                    media_files.append(files)
        
        return [f for f in media_files if f and os.path.exists(f)]
    
    async def _upload_media_files(self, media_files: list, spider):
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
                
                # Upload file
                caption = f"📁 File from VivBliss scraper\\n📄 {os.path.basename(file_path)}"
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