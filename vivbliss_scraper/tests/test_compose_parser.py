"""
Tests for Docker Compose file parser.
"""
import pytest
import tempfile
import os
from pathlib import Path
from vivbliss_scraper.config.compose_parser import ComposeParser, ComposeParseError


class TestComposeParser:
    """Test Docker Compose parser functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = ComposeParser()
        self.temp_dir = tempfile.mkdtemp()
    
    def test_parser_initialization(self):
        """Test parser initialization"""
        assert self.parser is not None
        assert hasattr(self.parser, 'parse_file')
        assert hasattr(self.parser, 'extract_environment')
    
    def test_parse_simple_compose_file(self):
        """Test parsing a simple compose file"""
        compose_content = """
version: '3.8'
services:
  app:
    image: myapp:latest
    environment:
      - DATABASE_URL=postgresql://localhost:5432/mydb
      - DEBUG=true
"""
        compose_file = Path(self.temp_dir) / "docker-compose.yml"
        compose_file.write_text(compose_content)
        
        result = self.parser.parse_file(str(compose_file))
        
        assert 'services' in result
        assert 'app' in result['services']
        assert 'environment' in result['services']['app']
    
    def test_parse_compose_with_env_file(self):
        """Test parsing compose file with env_file reference"""
        compose_content = """
version: '3.8'
services:
  app:
    image: myapp:latest
    env_file:
      - .env
      - .env.local
    environment:
      - NODE_ENV=production
"""
        compose_file = Path(self.temp_dir) / "docker-compose.yml"
        compose_file.write_text(compose_content)
        
        result = self.parser.parse_file(str(compose_file))
        
        assert 'env_file' in result['services']['app']
        assert isinstance(result['services']['app']['env_file'], list)
        assert len(result['services']['app']['env_file']) == 2
    
    def test_parse_compose_with_variable_substitution(self):
        """Test parsing compose file with variable substitution"""
        compose_content = """
version: '3.8'
services:
  db:
    image: postgres:13
    environment:
      POSTGRES_USER: ${DB_USER:-admin}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME:-myapp_db}
"""
        compose_file = Path(self.temp_dir) / "docker-compose.yml"
        compose_file.write_text(compose_content)
        
        result = self.parser.parse_file(str(compose_file))
        
        env = result['services']['db']['environment']
        assert 'POSTGRES_USER' in env
        assert 'POSTGRES_PASSWORD' in env
        assert 'POSTGRES_DB' in env
    
    def test_extract_environment_variables(self):
        """Test extracting environment variables from parsed compose"""
        compose_data = {
            'services': {
                'app': {
                    'environment': {
                        'DATABASE_URL': 'postgresql://localhost:5432/mydb',
                        'DEBUG': 'true',
                        'API_KEY': '${API_KEY}'
                    }
                },
                'worker': {
                    'environment': [
                        'WORKER_TIMEOUT=30',
                        'QUEUE_NAME=default'
                    ]
                }
            }
        }
        
        env_vars = self.parser.extract_environment(compose_data)
        
        assert 'DATABASE_URL' in env_vars
        assert 'DEBUG' in env_vars
        assert 'API_KEY' in env_vars
        assert 'WORKER_TIMEOUT' in env_vars
        assert 'QUEUE_NAME' in env_vars
        
        assert env_vars['DATABASE_URL'] == 'postgresql://localhost:5432/mydb'
        assert env_vars['DEBUG'] == 'true'
        assert env_vars['WORKER_TIMEOUT'] == '30'
    
    def test_extract_with_service_filter(self):
        """Test extracting environment variables for specific service"""
        compose_data = {
            'services': {
                'app': {
                    'environment': {
                        'APP_ENV': 'production'
                    }
                },
                'db': {
                    'environment': {
                        'POSTGRES_USER': 'admin'
                    }
                }
            }
        }
        
        env_vars = self.parser.extract_environment(compose_data, service_name='app')
        
        assert 'APP_ENV' in env_vars
        assert 'POSTGRES_USER' not in env_vars
    
    def test_parse_nonexistent_file(self):
        """Test parsing non-existent file raises error"""
        with pytest.raises(ComposeParseError, match="File not found"):
            self.parser.parse_file("/nonexistent/docker-compose.yml")
    
    def test_parse_invalid_yaml(self):
        """Test parsing invalid YAML raises error"""
        invalid_yaml = """
version: '3.8'
services:
  app:
    image: myapp
    environment:
      - INVALID_YAML: [unclosed bracket
"""
        compose_file = Path(self.temp_dir) / "invalid-compose.yml"
        compose_file.write_text(invalid_yaml)
        
        with pytest.raises(ComposeParseError, match="Invalid YAML"):
            self.parser.parse_file(str(compose_file))
    
    def test_extract_from_env_files(self):
        """Test extracting environment variables from referenced env files"""
        # Create env files
        env_file1 = Path(self.temp_dir) / ".env"
        env_file1.write_text("DATABASE_URL=postgres://localhost:5432/db\nDEBUG=true\n")
        
        env_file2 = Path(self.temp_dir) / ".env.local"
        env_file2.write_text("API_KEY=secret123\nDEBUG=false\n")  # DEBUG should override
        
        compose_content = f"""
version: '3.8'
services:
  app:
    image: myapp:latest
    env_file:
      - {env_file1}
      - {env_file2}
    environment:
      - NODE_ENV=production
"""
        compose_file = Path(self.temp_dir) / "docker-compose.yml"
        compose_file.write_text(compose_content)
        
        env_vars = self.parser.extract_environment_from_file(str(compose_file))
        
        assert 'DATABASE_URL' in env_vars
        assert 'DEBUG' in env_vars
        assert 'API_KEY' in env_vars
        assert 'NODE_ENV' in env_vars
        
        # Later env files and environment should override earlier ones
        assert env_vars['DEBUG'] == 'false'  # from .env.local
        assert env_vars['NODE_ENV'] == 'production'  # from environment
    
    def test_resolve_variable_substitution(self):
        """Test resolving variable substitution with defaults"""
        env_vars = {
            'EXISTING_VAR': 'existing_value'
        }
        
        # Test with existing variable
        result = self.parser.resolve_variable('${EXISTING_VAR}', env_vars)
        assert result == 'existing_value'
        
        # Test with default value
        result = self.parser.resolve_variable('${MISSING_VAR:-default_value}', env_vars)
        assert result == 'default_value'
        
        # Test with missing variable and no default
        result = self.parser.resolve_variable('${MISSING_VAR}', env_vars)
        assert result == '${MISSING_VAR}'  # Should remain unresolved
        
        # Test non-variable string
        result = self.parser.resolve_variable('plain_string', env_vars)
        assert result == 'plain_string'
    
    def test_multiple_services_extraction(self):
        """Test extracting environment from multiple services"""
        compose_content = """
version: '3.8'
services:
  web:
    image: nginx
    environment:
      - NGINX_PORT=80
  app:
    image: myapp
    environment:
      - APP_ENV=production
      - DATABASE_URL=postgresql://db:5432/app
  db:
    image: postgres
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secret
"""
        compose_file = Path(self.temp_dir) / "docker-compose.yml"
        compose_file.write_text(compose_content)
        
        env_vars = self.parser.extract_environment_from_file(str(compose_file))
        
        # Should include variables from all services
        assert 'NGINX_PORT' in env_vars
        assert 'APP_ENV' in env_vars
        assert 'DATABASE_URL' in env_vars
        assert 'POSTGRES_USER' in env_vars
        assert 'POSTGRES_PASSWORD' in env_vars
    
    def test_parse_compose_with_extends(self):
        """Test parsing compose file with extends (basic support)"""
        base_compose = Path(self.temp_dir) / "docker-compose.base.yml"
        base_compose.write_text("""
version: '3.8'
services:
  app:
    image: myapp:latest
    environment:
      - BASE_ENV=base_value
""")
        
        compose_content = f"""
version: '3.8'
services:
  app:
    extends:
      file: {base_compose}
      service: app
    environment:
      - OVERRIDE_ENV=override_value
"""
        compose_file = Path(self.temp_dir) / "docker-compose.yml"
        compose_file.write_text(compose_content)
        
        # Note: Full extends support might be complex, 
        # for now just ensure it doesn't crash
        result = self.parser.parse_file(str(compose_file))
        assert 'services' in result
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)


class TestComposeEnvironmentIntegration:
    """Test integration with environment loading"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = ComposeParser()
        self.temp_dir = tempfile.mkdtemp()
    
    def test_load_environment_with_current_env(self):
        """Test loading environment with current process environment"""
        # Set some environment variables
        os.environ['TEST_VAR'] = 'test_value'
        os.environ['DB_PASSWORD'] = 'secret'
        
        compose_content = """
version: '3.8'
services:
  app:
    environment:
      - TEST_VAR=${TEST_VAR}
      - DB_PASSWORD=${DB_PASSWORD}
      - DEFAULT_VAR=${MISSING_VAR:-default}
"""
        compose_file = Path(self.temp_dir) / "docker-compose.yml"
        compose_file.write_text(compose_content)
        
        env_vars = self.parser.extract_environment_from_file(
            str(compose_file), 
            resolve_variables=True
        )
        
        assert env_vars['TEST_VAR'] == 'test_value'
        assert env_vars['DB_PASSWORD'] == 'secret'
        assert env_vars['DEFAULT_VAR'] == 'default'
        
        # Clean up
        del os.environ['TEST_VAR']
        del os.environ['DB_PASSWORD']
    
    def test_priority_order(self):
        """Test that environment variables follow correct priority order"""
        # 1. Process environment (highest)
        # 2. compose environment section
        # 3. env_file (lowest)
        
        os.environ['PRIORITY_TEST'] = 'process_env'
        
        env_file = Path(self.temp_dir) / ".env"
        env_file.write_text("PRIORITY_TEST=env_file\nENV_FILE_ONLY=from_env_file\n")
        
        compose_content = f"""
version: '3.8'
services:
  app:
    env_file:
      - {env_file}
    environment:
      - PRIORITY_TEST=compose_env
      - COMPOSE_ONLY=from_compose
"""
        compose_file = Path(self.temp_dir) / "docker-compose.yml"
        compose_file.write_text(compose_content)
        
        env_vars = self.parser.extract_environment_from_file(
            str(compose_file),
            resolve_variables=True
        )
        
        # ComposeParser doesn't handle process env priority by itself
        # That's handled by EnvironmentExtractor
        # So compose environment should win here
        assert env_vars['PRIORITY_TEST'] == 'compose_env'
        assert env_vars['ENV_FILE_ONLY'] == 'from_env_file'
        assert env_vars['COMPOSE_ONLY'] == 'from_compose'
        
        # Clean up
        del os.environ['PRIORITY_TEST']
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)