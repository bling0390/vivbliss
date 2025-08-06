import re
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional
from scrapy.http import Response
from vivbliss_scraper.items import VivblissMediaItem


class MediaExtractor:
    """Extract media URLs from web pages"""
    
    # Supported image formats
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
    
    # Supported video formats
    VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mkv', '.mov', '.webm', '.flv'}
    
    def extract_image_urls(self, response: Response, min_width: int = 0, min_height: int = 0) -> List[str]:
        """Extract image URLs from various sources in the HTML"""
        urls = set()
        
        # Extract from img tags
        for img in response.css('img'):
            # Try different attributes
            src = (img.attrib.get('src') or 
                   img.attrib.get('data-src') or 
                   img.attrib.get('data-lazy-src'))
            if src:
                # Filter by size if specified
                if min_width > 0 or min_height > 0:
                    width_attr = img.attrib.get('width')
                    height_attr = img.attrib.get('height')
                    
                    # Only filter if both dimensions are specified and too small
                    if width_attr and height_attr:
                        width = int(width_attr)
                        height = int(height_attr)
                        if width < min_width or height < min_height:
                            continue
                    # If no size attributes, assume image might be large enough
                
                urls.add(response.urljoin(src))
        
        # Return as sorted list
        return sorted(list(urls))
    
    def extract_video_urls(self, response: Response) -> List[str]:
        """Extract video URLs from video tags and sources"""
        urls = set()
        
        # Extract from video tags
        for video in response.css('video'):
            # Direct src attribute
            src = video.attrib.get('src')
            if src:
                urls.add(response.urljoin(src))
            
            # Source elements within video
            for source in video.css('source'):
                src = source.attrib.get('src')
                if src:
                    urls.add(response.urljoin(src))
        
        return sorted(list(urls))
    
    def extract_embedded_media_urls(self, response: Response) -> List[str]:
        """Extract media URLs from iframe embeds"""
        urls = []
        
        for iframe in response.css('iframe'):
            src = iframe.attrib.get('src', '')
            if any(provider in src for provider in ['youtube.com', 'vimeo.com', 'player.']):
                urls.append(src)
        
        return urls
    
    def extract_background_image_urls(self, response: Response) -> List[str]:
        """Extract URLs from CSS background images"""
        urls = set()
        
        # Extract from inline styles
        for element in response.css('*[style*="background"]'):
            style = element.attrib.get('style', '')
            # Extract URLs from background-image property
            url_matches = re.findall(r'url\(["\']?([^"\'()]+)["\']?\)', style)
            for url in url_matches:
                if self.is_valid_image_url(url):
                    urls.add(response.urljoin(url))
        
        # Extract from data-bg attributes
        for element in response.css('*[data-bg]'):
            bg_url = element.attrib.get('data-bg')
            if bg_url and self.is_valid_image_url(bg_url):
                urls.add(response.urljoin(bg_url))
        
        return sorted(list(urls))
    
    def is_valid_image_url(self, url: str) -> bool:
        """Check if URL points to a valid image format"""
        if not url or not isinstance(url, str):
            return False
        
        # Parse URL to get path
        parsed = urlparse(url.lower())
        path = parsed.path
        
        # Check if path ends with image extension
        return any(path.endswith(ext) for ext in self.IMAGE_EXTENSIONS)
    
    def is_valid_video_url(self, url: str) -> bool:
        """Check if URL points to a valid video format"""
        if not url or not isinstance(url, str):
            return False
        
        # Parse URL to get path
        parsed = urlparse(url.lower())
        path = parsed.path
        
        # Check if path ends with video extension
        return any(path.endswith(ext) for ext in self.VIDEO_EXTENSIONS)
    
    def extract_all_media(self, response: Response) -> Dict[str, List[str]]:
        """Extract all media URLs from a page"""
        # Extract different types of media
        image_urls = self.extract_image_urls(response)
        video_urls = self.extract_video_urls(response)
        background_images = self.extract_background_image_urls(response)
        embedded_media = self.extract_embedded_media_urls(response)
        
        # Combine image URLs and deduplicate
        all_image_urls = list(set(image_urls + background_images))
        
        # Combine video URLs with embedded media
        all_video_urls = list(set(video_urls + embedded_media))
        
        return {
            'image_urls': all_image_urls,
            'video_urls': all_video_urls
        }
    
    def create_media_item(self, response: Response) -> VivblissMediaItem:
        """Create a VivblissMediaItem from response"""
        # Get metadata from response
        meta = response.meta.get('item', {})
        
        # Extract all media
        media_data = self.extract_all_media(response)
        
        # Create item
        item = VivblissMediaItem()
        item['title'] = meta.get('title', '')
        item['source_url'] = meta.get('url', response.url)
        item['image_urls'] = media_data['image_urls']
        item['video_urls'] = media_data['video_urls']
        item['category'] = meta.get('category', '')
        item['date'] = meta.get('date', '')
        
        return item