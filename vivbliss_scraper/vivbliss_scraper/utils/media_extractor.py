"""
媒体提取器和验证器
用于从网页中提取和验证图片、视频等媒体内容
"""

import re
import logging
import requests
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional, Tuple
import mimetypes
from scrapy.http import Response
import time


class MediaValidator:
    """媒体URL验证器"""
    
    # 支持的图片格式
    SUPPORTED_IMAGE_FORMATS = {
        '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg', '.ico'
    }
    
    # 支持的视频格式
    SUPPORTED_VIDEO_FORMATS = {
        '.mp4', '.webm', '.mov', '.avi', '.mkv', '.flv', '.wmv', '.3gp', '.m4v'
    }
    
    # 视频平台域名
    VIDEO_PLATFORMS = {
        'youtube.com', 'youtu.be', 'vimeo.com', 'dailymotion.com', 
        'twitch.tv', 'tiktok.com', 'bilibili.com'
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def is_valid_image_url(self, url: str) -> bool:
        """验证图片URL有效性"""
        if not url or not isinstance(url, str):
            return False
        
        try:
            # 检查URL格式
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # 检查文件扩展名
            path = parsed.path.lower()
            if any(path.endswith(ext) for ext in self.SUPPORTED_IMAGE_FORMATS):
                return True
            
            # 检查是否包含图片关键词
            image_keywords = ['image', 'img', 'photo', 'picture', 'thumbnail', 'avatar']
            if any(keyword in url.lower() for keyword in image_keywords):
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"验证图片URL时出错: {url}, 错误: {e}")
            return False
    
    def is_valid_video_url(self, url: str) -> bool:
        """验证视频URL有效性"""
        if not url or not isinstance(url, str):
            return False
        
        try:
            # 检查URL格式
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # 检查视频平台
            domain = parsed.netloc.lower()
            if any(platform in domain for platform in self.VIDEO_PLATFORMS):
                return True
            
            # 检查文件扩展名
            path = parsed.path.lower()
            if any(path.endswith(ext) for ext in self.SUPPORTED_VIDEO_FORMATS):
                return True
            
            # 检查是否包含视频关键词
            video_keywords = ['video', 'movie', 'film', 'clip', 'media', 'embed']
            if any(keyword in url.lower() for keyword in video_keywords):
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"验证视频URL时出错: {url}, 错误: {e}")
            return False
    
    def check_url_accessibility(self, url: str, timeout: int = 5) -> bool:
        """检查URL是否可访问"""
        try:
            response = self.session.head(url, timeout=timeout, allow_redirects=True)
            return response.status_code == 200
        except Exception as e:
            self.logger.debug(f"URL不可访问: {url}, 错误: {e}")
            return False
    
    def get_media_info(self, url: str) -> Dict:
        """获取媒体文件信息"""
        info = {
            'url': url,
            'type': 'unknown',
            'format': '',
            'accessible': False,
            'content_type': '',
            'size': 0
        }
        
        try:
            # 基于URL判断类型
            if self.is_valid_image_url(url):
                info['type'] = 'image'
            elif self.is_valid_video_url(url):
                info['type'] = 'video'
            
            # 获取文件格式
            parsed = urlparse(url)
            path = parsed.path.lower()
            if '.' in path:
                info['format'] = path.split('.')[-1]
            
            # 检查可访问性（可选，因为会增加请求时间）
            # info['accessible'] = self.check_url_accessibility(url)
            
        except Exception as e:
            self.logger.error(f"获取媒体信息失败: {url}, 错误: {e}")
        
        return info


class MediaExtractor:
    """媒体内容提取器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validator = MediaValidator()
        
        # 图片选择器模式
        self.image_selectors = [
            'img::attr(src)',
            'img::attr(data-src)',
            'img::attr(data-original)',
            '[style*="background-image"]::attr(style)',
            'source::attr(src)',
            'source::attr(srcset)',
            '.image::attr(data-url)',
            '.photo::attr(href)',
            '.gallery img::attr(src)',
            '.product-image img::attr(src)',
            '.thumbnail img::attr(src)'
        ]
        
        # 视频选择器模式
        self.video_selectors = [
            'video::attr(src)',
            'video source::attr(src)',
            'iframe[src*="youtube"]::attr(src)',
            'iframe[src*="vimeo"]::attr(src)',
            'iframe[src*="dailymotion"]::attr(src)',
            '[data-video-url]::attr(data-video-url)',
            '[data-video-src]::attr(data-video-src)',
            '.video-player::attr(data-src)',
            '.video-embed::attr(src)',
            'embed[src*="video"]::attr(src)'
        ]
    
    def extract_images_from_response(self, response: Response) -> List[str]:
        """从响应中提取所有图片URL"""
        images = []
        
        try:
            # 使用各种选择器提取图片
            for selector in self.image_selectors:
                urls = response.css(selector).getall()
                for url in urls:
                    if url:
                        # 处理背景图片样式
                        if 'background-image' in url:
                            url = self._extract_url_from_style(url)
                        
                        # 处理srcset属性
                        if 'srcset' in selector.lower():
                            urls_from_srcset = self._parse_srcset(url)
                            images.extend(urls_from_srcset)
                        else:
                            images.append(url)
            
            # 去重并转换为绝对URL
            unique_images = list(set(images))
            absolute_images = []
            
            for img_url in unique_images:
                if img_url:
                    # 转换为绝对URL
                    absolute_url = response.urljoin(img_url.strip())
                    
                    # 验证图片URL
                    if self.validator.is_valid_image_url(absolute_url):
                        absolute_images.append(absolute_url)
            
            self.logger.info(f"从 {response.url} 提取到 {len(absolute_images)} 个有效图片")
            return absolute_images
            
        except Exception as e:
            self.logger.error(f"提取图片时出错: {e}")
            return []
    
    def extract_videos_from_response(self, response: Response) -> List[str]:
        """从响应中提取所有视频URL"""
        videos = []
        
        try:
            # 使用各种选择器提取视频
            for selector in self.video_selectors:
                urls = response.css(selector).getall()
                for url in urls:
                    if url:
                        videos.append(url)
            
            # 去重并转换为绝对URL
            unique_videos = list(set(videos))
            absolute_videos = []
            
            for video_url in unique_videos:
                if video_url:
                    # 转换为绝对URL
                    absolute_url = response.urljoin(video_url.strip())
                    
                    # 验证视频URL
                    if self.validator.is_valid_video_url(absolute_url):
                        absolute_videos.append(absolute_url)
            
            self.logger.info(f"从 {response.url} 提取到 {len(absolute_videos)} 个有效视频")
            return absolute_videos
            
        except Exception as e:
            self.logger.error(f"提取视频时出错: {e}")
            return []
    
    def extract_all_media(self, response: Response) -> Dict[str, List[str]]:
        """提取所有媒体内容"""
        return {
            'images': self.extract_images_from_response(response),
            'videos': self.extract_videos_from_response(response),
            'total_media': 0  # 将在下面计算
        }
    
    def _extract_url_from_style(self, style_text: str) -> str:
        """从CSS样式中提取URL"""
        url_pattern = r'url\(["\']?([^"\']+)["\']?\)'
        match = re.search(url_pattern, style_text)
        return match.group(1) if match else ''
    
    def _parse_srcset(self, srcset: str) -> List[str]:
        """解析srcset属性中的URL"""
        urls = []
        if srcset:
            # srcset格式: "url1 1x, url2 2x" 或 "url1 100w, url2 200w"
            parts = srcset.split(',')
            for part in parts:
                url = part.strip().split()[0]  # 取第一部分作为URL
                if url:
                    urls.append(url)
        return urls
    
    def filter_high_quality_images(self, image_urls: List[str]) -> List[str]:
        """筛选高质量图片（基于URL模式）"""
        high_quality = []
        quality_indicators = [
            'hd', 'high', 'large', 'original', 'full', 'big',
            '1080', '720', '2k', '4k', 'retina'
        ]
        
        for url in image_urls:
            url_lower = url.lower()
            if any(indicator in url_lower for indicator in quality_indicators):
                high_quality.append(url)
        
        # 如果没有高质量指标，返回原列表
        return high_quality if high_quality else image_urls
    
    def prioritize_media_by_context(self, response: Response, media_dict: Dict) -> Dict:
        """根据上下文优先排序媒体"""
        # 获取页面标题用于相关性判断
        page_title = response.css('title::text').get('').lower()
        
        # 对图片进行优先级排序
        if media_dict.get('images'):
            prioritized_images = []
            other_images = []
            
            for img_url in media_dict['images']:
                img_lower = img_url.lower()
                # 检查是否与页面标题相关
                title_words = page_title.split()
                if any(word in img_lower for word in title_words if len(word) > 3):
                    prioritized_images.append(img_url)
                else:
                    other_images.append(img_url)
            
            # 合并列表，优先级高的在前
            media_dict['images'] = prioritized_images + other_images
        
        # 计算总媒体数量
        media_dict['total_media'] = (
            len(media_dict.get('images', [])) + 
            len(media_dict.get('videos', []))
        )
        
        return media_dict