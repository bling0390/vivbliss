"""
Scheduler configuration module for APScheduler setup and management.
"""
import os
from typing import Dict, Any, Optional


class SchedulerConfig:
    """Configuration class for APScheduler setup"""
    
    VALID_JOB_STORES = {'memory', 'mongodb', 'sqlalchemy', 'redis'}
    VALID_EXECUTORS = {'threadpool', 'processpool', 'asyncio'}
    
    def __init__(self, 
                 timezone: str = 'UTC',
                 job_store_type: str = 'memory',
                 executor_type: str = 'threadpool',
                 max_workers: int = 5,
                 misfire_grace_time: int = 60,
                 mongodb_uri: Optional[str] = None,
                 mongodb_database: str = 'scheduler_db'):
        """
        Initialize scheduler configuration.
        
        Args:
            timezone: Timezone for scheduler
            job_store_type: Type of job store ('memory', 'mongodb', etc.)
            executor_type: Type of executor ('threadpool', 'processpool', etc.)
            max_workers: Maximum number of worker threads/processes
            misfire_grace_time: Grace time for misfired jobs in seconds
            mongodb_uri: MongoDB connection URI (required if job_store_type is 'mongodb')
            mongodb_database: MongoDB database name for job storage
        """
        if job_store_type not in self.VALID_JOB_STORES:
            raise ValueError(f"Invalid job store type: {job_store_type}. "
                           f"Valid types: {self.VALID_JOB_STORES}")
        
        if executor_type not in self.VALID_EXECUTORS:
            raise ValueError(f"Invalid executor type: {executor_type}. "
                           f"Valid types: {self.VALID_EXECUTORS}")
        
        if max_workers <= 0:
            raise ValueError("Max workers must be positive")
        
        self.timezone = timezone
        self.job_store_type = job_store_type
        self.executor_type = executor_type
        self.max_workers = max_workers
        self.misfire_grace_time = misfire_grace_time
        self.mongodb_uri = mongodb_uri
        self.mongodb_database = mongodb_database
    
    def get_job_store_config(self) -> Dict[str, Any]:
        """Get job store configuration for APScheduler"""
        if self.job_store_type == 'memory':
            return {
                'default': {
                    'type': 'memory'
                }
            }
        elif self.job_store_type == 'mongodb':
            return {
                'default': {
                    'type': 'mongodb',
                    'client': self.mongodb_uri,
                    'database': self.mongodb_database
                }
            }
        # Add other job store types as needed
        else:
            return {
                'default': {
                    'type': self.job_store_type
                }
            }
    
    def get_executor_config(self) -> Dict[str, Any]:
        """Get executor configuration for APScheduler"""
        if self.executor_type == 'threadpool':
            return {
                'default': {
                    'type': 'threadpool',
                    'max_workers': self.max_workers
                }
            }
        elif self.executor_type == 'processpool':
            return {
                'default': {
                    'type': 'processpool',
                    'max_workers': self.max_workers
                }
            }
        elif self.executor_type == 'asyncio':
            return {
                'default': {
                    'type': 'asyncio'
                }
            }
        else:
            return {
                'default': {
                    'type': self.executor_type,
                    'max_workers': self.max_workers
                }
            }
    
    def get_scheduler_config(self) -> Dict[str, Any]:
        """Get complete scheduler configuration"""
        return {
            'timezone': self.timezone,
            'misfire_grace_time': self.misfire_grace_time,
            'job_defaults': {
                'coalesce': True,
                'max_instances': 3
            }
        }
    
    @classmethod
    def from_environment(cls, env_vars: Optional[Dict[str, str]] = None) -> 'SchedulerConfig':
        """
        Create SchedulerConfig from environment variables.
        
        Args:
            env_vars: Dictionary of environment variables. If None, uses os.environ
            
        Returns:
            SchedulerConfig instance
        """
        if env_vars is None:
            env_vars = dict(os.environ)
        
        # Map environment variables to config parameters
        timezone = env_vars.get('SCHEDULER_TIMEZONE', 'UTC')
        job_store_type = env_vars.get('SCHEDULER_JOB_STORE', 'memory').lower()
        executor_type = env_vars.get('SCHEDULER_EXECUTOR_TYPE', 'threadpool').lower()
        
        max_workers = int(env_vars.get('SCHEDULER_MAX_WORKERS', '5'))
        misfire_grace_time = int(env_vars.get('SCHEDULER_MISFIRE_GRACE_TIME', '60'))
        
        mongodb_uri = (env_vars.get('SCHEDULER_MONGODB_URI') or
                      env_vars.get('MONGODB_URI') or
                      env_vars.get('MONGO_URI'))
        
        mongodb_database = env_vars.get('SCHEDULER_MONGODB_DATABASE', 'scheduler_db')
        
        return cls(
            timezone=timezone,
            job_store_type=job_store_type,
            executor_type=executor_type,
            max_workers=max_workers,
            misfire_grace_time=misfire_grace_time,
            mongodb_uri=mongodb_uri,
            mongodb_database=mongodb_database
        )
    
    @classmethod
    def from_compose_file(cls, compose_file_path: str, service_name: Optional[str] = None) -> 'SchedulerConfig':
        """
        Create SchedulerConfig from Docker Compose file.
        
        Args:
            compose_file_path: Path to docker-compose.yml file
            service_name: Service name to extract config from (optional)
            
        Returns:
            SchedulerConfig instance
        """
        from ..config import EnvironmentExtractor
        
        extractor = EnvironmentExtractor()
        extractor.load_from_compose(compose_file_path, service_name)
        
        # Get all environment variables for broader compatibility
        all_env = extractor.get_environment()
        
        return cls.from_environment(all_env)