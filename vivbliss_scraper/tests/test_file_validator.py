import pytest
import tempfile
import os
from pathlib import Path
from vivbliss_scraper.telegram.file_validator import FileValidator


class TestFileValidator:
    
    def setup_method(self):
        """Setup test files"""
        self.validator = FileValidator()
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test files
        self.valid_image_file = os.path.join(self.temp_dir, "test.jpg")
        self.valid_video_file = os.path.join(self.temp_dir, "test.mp4")
        self.invalid_file = os.path.join(self.temp_dir, "test.txt")
        self.large_file = os.path.join(self.temp_dir, "large.jpg")
        
        # Create actual test files
        with open(self.valid_image_file, 'wb') as f:
            f.write(b'\xFF\xD8\xFF\xE0')  # JPEG header
            f.write(b'0' * 1000)  # 1KB file
        
        with open(self.valid_video_file, 'wb') as f:
            f.write(b'\x00\x00\x00\x18ftypmp41')  # MP4 header
            f.write(b'0' * 1000)  # 1KB file
        
        with open(self.invalid_file, 'w') as f:
            f.write("This is a text file")
        
        # Create large file (over 50MB limit)
        with open(self.large_file, 'wb') as f:
            f.write(b'\xFF\xD8\xFF\xE0')  # JPEG header
            f.write(b'0' * (51 * 1024 * 1024))  # 51MB file
    
    def teardown_method(self):
        """Cleanup test files"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_supported_image_extensions(self):
        """Test that supported image extensions are correctly defined"""
        expected_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
        assert self.validator.supported_image_extensions == expected_extensions
    
    def test_supported_video_extensions(self):
        """Test that supported video extensions are correctly defined"""
        expected_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.webm', '.flv'}
        assert self.validator.supported_video_extensions == expected_extensions
    
    def test_max_file_size_limit(self):
        """Test that max file size is correctly set to 50MB"""
        assert self.validator.max_file_size == 50 * 1024 * 1024  # 50MB
    
    def test_is_supported_image_extension_valid(self):
        """Test valid image extension recognition"""
        assert self.validator.is_supported_image_extension(self.valid_image_file) is True
        assert self.validator.is_supported_image_extension("test.png") is True
        assert self.validator.is_supported_image_extension("TEST.JPEG") is True  # Case insensitive
    
    def test_is_supported_image_extension_invalid(self):
        """Test invalid image extension recognition"""
        assert self.validator.is_supported_image_extension(self.invalid_file) is False
        assert self.validator.is_supported_image_extension("test.pdf") is False
    
    def test_is_supported_video_extension_valid(self):
        """Test valid video extension recognition"""
        assert self.validator.is_supported_video_extension(self.valid_video_file) is True
        assert self.validator.is_supported_video_extension("test.avi") is True
        assert self.validator.is_supported_video_extension("TEST.MOV") is True  # Case insensitive
    
    def test_is_supported_video_extension_invalid(self):
        """Test invalid video extension recognition"""
        assert self.validator.is_supported_video_extension(self.invalid_file) is False
        assert self.validator.is_supported_video_extension("test.exe") is False
    
    def test_check_file_size_valid(self):
        """Test file size validation for valid files"""
        assert self.validator.check_file_size(self.valid_image_file) is True
        assert self.validator.check_file_size(self.valid_video_file) is True
    
    def test_check_file_size_too_large(self):
        """Test file size validation for oversized files"""
        assert self.validator.check_file_size(self.large_file) is False
    
    def test_check_file_size_nonexistent_file(self):
        """Test file size validation for non-existent files"""
        assert self.validator.check_file_size("/nonexistent/file.jpg") is False
    
    def test_validate_image_file_valid(self):
        """Test complete image file validation for valid file"""
        result = self.validator.validate_image_file(self.valid_image_file)
        assert result['is_valid'] is True
        assert result['file_type'] == 'image'
        assert result['extension'] == '.jpg'
        assert result['size'] > 0
        assert 'errors' not in result or len(result['errors']) == 0
    
    def test_validate_image_file_invalid_extension(self):
        """Test image file validation for invalid extension"""
        result = self.validator.validate_image_file(self.invalid_file)
        assert result['is_valid'] is False
        assert 'Unsupported image format' in result['errors']
    
    def test_validate_image_file_too_large(self):
        """Test image file validation for oversized file"""
        result = self.validator.validate_image_file(self.large_file)
        assert result['is_valid'] is False
        assert 'File size exceeds maximum limit of 50MB' in result['errors']
    
    def test_validate_video_file_valid(self):
        """Test complete video file validation for valid file"""
        result = self.validator.validate_video_file(self.valid_video_file)
        assert result['is_valid'] is True
        assert result['file_type'] == 'video'
        assert result['extension'] == '.mp4'
        assert result['size'] > 0
        assert 'errors' not in result or len(result['errors']) == 0
    
    def test_validate_video_file_invalid_extension(self):
        """Test video file validation for invalid extension"""
        result = self.validator.validate_video_file(self.invalid_file)
        assert result['is_valid'] is False
        assert 'Unsupported video format' in result['errors']
    
    def test_validate_any_media_file_image(self):
        """Test generic media file validation for image"""
        result = self.validator.validate_file(self.valid_image_file)
        assert result['is_valid'] is True
        assert result['file_type'] == 'image'
    
    def test_validate_any_media_file_video(self):
        """Test generic media file validation for video"""
        result = self.validator.validate_file(self.valid_video_file)
        assert result['is_valid'] is True
        assert result['file_type'] == 'video'
    
    def test_validate_any_media_file_invalid(self):
        """Test generic media file validation for invalid file"""
        result = self.validator.validate_file(self.invalid_file)
        assert result['is_valid'] is False
        assert 'Unsupported file format' in result['errors']