"""
Tests for environment variable extractor.
"""
import pytest
import tempfile
import os
from pathlib import Path
from vivbliss_scraper.config.env_extractor import EnvironmentExtractor, EnvironmentError


class TestEnvironmentExtractor:
    """Test environment variable extraction functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.extractor = EnvironmentExtractor()
        self.temp_dir = tempfile.mkdtemp()
    
    def test_extractor_initialization(self):
        """Test extractor initialization"""
        assert self.extractor is not None
        assert hasattr(self.extractor, 'load_from_compose')
        assert hasattr(self.extractor, 'load_from_env_file')
        assert hasattr(self.extractor, 'get_environment')
    
    def test_load_from_env_file(self):
        """Test loading environment variables from .env file"""
        env_content = """
# Database configuration
DATABASE_URL=postgresql://localhost:5432/mydb
DATABASE_USER=admin
DATABASE_PASSWORD=secret123

# Application settings
DEBUG=true
PORT=8000

# Empty lines and comments should be ignored

MULTILINE_VAR="line1
line2"
QUOTED_VAR='single quotes'
UNQUOTED_VAR=no_quotes
"""
        env_file = Path(self.temp_dir) / ".env"
        env_file.write_text(env_content)
        
        env_vars = self.extractor.load_from_env_file(str(env_file))
        
        assert env_vars['DATABASE_URL'] == 'postgresql://localhost:5432/mydb'
        assert env_vars['DATABASE_USER'] == 'admin'
        assert env_vars['DATABASE_PASSWORD'] == 'secret123'
        assert env_vars['DEBUG'] == 'true'
        assert env_vars['PORT'] == '8000'
        assert env_vars['QUOTED_VAR'] == 'single quotes'
        assert env_vars['UNQUOTED_VAR'] == 'no_quotes'
    
    def test_load_from_compose_file(self):
        """Test loading environment variables from docker-compose file"""
        compose_content = """
version: '3.8'
services:
  app:
    image: myapp:latest
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://db:5432/app
      - API_KEY=${API_KEY:-default_key}
  db:
    image: postgres:13
    environment:
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: secret
"""
        compose_file = Path(self.temp_dir) / "docker-compose.yml"
        compose_file.write_text(compose_content)
        
        env_vars = self.extractor.load_from_compose(str(compose_file))
        
        assert 'NODE_ENV' in env_vars
        assert 'DATABASE_URL' in env_vars
        assert 'API_KEY' in env_vars
        assert 'POSTGRES_USER' in env_vars
        assert 'POSTGRES_PASSWORD' in env_vars
    
    def test_load_from_compose_with_service_filter(self):
        """Test loading environment variables from specific service"""
        compose_content = """
version: '3.8'
services:
  web:
    environment:
      - WEB_PORT=80
  app:
    environment:
      - APP_ENV=production
      - DATABASE_URL=postgresql://db:5432/app
  db:
    environment:
      - POSTGRES_USER=admin
"""
        compose_file = Path(self.temp_dir) / "docker-compose.yml"
        compose_file.write_text(compose_content)
        
        # Load only from 'app' service
        env_vars = self.extractor.load_from_compose(str(compose_file), service_name='app')
        
        assert 'APP_ENV' in env_vars
        assert 'DATABASE_URL' in env_vars
        assert 'WEB_PORT' not in env_vars
        assert 'POSTGRES_USER' not in env_vars
    
    def test_load_multiple_sources(self):
        """Test loading from multiple sources with correct priority"""
        # Create .env file
        env_file = Path(self.temp_dir) / ".env"
        env_file.write_text("""
DATABASE_URL=postgresql://localhost:5432/local
DEBUG=false
ENV_FILE_VAR=from_env_file
""")
        
        # Create docker-compose file
        compose_content = f"""
version: '3.8'
services:
  app:
    env_file:
      - {env_file}
    environment:
      - DATABASE_URL=postgresql://compose:5432/compose
      - COMPOSE_VAR=from_compose
"""
        compose_file = Path(self.temp_dir) / "docker-compose.yml"
        compose_file.write_text(compose_content)
        
        # Set process environment variable
        os.environ['DATABASE_URL'] = 'postgresql://process:5432/process'
        os.environ['PROCESS_VAR'] = 'from_process'
        
        try:
            extractor = EnvironmentExtractor()
            extractor.load_from_compose(str(compose_file))
            
            env_vars = extractor.get_environment()
            
            # Process env should have highest priority
            assert env_vars['DATABASE_URL'] == 'postgresql://process:5432/process'
            
            # Variables from different sources
            assert env_vars['ENV_FILE_VAR'] == 'from_env_file'
            assert env_vars['COMPOSE_VAR'] == 'from_compose'
            
            # Process variables that are not in compose file won't be included
            # unless explicitly added
            assert 'PROCESS_VAR' not in env_vars  # This is expected behavior
            
        finally:
            # Clean up process environment
            del os.environ['DATABASE_URL']
            del os.environ['PROCESS_VAR']
    
    def test_get_environment_with_filtering(self):
        """Test getting environment variables with prefix filtering"""
        extractor = EnvironmentExtractor()
        extractor.env_vars = {
            'DATABASE_URL': 'postgresql://localhost:5432/db',
            'DATABASE_USER': 'admin',
            'API_KEY': 'secret',
            'DEBUG': 'true',
            'TELEGRAM_BOT_TOKEN': 'bot_token',
            'TELEGRAM_CHAT_ID': '123456'
        }
        
        # Get all variables
        all_vars = extractor.get_environment()
        assert len(all_vars) == 6
        
        # Get only database variables
        db_vars = extractor.get_environment(prefix='DATABASE_')
        assert len(db_vars) == 2
        assert 'DATABASE_URL' in db_vars
        assert 'DATABASE_USER' in db_vars
        assert 'API_KEY' not in db_vars
        
        # Get telegram variables
        telegram_vars = extractor.get_environment(prefix='TELEGRAM_')
        assert len(telegram_vars) == 2
        assert 'TELEGRAM_BOT_TOKEN' in telegram_vars
        assert 'TELEGRAM_CHAT_ID' in telegram_vars
    
    def test_apply_to_os_environment(self):
        """Test applying extracted variables to OS environment"""
        extractor = EnvironmentExtractor()
        extractor.env_vars = {
            'TEST_VAR_1': 'value1',
            'TEST_VAR_2': 'value2'
        }
        
        # Ensure variables are not in OS env
        assert 'TEST_VAR_1' not in os.environ
        assert 'TEST_VAR_2' not in os.environ
        
        # Apply to OS environment
        extractor.apply_to_os_environment()
        
        # Check they are now in OS environment
        assert os.environ.get('TEST_VAR_1') == 'value1'
        assert os.environ.get('TEST_VAR_2') == 'value2'
        
        # Clean up
        del os.environ['TEST_VAR_1']
        del os.environ['TEST_VAR_2']
    
    def test_apply_with_prefix_filter(self):
        """Test applying only variables with specific prefix"""
        extractor = EnvironmentExtractor()
        extractor.env_vars = {
            'DATABASE_URL': 'postgresql://localhost:5432/db',
            'API_KEY': 'secret',
            'TELEGRAM_BOT_TOKEN': 'bot_token'
        }
        
        # Apply only DATABASE_ variables
        extractor.apply_to_os_environment(prefix='DATABASE_')
        
        assert os.environ.get('DATABASE_URL') == 'postgresql://localhost:5432/db'
        assert 'API_KEY' not in os.environ
        assert 'TELEGRAM_BOT_TOKEN' not in os.environ
        
        # Clean up
        del os.environ['DATABASE_URL']
    
    def test_load_nonexistent_env_file(self):
        """Test loading non-existent env file raises error"""
        with pytest.raises(EnvironmentError, match="Environment file not found"):
            self.extractor.load_from_env_file("/nonexistent/.env")
    
    def test_load_nonexistent_compose_file(self):
        """Test loading non-existent compose file raises error"""
        with pytest.raises(EnvironmentError, match="Compose file not found"):
            self.extractor.load_from_compose("/nonexistent/docker-compose.yml")
    
    def test_variable_resolution(self):
        """Test resolving variable references"""
        # Set up base variables
        base_vars = {
            'BASE_URL': 'https://api.example.com',
            'VERSION': 'v1'
        }
        
        extractor = EnvironmentExtractor()
        extractor.env_vars = base_vars.copy()
        
        # Test resolving variables with references
        test_vars = {
            'API_ENDPOINT': '${BASE_URL}/${VERSION}/users',
            'FALLBACK_VAR': '${MISSING_VAR:-default_value}',
            'NESTED_VAR': '${BASE_URL}/api/${VERSION}'
        }
        
        resolved = extractor.resolve_variables(test_vars)
        
        assert resolved['API_ENDPOINT'] == 'https://api.example.com/v1/users'
        assert resolved['FALLBACK_VAR'] == 'default_value'
        assert resolved['NESTED_VAR'] == 'https://api.example.com/api/v1'
    
    def test_merge_environments(self):
        """Test merging multiple environment dictionaries"""
        env1 = {'VAR1': 'value1', 'SHARED': 'from_env1'}
        env2 = {'VAR2': 'value2', 'SHARED': 'from_env2'}
        env3 = {'VAR3': 'value3', 'SHARED': 'from_env3'}
        
        merged = self.extractor.merge_environments([env1, env2, env3])
        
        # Later environments should override earlier ones
        assert merged['SHARED'] == 'from_env3'
        assert merged['VAR1'] == 'value1'
        assert merged['VAR2'] == 'value2'
        assert merged['VAR3'] == 'value3'
    
    def test_extract_with_docker_compose_override(self):
        """Test extracting from docker-compose with override files"""
        # Create base compose file
        base_compose = Path(self.temp_dir) / "docker-compose.yml"
        base_compose.write_text("""
version: '3.8'
services:
  app:
    environment:
      - BASE_VAR=base_value
      - OVERRIDE_VAR=base_override
""")
        
        # Create override compose file
        override_compose = Path(self.temp_dir) / "docker-compose.override.yml"
        override_compose.write_text("""
version: '3.8'
services:
  app:
    environment:
      - OVERRIDE_VAR=override_value
      - NEW_VAR=new_value
""")
        
        extractor = EnvironmentExtractor()
        
        # Load base file
        extractor.load_from_compose(str(base_compose))
        
        # Load override file (should merge/override)
        extractor.load_from_compose(str(override_compose))
        
        env_vars = extractor.get_environment()
        
        assert env_vars['BASE_VAR'] == 'base_value'
        assert env_vars['OVERRIDE_VAR'] == 'override_value'  # Should be overridden
        assert env_vars['NEW_VAR'] == 'new_value'
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)


class TestEnvironmentExtractorConfiguration:
    """Test environment extractor configuration and integration"""
    
    def test_configure_for_telegram(self):
        """Test configuring environment for Telegram integration"""
        extractor = EnvironmentExtractor()
        extractor.env_vars = {
            'TELEGRAM_API_ID': '12345',
            'TELEGRAM_API_HASH': 'abcdef123456',
            'TELEGRAM_SESSION_NAME': 'test_session',
            'TELEGRAM_CHAT_ID': '987654321',
            'OTHER_VAR': 'other_value'
        }
        
        telegram_config = extractor.get_environment(prefix='TELEGRAM_')
        
        assert len(telegram_config) == 4
        assert 'TELEGRAM_API_ID' in telegram_config
        assert 'TELEGRAM_API_HASH' in telegram_config
        assert 'TELEGRAM_SESSION_NAME' in telegram_config
        assert 'TELEGRAM_CHAT_ID' in telegram_config
        assert 'OTHER_VAR' not in telegram_config
    
    def test_configure_for_scheduler(self):
        """Test configuring environment for Scheduler"""
        extractor = EnvironmentExtractor()
        extractor.env_vars = {
            'SCHEDULER_TIMEZONE': 'Asia/Shanghai',
            'SCHEDULER_MAX_WORKERS': '10',
            'SCHEDULER_JOB_STORE': 'mongodb',
            'MONGODB_URI': 'mongodb://localhost:27017',
            'OTHER_VAR': 'other_value'
        }
        
        scheduler_config = extractor.get_environment(prefix='SCHEDULER_')
        
        assert len(scheduler_config) == 3
        assert 'SCHEDULER_TIMEZONE' in scheduler_config
        assert 'SCHEDULER_MAX_WORKERS' in scheduler_config
        assert 'SCHEDULER_JOB_STORE' in scheduler_config
        assert 'MONGODB_URI' not in scheduler_config
    
    def test_integration_with_existing_configs(self):
        """Test integration with existing configuration classes"""
        extractor = EnvironmentExtractor()
        extractor.env_vars = {
            'TELEGRAM_API_ID': '12345',
            'TELEGRAM_API_HASH': 'abcdef123456',
            'SCHEDULER_TIMEZONE': 'Asia/Shanghai',
            'MONGO_URI': 'mongodb://localhost:27017',
            'DEBUG': 'true'
        }
        
        # Test that we can extract relevant configs for different components
        telegram_vars = extractor.get_environment(prefix='TELEGRAM_')
        scheduler_vars = extractor.get_environment(prefix='SCHEDULER_')
        
        # Should be able to create config objects (integration test)
        assert len(telegram_vars) == 2
        assert len(scheduler_vars) == 1
        
        # Test getting all environment
        all_vars = extractor.get_environment()
        assert len(all_vars) == 5