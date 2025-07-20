import pytest
from datetime import datetime, timedelta
from vivbliss_scraper.scheduler.config import SchedulerConfig


class TestSchedulerConfig:
    """Test cases for scheduler configuration"""
    
    def test_init_default_config(self):
        """Test SchedulerConfig initialization with defaults"""
        config = SchedulerConfig()
        
        assert config.timezone == 'UTC'
        assert config.job_store_type == 'memory'
        assert config.executor_type == 'threadpool'
        assert config.max_workers == 5
        assert config.misfire_grace_time == 60
    
    def test_init_custom_config(self):
        """Test SchedulerConfig initialization with custom values"""
        config = SchedulerConfig(
            timezone='Asia/Shanghai',
            job_store_type='mongodb',
            executor_type='processpool',
            max_workers=10,
            misfire_grace_time=120
        )
        
        assert config.timezone == 'Asia/Shanghai'
        assert config.job_store_type == 'mongodb'
        assert config.executor_type == 'processpool'
        assert config.max_workers == 10
        assert config.misfire_grace_time == 120
    
    def test_invalid_job_store_type(self):
        """Test that invalid job store type raises ValueError"""
        with pytest.raises(ValueError, match="Invalid job store type"):
            SchedulerConfig(job_store_type='invalid')
    
    def test_invalid_executor_type(self):
        """Test that invalid executor type raises ValueError"""
        with pytest.raises(ValueError, match="Invalid executor type"):
            SchedulerConfig(executor_type='invalid')
    
    def test_invalid_max_workers(self):
        """Test that invalid max workers raises ValueError"""
        with pytest.raises(ValueError, match="Max workers must be positive"):
            SchedulerConfig(max_workers=0)
    
    def test_get_job_store_config_memory(self):
        """Test getting job store configuration for memory store"""
        config = SchedulerConfig(job_store_type='memory')
        job_store_config = config.get_job_store_config()
        
        assert 'default' in job_store_config
        assert job_store_config['default']['type'] == 'memory'
    
    def test_get_job_store_config_mongodb(self):
        """Test getting job store configuration for MongoDB store"""
        config = SchedulerConfig(
            job_store_type='mongodb',
            mongodb_uri='mongodb://localhost:27017',
            mongodb_database='scheduler_db'
        )
        job_store_config = config.get_job_store_config()
        
        assert 'default' in job_store_config
        assert job_store_config['default']['type'] == 'mongodb'
        assert job_store_config['default']['client'] == 'mongodb://localhost:27017'
        assert job_store_config['default']['database'] == 'scheduler_db'
    
    def test_get_executor_config_threadpool(self):
        """Test getting executor configuration for threadpool"""
        config = SchedulerConfig(executor_type='threadpool', max_workers=8)
        executor_config = config.get_executor_config()
        
        assert 'default' in executor_config
        assert executor_config['default']['type'] == 'threadpool'
        assert executor_config['default']['max_workers'] == 8
    
    def test_get_executor_config_processpool(self):
        """Test getting executor configuration for processpool"""
        config = SchedulerConfig(executor_type='processpool', max_workers=4)
        executor_config = config.get_executor_config()
        
        assert 'default' in executor_config
        assert executor_config['default']['type'] == 'processpool'
        assert executor_config['default']['max_workers'] == 4
    
    def test_get_scheduler_config(self):
        """Test getting complete scheduler configuration"""
        config = SchedulerConfig(
            timezone='Europe/London',
            misfire_grace_time=30
        )
        scheduler_config = config.get_scheduler_config()
        
        assert scheduler_config['timezone'] == 'Europe/London'
        assert scheduler_config['misfire_grace_time'] == 30
        assert 'job_defaults' in scheduler_config
        assert scheduler_config['job_defaults']['coalesce'] is True
        assert scheduler_config['job_defaults']['max_instances'] == 3