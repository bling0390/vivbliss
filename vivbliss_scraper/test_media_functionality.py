#!/usr/bin/env python3
"""
简单测试脚本：验证媒体提取功能
"""

import sys
import os
sys.path.insert(0, '.')

from scrapy.http import HtmlResponse
from vivbliss_scraper.spiders.vivbliss import VivblissSpider
from vivbliss_scraper.items import VivblissItem


def test_media_extraction():
    """测试媒体提取功能"""
    print("🚀 开始测试媒体提取功能...")
    
    # 创建爬虫实例
    spider = VivblissSpider()
    
    # 创建包含媒体内容的测试HTML
    test_html = """
    <html>
        <head><title>测试页面</title></head>
        <body>
            <article>
                <h2><a href="/test-article">测试文章标题</a></h2>
                <div class="content">
                    <p>这是测试内容</p>
                    <img src="/images/test1.jpg" alt="测试图片1">
                    <img src="/images/test2.png" alt="测试图片2">
                    <video src="/videos/test.mp4" controls></video>
                    <iframe src="https://youtube.com/embed/test123"></iframe>
                </div>
                <time>2024-01-15</time>
                <span class="category">测试分类</span>
            </article>
        </body>
    </html>
    """
    
    # 创建模拟响应
    response = HtmlResponse(
        url="https://vivbliss.com/test",
        body=test_html.encode('utf-8'),
        encoding='utf-8'
    )
    
    print("📄 解析测试页面...")
    
    # 运行解析
    items = list(spider.parse(response))
    
    if not items:
        print("❌ 没有提取到任何项目")
        return False
    
    item = items[0]
    print(f"✅ 成功提取项目: {type(item)}")
    
    # 检查基本字段
    print(f"📝 标题: {item.get('title', '无')}")
    print(f"🔗 URL: {item.get('url', '无')}")
    print(f"📂 分类: {item.get('category', '无')}")
    
    # 检查媒体字段
    images = item.get('images', [])
    videos = item.get('videos', [])
    media_count = item.get('media_count', 0)
    
    print(f"\n📷 图片数量: {len(images)}")
    for i, img in enumerate(images, 1):
        print(f"   {i}. {img}")
    
    print(f"\n🎥 视频数量: {len(videos)}")
    for i, video in enumerate(videos, 1):
        print(f"   {i}. {video}")
    
    print(f"\n📁 媒体总数: {media_count}")
    
    # 验证结果
    success = True
    if len(images) < 2:
        print("❌ 图片提取数量不符合预期")
        success = False
    
    if len(videos) < 1:
        print("❌ 视频提取数量不符合预期")
        success = False
    
    if media_count != len(images) + len(videos):
        print("❌ 媒体总数计算错误")
        success = False
    
    # 检查URL格式
    for img in images:
        if not img.startswith('http'):
            print(f"❌ 图片URL格式错误: {img}")
            success = False
    
    for video in videos:
        if not video.startswith('http'):
            print(f"❌ 视频URL格式错误: {video}")
            success = False
    
    if success:
        print("\n✅ 所有测试通过！媒体提取功能正常工作")
    else:
        print("\n❌ 部分测试失败")
    
    return success


def test_media_validation():
    """测试媒体验证功能"""
    print("\n🔍 测试媒体验证功能...")
    
    spider = VivblissSpider()
    
    # 测试图片URL验证
    test_image_urls = [
        "https://example.com/image.jpg",      # 有效
        "https://example.com/image.png",      # 有效
        "https://example.com/document.pdf",   # 无效
        "invalid-url",                        # 无效
        ""                                    # 无效
    ]
    
    valid_images = 0
    for url in test_image_urls:
        if spider.media_validator.is_valid_image_url(url):
            valid_images += 1
            print(f"✅ 有效图片URL: {url}")
        else:
            print(f"❌ 无效图片URL: {url}")
    
    # 测试视频URL验证
    test_video_urls = [
        "https://example.com/video.mp4",      # 有效
        "https://youtube.com/embed/abc123",   # 有效
        "https://example.com/image.jpg",      # 无效
        "invalid-url",                        # 无效
        ""                                    # 无效
    ]
    
    valid_videos = 0
    for url in test_video_urls:
        if spider.media_validator.is_valid_video_url(url):
            valid_videos += 1
            print(f"✅ 有效视频URL: {url}")
        else:
            print(f"❌ 无效视频URL: {url}")
    
    print(f"\n📊 验证结果: {valid_images}/5 图片URL有效, {valid_videos}/5 视频URL有效")
    
    # 预期结果: 2个有效图片URL, 2个有效视频URL
    success = (valid_images == 2 and valid_videos == 2)
    
    if success:
        print("✅ 媒体验证功能正常工作")
    else:
        print("❌ 媒体验证功能存在问题")
    
    return success


def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 VivBliss 爬虫媒体提取功能测试")
    print("=" * 60)
    
    try:
        # 测试媒体提取
        test1_passed = test_media_extraction()
        
        # 测试媒体验证
        test2_passed = test_media_validation()
        
        print("\n" + "=" * 60)
        print("📋 测试总结:")
        print(f"   媒体提取功能: {'✅ 通过' if test1_passed else '❌ 失败'}")
        print(f"   媒体验证功能: {'✅ 通过' if test2_passed else '❌ 失败'}")
        
        if test1_passed and test2_passed:
            print("\n🎉 所有测试通过！媒体提取功能已成功实现")
            return 0
        else:
            print("\n⚠️  部分测试失败，需要进一步调试")
            return 1
            
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)