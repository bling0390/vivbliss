import pytest
from unittest.mock import Mock, patch, MagicMock
from vivbliss_scraper.pipelines import MongoDBPipeline
from vivbliss_scraper.items import VivblissItem


class TestMongoDBPipelineFunctionality:
    """Test suite for MongoDBPipeline functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mongo_uri = "mongodb://localhost:27017"
        self.mongo_db = "test_vivbliss_db"
        self.pipeline = MongoDBPipeline(self.mongo_uri, self.mongo_db)
        self.spider = Mock()
        self.spider.logger = Mock()
        
    def test_pipeline_initialization(self):
        """Test pipeline is initialized with correct parameters"""
        assert self.pipeline.mongo_uri == self.mongo_uri
        assert self.pipeline.mongo_db == self.mongo_db
        assert self.pipeline.collection_name == 'vivbliss_items'
        assert self.pipeline.max_retries == 3
        assert self.pipeline.client is None
        assert self.pipeline.db is None
        
    def test_from_crawler_factory_method(self):
        """Test the from_crawler class method creates pipeline correctly"""
        mock_crawler = Mock()
        mock_crawler.settings.get.side_effect = lambda key: {
            'MONGO_URI': 'mongodb://test:27017',
            'MONGO_DATABASE': 'test_db'
        }.get(key)
        
        pipeline = MongoDBPipeline.from_crawler(mock_crawler)
        
        assert pipeline.mongo_uri == 'mongodb://test:27017'
        assert pipeline.mongo_db == 'test_db'
        mock_crawler.settings.get.assert_any_call('MONGO_URI')
        mock_crawler.settings.get.assert_any_call('MONGO_DATABASE')
        
    @patch('vivbliss_scraper.pipelines.mongodb_pipeline.pymongo.MongoClient')
    def test_successful_connection(self, mock_mongo_client):
        """Test successful MongoDB connection"""
        # Mock successful connection
        mock_client = Mock()
        mock_admin = Mock()
        mock_admin.command.return_value = {'ok': 1}  # ping success
        mock_client.admin = mock_admin
        mock_mongo_client.return_value = mock_client
        
        result = self.pipeline.retry_connection(self.spider)
        
        assert result is True
        assert self.pipeline.client is not None
        assert self.pipeline.db is not None
        self.spider.logger.info.assert_called()
        
    @patch('vivbliss_scraper.pipelines.mongodb_pipeline.pymongo.MongoClient')
    def test_connection_retry_on_failure(self, mock_mongo_client):
        """Test connection retries on failure"""
        # Mock connection failures followed by success
        mock_client = Mock()
        mock_admin = Mock()
        mock_admin.command.side_effect = [Exception("Connection failed"), Exception("Connection failed"), {'ok': 1}]
        mock_client.admin = mock_admin
        mock_mongo_client.return_value = mock_client
        
        with patch('time.sleep'):  # Mock sleep to speed up test
            result = self.pipeline.retry_connection(self.spider)
            
        assert result is True
        # Should have made 3 attempts
        assert mock_admin.command.call_count == 3
        self.spider.logger.warning.assert_called()
        
    @patch('vivbliss_scraper.pipelines.mongodb_pipeline.pymongo.MongoClient')
    def test_connection_failure_after_max_retries(self, mock_mongo_client):
        """Test connection failure after exhausting max retries"""
        # Mock all connection attempts failing
        mock_client = Mock()
        mock_client.admin.command.side_effect = Exception("Connection failed")
        mock_mongo_client.return_value = mock_client
        
        with patch('time.sleep'):  # Mock sleep to speed up test
            result = self.pipeline.retry_connection(self.spider)
            
        assert result is False
        # Should have made max_retries attempts
        assert mock_client.admin.command.call_count == self.pipeline.max_retries
        self.spider.logger.error.assert_called_with("All MongoDB connection attempts failed")
        
    @patch('vivbliss_scraper.pipelines.mongodb_pipeline.pymongo.MongoClient')
    def test_open_spider_successful(self, mock_mongo_client):
        """Test successful spider opening"""
        # Mock successful connection
        mock_client = Mock()
        mock_admin = Mock()
        mock_admin.command.return_value = {'ok': 1}
        mock_client.admin = mock_admin
        mock_mongo_client.return_value = mock_client
        
        # Should not raise exception
        self.pipeline.open_spider(self.spider)
        
        assert self.pipeline.client is not None
        assert self.pipeline.db is not None
        
    @patch('vivbliss_scraper.pipelines.mongodb_pipeline.pymongo.MongoClient')
    def test_open_spider_failure(self, mock_mongo_client):
        """Test spider opening failure when connection fails"""
        # Mock connection failure
        mock_client = Mock()
        mock_client.admin.command.side_effect = Exception("Connection failed")
        mock_mongo_client.return_value = mock_client
        
        with patch('time.sleep'):  # Mock sleep to speed up test
            with pytest.raises(Exception, match="Could not connect to MongoDB after all retries"):
                self.pipeline.open_spider(self.spider)
                
    def test_close_spider(self):
        """Test spider closing cleans up client connection"""
        # Mock client
        mock_client = Mock()
        self.pipeline.client = mock_client
        
        self.pipeline.close_spider(self.spider)
        
        mock_client.close.assert_called_once()
        
    def test_close_spider_no_client(self):
        """Test spider closing when no client exists"""
        # No exception should be raised
        self.pipeline.close_spider(self.spider)
        
    @patch('vivbliss_scraper.pipelines.mongodb_pipeline.ItemAdapter')
    def test_process_item_success(self, mock_item_adapter):
        """Test successful item processing"""
        # Setup mocks using MagicMock to support __getitem__
        mock_db = MagicMock()
        mock_collection = Mock()
        mock_db.__getitem__.return_value = mock_collection
        self.pipeline.db = mock_db
        
        mock_item_adapter.return_value.asdict.return_value = {'title': 'test item', 'url': 'http://test.com'}
        
        # Create test item
        item = VivblissItem()
        item['title'] = 'test item'
        item['url'] = 'http://test.com'
        
        result = self.pipeline.process_item(item, self.spider)
        
        # Verify item was inserted and returned
        assert result == item
        mock_collection.insert_one.assert_called_once()
        mock_item_adapter.assert_called_once_with(item)
        
    @patch('vivbliss_scraper.pipelines.mongodb_pipeline.ItemAdapter')
    @patch('vivbliss_scraper.pipelines.mongodb_pipeline.pymongo.MongoClient')
    def test_process_item_with_retry_on_error(self, mock_mongo_client, mock_item_adapter):
        """Test item processing with retry on database error"""
        # Setup mocks using MagicMock to support __getitem__
        mock_db = MagicMock()
        mock_collection = Mock()
        mock_db.__getitem__.return_value = mock_collection
        
        # First insert fails, then retry connection succeeds, then second insert succeeds
        mock_collection.insert_one.side_effect = [Exception("Insert failed"), None]
        
        # Mock successful retry connection
        mock_client = Mock()
        mock_admin = Mock()
        mock_admin.command.return_value = {'ok': 1}
        mock_client.admin = mock_admin
        mock_mongo_client.return_value = mock_client
        self.pipeline.db = mock_db
        
        mock_item_adapter.return_value.asdict.return_value = {'title': 'test item'}
        
        # Create test item
        item = VivblissItem()
        item['title'] = 'test item'
        
        result = self.pipeline.process_item(item, self.spider)
        
        # Verify retry was attempted and item was eventually processed
        assert result == item
        assert mock_collection.insert_one.call_count == 2
        self.spider.logger.error.assert_called()
        
    @patch('vivbliss_scraper.pipelines.mongodb_pipeline.ItemAdapter')
    @patch('vivbliss_scraper.pipelines.mongodb_pipeline.pymongo.MongoClient')
    def test_process_item_failure_after_retry(self, mock_mongo_client, mock_item_adapter):
        """Test item processing failure even after retry"""
        # Setup mocks using MagicMock to support __getitem__
        mock_db = MagicMock()
        mock_collection = Mock()
        mock_db.__getitem__.return_value = mock_collection
        
        # Both insert attempts fail
        mock_collection.insert_one.side_effect = Exception("Insert failed")
        
        # Mock failed retry connection
        mock_client = Mock()
        mock_client.admin.command.side_effect = Exception("Connection failed")
        mock_mongo_client.return_value = mock_client
        self.pipeline.db = mock_db
        
        mock_item_adapter.return_value.asdict.return_value = {'title': 'test item'}
        
        # Create test item
        item = VivblissItem()
        item['title'] = 'test item'
        
        with patch('time.sleep'):  # Mock sleep to speed up test
            with pytest.raises(Exception):
                self.pipeline.process_item(item, self.spider)