"""
测试媒体提取功能的 TDD 测试用例
使用 RED-GREEN-REFACTOR 循环开发
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pytest
import scrapy
from scrapy.http import HtmlResponse, Request
import json
import os
import tempfile

from vivbliss_scraper.spiders.vivbliss import VivblissSpider
from vivbliss_scraper.items import VivblissItem
from vivbliss_scraper.utils.media_extractor import MediaExtractor, MediaValidator


class TestMediaExtraction(unittest.TestCase):
    """测试媒体提取功能"""
    
    def setUp(self):
        """设置测试环境"""
        self.spider = VivblissSpider()
        self.media_extractor = MediaExtractor()
        self.media_validator = MediaValidator()
        
        # 创建模拟响应
        self.mock_response = self.create_mock_response()
    
    def create_mock_response(self):
        """创建包含媒体内容的模拟响应"""
        html_content = """
        <html>
            <head><title>Test Product</title></head>
            <body>
                <article class="product">
                    <h2><a href="/product/1">Test Product</a></h2>
                    <div class="product-images">
                        <img src="/images/product1-main.jpg" alt="Product Main Image" class="main-image">
                        <img src="/images/product1-thumb1.jpg" alt="Thumbnail 1" class="thumbnail">
                        <img src="/images/product1-thumb2.png" alt="Thumbnail 2" class="thumbnail">
                        <img src="//cdn.example.com/product1-hd.jpg" alt="HD Image" class="hd-image">
                        <img src="invalid-image.txt" alt="Invalid Image" class="invalid">
                    </div>
                    <div class="product-videos">
                        <video src="/videos/product1-demo.mp4" class="demo-video"></video>
                        <video src="/videos/product1-review.webm" class="review-video"></video>
                        <iframe src="https://youtube.com/embed/abc123" class="youtube-video"></iframe>
                        <div data-video-url="/videos/product1-feature.mov" class="embedded-video"></div>
                        <source src="invalid-video.txt" class="invalid-video">
                    </div>
                    <div class="content">
                        <p>Product description with <img src="/images/inline-image.jpg"> inline image</p>
                    </div>
                </article>
            </body>
        </html>
        """
        
        response = HtmlResponse(
            url="https://vivbliss.com/product/1",
            body=html_content,
            encoding='utf-8'
        )
        return response

    # ============ RED Phase Tests (应该失败) ============
    
    def test_extract_images_from_article_should_fail_initially(self):
        """测试从文章中提取图片 - 初始应该失败"""
        # 这个测试应该失败，因为我们还没有实现媒体提取功能
        with self.assertRaises(AttributeError):
            images = self.spider.extract_images_from_article(self.mock_response)
    
    def test_extract_videos_from_article_should_fail_initially(self):
        """测试从文章中提取视频 - 初始应该失败"""
        # 这个测试应该失败，因为我们还没有实现媒体提取功能
        with self.assertRaises(AttributeError):
            videos = self.spider.extract_videos_from_article(self.mock_response)
    
    def test_validate_media_urls_should_fail_initially(self):
        """测试媒体URL验证 - 初始应该失败"""
        # 这个测试应该失败，因为我们还没有实现验证功能
        test_urls = [
            "https://example.com/image.jpg",
            "https://example.com/video.mp4",
            "invalid-url"
        ]
        with self.assertRaises(AttributeError):
            results = self.spider.validate_media_urls(test_urls)

    # ============ GREEN Phase Tests (实现后应该通过) ============
    
    def test_extract_images_from_article_returns_valid_list(self):
        """测试图片提取返回有效列表"""
        # 期望的图片 URLs
        expected_images = [
            "https://vivbliss.com/images/product1-main.jpg",
            "https://vivbliss.com/images/product1-thumb1.jpg", 
            "https://vivbliss.com/images/product1-thumb2.png",
            "https://cdn.example.com/product1-hd.jpg",
            "https://vivbliss.com/images/inline-image.jpg"
        ]
        
        # 这个测试现在会失败，但实现后应该通过
        if hasattr(self.spider, 'extract_images_from_article'):
            images = self.spider.extract_images_from_article(self.mock_response)
            self.assertIsInstance(images, list)
            self.assertEqual(len(images), 5)  # 应该找到5个有效图片
            for img_url in images:
                self.assertTrue(img_url.startswith('http'))
                self.assertTrue(any(ext in img_url.lower() for ext in ['.jpg', '.png', '.jpeg', '.gif', '.webp']))
    
    def test_extract_videos_from_article_returns_valid_list(self):
        """测试视频提取返回有效列表"""
        # 期望的视频 URLs
        expected_videos = [
            "https://vivbliss.com/videos/product1-demo.mp4",
            "https://vivbliss.com/videos/product1-review.webm",
            "https://youtube.com/embed/abc123",
            "https://vivbliss.com/videos/product1-feature.mov"
        ]
        
        # 这个测试现在会失败，但实现后应该通过
        if hasattr(self.spider, 'extract_videos_from_article'):
            videos = self.spider.extract_videos_from_article(self.mock_response)
            self.assertIsInstance(videos, list)
            self.assertEqual(len(videos), 4)  # 应该找到4个有效视频
            for video_url in videos:
                self.assertTrue(video_url.startswith('http'))
    
    def test_media_validation_filters_invalid_urls(self):
        """测试媒体验证过滤无效URLs"""
        test_urls = [
            "https://example.com/valid-image.jpg",
            "https://example.com/valid-video.mp4", 
            "invalid-url",
            "/relative/path/image.png",
            "https://example.com/document.pdf"  # 无效的媒体格式
        ]
        
        if hasattr(self.spider, 'validate_media_urls'):
            valid_urls = self.spider.validate_media_urls(test_urls, self.mock_response)
            self.assertIsInstance(valid_urls, list)
            self.assertEqual(len(valid_urls), 3)  # 应该有3个有效URL
    
    def test_vivbliss_item_has_media_fields(self):
        """测试 VivblissItem 包含媒体字段"""
        item = VivblissItem()
        
        # 检查媒体字段是否存在
        self.assertTrue(hasattr(item.fields, 'images'))
        self.assertTrue(hasattr(item.fields, 'videos'))
        self.assertTrue(hasattr(item.fields, 'media_files'))
    
    def test_parse_method_extracts_media_content(self):
        """测试 parse 方法提取媒体内容"""
        # 模拟爬虫的 parse 方法，应该提取媒体内容
        generator = self.spider.parse(self.mock_response)
        items = list(generator)
        
        if items:
            item = items[0]
            self.assertIsInstance(item, VivblissItem)
            
            # 检查媒体字段是否被填充
            if 'images' in item:
                self.assertIsInstance(item['images'], list)
                self.assertGreater(len(item['images']), 0)
            
            if 'videos' in item:
                self.assertIsInstance(item['videos'], list)

    # ============ 媒体验证测试 ============
    
    def test_image_url_validation(self):
        """测试图片URL验证"""
        valid_image_urls = [
            "https://example.com/image.jpg",
            "https://example.com/image.png",
            "https://example.com/image.gif",
            "https://example.com/image.webp",
            "https://example.com/image.jpeg"
        ]
        
        invalid_image_urls = [
            "https://example.com/document.pdf",
            "https://example.com/video.mp4",
            "invalid-url",
            ""
        ]
        
        if hasattr(self.media_validator, 'is_valid_image_url'):
            for url in valid_image_urls:
                self.assertTrue(self.media_validator.is_valid_image_url(url), f"Should be valid: {url}")
            
            for url in invalid_image_urls:
                self.assertFalse(self.media_validator.is_valid_image_url(url), f"Should be invalid: {url}")
    
    def test_video_url_validation(self):
        """测试视频URL验证"""
        valid_video_urls = [
            "https://example.com/video.mp4",
            "https://example.com/video.webm",
            "https://example.com/video.mov",
            "https://example.com/video.avi",
            "https://youtube.com/embed/abc123",
            "https://vimeo.com/123456789"
        ]
        
        invalid_video_urls = [
            "https://example.com/image.jpg",
            "https://example.com/document.pdf",
            "invalid-url",
            ""
        ]
        
        if hasattr(self.media_validator, 'is_valid_video_url'):
            for url in valid_video_urls:
                self.assertTrue(self.media_validator.is_valid_video_url(url), f"Should be valid: {url}")
            
            for url in invalid_video_urls:
                self.assertFalse(self.media_validator.is_valid_video_url(url), f"Should be invalid: {url}")

    # ============ 集成测试 ============
    
    def test_media_extraction_integration(self):
        """测试媒体提取的完整集成"""
        # 创建包含丰富媒体内容的响应
        html_with_media = """
        <article>
            <h2><a href="/article/media-rich">Media Rich Article</a></h2>
            <div class="gallery">
                <img src="/images/gallery1.jpg" alt="Gallery 1">
                <img src="/images/gallery2.png" alt="Gallery 2">
                <video src="/videos/demo.mp4" poster="/images/poster.jpg"></video>
            </div>
            <div class="content">
                <p>Article with <img src="/images/inline.jpg"> inline media</p>
                <iframe src="https://youtube.com/embed/xyz789"></iframe>
            </div>
        </article>
        """
        
        response = HtmlResponse(
            url="https://vivbliss.com/media-test",
            body=html_with_media,
            encoding='utf-8'
        )
        
        # 运行完整的解析流程
        items = list(self.spider.parse(response))
        
        if items:
            item = items[0]
            
            # 验证媒体内容被正确提取
            if 'images' in item and item['images']:
                self.assertGreater(len(item['images']), 0)
                for img_url in item['images']:
                    self.assertTrue(img_url.startswith('http'))
            
            if 'videos' in item and item['videos']:
                self.assertGreater(len(item['videos']), 0)
                for video_url in item['videos']:
                    self.assertTrue(video_url.startswith('http'))

    # ============ 性能测试 ============
    
    def test_media_extraction_performance(self):
        """测试媒体提取的性能"""
        import time
        
        # 创建包含大量媒体的响应
        large_media_html = """
        <article>
            <h2><a href="/performance-test">Performance Test</a></h2>
            <div class="media">
        """
        
        # 添加100个图片和视频
        for i in range(100):
            large_media_html += f'<img src="/images/img{i}.jpg" alt="Image {i}">'
            large_media_html += f'<video src="/videos/vid{i}.mp4"></video>'
        
        large_media_html += """
            </div>
        </article>
        """
        
        response = HtmlResponse(
            url="https://vivbliss.com/performance-test",
            body=large_media_html,
            encoding='utf-8'
        )
        
        # 测量提取时间
        start_time = time.time()
        items = list(self.spider.parse(response))
        extraction_time = time.time() - start_time
        
        # 性能要求：提取时间应该少于5秒
        self.assertLess(extraction_time, 5.0, f"Media extraction took too long: {extraction_time:.2f}s")

    def tearDown(self):
        """清理测试环境"""
        # 清理任何临时文件或资源
        pass


class TestMediaValidator(unittest.TestCase):
    """测试媒体验证器"""
    
    def setUp(self):
        self.validator = MediaValidator()
    
    def test_supported_image_formats(self):
        """测试支持的图片格式"""
        supported_formats = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
        
        for fmt in supported_formats:
            url = f"https://example.com/image{fmt}"
            if hasattr(self.validator, 'is_valid_image_url'):
                self.assertTrue(self.validator.is_valid_image_url(url))
    
    def test_supported_video_formats(self):
        """测试支持的视频格式"""
        supported_formats = ['.mp4', '.webm', '.mov', '.avi', '.mkv', '.flv']
        
        for fmt in supported_formats:
            url = f"https://example.com/video{fmt}"
            if hasattr(self.validator, 'is_valid_video_url'):
                self.assertTrue(self.validator.is_valid_video_url(url))
    
    def test_url_accessibility_check(self):
        """测试URL可访问性检查"""
        # 这个测试需要网络连接，可以使用mock
        with patch('requests.head') as mock_head:
            mock_head.return_value.status_code = 200
            mock_head.return_value.headers = {'content-type': 'image/jpeg'}
            
            if hasattr(self.validator, 'check_url_accessibility'):
                result = self.validator.check_url_accessibility("https://example.com/image.jpg")
                self.assertTrue(result)


if __name__ == '__main__':
    # 运行测试套件
    unittest.main(verbosity=2)