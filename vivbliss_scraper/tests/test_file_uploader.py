import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock, call
from vivbliss_scraper.telegram.file_uploader import FileUploader


class TestFileUploader:
    
    def setup_method(self):
        """Setup test environment"""
        self.mock_client = AsyncMock()
        self.uploader = FileUploader(self.mock_client)
        self.test_chat_id = -1001234567890
        
        # Create test files
        self.temp_dir = tempfile.mkdtemp()
        self.test_image = os.path.join(self.temp_dir, "test.jpg")
        self.test_video = os.path.join(self.temp_dir, "test.mp4")
        
        with open(self.test_image, 'wb') as f:
            f.write(b'\xFF\xD8\xFF\xE0')  # JPEG header
            f.write(b'0' * 1000)  # 1KB file
        
        with open(self.test_video, 'wb') as f:
            f.write(b'\x00\x00\x00\x18ftypmp41')  # MP4 header
            f.write(b'0' * 1000)  # 1KB file
    
    def teardown_method(self):
        """Cleanup test files"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_init_with_client(self):
        """Test FileUploader initialization with client"""
        uploader = FileUploader(self.mock_client)
        assert uploader.client == self.mock_client
        assert uploader.max_retries == 3
        assert uploader.retry_delay == 1
    
    def test_init_with_custom_retry_settings(self):
        """Test FileUploader initialization with custom retry settings"""
        uploader = FileUploader(
            self.mock_client, 
            max_retries=5, 
            retry_delay=2
        )
        assert uploader.max_retries == 5
        assert uploader.retry_delay == 2
    
    @pytest.mark.asyncio
    async def test_upload_image_success(self):
        """Test successful image upload"""
        self.mock_client.send_photo.return_value = Mock(
            message_id=123,
            photo=Mock(file_id="test_file_id")
        )
        
        result = await self.uploader.upload_image(
            chat_id=self.test_chat_id,
            file_path=self.test_image,
            caption="Test caption"
        )
        
        assert result['success'] is True
        assert result['message_id'] == 123
        assert result['file_id'] == "test_file_id"
        assert result['file_type'] == 'image'
        
        self.mock_client.send_photo.assert_called_once_with(
            chat_id=self.test_chat_id,
            photo=self.test_image,
            caption="Test caption"
        )
    
    @pytest.mark.asyncio
    async def test_upload_image_file_not_found(self):
        """Test image upload with non-existent file"""
        result = await self.uploader.upload_image(
            chat_id=self.test_chat_id,
            file_path="/nonexistent/file.jpg"
        )
        
        assert result['success'] is False
        assert 'File not found' in result['error']
        self.mock_client.send_photo.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_upload_image_with_retry_on_failure(self):
        """Test image upload retry mechanism on failure"""
        self.mock_client.send_photo.side_effect = [
            Exception("Network error"),
            Exception("Timeout"),
            Mock(message_id=123, photo=Mock(file_id="test_file_id"))
        ]
        
        result = await self.uploader.upload_image(
            chat_id=self.test_chat_id,
            file_path=self.test_image
        )
        
        assert result['success'] is True
        assert result['attempts'] == 3
        assert self.mock_client.send_photo.call_count == 3
    
    @pytest.mark.asyncio
    async def test_upload_image_retry_exhausted(self):
        """Test image upload when all retries are exhausted"""
        self.mock_client.send_photo.side_effect = Exception("Persistent error")
        
        result = await self.uploader.upload_image(
            chat_id=self.test_chat_id,
            file_path=self.test_image
        )
        
        assert result['success'] is False
        assert 'Persistent error' in result['error']
        assert result['attempts'] == 3
        assert self.mock_client.send_photo.call_count == 3
    
    @pytest.mark.asyncio
    async def test_upload_video_success(self):
        """Test successful video upload"""
        self.mock_client.send_video.return_value = Mock(
            message_id=456,
            video=Mock(file_id="video_file_id")
        )
        
        result = await self.uploader.upload_video(
            chat_id=self.test_chat_id,
            file_path=self.test_video,
            caption="Video caption"
        )
        
        assert result['success'] is True
        assert result['message_id'] == 456
        assert result['file_id'] == "video_file_id"
        assert result['file_type'] == 'video'
        
        self.mock_client.send_video.assert_called_once_with(
            chat_id=self.test_chat_id,
            video=self.test_video,
            caption="Video caption"
        )
    
    @pytest.mark.asyncio
    async def test_upload_video_file_not_found(self):
        """Test video upload with non-existent file"""
        result = await self.uploader.upload_video(
            chat_id=self.test_chat_id,
            file_path="/nonexistent/video.mp4"
        )
        
        assert result['success'] is False
        assert 'File not found' in result['error']
        self.mock_client.send_video.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_upload_file_auto_detect_image(self):
        """Test automatic file type detection for image"""
        self.mock_client.send_photo.return_value = Mock(
            message_id=123,
            photo=Mock(file_id="test_file_id")
        )
        
        result = await self.uploader.upload_file(
            chat_id=self.test_chat_id,
            file_path=self.test_image
        )
        
        assert result['success'] is True
        assert result['file_type'] == 'image'
        self.mock_client.send_photo.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_upload_file_auto_detect_video(self):
        """Test automatic file type detection for video"""
        self.mock_client.send_video.return_value = Mock(
            message_id=456,
            video=Mock(file_id="video_file_id")
        )
        
        result = await self.uploader.upload_file(
            chat_id=self.test_chat_id,
            file_path=self.test_video
        )
        
        assert result['success'] is True
        assert result['file_type'] == 'video'
        self.mock_client.send_video.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_upload_file_unsupported_format(self):
        """Test upload of unsupported file format"""
        unsupported_file = os.path.join(self.temp_dir, "test.txt")
        with open(unsupported_file, 'w') as f:
            f.write("Text content")
        
        result = await self.uploader.upload_file(
            chat_id=self.test_chat_id,
            file_path=unsupported_file
        )
        
        assert result['success'] is False
        assert 'Unsupported file format' in result['error']
    
    @pytest.mark.asyncio
    async def test_upload_multiple_files_success(self):
        """Test batch upload of multiple files"""
        self.mock_client.send_photo.return_value = Mock(
            message_id=123, photo=Mock(file_id="img_id")
        )
        self.mock_client.send_video.return_value = Mock(
            message_id=456, video=Mock(file_id="vid_id")
        )
        
        files = [self.test_image, self.test_video]
        results = await self.uploader.upload_multiple_files(
            chat_id=self.test_chat_id,
            file_paths=files
        )
        
        assert len(results) == 2
        assert all(result['success'] for result in results)
        assert results[0]['file_type'] == 'image'
        assert results[1]['file_type'] == 'video'
    
    @pytest.mark.asyncio
    async def test_upload_multiple_files_partial_failure(self):
        """Test batch upload with some failures"""
        self.mock_client.send_photo.return_value = Mock(
            message_id=123, photo=Mock(file_id="img_id")
        )
        
        files = [self.test_image, "/nonexistent/file.jpg"]
        results = await self.uploader.upload_multiple_files(
            chat_id=self.test_chat_id,
            file_paths=files
        )
        
        assert len(results) == 2
        assert results[0]['success'] is True
        assert results[1]['success'] is False
    
    @pytest.mark.asyncio
    async def test_get_upload_progress_tracking(self):
        """Test upload progress tracking functionality"""
        files = [self.test_image, self.test_video]
        
        self.mock_client.send_photo.return_value = Mock(
            message_id=123, photo=Mock(file_id="img_id")
        )
        self.mock_client.send_video.return_value = Mock(
            message_id=456, video=Mock(file_id="vid_id")
        )
        
        progress_callback = Mock()
        
        results = await self.uploader.upload_multiple_files(
            chat_id=self.test_chat_id,
            file_paths=files,
            progress_callback=progress_callback
        )
        
        # Verify progress callback was called
        assert progress_callback.call_count >= 2  # At least called for completion
        assert all(result['success'] for result in results)