import pytest
from unittest.mock import Mock, patch
from scrapy.http import HtmlResponse, Request
from scrapy.selector import Selector
from vivbliss_scraper.extractors.media_extractor import MediaExtractor
from vivbliss_scraper.items import VivblissMediaItem


class TestMediaExtractor:
    """Test suite for MediaExtractor functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.extractor = MediaExtractor()
        
    def _create_response(self, html: str, url: str = "https://example.com/article", meta: dict = None) -> HtmlResponse:
        """Create a proper HtmlResponse for testing"""
        request = Request(url=url, meta=meta or {})
        return HtmlResponse(
            url=url,
            body=html.encode('utf-8'),
            encoding='utf-8',
            request=request
        )
        
    def test_extract_image_urls_from_img_tags(self):
        """Test extraction of image URLs from img tags"""
        html = '''
        <div class="article">
            <img src="/images/photo1.jpg" alt="Photo 1">
            <img src="https://cdn.example.com/photo2.png" alt="Photo 2">
            <img data-src="/lazy/photo3.webp" alt="Photo 3">
        </div>
        '''
        response = self._create_response(html)
        
        urls = self.extractor.extract_image_urls(response)
        
        assert len(urls) == 3
        assert "https://example.com/images/photo1.jpg" in urls
        assert "https://cdn.example.com/photo2.png" in urls
        assert "https://example.com/lazy/photo3.webp" in urls
        
    def test_extract_video_urls_from_video_tags(self):
        """Test extraction of video URLs from video tags"""
        html = '''
        <div class="content">
            <video src="/videos/clip1.mp4"></video>
            <video>
                <source src="https://cdn.example.com/video2.webm" type="video/webm">
                <source src="/videos/video2.mp4" type="video/mp4">
            </video>
        </div>
        '''
        response = self._create_response(html)
        
        urls = self.extractor.extract_video_urls(response)
        
        assert len(urls) == 3
        assert "https://example.com/videos/clip1.mp4" in urls
        assert "https://cdn.example.com/video2.webm" in urls
        assert "https://example.com/videos/video2.mp4" in urls
        
    def test_extract_media_from_iframe(self):
        """Test extraction of media URLs from iframe embeds"""
        html = '''
        <div class="content">
            <iframe src="https://player.vimeo.com/video/123456"></iframe>
            <iframe src="https://www.youtube.com/embed/abcdef"></iframe>
        </div>
        '''
        response = self._create_response(html)
        
        urls = self.extractor.extract_embedded_media_urls(response)
        
        assert len(urls) == 2
        assert any("vimeo" in url for url in urls)
        assert any("youtube" in url for url in urls)
        
    def test_validate_media_urls(self):
        """Test URL validation for supported media formats"""
        valid_image_urls = [
            "https://example.com/image.jpg",
            "https://example.com/image.png",
            "https://example.com/image.gif",
            "https://example.com/image.webp",
        ]
        
        valid_video_urls = [
            "https://example.com/video.mp4",
            "https://example.com/video.avi",
            "https://example.com/video.mkv",
            "https://example.com/video.webm",
        ]
        
        invalid_urls = [
            "https://example.com/document.pdf",
            "https://example.com/script.js",
            "https://example.com/style.css",
            "not-a-url",
            "",
        ]
        
        for url in valid_image_urls:
            assert self.extractor.is_valid_image_url(url) is True
            
        for url in valid_video_urls:
            assert self.extractor.is_valid_video_url(url) is True
            
        for url in invalid_urls:
            assert self.extractor.is_valid_image_url(url) is False
            assert self.extractor.is_valid_video_url(url) is False
            
    def test_extract_all_media_urls(self):
        """Test extraction of all media URLs from a page"""
        html = '''
        <article>
            <img src="/images/hero.jpg">
            <video src="/videos/intro.mp4"></video>
            <img data-lazy-src="https://cdn.example.com/lazy.png">
            <iframe src="https://player.vimeo.com/video/789"></iframe>
        </article>
        '''
        response = self._create_response(html)
        
        media_data = self.extractor.extract_all_media(response)
        
        assert "image_urls" in media_data
        assert "video_urls" in media_data
        assert len(media_data["image_urls"]) >= 2
        assert len(media_data["video_urls"]) >= 2
        
    def test_create_media_item(self):
        """Test creation of VivblissMediaItem with extracted URLs"""
        html = '''
        <article>
            <h1>Test Article</h1>
            <img src="/images/test.jpg">
            <video src="/videos/test.mp4"></video>
        </article>
        '''
        meta = {
            'item': {
                'title': 'Test Article',
                'url': 'https://example.com/test-article'
            }
        }
        response = self._create_response(html, meta=meta)
        
        media_item = self.extractor.create_media_item(response)
        
        assert isinstance(media_item, VivblissMediaItem)
        assert media_item['title'] == 'Test Article'
        assert media_item['source_url'] == 'https://example.com/test-article'
        assert len(media_item['image_urls']) > 0
        assert len(media_item['video_urls']) > 0
        
    def test_handle_relative_urls(self):
        """Test proper handling of relative URLs"""
        html = '''
        <div>
            <img src="/images/local.jpg">
            <img src="../images/parent.png">
            <img src="./images/current.gif">
            <img src="images/noprefix.webp">
        </div>
        '''
        response = self._create_response(html, url="https://example.com/articles/page.html")
        
        urls = self.extractor.extract_image_urls(response)
        
        assert "https://example.com/images/local.jpg" in urls
        assert "https://example.com/images/parent.png" in urls
        assert "https://example.com/articles/images/current.gif" in urls
        assert "https://example.com/articles/images/noprefix.webp" in urls
        
    def test_deduplicate_urls(self):
        """Test that duplicate URLs are removed"""
        html = '''
        <div>
            <img src="/images/dup.jpg">
            <img src="/images/dup.jpg">
            <img data-src="/images/dup.jpg">
            <img src="https://example.com/images/dup.jpg">
        </div>
        '''
        response = self._create_response(html)
        
        urls = self.extractor.extract_image_urls(response)
        
        # Should only have one URL after deduplication
        assert len(urls) == 1
        assert urls[0] == "https://example.com/images/dup.jpg"
        
    def test_extract_from_background_images(self):
        """Test extraction of URLs from CSS background images"""
        html = '''
        <div style="background-image: url('/images/bg1.jpg')"></div>
        <div style="background: url('https://cdn.example.com/bg2.png') no-repeat"></div>
        <div data-bg="/images/bg3.webp"></div>
        '''
        response = self._create_response(html)
        
        urls = self.extractor.extract_background_image_urls(response)
        
        assert len(urls) >= 2
        assert "https://example.com/images/bg1.jpg" in urls
        assert "https://cdn.example.com/bg2.png" in urls
        
    def test_filter_by_size_attribute(self):
        """Test filtering images by size attributes"""
        html = '''
        <div>
            <img src="/images/thumb.jpg" width="50" height="50">
            <img src="/images/medium.jpg" width="300" height="200">
            <img src="/images/large.jpg" width="1920" height="1080">
        </div>
        '''
        response = self._create_response(html)
        
        # Get only images larger than 100x100
        urls = self.extractor.extract_image_urls(
            response, 
            min_width=100, 
            min_height=100
        )
        
        assert len(urls) == 2
        assert "https://example.com/images/medium.jpg" in urls
        assert "https://example.com/images/large.jpg" in urls
        assert "https://example.com/images/thumb.jpg" not in urls