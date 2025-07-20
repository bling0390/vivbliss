"""
File uploader module for sending images and videos to Telegram using Pyrogram.
"""
import os
import asyncio
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from pyrogram import Client
from .file_validator import FileValidator


class FileUploader:
    """File uploader for sending media files to Telegram."""
    
    def __init__(self, client: Client, max_retries: int = 3, retry_delay: int = 1):
        """
        Initialize file uploader.
        
        Args:
            client: Pyrogram client instance
            max_retries: Maximum retry attempts for failed uploads
            retry_delay: Delay between retries in seconds
        """
        self.client = client
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.validator = FileValidator()
    
    async def upload_image(self, chat_id: int, file_path: str, caption: str = "") -> Dict[str, Any]:
        """
        Upload image file to Telegram.
        
        Args:
            chat_id: Telegram chat ID to send to
            file_path: Path to the image file
            caption: Optional caption for the image
            
        Returns:
            Dictionary with upload result
        """
        # Check if file exists
        if not os.path.exists(file_path):
            return {
                'success': False,
                'error': 'File not found',
                'file_type': 'image'
            }
        
        # Attempt upload with retries
        for attempt in range(1, self.max_retries + 1):
            try:
                message = await self.client.send_photo(
                    chat_id=chat_id,
                    photo=file_path,
                    caption=caption
                )
                
                return {
                    'success': True,
                    'message_id': message.message_id,
                    'file_id': message.photo.file_id,
                    'file_type': 'image',
                    'attempts': attempt
                }
                
            except Exception as e:
                if attempt == self.max_retries:
                    return {
                        'success': False,
                        'error': str(e),
                        'file_type': 'image',
                        'attempts': attempt
                    }
                
                # Wait before retrying
                await asyncio.sleep(self.retry_delay)
        
        return {
            'success': False,
            'error': 'Max retries exceeded',
            'file_type': 'image'
        }
    
    async def upload_video(self, chat_id: int, file_path: str, caption: str = "") -> Dict[str, Any]:
        """
        Upload video file to Telegram.
        
        Args:
            chat_id: Telegram chat ID to send to
            file_path: Path to the video file
            caption: Optional caption for the video
            
        Returns:
            Dictionary with upload result
        """
        # Check if file exists
        if not os.path.exists(file_path):
            return {
                'success': False,
                'error': 'File not found',
                'file_type': 'video'
            }
        
        # Attempt upload with retries
        for attempt in range(1, self.max_retries + 1):
            try:
                message = await self.client.send_video(
                    chat_id=chat_id,
                    video=file_path,
                    caption=caption
                )
                
                return {
                    'success': True,
                    'message_id': message.message_id,
                    'file_id': message.video.file_id,
                    'file_type': 'video',
                    'attempts': attempt
                }
                
            except Exception as e:
                if attempt == self.max_retries:
                    return {
                        'success': False,
                        'error': str(e),
                        'file_type': 'video',
                        'attempts': attempt
                    }
                
                # Wait before retrying
                await asyncio.sleep(self.retry_delay)
        
        return {
            'success': False,
            'error': 'Max retries exceeded',
            'file_type': 'video'
        }
    
    async def upload_file(self, chat_id: int, file_path: str, caption: str = "") -> Dict[str, Any]:
        """
        Auto-detect file type and upload accordingly.
        
        Args:
            chat_id: Telegram chat ID to send to
            file_path: Path to the media file
            caption: Optional caption for the file
            
        Returns:
            Dictionary with upload result
        """
        if self.validator.is_supported_image_extension(file_path):
            return await self.upload_image(chat_id, file_path, caption)
        elif self.validator.is_supported_video_extension(file_path):
            return await self.upload_video(chat_id, file_path, caption)
        else:
            return {
                'success': False,
                'error': 'Unsupported file format',
                'file_type': 'unknown'
            }
    
    async def upload_multiple_files(
        self, 
        chat_id: int, 
        file_paths: List[str], 
        progress_callback: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Upload multiple files to Telegram.
        
        Args:
            chat_id: Telegram chat ID to send to
            file_paths: List of file paths to upload
            progress_callback: Optional callback for progress tracking
            
        Returns:
            List of upload results for each file
        """
        results = []
        total_files = len(file_paths)
        
        for i, file_path in enumerate(file_paths):
            # Call progress callback if provided
            if progress_callback:
                progress_callback(i, total_files, file_path)
            
            result = await self.upload_file(chat_id, file_path)
            results.append(result)
        
        # Final progress callback
        if progress_callback:
            progress_callback(total_files, total_files, "completed")
        
        return results