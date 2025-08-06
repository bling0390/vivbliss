import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import asyncio
from pathlib import Path
from vivbliss_scraper.telegram.pipeline import TelegramUploadPipeline
from vivbliss_scraper.items import VivblissMediaItem


class TestTelegramMediaIntegration:
    """Test suite for Telegram media upload integration"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.spider = Mock()
        self.spider.name = "test_spider"
        
        # Mock settings
        self.settings = {
            'TELEGRAM_API_ID': '12345',
            'TELEGRAM_API_HASH': 'test_hash',
            'TELEGRAM_SESSION_NAME': 'test_session',
            'TELEGRAM_CHAT_ID': '-1001234567890',
            'TELEGRAM_BOT_TOKEN': '123456:ABC-DEF',
            'TELEGRAM_ENABLE_UPLOAD': True,
        }
        
    @pytest.mark.asyncio
    async def test_process_media_item_with_downloaded_files(self):
        """Test processing item with downloaded media files"""
        # Create item with downloaded media
        item = VivblissMediaItem(
            title="Product Demo Video",
            source_url="https://example.com/product",
            images=[
                {
                    'url': 'https://example.com/product1.jpg',
                    'path': 'full/product1.jpg',
                    'checksum': 'abc123'
                },
                {
                    'url': 'https://example.com/product2.png',
                    'path': 'full/product2.png',
                    'checksum': 'def456'
                }
            ],
            videos=[
                {
                    'url': 'https://example.com/demo.mp4',
                    'path': 'full/demo.mp4',
                    'checksum': 'ghi789'
                }
            ]
        )
        
        with patch('vivbliss_scraper.telegram.pipeline.TelegramUploadPipeline.process_item') as mock_process:
            pipeline = TelegramUploadPipeline(
                api_id=self.settings['TELEGRAM_API_ID'],
                api_hash=self.settings['TELEGRAM_API_HASH'],
                session_name=self.settings['TELEGRAM_SESSION_NAME'],
                chat_id=self.settings['TELEGRAM_CHAT_ID'],
                bot_token=self.settings.get('TELEGRAM_BOT_TOKEN'),
                enable_upload=self.settings.get('TELEGRAM_ENABLE_UPLOAD', True)
            )
            
            # Mock the file uploader
            with patch.object(pipeline, 'file_uploader') as mock_uploader:
                mock_uploader.upload_files = AsyncMock(return_value={
                    'successful': 3,
                    'failed': 0,
                    'results': [
                        {'file': 'full/product1.jpg', 'status': 'success'},
                        {'file': 'full/product2.png', 'status': 'success'},
                        {'file': 'full/demo.mp4', 'status': 'success'}
                    ]
                })
                
                # Process item
                result = await pipeline.process_item_async(item, self.spider)
                
                # Verify files were uploaded
                mock_uploader.upload_files.assert_called_once()
                uploaded_files = mock_uploader.upload_files.call_args[0][0]
                assert len(uploaded_files) == 3
                
    def test_extract_media_files_from_item(self):
        """Test extraction of media file paths from item"""
        pipeline = TelegramUploadPipeline(
            api_id=self.settings['TELEGRAM_API_ID'],
            api_hash=self.settings['TELEGRAM_API_HASH'],
            session_name=self.settings['TELEGRAM_SESSION_NAME'],
            chat_id=self.settings['TELEGRAM_CHAT_ID'],
            bot_token=self.settings.get('TELEGRAM_BOT_TOKEN'),
            enable_upload=self.settings.get('TELEGRAM_ENABLE_UPLOAD', True)
        )
        
        item = VivblissMediaItem(
            title="Test Product",
            images=[
                {'path': 'images/full/img1.jpg', 'url': 'https://example.com/img1.jpg'},
                {'path': 'images/full/img2.png', 'url': 'https://example.com/img2.png'}
            ],
            videos=[
                {'path': 'videos/full/video1.mp4', 'url': 'https://example.com/video1.mp4'}
            ]
        )
        
        # Mock os.path.exists to return True for our test files
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            
            media_files = pipeline.extract_media_files(item)
            
            assert len(media_files) == 3
            # The paths get prefixed with store directories
            assert 'images/images/full/img1.jpg' in media_files
            assert 'images/images/full/img2.png' in media_files
            assert 'videos/videos/full/video1.mp4' in media_files
        
    def test_build_media_caption(self):
        """Test building captions for media uploads"""
        pipeline = TelegramUploadPipeline(
            api_id=self.settings['TELEGRAM_API_ID'],
            api_hash=self.settings['TELEGRAM_API_HASH'],
            session_name=self.settings['TELEGRAM_SESSION_NAME'],
            chat_id=self.settings['TELEGRAM_CHAT_ID'],
            bot_token=self.settings.get('TELEGRAM_BOT_TOKEN'),
            enable_upload=self.settings.get('TELEGRAM_ENABLE_UPLOAD', True)
        )
        
        item = VivblissMediaItem(
            title="Amazing Product Demo",
            source_url="https://example.com/product/123",
            category="Electronics",
            date="2024-01-15"
        )
        
        caption = pipeline.build_media_caption(item)
        
        assert "Amazing Product Demo" in caption
        assert "Electronics" in caption
        assert "2024-01-15" in caption
        assert "https://example.com/product/123" in caption
        
    @pytest.mark.asyncio
    async def test_upload_with_caption_and_grouping(self):
        """Test uploading media with captions as grouped album"""
        pipeline = TelegramUploadPipeline(
            api_id=self.settings['TELEGRAM_API_ID'],
            api_hash=self.settings['TELEGRAM_API_HASH'],
            session_name=self.settings['TELEGRAM_SESSION_NAME'],
            chat_id=self.settings['TELEGRAM_CHAT_ID'],
            bot_token=self.settings.get('TELEGRAM_BOT_TOKEN'),
            enable_upload=self.settings.get('TELEGRAM_ENABLE_UPLOAD', True)
        )
        
        item = VivblissMediaItem(
            title="Product Gallery",
            source_url="https://example.com/gallery",
            images=[
                {'path': 'full/img1.jpg'},
                {'path': 'full/img2.jpg'},
                {'path': 'full/img3.jpg'}
            ]
        )
        
        with patch.object(pipeline, 'file_uploader') as mock_uploader:
            mock_uploader.upload_album = AsyncMock(return_value={
                'successful': 3,
                'failed': 0,
                'album_id': 'album_123'
            })
            
            result = await pipeline.upload_media_album(item, self.spider)
            
            # Verify album upload was called
            mock_uploader.upload_album.assert_called_once()
            files, caption = mock_uploader.upload_album.call_args[0]
            assert len(files) == 3
            assert "Product Gallery" in caption
            
    def test_handle_mixed_media_types(self):
        """Test handling items with both images and videos"""
        pipeline = TelegramUploadPipeline(
            api_id=self.settings['TELEGRAM_API_ID'],
            api_hash=self.settings['TELEGRAM_API_HASH'],
            session_name=self.settings['TELEGRAM_SESSION_NAME'],
            chat_id=self.settings['TELEGRAM_CHAT_ID'],
            bot_token=self.settings.get('TELEGRAM_BOT_TOKEN'),
            enable_upload=self.settings.get('TELEGRAM_ENABLE_UPLOAD', True)
        )
        
        item = VivblissMediaItem(
            title="Product Package",
            images=[
                {'path': 'full/cover.jpg'},
                {'path': 'full/detail.png'}
            ],
            videos=[
                {'path': 'full/demo.mp4'},
                {'path': 'full/tutorial.webm'}
            ]
        )
        
        media_files = pipeline.extract_media_files(item)
        
        # Should extract all media files
        assert len(media_files) == 4
        
        # Group by type
        images, videos = pipeline.group_media_by_type(media_files)
        assert len(images) == 2
        assert len(videos) == 2
        
    @pytest.mark.asyncio
    async def test_retry_failed_uploads(self):
        """Test retry mechanism for failed uploads"""
        pipeline = TelegramUploadPipeline(
            api_id=self.settings['TELEGRAM_API_ID'],
            api_hash=self.settings['TELEGRAM_API_HASH'],
            session_name=self.settings['TELEGRAM_SESSION_NAME'],
            chat_id=self.settings['TELEGRAM_CHAT_ID'],
            bot_token=self.settings.get('TELEGRAM_BOT_TOKEN'),
            enable_upload=self.settings.get('TELEGRAM_ENABLE_UPLOAD', True)
        )
        pipeline.max_retries = 3
        
        item = VivblissMediaItem(
            title="Test Product",
            images=[{'path': 'full/test.jpg'}]
        )
        
        with patch.object(pipeline, 'file_uploader') as mock_uploader:
            # Simulate failures then success
            mock_uploader.upload_files = AsyncMock(
                side_effect=[
                    Exception("Network error"),
                    Exception("Timeout"),
                    {'successful': 1, 'failed': 0}
                ]
            )
            
            result = await pipeline.process_item_with_retry(item, self.spider)
            
            # Should have retried 3 times
            assert mock_uploader.upload_files.call_count == 3
            assert result['successful'] == 1
            
    def test_skip_upload_when_disabled(self):
        """Test that uploads are skipped when TELEGRAM_ENABLE_UPLOAD is False"""
        settings = self.settings.copy()
        settings['TELEGRAM_ENABLE_UPLOAD'] = False
        
        pipeline = TelegramUploadPipeline(
            api_id=settings['TELEGRAM_API_ID'],
            api_hash=settings['TELEGRAM_API_HASH'],
            session_name=settings['TELEGRAM_SESSION_NAME'],
            chat_id=settings['TELEGRAM_CHAT_ID'],
            bot_token=settings.get('TELEGRAM_BOT_TOKEN'),
            enable_upload=settings['TELEGRAM_ENABLE_UPLOAD']
        )
        
        item = VivblissMediaItem(
            title="Test Product",
            images=[{'path': 'full/test.jpg'}]
        )
        
        # Should not attempt upload
        result = pipeline.process_item(item, self.spider)
        assert result == item
        assert not hasattr(item, 'telegram_upload_status')
        
    @pytest.mark.asyncio
    async def test_handle_large_media_files(self):
        """Test handling of large media files"""
        pipeline = TelegramUploadPipeline(
            api_id=self.settings['TELEGRAM_API_ID'],
            api_hash=self.settings['TELEGRAM_API_HASH'],
            session_name=self.settings['TELEGRAM_SESSION_NAME'],
            chat_id=self.settings['TELEGRAM_CHAT_ID'],
            bot_token=self.settings.get('TELEGRAM_BOT_TOKEN'),
            enable_upload=self.settings.get('TELEGRAM_ENABLE_UPLOAD', True)
        )
        
        # Create item with large file
        item = VivblissMediaItem(
            title="Large Video",
            videos=[{
                'path': 'full/large_video.mp4',
                'size': 60 * 1024 * 1024  # 60MB, over Telegram limit
            }]
        )
        
        with patch.object(pipeline, 'file_uploader') as mock_uploader:
            mock_uploader.validate_file_size = Mock(return_value=False)
            
            result = await pipeline.process_item_async(item, self.spider)
            
            # Should skip large files
            assert 'skipped_files' in result
            assert len(result['skipped_files']) == 1
            assert 'size_exceeded' in result['skipped_files'][0]['reason']
            
    def test_preserve_original_item_data(self):
        """Test that original item data is preserved after upload"""
        pipeline = TelegramUploadPipeline(
            api_id=self.settings['TELEGRAM_API_ID'],
            api_hash=self.settings['TELEGRAM_API_HASH'],
            session_name=self.settings['TELEGRAM_SESSION_NAME'],
            chat_id=self.settings['TELEGRAM_CHAT_ID'],
            bot_token=self.settings.get('TELEGRAM_BOT_TOKEN'),
            enable_upload=self.settings.get('TELEGRAM_ENABLE_UPLOAD', True)
        )
        
        original_item = VivblissMediaItem(
            title="Test Product",
            source_url="https://example.com/test",
            category="Test Category",
            images=[{'path': 'full/test.jpg'}]
        )
        
        # Make a copy to compare
        item_copy = original_item.copy()
        
        with patch.object(pipeline, 'file_uploader'):
            result = pipeline.process_item(original_item, self.spider)
            
            # Original fields should be preserved
            assert result['title'] == item_copy['title']
            assert result['source_url'] == item_copy['source_url']
            assert result['category'] == item_copy['category']
            
            # Should add upload status
            assert 'telegram_upload_status' in result