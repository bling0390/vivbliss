"""
Docker Compose file parser for extracting environment variables.
"""
import re
import os
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Union


class ComposeParseError(Exception):
    """Exception raised when parsing Docker Compose files fails"""
    pass


class ComposeParser:
    """Parser for Docker Compose YAML files"""
    
    def __init__(self):
        """Initialize the compose parser"""
        # Pattern for variable substitution: ${VAR} or ${VAR:-default}
        self.var_pattern = re.compile(r'\$\{([^}]+)\}')
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a Docker Compose YAML file.
        
        Args:
            file_path: Path to the docker-compose.yml file
            
        Returns:
            Parsed compose file as dictionary
            
        Raises:
            ComposeParseError: If file cannot be read or parsed
        """
        try:
            compose_path = Path(file_path)
            if not compose_path.exists():
                raise ComposeParseError(f"File not found: {file_path}")
            
            with open(compose_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse YAML
            try:
                data = yaml.safe_load(content)
                if not isinstance(data, dict):
                    raise ComposeParseError(f"Invalid compose file structure: {file_path}")
                
                return data
                
            except yaml.YAMLError as e:
                raise ComposeParseError(f"Invalid YAML in {file_path}: {e}")
                
        except IOError as e:
            raise ComposeParseError(f"Cannot read file {file_path}: {e}")
    
    def extract_environment(self, compose_data: Dict[str, Any], 
                          service_name: Optional[str] = None) -> Dict[str, str]:
        """
        Extract environment variables from parsed compose data.
        
        Args:
            compose_data: Parsed compose file data
            service_name: If specified, extract only from this service
            
        Returns:
            Dictionary of environment variables
        """
        env_vars = {}
        
        if 'services' not in compose_data:
            return env_vars
        
        services = compose_data['services']
        if service_name:
            services = {service_name: services.get(service_name, {})}
        
        for svc_name, service_config in services.items():
            if not isinstance(service_config, dict):
                continue
            
            # Extract from 'environment' section
            if 'environment' in service_config:
                env_section = service_config['environment']
                
                if isinstance(env_section, list):
                    # Format: ["KEY=value", "KEY2=value2"]
                    for env_var in env_section:
                        if isinstance(env_var, str) and '=' in env_var:
                            key, value = env_var.split('=', 1)
                            env_vars[key.strip()] = value.strip()
                
                elif isinstance(env_section, dict):
                    # Format: {"KEY": "value", "KEY2": "value2"}
                    for key, value in env_section.items():
                        env_vars[str(key)] = str(value) if value is not None else ''
        
        return env_vars
    
    def extract_environment_from_file(self, file_path: str, 
                                    service_name: Optional[str] = None,
                                    resolve_variables: bool = False) -> Dict[str, str]:
        """
        Extract environment variables from a compose file, including env_file references.
        
        Args:
            file_path: Path to docker-compose.yml
            service_name: If specified, extract only from this service
            resolve_variables: Whether to resolve variable substitutions
            
        Returns:
            Dictionary of environment variables
        """
        compose_data = self.parse_file(file_path)
        compose_dir = Path(file_path).parent
        
        # Start with variables from env_file references
        env_vars = {}
        
        if 'services' in compose_data:
            services = compose_data['services']
            if service_name:
                services = {service_name: services.get(service_name, {})}
            
            for svc_name, service_config in services.items():
                if not isinstance(service_config, dict):
                    continue
                
                # Load from env_file references first (lower priority)
                if 'env_file' in service_config:
                    env_files = service_config['env_file']
                    if isinstance(env_files, str):
                        env_files = [env_files]
                    
                    for env_file in env_files:
                        env_file_path = compose_dir / env_file
                        if env_file_path.exists():
                            file_vars = self._parse_env_file(env_file_path)
                            env_vars.update(file_vars)
        
        # Then add/override with environment section (higher priority)
        compose_env_vars = self.extract_environment(compose_data, service_name)
        env_vars.update(compose_env_vars)
        
        # Resolve variable substitutions if requested
        if resolve_variables:
            env_vars = self._resolve_all_variables(env_vars)
        
        return env_vars
    
    def resolve_variable(self, value: str, env_vars: Dict[str, str]) -> str:
        """
        Resolve variable substitution in a value.
        
        Args:
            value: String that may contain variable references
            env_vars: Available environment variables
            
        Returns:
            String with variables resolved
        """
        if not isinstance(value, str):
            return str(value)
        
        def replace_var(match):
            var_expr = match.group(1)
            
            # Handle default values: VAR:-default
            if ':-' in var_expr:
                var_name, default_value = var_expr.split(':-', 1)
                # Check process environment first, then provided env_vars, then use default
                if var_name in os.environ:
                    return os.environ[var_name]
                elif var_name in env_vars:
                    return env_vars[var_name]
                else:
                    return default_value
            else:
                # No default, use process environment or provided env_vars
                var_name = var_expr
                if var_name in os.environ:
                    return os.environ[var_name]
                elif var_name in env_vars:
                    return env_vars[var_name]
                else:
                    return match.group(0)  # Return unresolved
        
        return self.var_pattern.sub(replace_var, value)
    
    def _parse_env_file(self, env_file_path: Path) -> Dict[str, str]:
        """
        Parse a .env file and return environment variables.
        
        Args:
            env_file_path: Path to .env file
            
        Returns:
            Dictionary of environment variables
        """
        env_vars = {}
        
        try:
            with open(env_file_path, 'r', encoding='utf-8') as f:
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
                        
                        # Remove quotes if present
                        if (value.startswith('"') and value.endswith('"')) or \
                           (value.startswith("'") and value.endswith("'")):
                            value = value[1:-1]
                        
                        env_vars[key] = value
                        
        except IOError:
            # If env file doesn't exist, just skip it
            pass
        
        return env_vars
    
    def _resolve_all_variables(self, env_vars: Dict[str, str]) -> Dict[str, str]:
        """
        Resolve all variable substitutions in environment variables.
        
        Args:
            env_vars: Environment variables that may contain substitutions
            
        Returns:
            Environment variables with substitutions resolved
        """
        resolved = {}
        
        # Start with process environment for highest priority resolution context
        resolution_context = dict(os.environ)
        
        # Don't add env_vars to context as they may contain unresolved references
        # Only add resolved values as we compute them
        
        for key, value in env_vars.items():
            # Resolve this variable without including its own unresolved value in context
            resolved_value = self.resolve_variable(value, resolution_context)
            resolved[key] = resolved_value
            
            # Add resolved value to context for future resolutions
            resolution_context[key] = resolved_value
        
        return resolved