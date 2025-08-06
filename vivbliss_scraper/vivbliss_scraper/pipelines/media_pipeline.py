import os
import hashlib
from typing import List, Tuple, Dict, Any, Optional
from urllib.parse import urlparse
from pathlib import Path

from scrapy import Spider
from scrapy.http import Request
from scrapy.exceptions import DropItem
from PIL import Image

from vivbliss_scraper.items import VivblissMediaItem


class MediaDownloadPipeline:
    """Pipeline for downloading images and videos"""
    
    def __init__(self, settings: dict):
        """Initialize pipeline with settings"""
        self.images_store = settings.get('IMAGES_STORE', 'images')
        self.files_store = settings.get('FILES_STORE', 'videos')
        self.images_min_width = settings.get('IMAGES_MIN_WIDTH', 0)
        self.images_min_height = settings.get('IMAGES_MIN_HEIGHT', 0)
        self.images_expires = settings.get('IMAGES_EXPIRES', 90)
        self.files_expires = settings.get('FILES_EXPIRES', 90)
        
        # Create directories if they don't exist
        Path(self.images_store).mkdir(parents=True, exist_ok=True)
        Path(self.files_store).mkdir(parents=True, exist_ok=True)
        
    @classmethod
    def from_crawler(cls, crawler):
        """Create pipeline instance from crawler"""
        return cls(crawler.settings)
    
    def process_item(self, item: VivblissMediaItem, spider: Spider) -> VivblissMediaItem:
        """Process media item for downloading"""
        if not isinstance(item, VivblissMediaItem):
            return item
            
        # Process images
        item = self.process_image_urls(item, spider)
        
        # Process videos
        item = self.process_video_urls(item, spider)
        
        return item
    
    def process_image_urls(self, item: VivblissMediaItem, spider: Spider) -> VivblissMediaItem:
        """Process image URLs for downloading"""
        if 'image_urls' in item and item['image_urls']:
            # Generate requests
            requests = list(self.get_media_requests(item, spider, 'image'))
            
            # Download images (simulated for now)
            results = []
            for request in requests:
                # In real implementation, this would download the image
                # For now, we'll simulate success
                result = (True, {
                    'url': request.url,
                    'path': self.file_path(request, item=item, media_type='image'),
                    'checksum': hashlib.md5(request.url.encode()).hexdigest()
                })
                results.append(result)
            
            # Process results
            item = self.item_completed(results, item, spider, 'image')
            
        return item
    
    def process_video_urls(self, item: VivblissMediaItem, spider: Spider) -> VivblissMediaItem:
        """Process video URLs for downloading"""
        if 'video_urls' in item and item['video_urls']:
            # Generate requests
            requests = list(self.get_media_requests(item, spider, 'video'))
            
            # Download videos (simulated for now)
            results = []
            for request in requests:
                # In real implementation, this would download the video
                # For now, we'll simulate success
                result = (True, {
                    'url': request.url,
                    'path': self.file_path(request, item=item, media_type='video'),
                    'checksum': hashlib.md5(request.url.encode()).hexdigest()
                })
                results.append(result)
            
            # Process results
            item = self.item_completed(results, item, spider, 'video')
            
        return item
    
    def get_media_requests(self, item: VivblissMediaItem, spider: Spider, media_type: str):
        """Generate download requests for media URLs"""
        url_field = f'{media_type}_urls'
        if url_field not in item:
            return
            
        # Deduplicate URLs
        seen_urls = set()
        for url in item[url_field]:
            if url not in seen_urls:
                seen_urls.add(url)
                request = Request(url)
                request.meta['media_type'] = media_type
                request.meta['item'] = item
                yield request
    
    def item_completed(self, results: List[Tuple[bool, Any]], item: VivblissMediaItem, 
                      spider: Spider, media_type: str) -> VivblissMediaItem:
        """Process download results"""
        field_name = f'{media_type}s'  # 'images' or 'videos'
        
        # Initialize fields if not present
        if field_name not in item:
            item[field_name] = []
        if 'download_errors' not in item:
            item['download_errors'] = []
            
        # Process results
        for success, result in results:
            if success:
                # Store successful download info
                item[field_name].append({
                    'url': result['url'],
                    'path': result['path'],
                    'checksum': result.get('checksum', '')
                })
            else:
                # Store error info
                item['download_errors'].append({
                    'url': getattr(result, 'url', 'unknown'),
                    'error': str(result),
                    'media_type': media_type
                })
                
        return item
    
    def file_path(self, request: Request, item: VivblissMediaItem = None, 
                  media_type: str = 'image') -> str:
        """Generate file path for downloaded media"""
        # Get URL path
        url_path = urlparse(request.url).path
        filename = os.path.basename(url_path)
        
        # Get category for organization
        category = 'uncategorized'
        if item and 'category' in item:
            category = item['category'] or 'uncategorized'
            # Sanitize category name
            category = "".join(c for c in category if c.isalnum() or c in (' ', '-', '_')).rstrip()
            category = category.replace(' ', '_')
        
        # Build path
        media_dir = 'images' if media_type == 'image' else 'videos'
        return os.path.join(media_dir, category, filename)
    
    def check_image_size(self, image_path: str) -> bool:
        """Check if image meets minimum size requirements"""
        try:
            img = Image.open(image_path)
            width, height = img.size
            img.close()
            return (width >= self.images_min_width and 
                   height >= self.images_min_height)
        except Exception:
            return True  # If we can't check, assume it's OK
    
    def store_download_info(self, item: VivblissMediaItem, url: str, path: str, 
                           media_type: str, checksum: str, size: int = 0):
        """Store download information in item"""
        field_name = f'{media_type}s'
        
        if field_name not in item:
            item[field_name] = []
            
        item[field_name].append({
            'url': url,
            'path': path,
            'checksum': checksum,
            'size': size
        })