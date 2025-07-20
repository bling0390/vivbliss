import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from apscheduler.schedulers.background import BackgroundScheduler
from vivbliss_scraper.scheduler.scheduler import SpiderScheduler
from vivbliss_scraper.scheduler.task_manager import ScheduledTask


class TestSpiderScheduler:
    """Integration tests for SpiderScheduler"""
    
    def setup_method(self):
        """Set up test environment"""
        self.scheduler = SpiderScheduler()
    
    def teardown_method(self):
        """Clean up after tests"""
        if self.scheduler.is_running():
            self.scheduler.shutdown()
    
    def test_scheduler_initialization(self):
        """Test scheduler initialization"""
        assert isinstance(self.scheduler.scheduler, BackgroundScheduler)
        assert self.scheduler.task_manager is not None
        assert not self.scheduler.is_running()
    
    def test_start_stop_scheduler(self):
        """Test starting and stopping scheduler"""
        # Start scheduler
        self.scheduler.start()
        assert self.scheduler.is_running()
        
        # Stop scheduler
        self.scheduler.shutdown()
        assert not self.scheduler.is_running()
    
    def test_add_scheduled_spider(self):
        """Test adding a scheduled spider task"""
        task = self.scheduler.add_spider_task(
            task_id='test_spider_1',
            name='Test Spider Task',
            spider_name='vivbliss',
            cron_expression='0 10 * * *',
            description='Daily spider run at 10:00'
        )
        
        assert task is not None
        assert task.task_id == 'test_spider_1'
        assert task.name == 'Test Spider Task'
        assert task.spider_name == 'vivbliss'
        assert task.schedule_type == 'cron'
    
    def test_add_interval_spider_task(self):
        """Test adding an interval-based spider task"""
        task = self.scheduler.add_interval_spider_task(
            task_id='interval_spider_1',
            name='Interval Spider',
            spider_name='vivbliss',
            hours=2,
            minutes=30,
            spider_args={'custom_arg': 'value'}
        )
        
        assert task is not None
        assert task.schedule_type == 'interval'
        assert task.schedule_config['hours'] == 2
        assert task.schedule_config['minutes'] == 30
        assert task.spider_args == {'custom_arg': 'value'}
    
    def test_remove_spider_task(self):
        """Test removing a spider task"""
        # Add task
        task = self.scheduler.add_spider_task(
            task_id='remove_test',
            name='Task to Remove',
            spider_name='vivbliss',
            cron_expression='0 10 * * *'
        )
        
        # Remove task
        result = self.scheduler.remove_task('remove_test')
        assert result is True
        
        # Verify task is removed
        assert self.scheduler.get_task('remove_test') is None
    
    def test_list_all_tasks(self):
        """Test listing all scheduled tasks"""
        # Add multiple tasks
        self.scheduler.add_spider_task(
            task_id='task_1',
            name='Task 1',
            spider_name='spider1',
            cron_expression='0 10 * * *'
        )
        self.scheduler.add_spider_task(
            task_id='task_2',
            name='Task 2',
            spider_name='spider2',
            cron_expression='0 14 * * *'
        )
        
        tasks = self.scheduler.list_tasks()
        assert len(tasks) == 2
        assert any(t.task_id == 'task_1' for t in tasks)
        assert any(t.task_id == 'task_2' for t in tasks)
    
    def test_get_task_info(self):
        """Test getting task information"""
        task = self.scheduler.add_spider_task(
            task_id='info_test',
            name='Info Test Task',
            spider_name='vivbliss',
            cron_expression='30 14 * * 1-5',
            description='Weekday afternoon run'
        )
        
        task_info = self.scheduler.get_task_info('info_test')
        
        assert task_info is not None
        assert task_info['task_id'] == 'info_test'
        assert task_info['name'] == 'Info Test Task'
        assert task_info['spider_name'] == 'vivbliss'
        assert task_info['enabled'] is True
        assert task_info['description'] == 'Weekday afternoon run'
        assert 'next_run_time' in task_info
    
    @patch('vivbliss_scraper.scheduler.task_manager.CrawlerProcess')
    def test_spider_execution(self, mock_crawler_process):
        """Test that spider is executed on schedule"""
        mock_process = Mock()
        mock_crawler_process.return_value = mock_process
        
        # Start scheduler
        self.scheduler.start()
        
        # Add task that runs immediately
        task = self.scheduler.add_interval_spider_task(
            task_id='immediate_task',
            name='Immediate Task',
            spider_name='vivbliss',
            seconds=1
        )
        
        # Wait for execution
        time.sleep(2)
        
        # Verify spider was called
        mock_crawler_process.assert_called()
        mock_process.crawl.assert_called_with('vivbliss')
    
    def test_enable_disable_task(self):
        """Test enabling and disabling tasks"""
        task = self.scheduler.add_spider_task(
            task_id='toggle_test',
            name='Toggle Test',
            spider_name='vivbliss',
            cron_expression='0 10 * * *'
        )
        
        # Initially enabled
        assert task.enabled is True
        
        # Disable task
        result = self.scheduler.disable_task('toggle_test')
        assert result is True
        task_info = self.scheduler.get_task_info('toggle_test')
        assert task_info['enabled'] is False
        
        # Enable task
        result = self.scheduler.enable_task('toggle_test')
        assert result is True
        task_info = self.scheduler.get_task_info('toggle_test')
        assert task_info['enabled'] is True
    
    def test_update_task_schedule(self):
        """Test updating task schedule"""
        # Add initial task
        task = self.scheduler.add_spider_task(
            task_id='update_test',
            name='Update Test',
            spider_name='vivbliss',
            cron_expression='0 10 * * *'
        )
        
        # Update to new schedule
        updated_task = self.scheduler.update_task_schedule(
            task_id='update_test',
            cron_expression='0 14 * * *'
        )
        
        assert updated_task is not None
        task_info = self.scheduler.get_task_info('update_test')
        assert '14' in str(task_info.get('schedule', ''))
    
    def test_load_save_tasks(self):
        """Test loading and saving tasks configuration"""
        # Add some tasks
        self.scheduler.add_spider_task(
            task_id='persist_1',
            name='Persistent Task 1',
            spider_name='spider1',
            cron_expression='0 10 * * *'
        )
        self.scheduler.add_interval_spider_task(
            task_id='persist_2',
            name='Persistent Task 2',
            spider_name='spider2',
            hours=4
        )
        
        # Save tasks
        config = self.scheduler.export_tasks()
        assert len(config['tasks']) == 2
        
        # Create new scheduler and load tasks
        new_scheduler = SpiderScheduler()
        new_scheduler.import_tasks(config)
        
        # Verify tasks are loaded
        tasks = new_scheduler.list_tasks()
        assert len(tasks) == 2
        assert any(t.task_id == 'persist_1' for t in tasks)
        assert any(t.task_id == 'persist_2' for t in tasks)