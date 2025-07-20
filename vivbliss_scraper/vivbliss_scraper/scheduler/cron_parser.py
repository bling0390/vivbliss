"""
Cron expression parser and validator for scheduler.
"""
import re
from typing import Dict, Any, Optional
from datetime import datetime
from croniter import croniter
from dataclasses import dataclass


@dataclass
class CronExpression:
    """Represents a cron expression"""
    
    minute: str
    hour: str
    day: str
    month: str
    day_of_week: str
    
    def __str__(self) -> str:
        """Convert to cron string format"""
        return f"{self.minute} {self.hour} {self.day} {self.month} {self.day_of_week}"
    
    @classmethod
    def from_string(cls, cron_string: str) -> 'CronExpression':
        """
        Create CronExpression from string.
        
        Args:
            cron_string: Cron expression string (e.g., "30 10 * * 1-5")
            
        Returns:
            CronExpression instance
            
        Raises:
            ValueError: If cron string is invalid
        """
        parts = cron_string.strip().split()
        
        if len(parts) != 5:
            raise ValueError(f"Invalid cron expression: {cron_string}. "
                           "Must have 5 fields: minute hour day month day_of_week")
        
        return cls(
            minute=parts[0],
            hour=parts[1],
            day=parts[2],
            month=parts[3],
            day_of_week=parts[4]
        )


class CronParser:
    """Parser and validator for cron expressions"""
    
    # Common cron aliases
    ALIASES = {
        '@yearly': '0 0 1 1 *',
        '@annually': '0 0 1 1 *',
        '@monthly': '0 0 1 * *',
        '@weekly': '0 0 * * 0',
        '@daily': '0 0 * * *',
        '@midnight': '0 0 * * *',
        '@hourly': '0 * * * *'
    }
    
    def __init__(self):
        """Initialize cron parser"""
        pass
    
    def validate(self, cron_expression: str) -> bool:
        """
        Validate cron expression.
        
        Args:
            cron_expression: Cron expression to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Handle aliases
            if cron_expression in self.ALIASES:
                cron_expression = self.ALIASES[cron_expression]
            
            # Use croniter to validate
            croniter(cron_expression)
            return True
        except Exception:
            return False
    
    def parse(self, cron_expression: str) -> Dict[str, Any]:
        """
        Parse cron expression into APScheduler trigger kwargs.
        
        Args:
            cron_expression: Cron expression to parse
            
        Returns:
            Dictionary with trigger kwargs for APScheduler
            
        Raises:
            ValueError: If cron expression is invalid
        """
        # Handle aliases
        if cron_expression in self.ALIASES:
            cron_expression = self.ALIASES[cron_expression]
        
        if not self.validate(cron_expression):
            raise ValueError(f"Invalid cron expression: {cron_expression}")
        
        expr = CronExpression.from_string(cron_expression)
        
        trigger_kwargs = {}
        
        # Parse minute
        if expr.minute != '*':
            if '/' in expr.minute:
                # Handle */N format
                if expr.minute.startswith('*/'):
                    trigger_kwargs['minute'] = f"*/{expr.minute[2:]}"
                else:
                    trigger_kwargs['minute'] = expr.minute
            elif ',' in expr.minute:
                trigger_kwargs['minute'] = expr.minute
            elif '-' in expr.minute:
                trigger_kwargs['minute'] = expr.minute
            else:
                trigger_kwargs['minute'] = int(expr.minute)
        
        # Parse hour
        if expr.hour != '*':
            if '/' in expr.hour:
                trigger_kwargs['hour'] = expr.hour
            elif ',' in expr.hour:
                trigger_kwargs['hour'] = expr.hour
            elif '-' in expr.hour:
                trigger_kwargs['hour'] = expr.hour
            else:
                trigger_kwargs['hour'] = int(expr.hour)
        
        # Parse day
        if expr.day != '*':
            if '/' in expr.day:
                trigger_kwargs['day'] = expr.day
            elif ',' in expr.day:
                trigger_kwargs['day'] = expr.day
            elif '-' in expr.day:
                trigger_kwargs['day'] = expr.day
            else:
                trigger_kwargs['day'] = int(expr.day)
        
        # Parse month
        if expr.month != '*':
            if '/' in expr.month:
                trigger_kwargs['month'] = expr.month
            elif ',' in expr.month:
                trigger_kwargs['month'] = expr.month
            elif '-' in expr.month:
                trigger_kwargs['month'] = expr.month
            else:
                trigger_kwargs['month'] = int(expr.month)
        
        # Parse day of week
        if expr.day_of_week != '*':
            if ',' in expr.day_of_week:
                trigger_kwargs['day_of_week'] = expr.day_of_week
            elif '-' in expr.day_of_week:
                trigger_kwargs['day_of_week'] = expr.day_of_week
            else:
                trigger_kwargs['day_of_week'] = int(expr.day_of_week)
        
        return trigger_kwargs
    
    def get_next_run_time(self, cron_expression: str, base_time: Optional[datetime] = None) -> datetime:
        """
        Get next run time for cron expression.
        
        Args:
            cron_expression: Cron expression
            base_time: Base time to calculate from (default: now)
            
        Returns:
            Next run time
        """
        # Handle aliases
        if cron_expression in self.ALIASES:
            cron_expression = self.ALIASES[cron_expression]
        
        if base_time is None:
            base_time = datetime.now()
        
        cron = croniter(cron_expression, base_time)
        return cron.get_next(datetime)
    
    def to_apscheduler_trigger(self, cron_expression: str) -> Dict[str, Any]:
        """
        Convert cron expression to APScheduler trigger configuration.
        
        Args:
            cron_expression: Cron expression
            
        Returns:
            Dictionary with trigger configuration
        """
        trigger_kwargs = self.parse(cron_expression)
        trigger_kwargs['trigger'] = 'cron'
        return trigger_kwargs