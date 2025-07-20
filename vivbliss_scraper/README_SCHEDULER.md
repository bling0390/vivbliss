# VivBliss Spider Scheduler

A powerful scheduling system for automating Scrapy spider execution using APScheduler with cron expressions and interval-based scheduling.

## 🚀 Features

- **Cron-based Scheduling**: Full cron expression support with aliases
- **Interval Scheduling**: Run spiders at specific intervals (minutes, hours, days)
- **Task Management**: Create, update, enable/disable, and remove scheduled tasks
- **Persistence**: Export/import task configurations
- **CLI Interface**: Command-line management tool
- **Monitoring**: Task status tracking and logging
- **Flexible Configuration**: Multiple job stores and executors
- **Test-Driven Development**: 100% test coverage with comprehensive test suite

## 📦 Installation

Dependencies are automatically installed with the main package:

```bash
pip install apscheduler>=3.10.0 croniter>=1.4.0
```

## 🏗️ Architecture

```
vivbliss_scraper/scheduler/
├── __init__.py              # Package initialization
├── config.py                # Scheduler configuration
├── scheduler.py             # Main scheduler class
├── task_manager.py          # Task management logic
├── cron_parser.py           # Cron expression parser
├── cli.py                   # Command-line interface
└── example_usage.py         # Usage examples
```

## 🔧 Configuration

### Basic Configuration

```python
from vivbliss_scraper.scheduler import SpiderScheduler, SchedulerConfig

# Default configuration
config = SchedulerConfig()

# Custom configuration
config = SchedulerConfig(
    timezone='Asia/Shanghai',
    job_store_type='mongodb',  # 'memory', 'mongodb', 'sqlalchemy'
    executor_type='threadpool',  # 'threadpool', 'processpool'
    max_workers=10,
    misfire_grace_time=120
)

scheduler = SpiderScheduler(config)
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SCHEDULER_TIMEZONE` | Default timezone | `UTC` |
| `SCHEDULER_MAX_WORKERS` | Maximum worker threads | `5` |
| `SCHEDULER_JOB_STORE` | Job store type | `memory` |

## 💻 Usage Examples

### Basic Scheduling

```python
from vivbliss_scraper.scheduler import SpiderScheduler

scheduler = SpiderScheduler()

# Add daily task at 10:30 AM
task = scheduler.add_spider_task(
    task_id='daily_scrape',
    name='Daily VivBliss Scrape',
    spider_name='vivbliss',
    cron_expression='30 10 * * *',
    description='Daily scraping at 10:30 AM'
)

# Add interval task (every 2 hours)
task = scheduler.add_interval_spider_task(
    task_id='hourly_scrape',
    name='Bi-hourly Scrape',
    spider_name='vivbliss',
    hours=2
)

# Start scheduler
scheduler.start()

# Keep running
try:
    import time
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    scheduler.shutdown()
```

### Advanced Task Configuration

```python
# Task with custom spider arguments and settings
task = scheduler.add_spider_task(
    task_id='custom_scrape',
    name='Custom Spider Run',
    spider_name='vivbliss',
    cron_expression='0 */4 * * *',  # Every 4 hours
    spider_args={
        'start_urls': ['https://vivbliss.com/category/tech'],
        'category': 'technology'
    },
    spider_settings={
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS': 1,
        'USER_AGENT': 'VivBliss Custom Bot 1.0'
    }
)
```

### Task Management

```python
# List all tasks
tasks = scheduler.list_tasks()
for task in tasks:
    print(f"{task.task_id}: {task.name} ({task.schedule_type})")

# Get task information
task_info = scheduler.get_task_info('daily_scrape')
print(f"Next run: {task_info['next_run_time']}")

# Enable/disable tasks
scheduler.disable_task('daily_scrape')
scheduler.enable_task('daily_scrape')

# Update task schedule
scheduler.update_task_schedule('daily_scrape', '0 14 * * *')  # Change to 2 PM

# Remove task
scheduler.remove_task('daily_scrape')
```

### Task Persistence

```python
# Export all tasks
config = scheduler.export_tasks()
with open('scheduler_config.json', 'w') as f:
    json.dump(config, f, indent=2)

# Import tasks to new scheduler
new_scheduler = SpiderScheduler()
with open('scheduler_config.json', 'r') as f:
    config = json.load(f)
new_scheduler.import_tasks(config)
```

## 📅 Cron Expression Guide

### Basic Syntax

```
* * * * *
│ │ │ │ │
│ │ │ │ └─── Day of week (0-7, Sunday = 0 or 7)
│ │ │ └───── Month (1-12)
│ │ └─────── Day of month (1-31)
│ └───────── Hour (0-23)
└─────────── Minute (0-59)
```

### Common Examples

| Expression | Description |
|------------|-------------|
| `* * * * *` | Every minute |
| `0 * * * *` | Every hour |
| `0 0 * * *` | Daily at midnight |
| `30 10 * * *` | Daily at 10:30 AM |
| `0 9 * * 1-5` | Weekdays at 9:00 AM |
| `0 14 * * 0` | Sundays at 2:00 PM |
| `0 0 1 * *` | First day of every month |
| `*/15 * * * *` | Every 15 minutes |
| `0 9,21 * * *` | Twice daily (9 AM and 9 PM) |

### Cron Aliases

| Alias | Expression | Description |
|-------|------------|-------------|
| `@yearly` | `0 0 1 1 *` | January 1st every year |
| `@monthly` | `0 0 1 * *` | First day of every month |
| `@weekly` | `0 0 * * 0` | Every Sunday at midnight |
| `@daily` | `0 0 * * *` | Every day at midnight |
| `@hourly` | `0 * * * *` | Every hour |

## 🖥️ Command Line Interface

### Installation

The CLI is available after installing the package:

```bash
# Start scheduler daemon
python -m vivbliss_scraper.scheduler.cli start

# Add cron task
python -m vivbliss_scraper.scheduler.cli add-cron daily_task vivbliss "0 10 * * *" \\
    --name "Daily Scrape" \\
    --description "Daily scraping at 10 AM"

# Add interval task  
python -m vivbliss_scraper.scheduler.cli add-interval hourly_task vivbliss \\
    --hours 2 \\
    --name "Bi-hourly Scrape"

# List tasks
python -m vivbliss_scraper.scheduler.cli list

# Show task details
python -m vivbliss_scraper.scheduler.cli show daily_task

# Enable/disable tasks
python -m vivbliss_scraper.scheduler.cli disable daily_task
python -m vivbliss_scraper.scheduler.cli enable daily_task

# Remove task
python -m vivbliss_scraper.scheduler.cli remove daily_task

# Export/import tasks
python -m vivbliss_scraper.scheduler.cli export tasks.json
python -m vivbliss_scraper.scheduler.cli import tasks.json

# Show status
python -m vivbliss_scraper.scheduler.cli status
```

### CLI Output Examples

```bash
$ python -m vivbliss_scraper.scheduler.cli list
Task ID              Name                      Spider          Type       Enabled
-------------------------------------------------------------------------------------
daily_scrape         Daily VivBliss Scrape     vivbliss        cron       Yes
hourly_scrape        Bi-hourly Scrape         vivbliss        interval   Yes

$ python -m vivbliss_scraper.scheduler.cli status
Scheduler Status:
  Running: True
  Total tasks: 2
  Enabled tasks: 2
  Disabled tasks: 0
  Pending jobs: 2
  Timezone: UTC
  Job store: memory
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all scheduler tests
python -m pytest tests/test_scheduler_*.py tests/test_cron_*.py tests/test_task_*.py -v

# Run with coverage
coverage run -m pytest tests/test_scheduler_*.py tests/test_cron_*.py tests/test_task_*.py
coverage report --show-missing

# Test specific modules
python -m pytest tests/test_scheduler_config.py -v          # Configuration tests
python -m pytest tests/test_cron_parser.py -v              # Cron parser tests
python -m pytest tests/test_task_manager.py -v             # Task manager tests
python -m pytest tests/test_scheduler_integration.py -v    # Integration tests
```

## 📊 Monitoring and Logging

### Task Status Monitoring

```python
# Get scheduler status
status = scheduler.get_scheduler_status()
print(f"Running: {status['running']}")
print(f"Total tasks: {status['total_tasks']}")
print(f"Enabled tasks: {status['enabled_tasks']}")

# Get detailed task information
task_info = scheduler.get_task_info('task_id')
print(f"Last run: {task_info['last_run']}")
print(f"Next run: {task_info['next_run_time']}")
```

### Logging Configuration

```python
import logging

# Configure logging for scheduler
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('vivbliss_scraper.scheduler')
logger.setLevel(logging.DEBUG)

# The scheduler will log:
# - Task addition/removal
# - Schedule execution
# - Error handling
# - Status changes
```

### Log Output Example

```
INFO:vivbliss_scraper.scheduler.task_manager:Added scheduled task: daily_scrape
INFO:apscheduler.scheduler:Adding job tentatively -- it will be properly scheduled when the scheduler starts
INFO:vivbliss_scraper.scheduler.task_manager:Starting spider run for task: daily_scrape
INFO:vivbliss_scraper.scheduler.task_manager:Completed spider run for task: daily_scrape
```

## 🔧 Advanced Configuration

### MongoDB Job Store

```python
config = SchedulerConfig(
    job_store_type='mongodb',
    mongodb_uri='mongodb://localhost:27017',
    mongodb_database='scheduler_db'
)
```

### Process Pool Executor

```python
config = SchedulerConfig(
    executor_type='processpool',
    max_workers=4
)
```

### Custom Job Defaults

```python
# Job defaults are automatically configured:
job_defaults = {
    'coalesce': True,        # Combine multiple pending executions
    'max_instances': 3,      # Maximum concurrent instances
    'misfire_grace_time': 60 # Grace time for misfired jobs
}
```

## 🔄 Integration with Scrapy

The scheduler integrates seamlessly with your existing Scrapy project:

### Project Structure

```
your_project/
├── scrapy.cfg
├── your_project/
│   ├── spiders/
│   │   ├── spider1.py
│   │   └── spider2.py
│   ├── settings.py
│   └── pipelines.py
└── scheduler_config.json  # Optional: persistent task configuration
```

### Running Scheduled Spiders

The scheduler uses Scrapy's `CrawlerProcess` to execute spiders:

1. **Project Settings**: Uses your project's `settings.py`
2. **Custom Settings**: Can override settings per task
3. **Spider Arguments**: Pass custom arguments to spiders
4. **Pipeline Integration**: Works with existing pipelines

### Example Spider Integration

```python
# In your spider
class MySpider(scrapy.Spider):
    name = 'my_spider'
    
    def __init__(self, category=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category = category or 'default'
        
    def start_requests(self):
        # Use scheduler-provided arguments
        urls = getattr(self, 'start_urls', [self.start_urls[0]])
        for url in urls:
            yield scrapy.Request(url)

# Schedule with custom arguments
scheduler.add_spider_task(
    task_id='categorized_scrape',
    spider_name='my_spider',
    cron_expression='0 10 * * *',
    spider_args={
        'category': 'technology',
        'start_urls': ['https://example.com/tech']
    }
)
```

## 🚨 Error Handling

### Misfire Handling

```python
# Configure misfire grace time
config = SchedulerConfig(misfire_grace_time=300)  # 5 minutes

# Jobs that miss their scheduled time by more than grace_time are skipped
```

### Exception Handling

```python
# The scheduler handles various error scenarios:
# - Spider not found
# - Invalid cron expressions
# - Duplicate task IDs
# - Job store connection errors
# - Spider execution failures

try:
    scheduler.add_spider_task(
        task_id='test_task',
        spider_name='nonexistent_spider',
        cron_expression='invalid cron'
    )
except ValueError as e:
    print(f"Configuration error: {e}")
except RuntimeError as e:
    print(f"Runtime error: {e}")
```

## 📈 Performance Considerations

### Resource Management

- **Thread Pool**: Default 5 workers, configurable
- **Process Pool**: Available for CPU-intensive tasks
- **Memory Usage**: In-memory job store for development
- **Persistence**: MongoDB/SQLAlchemy for production

### Scaling Guidelines

- **Small Projects**: Memory job store, thread pool executor
- **Medium Projects**: MongoDB job store, increased workers
- **Large Projects**: Distributed setup with external job store

### Best Practices

1. **Monitor Resource Usage**: Track memory and CPU usage
2. **Configure Appropriate Workers**: Based on your spider requirements  
3. **Use Process Pool**: For CPU-intensive spiders
4. **Persistent Storage**: For production environments
5. **Error Monitoring**: Implement proper logging and alerting

## 🔐 Security Considerations

- **Credential Management**: Store sensitive configuration in environment variables
- **Access Control**: Restrict CLI access in production
- **Log Security**: Avoid logging sensitive spider arguments
- **Network Security**: Secure job store connections

## 🤝 Contributing

1. **Write Tests**: Maintain 100% test coverage
2. **Follow TDD**: Red-Green-Refactor cycle
3. **Code Style**: Follow existing patterns
4. **Documentation**: Update README for new features

## 📄 License

This scheduler module is part of the VivBliss scraper project and follows the same licensing terms.

## 🐛 Troubleshooting

### Common Issues

1. **Scheduler Won't Start**
   - Check job store connectivity
   - Verify configuration parameters
   - Check for port conflicts

2. **Tasks Not Executing**
   - Verify cron expressions
   - Check task enabled status
   - Review spider availability

3. **Memory Issues**
   - Reduce max_workers
   - Use process pool executor
   - Monitor resource usage

4. **Job Store Errors**
   - Check database connectivity
   - Verify credentials
   - Test job store configuration

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable debug logging for all scheduler components
```

### Health Checks

```python
# Check scheduler health
status = scheduler.get_scheduler_status()
if not status['running']:
    print("Scheduler is not running!")

# Verify task configuration
for task in scheduler.list_tasks():
    task_info = scheduler.get_task_info(task.task_id)
    if not task_info['next_run_time']:
        print(f"Task {task.task_id} has no next run time!")
```

This scheduler provides a robust, production-ready solution for automating your Scrapy spider execution with comprehensive testing, monitoring, and management capabilities.