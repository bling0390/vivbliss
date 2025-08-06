import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from scrapy.http import HtmlResponse, Request
from scrapy import Spider

from vivbliss_scraper.extractors.media_extractor import MediaExtractor
from vivbliss_scraper.pipelines.media_pipeline import MediaDownloadPipeline
from vivbliss_scraper.telegram.pipeline import TelegramUploadPipeline
from vivbliss_scraper.items import VivblissMediaItem


class TestMediaWorkflowIntegration:
    """Integration tests for complete media download and upload workflow"""
    
    def setup_method(self):
        """Set up test environment"""
        self.spider = Mock(spec=Spider)
        self.spider.name = "test_spider"
        self.spider.logger = Mock()
        
        # Create temp directories for testing
        self.temp_dir = tempfile.mkdtemp()
        self.images_store = os.path.join(self.temp_dir, 'images')
        self.videos_store = os.path.join(self.temp_dir, 'videos')
        
        Path(self.images_store).mkdir(parents=True, exist_ok=True)
        Path(self.videos_store).mkdir(parents=True, exist_ok=True)
        
        # Media downloader settings
        self.media_settings = {
            'IMAGES_STORE': self.images_store,
            'FILES_STORE': self.videos_store,
            'IMAGES_MIN_WIDTH': 100,
            'IMAGES_MIN_HEIGHT': 100,
        }
        
        # Telegram settings
        self.telegram_settings = {
            'TELEGRAM_API_ID': '12345',
            'TELEGRAM_API_HASH': 'test_hash',
            'TELEGRAM_SESSION_NAME': 'test_session',
            'TELEGRAM_CHAT_ID': '-1001234567890',
            'TELEGRAM_BOT_TOKEN': '123456:ABC-DEF',
            'TELEGRAM_ENABLE_UPLOAD': True,
        }
        
        # Initialize components
        self.extractor = MediaExtractor()
        self.media_pipeline = MediaDownloadPipeline(self.media_settings)
        self.telegram_pipeline = TelegramUploadPipeline(
            api_id=self.telegram_settings['TELEGRAM_API_ID'],
            api_hash=self.telegram_settings['TELEGRAM_API_HASH'],
            session_name=self.telegram_settings['TELEGRAM_SESSION_NAME'],
            chat_id=int(self.telegram_settings['TELEGRAM_CHAT_ID']),
            bot_token=self.telegram_settings['TELEGRAM_BOT_TOKEN'],
            enable_upload=self.telegram_settings['TELEGRAM_ENABLE_UPLOAD'],
            images_store=self.images_store,
            files_store=self.videos_store
        )
        
    def teardown_method(self):
        """Clean up temp directories"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def _create_response(self, html: str, url: str = "https://example.com/product", meta: dict = None) -> HtmlResponse:
        """Create a proper HtmlResponse for testing"""
        request = Request(url=url, meta=meta or {})
        return HtmlResponse(
            url=url,
            body=html.encode('utf-8'),
            encoding='utf-8',
            request=request
        )
    
    def _create_test_files(self, media_item: VivblissMediaItem):
        """Create actual test files for the paths in media item"""
        if 'images' in media_item:
            for img_info in media_item['images']:
                file_path = img_info['path']
                if not os.path.isabs(file_path):
                    file_path = os.path.join(self.images_store, file_path)
                    
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'wb') as f:
                    # Write a minimal JPEG header
                    f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF')
                    
        if 'videos' in media_item:
            for video_info in media_item['videos']:
                file_path = video_info['path'] 
                if not os.path.isabs(file_path):
                    file_path = os.path.join(self.videos_store, file_path)
                    
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'wb') as f:
                    # Write minimal MP4 header
                    f.write(b'\x00\x00\x00\x20ftypmp4\x00')
    
    def test_extract_media_urls_from_html(self):
        """Test URL extraction from HTML page"""
        html = '''
        <div class="product-gallery">
            <img src="/images/product1.jpg" alt="Product Image 1">
            <img src="/images/product2.png" alt="Product Image 2">
            <video src="/videos/demo.mp4" controls></video>
            <img src="/images/thumbnail.jpg" width="50" height="50" alt="Thumbnail">
        </div>
        '''
        response = self._create_response(html)
        
        # Extract all media URLs
        media_data = self.extractor.extract_all_media(response)
        
        assert len(media_data['image_urls']) >= 3  # Including thumbnail
        assert len(media_data['video_urls']) >= 1
        assert "https://example.com/images/product1.jpg" in media_data['image_urls']
        assert "https://example.com/videos/demo.mp4" in media_data['video_urls']
        
        # Test filtering by size - only the thumbnail has size attributes and should be filtered out
        large_images = self.extractor.extract_image_urls(response, min_width=100, min_height=100)
        # Images without width/height attributes pass through (they could be large)
        # Only the thumbnail (50x50) should be filtered out
        assert len(large_images) == 2  # Should exclude thumbnail
        
    def test_create_media_item_with_metadata(self):
        """Test creating VivblissMediaItem with proper metadata"""
        html = '''
        <article class="product">
            <h1>Amazing Product Demo</h1>
            <img src="/images/main.jpg" alt="Main Image">
            <video src="/videos/tutorial.mp4"></video>
        </article>
        '''
        meta = {
            'item': {
                'title': 'Amazing Product Demo',
                'url': 'https://example.com/products/amazing-demo',
                'category': 'Electronics',
                'date': '2024-01-15'
            }
        }
        response = self._create_response(html, meta=meta)
        
        media_item = self.extractor.create_media_item(response)
        
        assert media_item['title'] == 'Amazing Product Demo'
        assert media_item['source_url'] == 'https://example.com/products/amazing-demo'
        assert media_item['category'] == 'Electronics'
        assert len(media_item['image_urls']) == 1
        assert len(media_item['video_urls']) == 1
        
    def test_media_download_pipeline_processing(self):
        """Test media download pipeline processes VivblissMediaItem correctly"""
        item = VivblissMediaItem(
            title="Test Product",
            source_url="https://example.com/test",
            image_urls=[
                "https://example.com/img1.jpg",
                "https://example.com/img2.png"
            ],
            video_urls=[
                "https://example.com/video1.mp4"
            ],
            category="Electronics"
        )
        
        # Process item through pipeline
        result = self.media_pipeline.process_item(item, self.spider)
        
        # Check that download info was added
        assert 'images' in result
        assert 'videos' in result
        assert len(result['images']) == 2
        assert len(result['videos']) == 1
        
        # Check file paths are properly generated
        for img_info in result['images']:
            assert 'Electronics' in img_info['path']
            assert img_info['path'].startswith('images/')
            
    def test_telegram_pipeline_media_extraction(self):
        """Test Telegram pipeline extracts media files correctly"""
        # Create item with downloaded media
        item = VivblissMediaItem(
            title="Product Gallery",
            images=[
                {'path': 'full/img1.jpg', 'url': 'https://example.com/img1.jpg'},
                {'path': 'full/img2.png', 'url': 'https://example.com/img2.png'}
            ],
            videos=[
                {'path': 'full/video1.mp4', 'url': 'https://example.com/video1.mp4'}
            ]
        )
        
        # Create test files
        self._create_test_files(item)
        
        # Extract media files
        media_files = self.telegram_pipeline.extract_media_files(item)
        
        assert len(media_files) == 3
        # Check all files exist
        for file_path in media_files:
            assert os.path.exists(file_path)
            
    def test_telegram_caption_generation(self):
        """Test caption generation for product media"""
        item = VivblissMediaItem(
            title="Professional Camera Kit",
            source_url="https://example.com/camera-kit",
            category="Photography",
            date="2024-01-20"
        )
        
        caption = self.telegram_pipeline.build_media_caption(item)
        
        assert "Professional Camera Kit" in caption
        assert "Photography" in caption
        assert "2024-01-20" in caption
        assert "https://example.com/camera-kit" in caption
        assert "🛍️" in caption  # Product emoji
        
    @pytest.mark.asyncio
    async def test_complete_workflow_integration(self):
        """Test complete workflow from HTML to Telegram upload"""
        # Step 1: Extract media URLs from HTML
        html = '''
        <div class="product-showcase">
            <h2>Premium Headphones</h2>
            <img src="/images/headphones-main.jpg" alt="Main product image">
            <img src="/images/headphones-side.png" alt="Side view">
            <video src="/videos/headphones-demo.mp4" controls></video>
        </div>
        '''
        meta = {
            'item': {
                'title': 'Premium Headphones',
                'url': 'https://store.example.com/headphones',
                'category': 'Audio',
                'date': '2024-01-25'
            }
        }
        response = self._create_response(html, "https://store.example.com/headphones", meta=meta)
        
        # Step 2: Create media item
        media_item = self.extractor.create_media_item(response)
        
        # Step 3: Process through download pipeline (simulated)
        processed_item = self.media_pipeline.process_item(media_item, self.spider)
        
        # Step 4: Create actual files for Telegram pipeline
        self._create_test_files(processed_item)
        
        # Step 5: Mock Telegram uploader and test upload
        with patch.object(self.telegram_pipeline, 'uploader') as mock_uploader:
            mock_uploader.upload_file = Mock(return_value={
                'success': True,
                'message_id': 12345,
                'file_id': 'test_file_id'
            })
            
            # Process through Telegram pipeline (async version to avoid loop conflict)
            final_item = await self.telegram_pipeline.process_item_async(processed_item, self.spider)
            
            # Verify upload was called for all media files
            assert mock_uploader.upload_file.call_count >= 3  # 2 images + 1 video
            
            # Check captions contain product information
            for call in mock_uploader.upload_file.call_args_list:
                caption = call[1]['caption']  # keyword argument
                assert "Premium Headphones" in caption
                assert "Audio" in caption
                
        assert final_item['title'] == 'Premium Headphones'
        assert final_item['category'] == 'Audio'
        
    def test_error_handling_workflow(self):
        """Test error handling in the complete workflow"""
        # Create item with invalid media URLs
        item = VivblissMediaItem(
            title="Test Product",
            image_urls=["https://invalid-url.com/nonexistent.jpg"],
            video_urls=["https://invalid-url.com/nonexistent.mp4"]
        )
        
        # Process through pipeline - should handle failures gracefully
        result = self.media_pipeline.process_item(item, self.spider)
        
        # Should have error information
        assert 'download_errors' in result
        # At minimum, the item structure should be preserved
        assert result['title'] == 'Test Product'
        
    def test_mixed_media_type_handling(self):
        """Test handling of items with both images and videos"""
        item = VivblissMediaItem(
            title="Mixed Media Product",
            images=[
                {'path': 'Electronics/img1.jpg', 'url': 'https://example.com/img1.jpg'},
                {'path': 'Electronics/img2.png', 'url': 'https://example.com/img2.png'}
            ],
            videos=[
                {'path': 'Electronics/video1.mp4', 'url': 'https://example.com/video1.mp4'},
                {'path': 'Electronics/video2.webm', 'url': 'https://example.com/video2.webm'}
            ]
        )
        
        # Create test files
        self._create_test_files(item)
        
        # Test file grouping
        media_files = self.telegram_pipeline.extract_media_files(item)
        images, videos = self.telegram_pipeline.group_media_by_type(media_files)
        
        assert len(images) == 2
        assert len(videos) == 2
        
        # All files should exist
        for file_path in images + videos:
            assert os.path.exists(file_path)
            
    def test_performance_with_many_media_files(self):
        """Test handling of items with many media files"""
        # Create item with many media files
        images = []
        videos = []
        
        for i in range(10):
            images.append({
                'path': f'Electronics/bulk_img_{i}.jpg',
                'url': f'https://example.com/img_{i}.jpg'
            })
            
        for i in range(5):
            videos.append({
                'path': f'Electronics/bulk_video_{i}.mp4',
                'url': f'https://example.com/video_{i}.mp4'
            })
            
        item = VivblissMediaItem(
            title="Bulk Media Product",
            images=images,
            videos=videos,
            category="Electronics"
        )
        
        # Create test files
        self._create_test_files(item)
        
        # Extract and verify all files
        media_files = self.telegram_pipeline.extract_media_files(item)
        assert len(media_files) == 15  # 10 images + 5 videos
        
        # All files should exist
        for file_path in media_files:
            assert os.path.exists(file_path)