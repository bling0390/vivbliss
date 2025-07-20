#!/usr/bin/env python3
"""
Command-line interface for managing environment variables from Docker Compose.
"""
import argparse
import sys
from pathlib import Path
from typing import Optional

from .env_extractor import EnvironmentExtractor, EnvironmentError
from .compose_parser import ComposeParseError


class EnvironmentCLI:
    """Command-line interface for environment variable management"""
    
    def __init__(self):
        """Initialize the CLI"""
        self.extractor = EnvironmentExtractor()
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser"""
        parser = argparse.ArgumentParser(
            description='VivBliss Environment Variable Manager',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s extract docker-compose.yml                    # Extract all environment variables
  %(prog)s extract docker-compose.yml --service app      # Extract from specific service
  %(prog)s extract docker-compose.yml --prefix TELEGRAM  # Extract variables with prefix
  %(prog)s validate docker-compose.yml --telegram        # Validate Telegram config
  %(prog)s export docker-compose.yml --output .env       # Export to .env file
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Extract command
        extract_parser = subparsers.add_parser('extract', help='Extract environment variables')
        extract_parser.add_argument('compose_file', help='Path to docker-compose.yml file')
        extract_parser.add_argument('--service', help='Service name to extract from')
        extract_parser.add_argument('--prefix', help='Variable prefix to filter by')
        extract_parser.add_argument('--format', choices=['table', 'json', 'env'], 
                                   default='table', help='Output format')
        
        # Validate command
        validate_parser = subparsers.add_parser('validate', help='Validate configuration')
        validate_parser.add_argument('compose_file', help='Path to docker-compose.yml file')
        validate_parser.add_argument('--service', help='Service name to validate')
        validate_parser.add_argument('--telegram', action='store_true', 
                                   help='Validate Telegram configuration')
        validate_parser.add_argument('--scheduler', action='store_true',
                                   help='Validate Scheduler configuration')
        
        # Export command
        export_parser = subparsers.add_parser('export', help='Export environment variables')
        export_parser.add_argument('compose_file', help='Path to docker-compose.yml file')
        export_parser.add_argument('--output', '-o', required=True, 
                                 help='Output file path (.env format)')
        export_parser.add_argument('--service', help='Service name to export from')
        export_parser.add_argument('--prefix', help='Variable prefix to filter by')
        
        # Info command
        info_parser = subparsers.add_parser('info', help='Show environment information')
        info_parser.add_argument('compose_file', help='Path to docker-compose.yml file')
        info_parser.add_argument('--service', help='Service name to analyze')
        
        return parser
    
    def cmd_extract(self, args):
        """Extract environment variables"""
        try:
            self.extractor.load_from_compose(args.compose_file, args.service)
            
            if args.prefix:
                env_vars = self.extractor.get_environment(prefix=args.prefix)
            else:
                env_vars = self.extractor.get_environment()
            
            if args.format == 'json':
                import json
                print(json.dumps(env_vars, indent=2))
            elif args.format == 'env':
                for key, value in sorted(env_vars.items()):
                    print(f"{key}={value}")
            else:  # table format
                if not env_vars:
                    print("No environment variables found")
                    return
                
                print(f"{'Variable':<30} {'Value':<50}")
                print("-" * 82)
                for key, value in sorted(env_vars.items()):
                    # Truncate long values
                    display_value = value[:47] + "..." if len(value) > 50 else value
                    print(f"{key:<30} {display_value:<50}")
                
                print(f"\nTotal variables: {len(env_vars)}")
            
        except (EnvironmentError, ComposeParseError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    def cmd_validate(self, args):
        """Validate configuration"""
        try:
            self.extractor.load_from_compose(args.compose_file, args.service)
            
            validation_errors = []
            
            if args.telegram:
                validation_errors.extend(self._validate_telegram_config())
            
            if args.scheduler:
                validation_errors.extend(self._validate_scheduler_config())
            
            if not args.telegram and not args.scheduler:
                # Validate all configurations
                validation_errors.extend(self._validate_telegram_config())
                validation_errors.extend(self._validate_scheduler_config())
            
            if validation_errors:
                print("Validation Errors:")
                for error in validation_errors:
                    print(f"  - {error}")
                sys.exit(1)
            else:
                print("✅ All configurations are valid!")
            
        except (EnvironmentError, ComposeParseError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    def cmd_export(self, args):
        """Export environment variables to file"""
        try:
            self.extractor.load_from_compose(args.compose_file, args.service)
            
            output_path = Path(args.output)
            self.extractor.export_environment(str(output_path), prefix=args.prefix)
            
            print(f"Environment variables exported to: {output_path}")
            
        except (EnvironmentError, ComposeParseError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    def cmd_info(self, args):
        """Show environment information"""
        try:
            self.extractor.load_from_compose(args.compose_file, args.service)
            
            stats = self.extractor.get_stats()
            
            print("Environment Information:")
            print(f"  Total variables: {stats['total_variables']}")
            print(f"  Telegram variables: {stats['telegram_vars']}")
            print(f"  Scheduler variables: {stats['scheduler_vars']}")
            print(f"  Database variables: {stats['database_vars']}")
            
            print(f"\nSources:")
            for source in stats['sources']:
                print(f"  - {source}")
            
            # Show variable breakdown
            telegram_vars = self.extractor.get_telegram_config()
            scheduler_vars = self.extractor.get_scheduler_config()
            database_vars = self.extractor.get_database_config()
            
            if telegram_vars:
                print(f"\nTelegram Configuration:")
                for key, value in telegram_vars.items():
                    masked_value = "*" * len(value) if 'HASH' in key or 'TOKEN' in key else value
                    print(f"  {key}: {masked_value}")
            
            if scheduler_vars:
                print(f"\nScheduler Configuration:")
                for key, value in scheduler_vars.items():
                    print(f"  {key}: {value}")
            
            if database_vars:
                print(f"\nDatabase Configuration:")
                for key, value in database_vars.items():
                    masked_value = "*" * len(value) if 'PASSWORD' in key or 'SECRET' in key else value
                    print(f"  {key}: {masked_value}")
            
        except (EnvironmentError, ComposeParseError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    def _validate_telegram_config(self) -> list:
        """Validate Telegram configuration"""
        errors = []
        telegram_vars = self.extractor.get_telegram_config()
        
        required_vars = ['TELEGRAM_API_ID', 'TELEGRAM_API_HASH']
        missing_vars = self.extractor.validate_required_variables(required_vars)
        
        # Check for alternative variable names
        if 'TELEGRAM_API_ID' in missing_vars:
            all_vars = self.extractor.get_environment()
            if not any(key in all_vars for key in ['API_ID', 'TG_API_ID']):
                errors.append("Missing Telegram API ID (TELEGRAM_API_ID, API_ID, or TG_API_ID)")
        
        if 'TELEGRAM_API_HASH' in missing_vars:
            all_vars = self.extractor.get_environment()
            if not any(key in all_vars for key in ['API_HASH', 'TG_API_HASH']):
                errors.append("Missing Telegram API Hash (TELEGRAM_API_HASH, API_HASH, or TG_API_HASH)")
        
        # Validate API ID format
        api_id = telegram_vars.get('TELEGRAM_API_ID')
        if api_id and not api_id.isdigit():
            errors.append("Telegram API ID must be numeric")
        
        return errors
    
    def _validate_scheduler_config(self) -> list:
        """Validate Scheduler configuration"""
        errors = []
        scheduler_vars = self.extractor.get_scheduler_config()
        
        # Check max workers
        max_workers = scheduler_vars.get('SCHEDULER_MAX_WORKERS')
        if max_workers:
            try:
                workers = int(max_workers)
                if workers <= 0:
                    errors.append("SCHEDULER_MAX_WORKERS must be positive")
            except ValueError:
                errors.append("SCHEDULER_MAX_WORKERS must be a number")
        
        # Check job store type
        job_store = scheduler_vars.get('SCHEDULER_JOB_STORE')
        if job_store and job_store.lower() not in ['memory', 'mongodb', 'sqlalchemy', 'redis']:
            errors.append(f"Invalid SCHEDULER_JOB_STORE: {job_store}")
        
        # Check MongoDB URI if using MongoDB job store
        if job_store and job_store.lower() == 'mongodb':
            all_vars = self.extractor.get_environment()
            mongodb_uri = (all_vars.get('SCHEDULER_MONGODB_URI') or
                          all_vars.get('MONGODB_URI') or
                          all_vars.get('MONGO_URI'))
            if not mongodb_uri:
                errors.append("MongoDB job store requires MONGODB_URI or MONGO_URI")
        
        return errors
    
    def run(self):
        """Run the CLI"""
        parser = self.create_parser()
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            return
        
        # Check if compose file exists
        if hasattr(args, 'compose_file'):
            compose_path = Path(args.compose_file)
            if not compose_path.exists():
                print(f"Error: Compose file not found: {args.compose_file}", file=sys.stderr)
                sys.exit(1)
        
        # Execute command
        command_method = getattr(self, f'cmd_{args.command}', None)
        if command_method:
            command_method(args)
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            sys.exit(1)


def main():
    """Main entry point"""
    cli = EnvironmentCLI()
    cli.run()


if __name__ == '__main__':
    main()