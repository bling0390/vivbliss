import pytest
import sys
import subprocess
from unittest.mock import patch


class TestPILDependency:
    """Test suite for PIL/Pillow dependency requirements"""
    
    def test_pil_import_available(self):
        """Test that PIL can be imported successfully"""
        # This test should fail if PIL/Pillow is not installed
        try:
            from PIL import Image
            assert Image is not None
        except ImportError as e:
            pytest.fail(f"PIL/Pillow not available: {e}")
    
    def test_pil_image_functionality(self):
        """Test that PIL Image functionality works correctly"""
        from PIL import Image
        
        # Test that we can use Image.open (even with mocked file)
        assert hasattr(Image, 'open')
        assert callable(Image.open)
    
    def test_media_pipeline_pil_import(self):
        """Test that media pipeline can import PIL without errors"""
        # This will fail if PIL is not available for the media pipeline
        try:
            from vivbliss_scraper.pipelines.media_pipeline import MediaDownloadPipeline
            # Verify the pipeline class can be instantiated with minimal settings
            settings = {
                'IMAGES_STORE': 'test_images',
                'FILES_STORE': 'test_videos'
            }
            pipeline = MediaDownloadPipeline(settings)
            assert pipeline is not None
        except ImportError as e:
            if "PIL" in str(e) or "Pillow" in str(e):
                pytest.fail(f"MediaDownloadPipeline failed to import due to missing PIL: {e}")
            else:
                # Re-raise if it's a different import error
                raise
    
    def test_pil_in_requirements_txt(self):
        """Test that PIL/Pillow is listed in requirements.txt"""
        import os
        requirements_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'requirements.txt'
        )
        
        if not os.path.exists(requirements_path):
            pytest.fail("requirements.txt file not found")
        
        with open(requirements_path, 'r') as f:
            requirements_content = f.read().lower()
        
        # Check if PIL or Pillow is in requirements
        has_pillow = ('pillow' in requirements_content)
        has_pil = ('pil' in requirements_content and 'pillow' not in requirements_content)
        
        if not (has_pillow or has_pil):
            pytest.fail("PIL/Pillow dependency not found in requirements.txt")
    
    def test_media_pipeline_handles_missing_pil_gracefully(self):
        """Test that media pipeline handles PIL errors gracefully"""
        # This test ensures our code can handle PIL-related errors gracefully
        from vivbliss_scraper.pipelines.media_pipeline import MediaDownloadPipeline
        
        settings = {
            'IMAGES_STORE': 'test_images',
            'FILES_STORE': 'test_videos'
        }
        pipeline = MediaDownloadPipeline(settings)
        
        # Test with a non-existent file path - should return True due to exception handling
        result = pipeline.check_image_size('/fake/path/that/does/not/exist.jpg')
        assert result is True  # Should default to accepting images when PIL encounters errors
        
        # Test with an invalid file path - should also return True
        result = pipeline.check_image_size('')
        assert result is True