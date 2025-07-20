import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, AsyncMock, patch
from vivbliss_scraper.telegram.config import TelegramConfig
from vivbliss_scraper.telegram.file_validator import FileValidator
from vivbliss_scraper.telegram.file_uploader import FileUploader


class TestTelegramIntegration:
    """Integration tests for the complete Telegram file upload workflow."""
    
    def setup_method(self):
        """Setup test environment"""
        self.config = TelegramConfig(
            api_id="12345",
            api_hash="test_hash",
            session_name="test_session"
        )
        self.validator = FileValidator()
        
        # Create test files
        self.temp_dir = tempfile.mkdtemp()
        self.test_image = os.path.join(self.temp_dir, "test.jpg")
        self.test_video = os.path.join(self.temp_dir, "test.mp4")
        self.invalid_file = os.path.join(self.temp_dir, "test.txt")
        
        with open(self.test_image, 'wb') as f:
            f.write(b'\xFF\xD8\xFF\xE0')  # JPEG header
            f.write(b'0' * 1000)  # 1KB file
        
        with open(self.test_video, 'wb') as f:
            f.write(b'\x00\x00\x00\x18ftypmp41')  # MP4 header
            f.write(b'0' * 1000)  # 1KB file
        
        with open(self.invalid_file, 'w') as f:
            f.write("Invalid file content")
    
    def teardown_method(self):
        """Cleanup test files"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @pytest.mark.asyncio
    async def test_complete_workflow_image_upload(self):
        """Test complete workflow from validation to upload for images"""
        # Step 1: Validate file
        validation_result = self.validator.validate_image_file(self.test_image)
        assert validation_result['is_valid'] is True
        
        # Step 2: Create mock client and uploader
        mock_client = AsyncMock()
        mock_client.send_photo.return_value = Mock(
            message_id=123,
            photo=Mock(file_id="test_file_id")
        )
        
        uploader = FileUploader(mock_client)
        
        # Step 3: Upload file
        upload_result = await uploader.upload_image(
            chat_id=-1001234567890,
            file_path=self.test_image,
            caption="Test image upload"
        )
        
        # Verify results
        assert upload_result['success'] is True
        assert upload_result['file_type'] == 'image'
        assert upload_result['message_id'] == 123
        
        mock_client.send_photo.assert_called_once_with(
            chat_id=-1001234567890,
            photo=self.test_image,
            caption="Test image upload"
        )
    
    @pytest.mark.asyncio
    async def test_batch_upload_workflow(self):
        """Test batch upload workflow with mixed file types"""
        mock_client = AsyncMock()
        mock_client.send_photo.return_value = Mock(
            message_id=123, photo=Mock(file_id="img_id")
        )
        mock_client.send_video.return_value = Mock(
            message_id=456, video=Mock(file_id="vid_id")
        )
        
        uploader = FileUploader(mock_client)
        
        # Test batch upload
        file_paths = [self.test_image, self.test_video, self.invalid_file]
        results = await uploader.upload_multiple_files(
            chat_id=-1001234567890,
            file_paths=file_paths
        )
        
        # Verify results
        assert len(results) == 3
        assert results[0]['success'] is True  # Image upload
        assert results[1]['success'] is True  # Video upload
        assert results[2]['success'] is False  # Invalid file