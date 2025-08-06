import pytest
import sys
import os

class TestMongoDBPipelineImport:
    """Test suite for MongoDBPipeline import issues"""
    
    def test_import_mongodb_pipeline_from_pipelines_package(self):
        """Test that MongoDBPipeline can be imported from vivbliss_scraper.pipelines package"""
        # This should work according to settings.py configuration
        try:
            from vivbliss_scraper.pipelines import MongoDBPipeline
            assert MongoDBPipeline is not None
            assert hasattr(MongoDBPipeline, 'process_item')
            assert hasattr(MongoDBPipeline, 'open_spider') 
            assert hasattr(MongoDBPipeline, 'close_spider')
        except ImportError as e:
            pytest.fail(f"Failed to import MongoDBPipeline from pipelines package: {e}")
    
    def test_mongodb_pipeline_has_required_methods(self):
        """Test that MongoDBPipeline has all required pipeline methods"""
        from vivbliss_scraper.pipelines import MongoDBPipeline
        
        # Check required Scrapy pipeline methods
        assert callable(getattr(MongoDBPipeline, 'process_item', None))
        assert callable(getattr(MongoDBPipeline, 'open_spider', None))
        assert callable(getattr(MongoDBPipeline, 'close_spider', None))
        assert callable(getattr(MongoDBPipeline, 'from_crawler', None))
    
    def test_mongodb_pipeline_initialization(self):
        """Test that MongoDBPipeline can be instantiated properly"""
        from vivbliss_scraper.pipelines import MongoDBPipeline
        
        # Test initialization with mock parameters
        mongo_uri = "mongodb://localhost:27017"
        mongo_db = "test_db"
        
        pipeline = MongoDBPipeline(mongo_uri, mongo_db)
        assert pipeline.mongo_uri == mongo_uri
        assert pipeline.mongo_db == mongo_db
        assert pipeline.collection_name == 'vivbliss_items'
        assert pipeline.max_retries == 3
    
    def test_pipeline_import_path_consistency(self):
        """Test that the import path matches what's configured in settings.py"""
        # This test verifies that the import path in settings.py actually works
        settings_import_path = 'vivbliss_scraper.pipelines.MongoDBPipeline'
        
        # Simulate what Scrapy does when loading pipelines
        module_path, class_name = settings_import_path.rsplit('.', 1)
        
        try:
            module = __import__(module_path, fromlist=[class_name])
            pipeline_class = getattr(module, class_name)
            assert pipeline_class is not None
        except (ImportError, AttributeError) as e:
            pytest.fail(f"Settings.py import path '{settings_import_path}' is invalid: {e}")