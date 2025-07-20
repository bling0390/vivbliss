#!/usr/bin/env python3
"""
Command-line interface for managing scheduled spider tasks.
"""
import argparse
import json
import sys
from datetime import datetime
from typing import Dict, Any

from .scheduler import SpiderScheduler
from .config import SchedulerConfig


class SchedulerCLI:
    """Command-line interface for spider scheduler"""
    
    def __init__(self):
        self.scheduler = None
        self.config_file = 'scheduler_config.json'
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser"""
        parser = argparse.ArgumentParser(
            description='VivBliss Spider Scheduler Management',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s start                           # Start scheduler daemon
  %(prog)s add-cron task1 vivbliss "0 10 * * *"  # Add daily task at 10:00
  %(prog)s add-interval task2 vivbliss --hours 2  # Add task every 2 hours
  %(prog)s list                            # List all tasks
  %(prog)s status                          # Show scheduler status
  %(prog)s remove task1                    # Remove task
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Start command
        subparsers.add_parser('start', help='Start scheduler daemon')
        
        # Stop command
        subparsers.add_parser('stop', help='Stop scheduler daemon')
        
        # Status command
        subparsers.add_parser('status', help='Show scheduler status')
        
        # Add cron task
        cron_parser = subparsers.add_parser('add-cron', help='Add cron-scheduled task')
        cron_parser.add_argument('task_id', help='Unique task identifier')
        cron_parser.add_argument('spider_name', help='Name of spider to run')
        cron_parser.add_argument('cron_expression', help='Cron expression (e.g., "0 10 * * *")')
        cron_parser.add_argument('--name', help='Human-readable task name')
        cron_parser.add_argument('--description', help='Task description')
        cron_parser.add_argument('--spider-args', help='Spider arguments (JSON)')
        cron_parser.add_argument('--spider-settings', help='Spider settings (JSON)')
        cron_parser.add_argument('--disabled', action='store_true', help='Create task disabled')
        
        # Add interval task
        interval_parser = subparsers.add_parser('add-interval', help='Add interval-scheduled task')
        interval_parser.add_argument('task_id', help='Unique task identifier')
        interval_parser.add_argument('spider_name', help='Name of spider to run')
        interval_parser.add_argument('--name', help='Human-readable task name')
        interval_parser.add_argument('--description', help='Task description')
        interval_parser.add_argument('--weeks', type=int, default=0, help='Interval in weeks')
        interval_parser.add_argument('--days', type=int, default=0, help='Interval in days')
        interval_parser.add_argument('--hours', type=int, default=0, help='Interval in hours')
        interval_parser.add_argument('--minutes', type=int, default=0, help='Interval in minutes')
        interval_parser.add_argument('--seconds', type=int, default=0, help='Interval in seconds')
        interval_parser.add_argument('--spider-args', help='Spider arguments (JSON)')
        interval_parser.add_argument('--spider-settings', help='Spider settings (JSON)')
        interval_parser.add_argument('--disabled', action='store_true', help='Create task disabled')
        
        # Remove task
        remove_parser = subparsers.add_parser('remove', help='Remove scheduled task')
        remove_parser.add_argument('task_id', help='Task ID to remove')
        
        # List tasks
        list_parser = subparsers.add_parser('list', help='List all scheduled tasks')
        list_parser.add_argument('--format', choices=['table', 'json'], default='table',
                               help='Output format')
        
        # Show task
        show_parser = subparsers.add_parser('show', help='Show task details')
        show_parser.add_argument('task_id', help='Task ID to show')
        
        # Enable/disable task
        enable_parser = subparsers.add_parser('enable', help='Enable task')
        enable_parser.add_argument('task_id', help='Task ID to enable')
        
        disable_parser = subparsers.add_parser('disable', help='Disable task')
        disable_parser.add_argument('task_id', help='Task ID to disable')
        
        # Export/import
        export_parser = subparsers.add_parser('export', help='Export tasks configuration')
        export_parser.add_argument('file', help='Output file path')
        
        import_parser = subparsers.add_parser('import', help='Import tasks configuration')
        import_parser.add_argument('file', help='Input file path')
        
        return parser
    
    def init_scheduler(self):
        """Initialize scheduler"""
        if self.scheduler is None:
            config = SchedulerConfig()
            self.scheduler = SpiderScheduler(config)
    
    def cmd_start(self, args):
        """Start scheduler daemon"""
        self.init_scheduler()
        
        if self.scheduler.is_running():
            print("Scheduler is already running")
            return
        
        self.scheduler.start()
        print("Scheduler started successfully")
        
        try:
            # Keep running until interrupted
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\\nShutting down scheduler...")
            self.scheduler.shutdown()
            print("Scheduler stopped")
    
    def cmd_stop(self, args):
        """Stop scheduler daemon"""
        self.init_scheduler()
        
        if not self.scheduler.is_running():
            print("Scheduler is not running")
            return
        
        self.scheduler.shutdown()
        print("Scheduler stopped")
    
    def cmd_status(self, args):
        """Show scheduler status"""
        self.init_scheduler()
        
        status = self.scheduler.get_scheduler_status()
        
        print("Scheduler Status:")
        print(f"  Running: {status['running']}")
        print(f"  Total tasks: {status['total_tasks']}")
        print(f"  Enabled tasks: {status['enabled_tasks']}")
        print(f"  Disabled tasks: {status['disabled_tasks']}")
        print(f"  Pending jobs: {status['pending_jobs']}")
        print(f"  Timezone: {status['timezone']}")
        print(f"  Job store: {status['job_store_type']}")
    
    def cmd_add_cron(self, args):
        """Add cron-scheduled task"""
        self.init_scheduler()
        
        spider_args = {}
        if args.spider_args:
            try:
                spider_args = json.loads(args.spider_args)
            except json.JSONDecodeError:
                print("Error: Invalid JSON in spider-args")
                return
        
        spider_settings = {}
        if args.spider_settings:
            try:
                spider_settings = json.loads(args.spider_settings)
            except json.JSONDecodeError:
                print("Error: Invalid JSON in spider-settings")
                return
        
        try:
            task = self.scheduler.add_spider_task(
                task_id=args.task_id,
                name=args.name or args.task_id,
                spider_name=args.spider_name,
                cron_expression=args.cron_expression,
                description=args.description or "",
                spider_args=spider_args,
                spider_settings=spider_settings,
                enabled=not args.disabled
            )
            
            print(f"Successfully added cron task: {task.task_id}")
            
        except Exception as e:
            print(f"Error adding task: {e}")
    
    def cmd_add_interval(self, args):
        """Add interval-scheduled task"""
        self.init_scheduler()
        
        spider_args = {}
        if args.spider_args:
            try:
                spider_args = json.loads(args.spider_args)
            except json.JSONDecodeError:
                print("Error: Invalid JSON in spider-args")
                return
        
        spider_settings = {}
        if args.spider_settings:
            try:
                spider_settings = json.loads(args.spider_settings)
            except json.JSONDecodeError:
                print("Error: Invalid JSON in spider-settings")
                return
        
        try:
            task = self.scheduler.add_interval_spider_task(
                task_id=args.task_id,
                name=args.name or args.task_id,
                spider_name=args.spider_name,
                weeks=args.weeks,
                days=args.days,
                hours=args.hours,
                minutes=args.minutes,
                seconds=args.seconds,
                description=args.description or "",
                spider_args=spider_args,
                spider_settings=spider_settings,
                enabled=not args.disabled
            )
            
            print(f"Successfully added interval task: {task.task_id}")
            
        except Exception as e:
            print(f"Error adding task: {e}")
    
    def cmd_remove(self, args):
        """Remove task"""
        self.init_scheduler()
        
        if self.scheduler.remove_task(args.task_id):
            print(f"Successfully removed task: {args.task_id}")
        else:
            print(f"Task not found: {args.task_id}")
    
    def cmd_list(self, args):
        """List all tasks"""
        self.init_scheduler()
        
        tasks = self.scheduler.list_tasks()
        
        if args.format == 'json':
            task_data = []
            for task in tasks:
                task_info = self.scheduler.get_task_info(task.task_id)
                task_data.append(task_info)
            print(json.dumps(task_data, indent=2))
        else:
            if not tasks:
                print("No scheduled tasks found")
                return
            
            print(f"{'Task ID':<20} {'Name':<25} {'Spider':<15} {'Type':<10} {'Enabled':<8}")
            print("-" * 85)
            
            for task in tasks:
                enabled = "Yes" if task.enabled else "No"
                print(f"{task.task_id:<20} {task.name:<25} {task.spider_name:<15} "
                      f"{task.schedule_type:<10} {enabled:<8}")
    
    def cmd_show(self, args):
        """Show task details"""
        self.init_scheduler()
        
        task_info = self.scheduler.get_task_info(args.task_id)
        if not task_info:
            print(f"Task not found: {args.task_id}")
            return
        
        print(f"Task Details: {args.task_id}")
        print("-" * 40)
        print(f"Name: {task_info['name']}")
        print(f"Spider: {task_info['spider_name']}")
        print(f"Type: {task_info['schedule_type']}")
        print(f"Schedule: {task_info['schedule']}")
        print(f"Enabled: {task_info['enabled']}")
        print(f"Description: {task_info['description']}")
        print(f"Created: {task_info['created_at']}")
        print(f"Last run: {task_info['last_run'] or 'Never'}")
        print(f"Next run: {task_info['next_run_time'] or 'N/A'}")
        
        if task_info['spider_args']:
            print(f"Spider args: {json.dumps(task_info['spider_args'], indent=2)}")
        
        if task_info['spider_settings']:
            print(f"Spider settings: {json.dumps(task_info['spider_settings'], indent=2)}")
    
    def cmd_enable(self, args):
        """Enable task"""
        self.init_scheduler()
        
        if self.scheduler.enable_task(args.task_id):
            print(f"Task enabled: {args.task_id}")
        else:
            print(f"Task not found: {args.task_id}")
    
    def cmd_disable(self, args):
        """Disable task"""
        self.init_scheduler()
        
        if self.scheduler.disable_task(args.task_id):
            print(f"Task disabled: {args.task_id}")
        else:
            print(f"Task not found: {args.task_id}")
    
    def cmd_export(self, args):
        """Export tasks"""
        self.init_scheduler()
        
        try:
            config = self.scheduler.export_tasks()
            with open(args.file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"Tasks exported to: {args.file}")
        except Exception as e:
            print(f"Error exporting tasks: {e}")
    
    def cmd_import(self, args):
        """Import tasks"""
        self.init_scheduler()
        
        try:
            with open(args.file, 'r') as f:
                config = json.load(f)
            self.scheduler.import_tasks(config)
            print(f"Tasks imported from: {args.file}")
        except Exception as e:
            print(f"Error importing tasks: {e}")
    
    def run(self):
        """Run CLI"""
        parser = self.create_parser()
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            return
        
        # Execute command
        command_method = getattr(self, f'cmd_{args.command.replace("-", "_")}', None)
        if command_method:
            command_method(args)
        else:
            print(f"Unknown command: {args.command}")


def main():
    """Main entry point"""
    cli = SchedulerCLI()
    cli.run()


if __name__ == '__main__':
    main()