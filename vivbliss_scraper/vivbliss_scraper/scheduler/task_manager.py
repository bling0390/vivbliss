"""
Task manager for handling scheduled spider tasks.
"""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


@dataclass
class ScheduledTask:
    """Represents a scheduled spider task"""
    
    task_id: str
    name: str
    spider_name: str
    schedule_type: str  # 'cron', 'interval', 'date'
    schedule_config: Dict[str, Any]
    enabled: bool = True
    description: str = ""
    spider_args: Optional[Dict[str, Any]] = None
    spider_settings: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate task after initialization"""
        valid_schedule_types = {'cron', 'interval', 'date'}
        if self.schedule_type not in valid_schedule_types:
            raise ValueError(f"Invalid schedule type: {self.schedule_type}. "
                           f"Valid types: {valid_schedule_types}")
        
        if self.spider_args is None:
            self.spider_args = {}
        
        if self.spider_settings is None:
            self.spider_settings = {}


class TaskManager:
    """Manages scheduled tasks for spider execution"""
    
    def __init__(self, scheduler):
        """
        Initialize task manager.
        
        Args:
            scheduler: APScheduler instance
        """
        self.scheduler = scheduler
        self.tasks: Dict[str, ScheduledTask] = {}
        self.logger = logging.getLogger(__name__)
    
    def add_task(self, task: ScheduledTask) -> bool:
        """
        Add a new scheduled task.
        
        Args:
            task: ScheduledTask instance
            
        Returns:
            True if task added successfully
            
        Raises:
            ValueError: If task ID already exists
        """
        if task.task_id in self.tasks:
            raise ValueError(f"Task with ID '{task.task_id}' already exists")
        
        try:
            # Add job to scheduler
            if task.schedule_type == 'cron':
                self.scheduler.add_job(
                    func=self._run_spider,
                    trigger='cron',
                    args=[task],
                    id=task.task_id,
                    name=task.name,
                    **task.schedule_config
                )
            elif task.schedule_type == 'interval':
                self.scheduler.add_job(
                    func=self._run_spider,
                    trigger='interval',
                    args=[task],
                    id=task.task_id,
                    name=task.name,
                    **task.schedule_config
                )
            elif task.schedule_type == 'date':
                self.scheduler.add_job(
                    func=self._run_spider,
                    trigger='date',
                    args=[task],
                    id=task.task_id,
                    name=task.name,
                    **task.schedule_config
                )
            
            self.tasks[task.task_id] = task
            self.logger.info(f"Added scheduled task: {task.task_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add task {task.task_id}: {e}")
            return False
    
    def remove_task(self, task_id: str) -> bool:
        """
        Remove a scheduled task.
        
        Args:
            task_id: ID of task to remove
            
        Returns:
            True if task removed successfully
        """
        if task_id not in self.tasks:
            return False
        
        try:
            self.scheduler.remove_job(task_id)
            del self.tasks[task_id]
            self.logger.info(f"Removed scheduled task: {task_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to remove task {task_id}: {e}")
            return False
    
    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[ScheduledTask]:
        """Get all scheduled tasks"""
        return list(self.tasks.values())
    
    def update_task(self, updated_task: ScheduledTask) -> bool:
        """
        Update an existing task.
        
        Args:
            updated_task: Updated ScheduledTask instance
            
        Returns:
            True if task updated successfully
        """
        if updated_task.task_id not in self.tasks:
            return False
        
        try:
            # Remove old job and add new one
            self.scheduler.remove_job(updated_task.task_id)
            
            # Add updated job
            if updated_task.schedule_type == 'cron':
                self.scheduler.add_job(
                    func=self._run_spider,
                    trigger='cron',
                    args=[updated_task],
                    id=updated_task.task_id,
                    name=updated_task.name,
                    **updated_task.schedule_config
                )
            elif updated_task.schedule_type == 'interval':
                self.scheduler.add_job(
                    func=self._run_spider,
                    trigger='interval',
                    args=[updated_task],
                    id=updated_task.task_id,
                    name=updated_task.name,
                    **updated_task.schedule_config
                )
            
            self.tasks[updated_task.task_id] = updated_task
            self.logger.info(f"Updated scheduled task: {updated_task.task_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update task {updated_task.task_id}: {e}")
            return False
    
    def enable_task(self, task_id: str) -> bool:
        """Enable a task"""
        if task_id not in self.tasks:
            return False
        
        try:
            self.scheduler.resume_job(task_id)
            self.tasks[task_id].enabled = True
            return True
        except Exception as e:
            self.logger.error(f"Failed to enable task {task_id}: {e}")
            return False
    
    def disable_task(self, task_id: str) -> bool:
        """Disable a task"""
        if task_id not in self.tasks:
            return False
        
        try:
            self.scheduler.pause_job(task_id)
            self.tasks[task_id].enabled = False
            return True
        except Exception as e:
            self.logger.error(f"Failed to disable task {task_id}: {e}")
            return False
    
    def _run_spider(self, task: ScheduledTask):
        """
        Execute spider for the given task.
        
        Args:
            task: ScheduledTask to execute
        """
        self.logger.info(f"Starting spider run for task: {task.task_id}")
        
        try:
            # Update last run time
            task.last_run = datetime.now()
            
            # Get project settings
            settings = get_project_settings()
            
            # Apply custom settings
            if task.spider_settings:
                settings.setdict(task.spider_settings)
            
            # Create crawler process
            process = CrawlerProcess(settings)
            
            # Start spider with arguments
            process.crawl(task.spider_name, **task.spider_args)
            process.start()
            
            self.logger.info(f"Completed spider run for task: {task.task_id}")
            
        except Exception as e:
            self.logger.error(f"Error running spider for task {task.task_id}: {e}")