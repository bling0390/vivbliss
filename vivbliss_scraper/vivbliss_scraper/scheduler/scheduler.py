"""
Main scheduler class for managing spider execution.
"""
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

from .config import SchedulerConfig
from .task_manager import TaskManager, ScheduledTask
from .cron_parser import CronParser


class SpiderScheduler:
    """Main scheduler for managing spider tasks"""
    
    def __init__(self, config: Optional[SchedulerConfig] = None):
        """
        Initialize spider scheduler.
        
        Args:
            config: SchedulerConfig instance (uses defaults if None)
        """
        self.config = config or SchedulerConfig()
        self.cron_parser = CronParser()
        self.logger = logging.getLogger(__name__)
        
        # Configure APScheduler
        jobstores = self.config.get_job_store_config()
        executors = self.config.get_executor_config()
        job_defaults = self.config.get_scheduler_config()
        
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults['job_defaults'],
            timezone=job_defaults['timezone']
        )
        
        self.task_manager = TaskManager(self.scheduler)
        self._running = False
    
    def start(self):
        """Start the scheduler"""
        if not self._running:
            self.scheduler.start()
            self._running = True
            self.logger.info("Spider scheduler started")
    
    def shutdown(self, wait: bool = True):
        """
        Shutdown the scheduler.
        
        Args:
            wait: Whether to wait for running jobs to complete
        """
        if self._running:
            self.scheduler.shutdown(wait=wait)
            self._running = False
            self.logger.info("Spider scheduler stopped")
    
    def is_running(self) -> bool:
        """Check if scheduler is running"""
        return self._running
    
    def add_spider_task(self, 
                       task_id: str,
                       name: str,
                       spider_name: str,
                       cron_expression: str,
                       description: str = "",
                       spider_args: Optional[Dict[str, Any]] = None,
                       spider_settings: Optional[Dict[str, Any]] = None,
                       enabled: bool = True) -> ScheduledTask:
        """
        Add a cron-based spider task.
        
        Args:
            task_id: Unique task identifier
            name: Human-readable task name
            spider_name: Name of the spider to run
            cron_expression: Cron expression for scheduling
            description: Task description
            spider_args: Arguments to pass to spider
            spider_settings: Custom settings for spider
            enabled: Whether task is enabled
            
        Returns:
            Created ScheduledTask instance
        """
        if not self.cron_parser.validate(cron_expression):
            raise ValueError(f"Invalid cron expression: {cron_expression}")
        
        schedule_config = self.cron_parser.parse(cron_expression)
        
        task = ScheduledTask(
            task_id=task_id,
            name=name,
            spider_name=spider_name,
            schedule_type='cron',
            schedule_config=schedule_config,
            description=description,
            spider_args=spider_args or {},
            spider_settings=spider_settings or {},
            enabled=enabled
        )
        
        if self.task_manager.add_task(task):
            return task
        else:
            raise RuntimeError(f"Failed to add task: {task_id}")
    
    def add_interval_spider_task(self,
                                task_id: str,
                                name: str,
                                spider_name: str,
                                weeks: int = 0,
                                days: int = 0,
                                hours: int = 0,
                                minutes: int = 0,
                                seconds: int = 0,
                                description: str = "",
                                spider_args: Optional[Dict[str, Any]] = None,
                                spider_settings: Optional[Dict[str, Any]] = None,
                                enabled: bool = True) -> ScheduledTask:
        """
        Add an interval-based spider task.
        
        Args:
            task_id: Unique task identifier
            name: Human-readable task name
            spider_name: Name of the spider to run
            weeks: Interval in weeks
            days: Interval in days
            hours: Interval in hours
            minutes: Interval in minutes
            seconds: Interval in seconds
            description: Task description
            spider_args: Arguments to pass to spider
            spider_settings: Custom settings for spider
            enabled: Whether task is enabled
            
        Returns:
            Created ScheduledTask instance
        """
        schedule_config = {}
        if weeks > 0:
            schedule_config['weeks'] = weeks
        if days > 0:
            schedule_config['days'] = days
        if hours > 0:
            schedule_config['hours'] = hours
        if minutes > 0:
            schedule_config['minutes'] = minutes
        if seconds > 0:
            schedule_config['seconds'] = seconds
        
        if not schedule_config:
            raise ValueError("At least one time interval must be specified")
        
        task = ScheduledTask(
            task_id=task_id,
            name=name,
            spider_name=spider_name,
            schedule_type='interval',
            schedule_config=schedule_config,
            description=description,
            spider_args=spider_args or {},
            spider_settings=spider_settings or {},
            enabled=enabled
        )
        
        if self.task_manager.add_task(task):
            return task
        else:
            raise RuntimeError(f"Failed to add task: {task_id}")
    
    def remove_task(self, task_id: str) -> bool:
        """Remove a scheduled task"""
        return self.task_manager.remove_task(task_id)
    
    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        """Get task by ID"""
        return self.task_manager.get_task(task_id)
    
    def list_tasks(self) -> List[ScheduledTask]:
        """List all scheduled tasks"""
        return self.task_manager.get_all_tasks()
    
    def enable_task(self, task_id: str) -> bool:
        """Enable a task"""
        return self.task_manager.enable_task(task_id)
    
    def disable_task(self, task_id: str) -> bool:
        """Disable a task"""
        return self.task_manager.disable_task(task_id)
    
    def update_task_schedule(self, task_id: str, cron_expression: str) -> Optional[ScheduledTask]:
        """
        Update task schedule.
        
        Args:
            task_id: Task ID to update
            cron_expression: New cron expression
            
        Returns:
            Updated task or None if not found
        """
        task = self.task_manager.get_task(task_id)
        if not task:
            return None
        
        if not self.cron_parser.validate(cron_expression):
            raise ValueError(f"Invalid cron expression: {cron_expression}")
        
        # Update schedule config
        task.schedule_config = self.cron_parser.parse(cron_expression)
        
        if self.task_manager.update_task(task):
            return task
        else:
            return None
    
    def get_task_info(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed task information.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task information dictionary or None
        """
        task = self.task_manager.get_task(task_id)
        if not task:
            return None
        
        # Get next run time from scheduler
        job = self.scheduler.get_job(task_id)
        next_run_time = getattr(job, 'next_run_time', None) if job else None
        
        return {
            'task_id': task.task_id,
            'name': task.name,
            'spider_name': task.spider_name,
            'schedule_type': task.schedule_type,
            'schedule': task.schedule_config,
            'enabled': task.enabled,
            'description': task.description,
            'spider_args': task.spider_args,
            'spider_settings': task.spider_settings,
            'created_at': task.created_at.isoformat(),
            'last_run': task.last_run.isoformat() if task.last_run else None,
            'next_run_time': next_run_time.isoformat() if next_run_time else None
        }
    
    def export_tasks(self) -> Dict[str, Any]:
        """
        Export all tasks configuration.
        
        Returns:
            Dictionary with tasks configuration
        """
        tasks_config = []
        for task in self.task_manager.get_all_tasks():
            task_config = {
                'task_id': task.task_id,
                'name': task.name,
                'spider_name': task.spider_name,
                'schedule_type': task.schedule_type,
                'schedule_config': task.schedule_config,
                'enabled': task.enabled,
                'description': task.description,
                'spider_args': task.spider_args,
                'spider_settings': task.spider_settings
            }
            tasks_config.append(task_config)
        
        return {
            'version': '1.0',
            'exported_at': datetime.now().isoformat(),
            'tasks': tasks_config
        }
    
    def import_tasks(self, config: Dict[str, Any]):
        """
        Import tasks configuration.
        
        Args:
            config: Tasks configuration dictionary
        """
        if 'tasks' not in config:
            raise ValueError("Invalid configuration: missing 'tasks' key")
        
        for task_config in config['tasks']:
            try:
                task = ScheduledTask(
                    task_id=task_config['task_id'],
                    name=task_config['name'],
                    spider_name=task_config['spider_name'],
                    schedule_type=task_config['schedule_type'],
                    schedule_config=task_config['schedule_config'],
                    enabled=task_config.get('enabled', True),
                    description=task_config.get('description', ''),
                    spider_args=task_config.get('spider_args', {}),
                    spider_settings=task_config.get('spider_settings', {})
                )
                
                self.task_manager.add_task(task)
                self.logger.info(f"Imported task: {task.task_id}")
                
            except Exception as e:
                self.logger.error(f"Failed to import task {task_config.get('task_id', 'unknown')}: {e}")
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """
        Get scheduler status information.
        
        Returns:
            Status information dictionary
        """
        return {
            'running': self.is_running(),
            'total_tasks': len(self.task_manager.tasks),
            'enabled_tasks': sum(1 for t in self.task_manager.tasks.values() if t.enabled),
            'disabled_tasks': sum(1 for t in self.task_manager.tasks.values() if not t.enabled),
            'pending_jobs': len(self.scheduler.get_jobs()) if self._running else 0,
            'timezone': self.config.timezone,
            'job_store_type': self.config.job_store_type
        }