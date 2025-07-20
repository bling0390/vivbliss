import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from vivbliss_scraper.scheduler.task_manager import TaskManager, ScheduledTask


class TestScheduledTask:
    """Test cases for ScheduledTask model"""
    
    def test_scheduled_task_creation(self):
        """Test creating a scheduled task"""
        task = ScheduledTask(
            task_id='test_task_1',
            name='Test Spider Run',
            spider_name='vivbliss',
            schedule_type='cron',
            schedule_config={'hour': 10, 'minute': 30},
            enabled=True,
            description='Daily spider run at 10:30'
        )
        
        assert task.task_id == 'test_task_1'
        assert task.name == 'Test Spider Run'
        assert task.spider_name == 'vivbliss'
        assert task.schedule_type == 'cron'
        assert task.schedule_config == {'hour': 10, 'minute': 30}
        assert task.enabled is True
        assert task.description == 'Daily spider run at 10:30'
    
    def test_scheduled_task_with_spider_args(self):
        """Test scheduled task with spider arguments"""
        task = ScheduledTask(
            task_id='test_task_2',
            name='Test with Args',
            spider_name='vivbliss',
            schedule_type='interval',
            schedule_config={'hours': 2},
            spider_args={'start_urls': ['https://example.com']},
            spider_settings={'DOWNLOAD_DELAY': 2}
        )
        
        assert task.spider_args == {'start_urls': ['https://example.com']}
        assert task.spider_settings == {'DOWNLOAD_DELAY': 2}
    
    def test_invalid_schedule_type(self):
        """Test that invalid schedule type raises ValueError"""
        with pytest.raises(ValueError, match="Invalid schedule type"):
            ScheduledTask(
                task_id='invalid',
                name='Invalid Task',
                spider_name='test',
                schedule_type='invalid_type',
                schedule_config={}
            )


class TestTaskManager:
    """Test cases for TaskManager"""
    
    def setup_method(self):
        """Set up test environment"""
        self.mock_scheduler = Mock()
        self.task_manager = TaskManager(self.mock_scheduler)
    
    def test_add_task(self):
        """Test adding a scheduled task"""
        task = ScheduledTask(
            task_id='task_1',
            name='Test Task',
            spider_name='vivbliss',
            schedule_type='interval',
            schedule_config={'hours': 1}
        )
        
        result = self.task_manager.add_task(task)
        
        assert result is True
        assert 'task_1' in self.task_manager.tasks
        assert self.task_manager.tasks['task_1'] == task
        self.mock_scheduler.add_job.assert_called_once()
    
    def test_add_duplicate_task(self):
        """Test adding duplicate task raises error"""
        task = ScheduledTask(
            task_id='task_1',
            name='Test Task',
            spider_name='vivbliss',
            schedule_type='interval',
            schedule_config={'hours': 1}
        )
        
        self.task_manager.add_task(task)
        
        with pytest.raises(ValueError, match="Task with ID .* already exists"):
            self.task_manager.add_task(task)
    
    def test_remove_task(self):
        """Test removing a scheduled task"""
        task = ScheduledTask(
            task_id='task_1',
            name='Test Task',
            spider_name='vivbliss',
            schedule_type='interval',
            schedule_config={'hours': 1}
        )
        
        self.task_manager.add_task(task)
        result = self.task_manager.remove_task('task_1')
        
        assert result is True
        assert 'task_1' not in self.task_manager.tasks
        self.mock_scheduler.remove_job.assert_called_once_with('task_1')
    
    def test_remove_nonexistent_task(self):
        """Test removing non-existent task returns False"""
        result = self.task_manager.remove_task('nonexistent')
        
        assert result is False
        self.mock_scheduler.remove_job.assert_not_called()
    
    def test_get_task(self):
        """Test getting a task by ID"""
        task = ScheduledTask(
            task_id='task_1',
            name='Test Task',
            spider_name='vivbliss',
            schedule_type='interval',
            schedule_config={'hours': 1}
        )
        
        self.task_manager.add_task(task)
        retrieved_task = self.task_manager.get_task('task_1')
        
        assert retrieved_task == task
    
    def test_get_all_tasks(self):
        """Test getting all tasks"""
        task1 = ScheduledTask(
            task_id='task_1',
            name='Task 1',
            spider_name='spider1',
            schedule_type='interval',
            schedule_config={'hours': 1}
        )
        task2 = ScheduledTask(
            task_id='task_2',
            name='Task 2',
            spider_name='spider2',
            schedule_type='cron',
            schedule_config={'hour': 10}
        )
        
        self.task_manager.add_task(task1)
        self.task_manager.add_task(task2)
        
        all_tasks = self.task_manager.get_all_tasks()
        
        assert len(all_tasks) == 2
        assert task1 in all_tasks
        assert task2 in all_tasks
    
    def test_update_task(self):
        """Test updating an existing task"""
        original_task = ScheduledTask(
            task_id='task_1',
            name='Original Task',
            spider_name='vivbliss',
            schedule_type='interval',
            schedule_config={'hours': 1}
        )
        
        self.task_manager.add_task(original_task)
        
        updated_task = ScheduledTask(
            task_id='task_1',
            name='Updated Task',
            spider_name='vivbliss',
            schedule_type='interval',
            schedule_config={'hours': 2}
        )
        
        result = self.task_manager.update_task(updated_task)
        
        assert result is True
        assert self.task_manager.tasks['task_1'].name == 'Updated Task'
        assert self.task_manager.tasks['task_1'].schedule_config == {'hours': 2}
        
        # Verify job was removed and re-added
        assert self.mock_scheduler.remove_job.call_count == 1
        assert self.mock_scheduler.add_job.call_count == 2
    
    def test_enable_disable_task(self):
        """Test enabling and disabling tasks"""
        task = ScheduledTask(
            task_id='task_1',
            name='Test Task',
            spider_name='vivbliss',
            schedule_type='interval',
            schedule_config={'hours': 1},
            enabled=True
        )
        
        self.task_manager.add_task(task)
        
        # Disable task
        result = self.task_manager.disable_task('task_1')
        assert result is True
        assert self.task_manager.tasks['task_1'].enabled is False
        self.mock_scheduler.pause_job.assert_called_once_with('task_1')
        
        # Enable task
        result = self.task_manager.enable_task('task_1')
        assert result is True
        assert self.task_manager.tasks['task_1'].enabled is True
        self.mock_scheduler.resume_job.assert_called_once_with('task_1')
    
    @patch('vivbliss_scraper.scheduler.task_manager.CrawlerProcess')
    def test_run_spider_task(self, mock_crawler_process):
        """Test running a spider task"""
        mock_process = Mock()
        mock_crawler_process.return_value = mock_process
        
        task = ScheduledTask(
            task_id='task_1',
            name='Test Task',
            spider_name='vivbliss',
            schedule_type='interval',
            schedule_config={'hours': 1},
            spider_args={'test_arg': 'value'},
            spider_settings={'DOWNLOAD_DELAY': 3}
        )
        
        self.task_manager._run_spider(task)
        
        mock_crawler_process.assert_called_once()
        mock_process.crawl.assert_called_once_with(
            'vivbliss',
            test_arg='value'
        )
        mock_process.start.assert_called_once()