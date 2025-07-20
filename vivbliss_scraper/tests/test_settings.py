import pytest
from vivbliss_scraper import settings


class TestSettings:
    def test_bot_name_is_set(self):
        assert hasattr(settings, 'BOT_NAME')
        assert settings.BOT_NAME == 'vivbliss_scraper'
    
    def test_spider_modules_configured(self):
        assert hasattr(settings, 'SPIDER_MODULES')
        assert 'vivbliss_scraper.spiders' in settings.SPIDER_MODULES
    
    def test_pipelines_configured(self):
        assert hasattr(settings, 'ITEM_PIPELINES')
        assert 'vivbliss_scraper.pipelines.MongoDBPipeline' in settings.ITEM_PIPELINES
    
    def test_mongodb_settings(self):
        assert hasattr(settings, 'MONGO_URI')
        assert hasattr(settings, 'MONGO_DATABASE')
    
    def test_user_agent_configured(self):
        assert hasattr(settings, 'USER_AGENT')
        assert settings.USER_AGENT != ''
    
    def test_robotstxt_obey(self):
        assert hasattr(settings, 'ROBOTSTXT_OBEY')
        assert settings.ROBOTSTXT_OBEY is True
    
    def test_download_delay_configured(self):
        assert hasattr(settings, 'DOWNLOAD_DELAY')
        assert settings.DOWNLOAD_DELAY >= 1