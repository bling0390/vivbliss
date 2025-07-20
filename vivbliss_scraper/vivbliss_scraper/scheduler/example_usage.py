"""
Example usage of the VivBliss spider scheduler.
"""
import time
from .scheduler import SpiderScheduler
from .config import SchedulerConfig


def basic_scheduler_example():
    """Basic scheduler usage example"""
    print("=== Basic Scheduler Example ===")
    
    # Create scheduler with default configuration
    scheduler = SpiderScheduler()
    
    # Add a cron-based task - run daily at 10:30 AM
    task1 = scheduler.add_spider_task(
        task_id='daily_scrape',
        name='Daily VivBliss Scrape',
        spider_name='vivbliss',
        cron_expression='30 10 * * *',
        description='Daily scraping of VivBliss website'
    )
    
    print(f"Added task: {task1.task_id}")
    
    # Add an interval-based task - run every 2 hours
    task2 = scheduler.add_interval_spider_task(
        task_id='hourly_scrape',
        name='Bi-hourly Scrape',
        spider_name='vivbliss',
        hours=2,
        description='Scrape every 2 hours'
    )
    
    print(f"Added task: {task2.task_id}")
    
    # List all tasks
    print("\\nScheduled tasks:")
    for task in scheduler.list_tasks():
        print(f"  - {task.task_id}: {task.name} ({task.schedule_type})")
    
    # Get task information
    task_info = scheduler.get_task_info('daily_scrape')
    if task_info:
        print(f"\\nTask details for '{task_info['task_id']}':")
        print(f"  Name: {task_info['name']}")
        print(f"  Schedule: {task_info['schedule']}")
        print(f"  Next run: {task_info['next_run_time']}")
    
    # Start scheduler
    print("\\nStarting scheduler...")
    scheduler.start()
    
    # Let it run for a short time
    print("Scheduler is running. Press Ctrl+C to stop.")
    try:
        time.sleep(10)
    except KeyboardInterrupt:
        pass
    
    # Stop scheduler
    print("\\nStopping scheduler...")
    scheduler.shutdown()
    print("Scheduler stopped.")


def advanced_scheduler_example():
    """Advanced scheduler configuration example"""
    print("\\n=== Advanced Scheduler Example ===")
    
    # Create custom configuration
    config = SchedulerConfig(
        timezone='Asia/Shanghai',
        job_store_type='memory',
        executor_type='threadpool',
        max_workers=3,
        misfire_grace_time=30
    )
    
    scheduler = SpiderScheduler(config)
    
    # Add task with custom spider arguments and settings
    task = scheduler.add_spider_task(
        task_id='custom_scrape',
        name='Custom Spider Run',
        spider_name='vivbliss',
        cron_expression='0 */4 * * *',  # Every 4 hours
        description='Custom scraping with specific settings',
        spider_args={
            'start_urls': ['https://vivbliss.com/category/tech']
        },
        spider_settings={
            'DOWNLOAD_DELAY': 2,
            'CONCURRENT_REQUESTS': 1,
            'USER_AGENT': 'VivBliss Custom Bot 1.0'
        }
    )
    
    print(f"Added custom task: {task.task_id}")
    
    # Show task details
    task_info = scheduler.get_task_info('custom_scrape')
    if task_info:
        print(f"\\nCustom task details:")
        print(f"  Spider args: {task_info['spider_args']}")
        print(f"  Spider settings: {task_info['spider_settings']}")
    
    # Export configuration
    config_data = scheduler.export_tasks()
    print(f"\\nExported {len(config_data['tasks'])} tasks")
    
    # Demonstrate task management
    print("\\nTask management:")
    
    # Disable task
    scheduler.disable_task('custom_scrape')
    print("  - Task disabled")
    
    # Enable task
    scheduler.enable_task('custom_scrape')
    print("  - Task enabled")
    
    # Update task schedule
    updated_task = scheduler.update_task_schedule('custom_scrape', '0 */6 * * *')
    if updated_task:
        print("  - Task schedule updated to every 6 hours")
    
    # Get scheduler status
    status = scheduler.get_scheduler_status()
    print(f"\\nScheduler status:")
    print(f"  Total tasks: {status['total_tasks']}")
    print(f"  Enabled tasks: {status['enabled_tasks']}")
    print(f"  Timezone: {status['timezone']}")


def cron_examples():
    """Examples of different cron expressions"""
    print("\\n=== Cron Expression Examples ===")
    
    scheduler = SpiderScheduler()
    
    # Common cron patterns
    examples = [
        ('every_minute', '* * * * *', 'Every minute'),
        ('hourly', '0 * * * *', 'Every hour'),
        ('daily_midnight', '0 0 * * *', 'Daily at midnight'),
        ('daily_10am', '0 10 * * *', 'Daily at 10:00 AM'),
        ('weekdays_9am', '0 9 * * 1-5', 'Weekdays at 9:00 AM'),
        ('sunday_2pm', '0 14 * * 0', 'Sundays at 2:00 PM'),
        ('first_of_month', '0 0 1 * *', 'First day of every month'),
        ('every_15min', '*/15 * * * *', 'Every 15 minutes'),
        ('twice_daily', '0 9,21 * * *', 'Twice daily (9 AM and 9 PM)'),
    ]
    
    for task_id, cron_expr, description in examples:
        try:
            task = scheduler.add_spider_task(
                task_id=task_id,
                name=description,
                spider_name='vivbliss',
                cron_expression=cron_expr,
                description=description
            )
            print(f"  {cron_expr:<15} - {description}")
        except Exception as e:
            print(f"  {cron_expr:<15} - ERROR: {e}")
    
    # Show cron aliases
    print("\\nCron aliases:")
    aliases = [
        ('@hourly', '0 * * * *', 'Every hour'),
        ('@daily', '0 0 * * *', 'Every day at midnight'),
        ('@weekly', '0 0 * * 0', 'Every Sunday at midnight'),
        ('@monthly', '0 0 1 * *', 'First day of every month'),
        ('@yearly', '0 0 1 1 *', 'January 1st every year'),
    ]
    
    for alias, equivalent, description in aliases:
        print(f"  {alias:<10} = {equivalent:<12} - {description}")


def persistence_example():
    """Example of task persistence"""
    print("\\n=== Task Persistence Example ===")
    
    scheduler = SpiderScheduler()
    
    # Add some tasks
    scheduler.add_spider_task(
        task_id='persist_1',
        name='Persistent Task 1',
        spider_name='vivbliss',
        cron_expression='0 10 * * *'
    )
    
    scheduler.add_interval_spider_task(
        task_id='persist_2',
        name='Persistent Task 2',
        spider_name='vivbliss',
        hours=6
    )
    
    print("Added 2 tasks to scheduler")
    
    # Export tasks
    config = scheduler.export_tasks()
    print(f"Exported configuration with {len(config['tasks'])} tasks")
    
    # Save to file (in real usage)
    # with open('scheduler_config.json', 'w') as f:
    #     json.dump(config, f, indent=2)
    
    # Create new scheduler and import
    new_scheduler = SpiderScheduler()
    new_scheduler.import_tasks(config)
    
    print(f"Imported {len(new_scheduler.list_tasks())} tasks to new scheduler")
    
    # Verify tasks
    for task in new_scheduler.list_tasks():
        print(f"  - {task.task_id}: {task.name}")


if __name__ == '__main__':
    # Run examples
    basic_scheduler_example()
    advanced_scheduler_example()
    cron_examples()
    persistence_example()
    
    print("\\n=== All examples completed ===")
    print("\\nTo use the scheduler in production:")
    print("1. Configure your spider settings")
    print("2. Set up appropriate cron expressions")
    print("3. Start the scheduler daemon")
    print("4. Monitor task execution through logs")
    print("\\nFor CLI usage: python -m vivbliss_scraper.scheduler.cli --help")