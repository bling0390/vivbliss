import pytest
from vivbliss_scraper.items import VivblissMediaItem


class TestVivblissMediaItem:
    """Test suite for VivblissMediaItem"""
    
    def test_media_item_fields(self):
        """Test that VivblissMediaItem has all required fields"""
        item = VivblissMediaItem()
        
        # Test required fields
        assert 'title' in item.fields
        assert 'source_url' in item.fields
        assert 'image_urls' in item.fields
        assert 'video_urls' in item.fields
        assert 'images' in item.fields  # For downloaded images
        assert 'videos' in item.fields  # For downloaded videos
        assert 'category' in item.fields
        assert 'date' in item.fields
        
    def test_media_item_initialization(self):
        """Test VivblissMediaItem can be initialized with data"""
        item = VivblissMediaItem(
            title="Product Demo",
            source_url="https://example.com/product",
            image_urls=["https://example.com/img1.jpg", "https://example.com/img2.png"],
            video_urls=["https://example.com/video1.mp4"],
            category="Electronics",
            date="2024-01-01"
        )
        
        assert item['title'] == "Product Demo"
        assert item['source_url'] == "https://example.com/product"
        assert len(item['image_urls']) == 2
        assert len(item['video_urls']) == 1
        assert item['category'] == "Electronics"
        assert item['date'] == "2024-01-01"
        
    def test_media_item_empty_lists(self):
        """Test that media URL lists can be empty"""
        item = VivblissMediaItem(
            title="Text Only Product",
            source_url="https://example.com/text",
            image_urls=[],
            video_urls=[]
        )
        
        assert item['image_urls'] == []
        assert item['video_urls'] == []
        
    def test_media_item_downloaded_fields(self):
        """Test fields for storing downloaded media info"""
        item = VivblissMediaItem()
        
        # Test setting downloaded images info
        item['images'] = [
            {'url': 'https://example.com/img1.jpg', 'path': 'full/img1.jpg'},
            {'url': 'https://example.com/img2.png', 'path': 'full/img2.png'}
        ]
        
        # Test setting downloaded videos info
        item['videos'] = [
            {'url': 'https://example.com/video1.mp4', 'path': 'full/video1.mp4'}
        ]
        
        assert len(item['images']) == 2
        assert item['images'][0]['path'] == 'full/img1.jpg'
        assert len(item['videos']) == 1
        assert item['videos'][0]['path'] == 'full/video1.mp4'