"""
Environment variable extractor that supports Docker Compose files and .env files.
"""
import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from .compose_parser import ComposeParser, ComposeParseError


class EnvironmentError(Exception):
    """Exception raised when environment extraction fails"""
    pass


class EnvironmentExtractor:
    """
    Extracts and manages environment variables from multiple sources:
    - Docker Compose files
    - .env files  
    - Process environment
    """
    
    def __init__(self):
        """Initialize the environment extractor"""
        self.env_vars: Dict[str, str] = {}
        self.compose_parser = ComposeParser()
        
        # Track sources for debugging
        self.sources: List[str] = []
    
    def load_from_env_file(self, env_file_path: str) -> Dict[str, str]:
        """
        Load environment variables from a .env file.
        
        Args:
            env_file_path: Path to .env file
            
        Returns:
            Dictionary of environment variables from the file
            
        Raises:
            EnvironmentError: If file cannot be read
        """
        env_path = Path(env_file_path)
        if not env_path.exists():
            raise EnvironmentError(f"Environment file not found: {env_file_path}")
        
        env_vars = {}
        
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse KEY=value
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Handle quoted values
                        if len(value) >= 2:
                            if (value.startswith('"') and value.endswith('"')) or \
                               (value.startswith("'") and value.endswith("'")):
                                value = value[1:-1]
                        
                        env_vars[key] = value
                    else:
                        # Handle KEY without value (set to empty string)
                        key = line.strip()
                        if key and not key.startswith('#'):
                            env_vars[key] = ''
        
        except IOError as e:
            raise EnvironmentError(f"Cannot read environment file {env_file_path}: {e}")
        
        # Merge into main environment
        self.env_vars.update(env_vars)
        self.sources.append(f"env_file:{env_file_path}")
        
        return env_vars
    
    def load_from_compose(self, compose_file_path: str, 
                         service_name: Optional[str] = None) -> Dict[str, str]:
        """
        Load environment variables from a Docker Compose file.
        
        Args:
            compose_file_path: Path to docker-compose.yml
            service_name: If specified, load only from this service
            
        Returns:
            Dictionary of environment variables from compose file
            
        Raises:
            EnvironmentError: If compose file cannot be parsed
        """
        compose_path = Path(compose_file_path)
        if not compose_path.exists():
            raise EnvironmentError(f"Compose file not found: {compose_file_path}")
        
        try:
            env_vars = self.compose_parser.extract_environment_from_file(
                str(compose_path),
                service_name=service_name,
                resolve_variables=True
            )
            
            # Apply process environment priority override
            for key in list(env_vars.keys()):
                if key in os.environ:
                    env_vars[key] = os.environ[key]
            
            # Merge into main environment
            self.env_vars.update(env_vars)
            service_suffix = f":{service_name}" if service_name else ""
            self.sources.append(f"compose:{compose_file_path}{service_suffix}")
            
            return env_vars
            
        except ComposeParseError as e:
            raise EnvironmentError(f"Cannot parse compose file {compose_file_path}: {e}")
    
    def get_environment(self, prefix: Optional[str] = None) -> Dict[str, str]:
        """
        Get environment variables, optionally filtered by prefix.
        
        Args:
            prefix: If specified, return only variables starting with this prefix
            
        Returns:
            Dictionary of environment variables
        """
        if prefix:
            return {
                key: value for key, value in self.env_vars.items()
                if key.startswith(prefix)
            }
        else:
            return self.env_vars.copy()
    
    def apply_to_os_environment(self, prefix: Optional[str] = None, 
                               overwrite: bool = True) -> None:
        """
        Apply extracted environment variables to the process environment.
        
        Args:
            prefix: If specified, apply only variables starting with this prefix
            overwrite: Whether to overwrite existing environment variables
        """
        env_to_apply = self.get_environment(prefix)
        
        for key, value in env_to_apply.items():
            if overwrite or key not in os.environ:
                os.environ[key] = value
    
    def resolve_variables(self, variables: Dict[str, str]) -> Dict[str, str]:
        """
        Resolve variable references in a dictionary of variables.
        
        Args:
            variables: Dictionary containing variables that may reference others
            
        Returns:
            Dictionary with variable references resolved
        """
        # Combine with current environment and loaded variables
        context = dict(os.environ)
        context.update(self.env_vars)
        context.update(variables)
        
        resolved = {}
        for key, value in variables.items():
            resolved[key] = self.compose_parser.resolve_variable(value, context)
        
        return resolved
    
    def merge_environments(self, env_dicts: List[Dict[str, str]]) -> Dict[str, str]:
        """
        Merge multiple environment dictionaries.
        Later dictionaries override earlier ones.
        
        Args:
            env_dicts: List of environment dictionaries to merge
            
        Returns:
            Merged environment dictionary
        """
        merged = {}
        for env_dict in env_dicts:
            merged.update(env_dict)
        return merged
    
    def load_from_multiple_sources(self, sources: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Load environment variables from multiple sources in order.
        
        Args:
            sources: List of source configurations, each containing:
                    - type: 'env_file' or 'compose'
                    - path: file path
                    - service: (compose only) service name
                    
        Returns:
            Dictionary of all loaded environment variables
        """
        all_env_vars = {}
        
        for source in sources:
            source_type = source.get('type')
            source_path = source.get('path')
            
            if not source_path:
                continue
            
            try:
                if source_type == 'env_file':
                    env_vars = self.load_from_env_file(source_path)
                    all_env_vars.update(env_vars)
                    
                elif source_type == 'compose':
                    service_name = source.get('service')
                    env_vars = self.load_from_compose(source_path, service_name)
                    all_env_vars.update(env_vars)
                    
            except EnvironmentError as e:
                # Log error but continue with other sources
                print(f"Warning: Failed to load from {source}: {e}")
        
        return all_env_vars
    
    def get_telegram_config(self) -> Dict[str, str]:
        """
        Get environment variables for Telegram configuration.
        
        Returns:
            Dictionary of Telegram-related environment variables
        """
        return self.get_environment(prefix='TELEGRAM_')
    
    def get_scheduler_config(self) -> Dict[str, str]:
        """
        Get environment variables for Scheduler configuration.
        
        Returns:
            Dictionary of Scheduler-related environment variables
        """
        return self.get_environment(prefix='SCHEDULER_')
    
    def get_database_config(self) -> Dict[str, str]:
        """
        Get environment variables for Database configuration.
        
        Returns:
            Dictionary of Database-related environment variables
        """
        # Include both MONGO_ and DATABASE_ prefixes
        mongo_vars = self.get_environment(prefix='MONGO_')
        db_vars = self.get_environment(prefix='DATABASE_')
        
        combined = {}
        combined.update(mongo_vars)
        combined.update(db_vars)
        
        return combined
    
    def validate_required_variables(self, required_vars: List[str]) -> List[str]:
        """
        Validate that required environment variables are present.
        
        Args:
            required_vars: List of required variable names
            
        Returns:
            List of missing variable names
        """
        missing = []
        for var_name in required_vars:
            if var_name not in self.env_vars and var_name not in os.environ:
                missing.append(var_name)
        return missing
    
    def export_environment(self, file_path: str, prefix: Optional[str] = None) -> None:
        """
        Export environment variables to a .env file.
        
        Args:
            file_path: Path where to save the .env file
            prefix: If specified, export only variables starting with this prefix
        """
        env_to_export = self.get_environment(prefix)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# Environment variables exported by EnvironmentExtractor\n")
            f.write(f"# Sources: {', '.join(self.sources)}\n\n")
            
            for key, value in sorted(env_to_export.items()):
                # Escape special characters in values
                if ' ' in value or '"' in value or "'" in value:
                    # Use double quotes and escape internal quotes
                    escaped_value = value.replace('"', '\\"')
                    f.write(f'{key}="{escaped_value}"\n')
                else:
                    f.write(f'{key}={value}\n')
    
    def clear(self) -> None:
        """Clear all loaded environment variables and sources"""
        self.env_vars.clear()
        self.sources.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about loaded environment variables.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'total_variables': len(self.env_vars),
            'sources': self.sources.copy(),
            'telegram_vars': len(self.get_telegram_config()),
            'scheduler_vars': len(self.get_scheduler_config()),
            'database_vars': len(self.get_database_config())
        }