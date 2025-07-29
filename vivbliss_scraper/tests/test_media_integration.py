"""
媒体提取功能集成测试
测试完整的媒体提取流程
"""

import unittest
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from scrapy.http import HtmlResponse, Request
    from vivbliss_scraper.spiders.vivbliss import VivblissSpider
    from vivbliss_scraper.items import VivblissItem
    from vivbliss_scraper.utils.media_extractor import MediaExtractor, MediaValidator
    SCRAPY_AVAILABLE = True
except ImportError:
    SCRAPY_AVAILABLE = False
    print("⚠️  Scrapy 未安装，将跳过需要 Scrapy 的测试")


class TestMediaIntegration(unittest.TestCase):
    """媒体提取集成测试"""
    
    def setUp(self):
        """设置测试环境"""
        if SCRAPY_AVAILABLE:
            self.spider = VivblissSpider()
            self.media_extractor = MediaExtractor()
            self.media_validator = MediaValidator()
    
    @unittest.skipUnless(SCRAPY_AVAILABLE, "需要 Scrapy")
    def test_complete_media_extraction_workflow(self):
        """测试完整的媒体提取工作流"""
        # 创建包含丰富媒体内容的测试HTML
        test_html = """
        <html>
            <head><title>媒体丰富的测试页面</title></head>
            <body>
                <article class="post">
                    <h2><a href="/media-rich-article">媒体丰富的文章</a></h2>
                    <div class="content">
                        <p>这是一篇包含多种媒体的文章</p>
                        
                        <!-- 多种图片格式 -->
                        <img src="/images/photo1.jpg" alt="照片1" class="main-image">
                        <img src="/images/photo2.png" alt="照片2" class="thumbnail">
                        <img src="//cdn.example.com/photo3.gif" alt="动图" class="gif">
                        <img src="/images/photo4.webp" alt="WebP图片">
                        
                        <!-- 多种视频格式 -->
                        <video src="/videos/demo.mp4" controls poster="/images/poster.jpg">
                            <source src="/videos/demo.webm" type="video/webm">
                            您的浏览器不支持视频标签
                        </video>
                        
                        <!-- 嵌入式视频 -->
                        <iframe src="https://www.youtube.com/embed/dQw4w9WgXcQ" 
                                width="560" height="315" frameborder="0"></iframe>
                        <iframe src="https://player.vimeo.com/video/123456789" 
                                width="640" height="360" frameborder="0"></iframe>
                        
                        <!-- 带data属性的媒体 -->
                        <div class="lazy-image" data-src="/images/lazy-photo.jpg"></div>
                        <div class="video-player" data-video-url="/videos/player-video.mp4"></div>
                        
                        <!-- 内联样式背景图 -->
                        <div style="background-image: url('/images/bg-image.jpg')" class="hero"></div>
                        
                        <!-- 无效的媒体（应被过滤） -->
                        <img src="/documents/file.pdf" alt="PDF文档">
                        <video src="/audio/music.mp3"></video>
                    </div>
                    
                    <time datetime="2024-01-15">2024年1月15日</time>
                    <span class="category">技术</span>
                </article>
            </body>
        </html>
        """
        
        # 创建响应对象
        response = HtmlResponse(
            url="https://vivbliss.com/media-test",
            body=test_html.encode('utf-8'),
            encoding='utf-8'
        )
        
        # 执行解析
        items = list(self.spider.parse(response))
        
        # 验证结果
        self.assertGreater(len(items), 0, "应该提取到至少一个项目")
        
        item = items[0]
        self.assertIsInstance(item, VivblissItem, "应该返回 VivblissItem 实例")
        
        # 验证基本字段
        self.assertIn('title', item)
        self.assertIn('url', item)
        self.assertIn('images', item)
        self.assertIn('videos', item)
        self.assertIn('media_files', item)
        self.assertIn('media_count', item)
        
        # 验证媒体提取结果
        images = item['images']
        videos = item['videos']
        
        print(f"\n📷 提取的图片 ({len(images)} 个):")
        for i, img in enumerate(images, 1):
            print(f"   {i}. {img}")
        
        print(f"\n🎥 提取的视频 ({len(videos)} 个):")
        for i, video in enumerate(videos, 1):
            print(f"   {i}. {video}")
        
        # 验证图片提取
        self.assertGreater(len(images), 0, "应该提取到图片")
        
        # 验证所有图片URL都是绝对路径
        for img_url in images:
            self.assertTrue(img_url.startswith('http'), f"图片URL应该是绝对路径: {img_url}")
        
        # 验证视频提取
        self.assertGreater(len(videos), 0, "应该提取到视频")
        
        # 验证所有视频URL都是绝对路径
        for video_url in videos:
            self.assertTrue(video_url.startswith('http'), f"视频URL应该是绝对路径: {video_url}")
        
        # 验证媒体总数计算
        expected_total = len(images) + len(videos)
        self.assertEqual(item['media_count'], expected_total, "媒体总数计算错误")
        
        # 验证媒体文件列表
        media_files = item['media_files']
        self.assertEqual(len(media_files), expected_total, "媒体文件列表长度错误")
        
        print(f"\n✅ 媒体提取测试通过:")
        print(f"   - 图片: {len(images)} 个")
        print(f"   - 视频: {len(videos)} 个")
        print(f"   - 总计: {item['media_count']} 个媒体文件")
    
    def test_media_validator_comprehensive(self):
        """全面测试媒体验证器"""
        # 测试图片URL验证
        image_test_cases = [
            # 有效的图片URL
            ("https://example.com/image.jpg", True),
            ("https://example.com/photo.jpeg", True),
            ("https://example.com/pic.png", True),
            ("https://example.com/animation.gif", True),
            ("https://example.com/modern.webp", True),
            ("https://example.com/bitmap.bmp", True),
            ("https://cdn.site.com/thumbnail.jpg", True),
            
            # 无效的图片URL
            ("https://example.com/document.pdf", False),
            ("https://example.com/video.mp4", False),
            ("https://example.com/audio.mp3", False),
            ("not-a-url", False),
            ("", False),
            (None, False),
        ]
        
        print("\n🔍 测试图片URL验证:")
        for url, expected in image_test_cases:
            with self.subTest(url=url):
                result = self.media_validator.is_valid_image_url(url)
                self.assertEqual(result, expected, 
                    f"图片URL验证失败: {url} -> 期望:{expected}, 实际:{result}")
                print(f"   {'✅' if result == expected else '❌'} {url} -> {result}")
        
        # 测试视频URL验证
        video_test_cases = [
            # 有效的视频URL
            ("https://example.com/video.mp4", True),
            ("https://example.com/clip.webm", True),
            ("https://example.com/movie.mov", True),
            ("https://example.com/film.avi", True),
            ("https://www.youtube.com/embed/abc123", True),
            ("https://player.vimeo.com/video/123456", True),
            ("https://www.youtube.com/watch?v=abc123", True),
            
            # 无效的视频URL
            ("https://example.com/image.jpg", False),
            ("https://example.com/document.pdf", False),
            ("https://example.com/audio.mp3", False),
            ("not-a-url", False),
            ("", False),
            (None, False),
        ]
        
        print("\n🔍 测试视频URL验证:")
        for url, expected in video_test_cases:
            with self.subTest(url=url):
                result = self.media_validator.is_valid_video_url(url)
                self.assertEqual(result, expected,
                    f"视频URL验证失败: {url} -> 期望:{expected}, 实际:{result}")
                print(f"   {'✅' if result == expected else '❌'} {url} -> {result}")
    
    @unittest.skipUnless(SCRAPY_AVAILABLE, "需要 Scrapy")
    def test_media_extraction_edge_cases(self):
        """测试媒体提取的边缘情况"""
        # 测试空内容
        empty_html = "<html><body><article><h2><a href='/empty'>空文章</a></h2></article></body></html>"
        response = HtmlResponse(url="https://vivbliss.com/empty", body=empty_html.encode('utf-8'))
        items = list(self.spider.parse(response))
        
        if items:
            item = items[0]
            self.assertEqual(len(item.get('images', [])), 0, "空文章不应该有图片")
            self.assertEqual(len(item.get('videos', [])), 0, "空文章不应该有视频")
            self.assertEqual(item.get('media_count', 0), 0, "空文章媒体总数应为0")
        
        # 测试无效媒体URL
        invalid_html = """
        <html><body>
            <article>
                <h2><a href='/invalid'>包含无效媒体的文章</a></h2>
                <img src="" alt="空URL">
                <img src="not-a-valid-url" alt="无效URL">
                <video src="/documents/file.txt"></video>
                <iframe src="javascript:alert('xss')"></iframe>
            </article>
        </body></html>
        """
        response = HtmlResponse(url="https://vivbliss.com/invalid", body=invalid_html.encode('utf-8'))
        items = list(self.spider.parse(response))
        
        if items:
            item = items[0]
            # 无效URL应该被过滤掉
            images = item.get('images', [])
            videos = item.get('videos', [])
            
            for img_url in images:
                self.assertTrue(img_url.startswith('http'), f"应过滤无效图片URL: {img_url}")
                self.assertTrue(self.media_validator.is_valid_image_url(img_url), 
                    f"应过滤无效图片URL: {img_url}")
            
            for video_url in videos:
                self.assertTrue(video_url.startswith('http'), f"应过滤无效视频URL: {video_url}")
                self.assertTrue(self.media_validator.is_valid_video_url(video_url),
                    f"应过滤无效视频URL: {video_url}")
        
        print("✅ 边缘情况测试通过")
    
    def test_media_extractor_without_scrapy(self):
        """不依赖Scrapy的媒体提取器测试"""
        # 测试验证器逻辑
        validator = MediaValidator()
        
        # 测试图片格式识别
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
        for ext in image_extensions:
            url = f"https://example.com/image{ext}"
            self.assertTrue(validator.is_valid_image_url(url), f"应识别{ext}为图片格式")
        
        # 测试视频格式识别
        video_extensions = ['.mp4', '.webm', '.mov', '.avi']
        for ext in video_extensions:
            url = f"https://example.com/video{ext}"
            self.assertTrue(validator.is_valid_video_url(url), f"应识别{ext}为视频格式")
        
        # 测试视频平台识别
        platform_urls = [
            "https://www.youtube.com/embed/abc123",
            "https://player.vimeo.com/video/123456",
            "https://www.dailymotion.com/embed/video/abc123"
        ]
        for url in platform_urls:
            self.assertTrue(validator.is_valid_video_url(url), f"应识别视频平台URL: {url}")
        
        print("✅ 独立验证器测试通过")


def run_tests():
    """运行所有测试"""
    print("🧪 开始运行媒体提取集成测试")
    print("=" * 60)
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMediaIntegration)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总:")
    print(f"   运行测试: {result.testsRun}")
    print(f"   成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   失败: {len(result.failures)}")
    print(f"   错误: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ 失败的测试:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback.splitlines()[-1]}")
    
    if result.errors:
        print("\n💥 错误的测试:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback.splitlines()[-1]}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print("\n🎉 所有集成测试通过！")
    else:
        print("\n⚠️  部分测试失败，需要进一步调试")
    
    return success


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)