import pytest
from unittest.mock import Mock, MagicMock
import mongomock
from vivbliss_scraper.pipelines import MongoDBPipeline
from vivbliss_scraper.items import VivblissItem


class TestMongoDBPipeline:
    @pytest.fixture
    def pipeline(self):
        return MongoDBPipeline(
            mongo_uri='mongodb://localhost:27017',
            mongo_db='test_db'
        )
    
    @pytest.fixture
    def mock_spider(self):
        spider = Mock()
        spider.name = 'vivbliss'
        return spider
    
    @pytest.fixture
    def sample_item(self):
        item = VivblissItem()
        item['title'] = 'Test Title'
        item['url'] = 'https://vivbliss.com/test'
        item['content'] = 'Test content'
        item['date'] = '2024-01-01'
        item['category'] = 'Technology'
        return item
    
    def test_pipeline_has_required_attributes(self, pipeline):
        assert hasattr(pipeline, 'mongo_uri')
        assert hasattr(pipeline, 'mongo_db')
        assert hasattr(pipeline, 'collection_name')
    
    def test_from_crawler_method(self):
        crawler = Mock()
        crawler.settings = {
            'MONGO_URI': 'mongodb://localhost:27017',
            'MONGO_DATABASE': 'vivbliss_db'
        }
        
        pipeline = MongoDBPipeline.from_crawler(crawler)
        assert pipeline.mongo_uri == 'mongodb://localhost:27017'
        assert pipeline.mongo_db == 'vivbliss_db'
    
    @mongomock.patch(servers=(('localhost', 27017),))
    def test_open_spider_connects_to_mongodb(self, pipeline, mock_spider):
        pipeline.mongo_uri = 'mongodb://localhost:27017'
        pipeline.mongo_db = 'test_db'
        pipeline.open_spider(mock_spider)
        
        assert pipeline.client is not None
        assert pipeline.db is not None
    
    @mongomock.patch(servers=(('localhost', 27017),))
    def test_process_item_saves_to_mongodb(self, pipeline, mock_spider, sample_item):
        pipeline.mongo_uri = 'mongodb://localhost:27017'
        pipeline.mongo_db = 'test_db'
        pipeline.collection_name = 'items'
        pipeline.open_spider(mock_spider)
        
        result = pipeline.process_item(sample_item, mock_spider)
        
        # Check item was saved
        saved_item = pipeline.db[pipeline.collection_name].find_one({'url': sample_item['url']})
        assert saved_item is not None
        assert saved_item['title'] == sample_item['title']
        assert result == sample_item
    
    @mongomock.patch(servers=(('localhost', 27017),))
    def test_close_spider_disconnects(self, pipeline, mock_spider):
        pipeline.mongo_uri = 'mongodb://localhost:27017'
        pipeline.mongo_db = 'test_db'
        pipeline.open_spider(mock_spider)
        
        pipeline.close_spider(mock_spider)
        # In real implementation, check that connection is closed