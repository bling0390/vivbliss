import pytest
from datetime import datetime, timedelta
from vivbliss_scraper.scheduler.cron_parser import CronParser, CronExpression


class TestCronExpression:
    """Test cases for CronExpression model"""
    
    def test_cron_expression_creation(self):
        """Test creating a cron expression object"""
        expr = CronExpression(
            minute='30',
            hour='10',
            day='*',
            month='*',
            day_of_week='1-5'
        )
        
        assert expr.minute == '30'
        assert expr.hour == '10'
        assert expr.day == '*'
        assert expr.month == '*'
        assert expr.day_of_week == '1-5'
    
    def test_cron_expression_to_string(self):
        """Test converting cron expression to string"""
        expr = CronExpression(
            minute='0',
            hour='*/2',
            day='1',
            month='*',
            day_of_week='*'
        )
        
        assert str(expr) == '0 */2 1 * *'
    
    def test_cron_expression_from_string(self):
        """Test creating cron expression from string"""
        expr = CronExpression.from_string('30 10 * * 1-5')
        
        assert expr.minute == '30'
        assert expr.hour == '10'
        assert expr.day == '*'
        assert expr.month == '*'
        assert expr.day_of_week == '1-5'
    
    def test_invalid_cron_string(self):
        """Test that invalid cron string raises ValueError"""
        with pytest.raises(ValueError, match="Invalid cron expression"):
            CronExpression.from_string('invalid cron')


class TestCronParser:
    """Test cases for CronParser"""
    
    def setup_method(self):
        """Set up test environment"""
        self.parser = CronParser()
    
    def test_parse_simple_cron(self):
        """Test parsing simple cron expressions"""
        # Every day at 10:30
        schedule = self.parser.parse('30 10 * * *')
        assert schedule['hour'] == 10
        assert schedule['minute'] == 30
        
        # Every Monday at 09:00
        schedule = self.parser.parse('0 9 * * 1')
        assert schedule['hour'] == 9
        assert schedule['minute'] == 0
        assert schedule['day_of_week'] == 1
    
    def test_parse_complex_cron(self):
        """Test parsing complex cron expressions"""
        # Every 15 minutes
        schedule = self.parser.parse('*/15 * * * *')
        assert 'minute' in schedule
        
        # Every 2 hours
        schedule = self.parser.parse('0 */2 * * *')
        assert 'hour' in schedule
        assert schedule['minute'] == 0
        
        # First day of every month at midnight
        schedule = self.parser.parse('0 0 1 * *')
        assert schedule['hour'] == 0
        assert schedule['minute'] == 0
        assert schedule['day'] == 1
    
    def test_validate_cron_expression(self):
        """Test validating cron expressions"""
        # Valid expressions
        assert self.parser.validate('30 10 * * *') is True
        assert self.parser.validate('*/15 * * * *') is True
        assert self.parser.validate('0 0 1,15 * *') is True
        
        # Invalid expressions
        assert self.parser.validate('invalid') is False
        assert self.parser.validate('60 * * * *') is False  # Invalid minute
        assert self.parser.validate('* 25 * * *') is False  # Invalid hour
    
    def test_get_next_run_time(self):
        """Test calculating next run time"""
        base_time = datetime(2024, 1, 1, 10, 0, 0)
        
        # Daily at 14:30
        next_run = self.parser.get_next_run_time('30 14 * * *', base_time)
        assert next_run.hour == 14
        assert next_run.minute == 30
        assert next_run.day == 1
        
        # If current time is past schedule, should be next day
        base_time = datetime(2024, 1, 1, 15, 0, 0)
        next_run = self.parser.get_next_run_time('30 14 * * *', base_time)
        assert next_run.day == 2
    
    def test_cron_to_apscheduler_trigger(self):
        """Test converting cron to APScheduler trigger kwargs"""
        # Daily at 10:30
        trigger_kwargs = self.parser.to_apscheduler_trigger('30 10 * * *')
        assert trigger_kwargs['trigger'] == 'cron'
        assert trigger_kwargs['hour'] == 10
        assert trigger_kwargs['minute'] == 30
        
        # Every Monday and Wednesday at 9:00
        trigger_kwargs = self.parser.to_apscheduler_trigger('0 9 * * 1,3')
        assert trigger_kwargs['trigger'] == 'cron'
        assert trigger_kwargs['hour'] == 9
        assert trigger_kwargs['minute'] == 0
        assert trigger_kwargs['day_of_week'] == '1,3'
    
    def test_common_cron_patterns(self):
        """Test parsing common cron patterns"""
        # Every minute
        assert self.parser.validate('* * * * *') is True
        
        # Every hour
        assert self.parser.validate('0 * * * *') is True
        
        # Every day at midnight
        assert self.parser.validate('0 0 * * *') is True
        
        # Every Sunday at 2:30 AM
        assert self.parser.validate('30 2 * * 0') is True
        
        # Every 5 minutes
        assert self.parser.validate('*/5 * * * *') is True
    
    def test_cron_aliases(self):
        """Test cron expression aliases"""
        # @hourly = 0 * * * *
        schedule = self.parser.parse('@hourly')
        assert schedule['minute'] == 0
        
        # @daily = 0 0 * * *
        schedule = self.parser.parse('@daily')
        assert schedule['hour'] == 0
        assert schedule['minute'] == 0
        
        # @weekly = 0 0 * * 0
        schedule = self.parser.parse('@weekly')
        assert schedule['hour'] == 0
        assert schedule['minute'] == 0
        assert schedule['day_of_week'] == 0
        
        # @monthly = 0 0 1 * *
        schedule = self.parser.parse('@monthly')
        assert schedule['hour'] == 0
        assert schedule['minute'] == 0
        assert schedule['day'] == 1