"""
File validation module for image and video files before Telegram upload.
"""
import os
from pathlib import Path
from typing import Dict, List, Set, Any


class FileValidator:
    """Validator for image and video files before Telegram upload."""
    
    def __init__(self):
        """Initialize file validator with supported formats and size limits."""
        self.supported_image_extensions: Set[str] = {
            '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'
        }
        self.supported_video_extensions: Set[str] = {
            '.mp4', '.avi', '.mkv', '.mov', '.webm', '.flv'
        }
        self.max_file_size: int = 50 * 1024 * 1024  # 50MB
    
    def is_supported_image_extension(self, file_path: str) -> bool:
        """
        Check if file has a supported image extension.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if extension is supported, False otherwise
        """
        file_extension = Path(file_path).suffix.lower()
        return file_extension in self.supported_image_extensions
    
    def is_supported_video_extension(self, file_path: str) -> bool:
        """
        Check if file has a supported video extension.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if extension is supported, False otherwise
        """
        file_extension = Path(file_path).suffix.lower()
        return file_extension in self.supported_video_extensions
    
    def check_file_size(self, file_path: str) -> bool:
        """
        Check if file size is within acceptable limits.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if file size is acceptable, False otherwise
        """
        try:
            file_size = os.path.getsize(file_path)
            return file_size <= self.max_file_size
        except (OSError, FileNotFoundError):
            return False
    
    def validate_image_file(self, file_path: str) -> Dict[str, Any]:
        """
        Validate image file for Telegram upload.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Dictionary with validation results
        """
        result = {
            'file_type': 'image',
            'extension': Path(file_path).suffix.lower(),
            'errors': []
        }
        
        # Check if file exists
        if not os.path.exists(file_path):
            result['is_valid'] = False
            result['errors'].append('File does not exist')
            return result
        
        # Check extension
        if not self.is_supported_image_extension(file_path):
            result['is_valid'] = False
            result['errors'].append('Unsupported image format')
        
        # Check file size
        if not self.check_file_size(file_path):
            result['is_valid'] = False
            result['errors'].append('File size exceeds maximum limit of 50MB')
        
        # Add file size info
        try:
            result['size'] = os.path.getsize(file_path)
        except (OSError, FileNotFoundError):
            result['size'] = 0
        
        # Set overall validation result
        result['is_valid'] = len(result['errors']) == 0
        
        return result
    
    def validate_video_file(self, file_path: str) -> Dict[str, Any]:
        """
        Validate video file for Telegram upload.
        
        Args:
            file_path: Path to the video file
            
        Returns:
            Dictionary with validation results
        """
        result = {
            'file_type': 'video',
            'extension': Path(file_path).suffix.lower(),
            'errors': []
        }
        
        # Check if file exists
        if not os.path.exists(file_path):
            result['is_valid'] = False
            result['errors'].append('File does not exist')
            return result
        
        # Check extension
        if not self.is_supported_video_extension(file_path):
            result['is_valid'] = False
            result['errors'].append('Unsupported video format')
        
        # Check file size
        if not self.check_file_size(file_path):
            result['is_valid'] = False
            result['errors'].append('File size exceeds maximum limit of 50MB')
        
        # Add file size info
        try:
            result['size'] = os.path.getsize(file_path)
        except (OSError, FileNotFoundError):
            result['size'] = 0
        
        # Set overall validation result
        result['is_valid'] = len(result['errors']) == 0
        
        return result
    
    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """
        Validate any media file (auto-detect type).
        
        Args:
            file_path: Path to the media file
            
        Returns:
            Dictionary with validation results
        """
        if self.is_supported_image_extension(file_path):
            return self.validate_image_file(file_path)
        elif self.is_supported_video_extension(file_path):
            return self.validate_video_file(file_path)
        else:
            return {
                'is_valid': False,
                'file_type': 'unknown',
                'extension': Path(file_path).suffix.lower(),
                'errors': ['Unsupported file format']
            }