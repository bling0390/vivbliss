import pytest
from unittest.mock import Mock, patch, MagicMock
import os
from scrapy import Spider
from scrapy.http import Request
from vivbliss_scraper.pipelines.media_pipeline import MediaDownloadPipeline
from vivbliss_scraper.items import VivblissMediaItem


class TestMediaDownloadPipeline:
    """Test suite for MediaDownloadPipeline"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.spider = Mock(spec=Spider)
        self.spider.name = "test_spider"
        
        # Create pipeline with mocked settings
        self.settings = {
            'IMAGES_STORE': '/tmp/test_images',
            'FILES_STORE': '/tmp/test_videos',
            'MEDIA_ALLOW_REDIRECTS': True,
            'IMAGES_MIN_HEIGHT': 100,
            'IMAGES_MIN_WIDTH': 100,
            'FILES_EXPIRES': 90,
            'IMAGES_EXPIRES': 90,
        }
        
        self.pipeline = MediaDownloadPipeline(self.settings)
                
    def test_pipeline_initialization(self):
        """Test that pipeline initializes with correct settings"""
        assert self.pipeline.images_store == '/tmp/test_images'
        assert self.pipeline.files_store == '/tmp/test_videos'
        assert self.pipeline.images_min_width == 100
        assert self.pipeline.images_min_height == 100
        
    def test_process_item_with_media_urls(self):
        """Test processing item with image and video URLs"""
        item = VivblissMediaItem(
            title="Test Product",
            source_url="https://example.com/product",
            image_urls=[
                "https://example.com/product1.jpg",
                "https://example.com/product2.png"
            ],
            video_urls=[
                "https://example.com/demo.mp4"
            ]
        )
        
        # Process item
        with patch.object(self.pipeline, 'process_image_urls') as mock_images:
            with patch.object(self.pipeline, 'process_video_urls') as mock_videos:
                mock_images.return_value = item
                mock_videos.return_value = item
                
                result = self.pipeline.process_item(item, self.spider)
                
                mock_images.assert_called_once_with(item, self.spider)
                mock_videos.assert_called_once_with(item, self.spider)
                assert result == item
                
    def test_get_media_requests_for_images(self):
        """Test generation of download requests for images"""
        item = VivblissMediaItem(
            title="Test Product",
            image_urls=[
                "https://example.com/img1.jpg",
                "https://example.com/img2.png"
            ]
        )
        
        requests = list(self.pipeline.get_media_requests(item, self.spider, 'image'))
        
        assert len(requests) == 2
        assert all(isinstance(r, Request) for r in requests)
        assert requests[0].url == "https://example.com/img1.jpg"
        assert requests[1].url == "https://example.com/img2.png"
        assert requests[0].meta['media_type'] == 'image'
        assert requests[0].meta['item'] == item
        
    def test_get_media_requests_for_videos(self):
        """Test generation of download requests for videos"""
        item = VivblissMediaItem(
            title="Test Product",
            video_urls=[
                "https://example.com/video1.mp4",
                "https://example.com/video2.webm"
            ]
        )
        
        requests = list(self.pipeline.get_media_requests(item, self.spider, 'video'))
        
        assert len(requests) == 2
        assert all(isinstance(r, Request) for r in requests)
        assert requests[0].url == "https://example.com/video1.mp4"
        assert requests[1].url == "https://example.com/video2.webm"
        assert requests[0].meta['media_type'] == 'video'
        
    def test_item_completed_with_downloads(self):
        """Test item completion with successful downloads"""
        item = VivblissMediaItem(
            title="Test Product",
            image_urls=["https://example.com/img1.jpg"],
            video_urls=["https://example.com/video1.mp4"]
        )
        
        # Mock download results
        image_results = [
            (True, {
                'url': 'https://example.com/img1.jpg',
                'path': 'full/abc123.jpg',
                'checksum': 'abc123'
            })
        ]
        
        video_results = [
            (True, {
                'url': 'https://example.com/video1.mp4',
                'path': 'full/def456.mp4',
                'checksum': 'def456'
            })
        ]
        
        # Process completion
        item = self.pipeline.item_completed(image_results, item, self.spider, 'image')
        item = self.pipeline.item_completed(video_results, item, self.spider, 'video')
        
        assert 'images' in item
        assert len(item['images']) == 1
        assert item['images'][0]['path'] == 'full/abc123.jpg'
        
        assert 'videos' in item
        assert len(item['videos']) == 1
        assert item['videos'][0]['path'] == 'full/def456.mp4'
        
    def test_item_completed_with_failures(self):
        """Test item completion with failed downloads"""
        item = VivblissMediaItem(
            title="Test Product",
            image_urls=["https://example.com/img1.jpg", "https://example.com/img2.jpg"],
        )
        
        # Mock download results with one success and one failure
        results = [
            (True, {
                'url': 'https://example.com/img1.jpg',
                'path': 'full/abc123.jpg',
                'checksum': 'abc123'
            }),
            (False, Exception("Download failed"))
        ]
        
        item = self.pipeline.item_completed(results, item, self.spider, 'image')
        
        assert 'images' in item
        assert len(item['images']) == 1  # Only successful download
        assert 'download_errors' in item
        assert len(item['download_errors']) == 1
        
    def test_filter_small_images(self):
        """Test filtering of images smaller than minimum dimensions"""
        # Create a mock image info
        with patch('vivbliss_scraper.pipelines.media_pipeline.Image.open') as mock_open:
            mock_image = MagicMock()
            mock_image.size = (50, 50)  # Too small
            mock_image.close = MagicMock()
            mock_open.return_value = mock_image
            
            result = self.pipeline.check_image_size('/tmp/small.jpg')
            assert result is False
            mock_image.close.assert_called_once()
            
            mock_image.size = (200, 200)  # Large enough
            mock_image.close.reset_mock()
            result = self.pipeline.check_image_size('/tmp/large.jpg')
            assert result is True
            mock_image.close.assert_called_once()
            
    def test_generate_file_path(self):
        """Test generation of storage file paths"""
        item = VivblissMediaItem(
            title="Test Product",
            category="Electronics"
        )
        
        # Test image path generation
        image_path = self.pipeline.file_path(
            Request("https://example.com/product.jpg"),
            item=item,
            media_type='image'
        )
        
        assert 'Electronics' in image_path
        assert 'images' in image_path
        assert image_path.endswith('.jpg')
        
        # Test video path generation
        video_path = self.pipeline.file_path(
            Request("https://example.com/demo.mp4"),
            item=item,
            media_type='video'
        )
        
        assert 'Electronics' in video_path
        assert 'videos' in video_path
        assert video_path.endswith('.mp4')
        
    def test_handle_duplicate_downloads(self):
        """Test handling of duplicate media URLs"""
        item = VivblissMediaItem(
            title="Test Product",
            image_urls=[
                "https://example.com/img.jpg",
                "https://example.com/img.jpg",  # Duplicate
                "https://example.com/other.jpg"
            ]
        )
        
        requests = list(self.pipeline.get_media_requests(item, self.spider, 'image'))
        
        # Should deduplicate URLs
        assert len(requests) == 2
        urls = [r.url for r in requests]
        assert urls.count("https://example.com/img.jpg") == 1
        
    def test_store_downloaded_file_info(self):
        """Test storing downloaded file information in item"""
        item = VivblissMediaItem(
            title="Test Product"
        )
        
        # Simulate storing download info
        self.pipeline.store_download_info(
            item,
            url="https://example.com/product.jpg",
            path="/tmp/test_images/full/abc123.jpg",
            media_type="image",
            checksum="abc123",
            size=1024576
        )
        
        assert 'images' in item
        assert len(item['images']) == 1
        assert item['images'][0]['url'] == "https://example.com/product.jpg"
        assert item['images'][0]['path'] == "/tmp/test_images/full/abc123.jpg"
        assert item['images'][0]['size'] == 1024576
        assert item['images'][0]['checksum'] == "abc123"