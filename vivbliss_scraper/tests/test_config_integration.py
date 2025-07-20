"""
Tests for configuration integration with Docker Compose environment loading.
"""
import pytest
import tempfile
import os
from pathlib import Path
from vivbliss_scraper.config.env_extractor import EnvironmentExtractor
from vivbliss_scraper.telegram.config import TelegramConfig
from vivbliss_scraper.scheduler.config import SchedulerConfig


class TestConfigurationIntegration:
    """Test integration between environment loading and existing configs"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.extractor = EnvironmentExtractor()
    
    def test_telegram_config_from_compose(self):
        """Test creating TelegramConfig from Docker Compose environment"""
        compose_content = """
version: '3.8'
services:
  scraper:
    image: vivbliss-scraper:latest
    environment:
      - TELEGRAM_API_ID=12345
      - TELEGRAM_API_HASH=abcdef123456789
      - TELEGRAM_SESSION_NAME=vivbliss_session
      - TELEGRAM_CHAT_ID=987654321
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
"""
        compose_file = Path(self.temp_dir) / "docker-compose.yml"
        compose_file.write_text(compose_content)
        
        # Set bot token in process environment
        os.environ['TELEGRAM_BOT_TOKEN'] = 'bot123456:ABCDEF123456789'
        
        try:
            # Load environment from compose
            self.extractor.load_from_compose(str(compose_file))
            telegram_vars = self.extractor.get_environment(prefix='TELEGRAM_')
            
            # Test that we can create TelegramConfig with these variables
            # Note: This would require actual TelegramConfig modification to accept env vars
            assert 'TELEGRAM_API_ID' in telegram_vars
            assert 'TELEGRAM_API_HASH' in telegram_vars
            assert 'TELEGRAM_SESSION_NAME' in telegram_vars
            assert 'TELEGRAM_CHAT_ID' in telegram_vars
            assert 'TELEGRAM_BOT_TOKEN' in telegram_vars
            
            assert telegram_vars['TELEGRAM_API_ID'] == '12345'
            assert telegram_vars['TELEGRAM_BOT_TOKEN'] == 'bot123456:ABCDEF123456789'
            
        finally:
            del os.environ['TELEGRAM_BOT_TOKEN']
    
    def test_scheduler_config_from_compose(self):
        """Test creating SchedulerConfig from Docker Compose environment"""
        compose_content = """
version: '3.8'
services:
  scheduler:
    image: vivbliss-scraper:latest
    environment:
      - SCHEDULER_TIMEZONE=Asia/Shanghai
      - SCHEDULER_MAX_WORKERS=10
      - SCHEDULER_JOB_STORE=mongodb
      - SCHEDULER_MISFIRE_GRACE_TIME=120
      - MONGODB_URI=mongodb://mongodb:27017
      - MONGODB_DATABASE=scheduler_db
"""
        compose_file = Path(self.temp_dir) / "docker-compose.yml"
        compose_file.write_text(compose_content)
        
        # Load environment from compose
        self.extractor.load_from_compose(str(compose_file))
        scheduler_vars = self.extractor.get_environment(prefix='SCHEDULER_')
        
        # Test scheduler-specific variables
        assert 'SCHEDULER_TIMEZONE' in scheduler_vars
        assert 'SCHEDULER_MAX_WORKERS' in scheduler_vars
        assert 'SCHEDULER_JOB_STORE' in scheduler_vars
        assert 'SCHEDULER_MISFIRE_GRACE_TIME' in scheduler_vars
        
        assert scheduler_vars['SCHEDULER_TIMEZONE'] == 'Asia/Shanghai'
        assert scheduler_vars['SCHEDULER_MAX_WORKERS'] == '10'
        assert scheduler_vars['SCHEDULER_JOB_STORE'] == 'mongodb'
    
    def test_multi_service_environment_extraction(self):
        """Test extracting environment from multiple services"""
        compose_content = """
version: '3.8'
services:
  web:
    image: nginx
    environment:
      - NGINX_PORT=80
      - NGINX_WORKER_PROCESSES=4
  
  app:
    image: vivbliss-scraper:latest
    environment:
      - TELEGRAM_API_ID=12345
      - TELEGRAM_API_HASH=abcdef123456789
      - DATABASE_URL=postgresql://db:5432/app
      - DEBUG=true
  
  scheduler:
    image: vivbliss-scraper:latest
    environment:
      - SCHEDULER_TIMEZONE=UTC
      - SCHEDULER_MAX_WORKERS=5
      - DATABASE_URL=postgresql://db:5432/scheduler
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=secret
      - POSTGRES_DB=vivbliss
"""
        compose_file = Path(self.temp_dir) / "docker-compose.yml"
        compose_file.write_text(compose_content)
        
        # Load all services
        self.extractor.load_from_compose(str(compose_file))
        all_vars = self.extractor.get_environment()
        
        # Should include variables from all services
        assert 'NGINX_PORT' in all_vars
        assert 'TELEGRAM_API_ID' in all_vars
        assert 'SCHEDULER_TIMEZONE' in all_vars
        assert 'POSTGRES_USER' in all_vars
        
        # Test service-specific extraction
        app_vars = self.extractor.load_from_compose(str(compose_file), service_name='app')
        assert 'TELEGRAM_API_ID' in app_vars
        assert 'NGINX_PORT' not in app_vars
        assert 'POSTGRES_USER' not in app_vars
    
    def test_env_file_and_compose_integration(self):
        """Test integration of env_file and compose environment"""
        # Create .env file
        env_file = Path(self.temp_dir) / ".env"
        env_file.write_text("""
# Common settings
DATABASE_URL=postgresql://localhost:5432/local
DEBUG=false

# Telegram settings
TELEGRAM_API_ID=12345
TELEGRAM_API_HASH=abcdef123456789

# Scheduler settings
SCHEDULER_TIMEZONE=UTC
SCHEDULER_MAX_WORKERS=5
""")
        
        # Create production .env file
        prod_env_file = Path(self.temp_dir) / ".env.production"
        prod_env_file.write_text("""
# Production overrides
DATABASE_URL=postgresql://prod-db:5432/vivbliss
DEBUG=false
SCHEDULER_MAX_WORKERS=10
""")
        
        compose_content = f"""
version: '3.8'
services:
  app:
    image: vivbliss-scraper:latest
    env_file:
      - {env_file}
      - {prod_env_file}
    environment:
      - NODE_ENV=production
      - TELEGRAM_SESSION_NAME=prod_session
      # This should override the env file value
      - SCHEDULER_TIMEZONE=Asia/Shanghai
"""
        compose_file = Path(self.temp_dir) / "docker-compose.yml"
        compose_file.write_text(compose_content)
        
        # Load and test
        self.extractor.load_from_compose(str(compose_file))
        env_vars = self.extractor.get_environment()
        
        # Test that compose environment overrides env_file
        assert env_vars['SCHEDULER_TIMEZONE'] == 'Asia/Shanghai'
        
        # Test that production env file overrides base env file
        assert env_vars['SCHEDULER_MAX_WORKERS'] == '10'
        assert env_vars['DATABASE_URL'] == 'postgresql://prod-db:5432/vivbliss'
        
        # Test that unique values are preserved
        assert env_vars['TELEGRAM_API_ID'] == '12345'
        assert env_vars['NODE_ENV'] == 'production'
        assert env_vars['TELEGRAM_SESSION_NAME'] == 'prod_session'
    
    def test_variable_substitution_with_defaults(self):
        """Test variable substitution with default values"""
        compose_content = """
version: '3.8'
services:
  app:
    environment:
      # Using defaults for missing variables
      - DATABASE_HOST=${DB_HOST:-localhost}
      - DATABASE_PORT=${DB_PORT:-5432}
      - DATABASE_NAME=${DB_NAME:-vivbliss}
      
      # Using existing process environment
      - API_SECRET=${API_SECRET}
      
      # Telegram config with defaults
      - TELEGRAM_API_ID=${TELEGRAM_API_ID:-12345}
      - TELEGRAM_API_HASH=${TELEGRAM_API_HASH:-default_hash}
      
      # Complex substitution
      - DATABASE_URL=postgresql://${DB_HOST:-localhost}:${DB_PORT:-5432}/${DB_NAME:-vivbliss}
"""
        compose_file = Path(self.temp_dir) / "docker-compose.yml"
        compose_file.write_text(compose_content)
        
        # Set some process environment variables
        os.environ['API_SECRET'] = 'super_secret_key'
        os.environ['DB_HOST'] = 'production-db'
        
        try:
            # Use compose parser directly with resolve_variables=True
            from vivbliss_scraper.config import ComposeParser
            parser = ComposeParser()
            env_vars = parser.extract_environment_from_file(
                str(compose_file), 
                resolve_variables=True
            )
            
            # Test defaults are used for missing variables
            assert env_vars['DATABASE_PORT'] == '5432'
            assert env_vars['DATABASE_NAME'] == 'vivbliss'
            assert env_vars['TELEGRAM_API_ID'] == '12345'
            assert env_vars['TELEGRAM_API_HASH'] == 'default_hash'
            
            # Test process environment is used
            assert env_vars['API_SECRET'] == 'super_secret_key'
            assert env_vars['DATABASE_HOST'] == 'production-db'
            
            # Test complex substitution
            expected_db_url = 'postgresql://production-db:5432/vivbliss'
            assert env_vars['DATABASE_URL'] == expected_db_url
            
        finally:
            del os.environ['API_SECRET']
            del os.environ['DB_HOST']
    
    def test_configuration_factory_pattern(self):
        """Test using environment extractor in a factory pattern"""
        compose_content = """
version: '3.8'
services:
  app:
    environment:
      # Telegram configuration
      - TELEGRAM_API_ID=12345
      - TELEGRAM_API_HASH=abcdef123456789
      - TELEGRAM_SESSION_NAME=test_session
      
      # Scheduler configuration  
      - SCHEDULER_TIMEZONE=Asia/Shanghai
      - SCHEDULER_MAX_WORKERS=8
      - SCHEDULER_JOB_STORE=memory
      
      # Database configuration
      - MONGO_URI=mongodb://mongodb:27017
      - MONGO_DATABASE=vivbliss_test
"""
        compose_file = Path(self.temp_dir) / "docker-compose.yml"
        compose_file.write_text(compose_content)
        
        # Load environment
        self.extractor.load_from_compose(str(compose_file))
        
        # Test factory-like creation of configs
        def create_telegram_config():
            telegram_env = self.extractor.get_environment(prefix='TELEGRAM_')
            # This would be the actual integration:
            # return TelegramConfig.from_environment(telegram_env)
            return telegram_env
        
        def create_scheduler_config():
            scheduler_env = self.extractor.get_environment(prefix='SCHEDULER_')
            # This would be the actual integration:
            # return SchedulerConfig.from_environment(scheduler_env)
            return scheduler_env
        
        telegram_config = create_telegram_config()
        scheduler_config = create_scheduler_config()
        
        # Verify configurations
        assert telegram_config['TELEGRAM_API_ID'] == '12345'
        assert telegram_config['TELEGRAM_SESSION_NAME'] == 'test_session'
        
        assert scheduler_config['SCHEDULER_TIMEZONE'] == 'Asia/Shanghai'
        assert scheduler_config['SCHEDULER_MAX_WORKERS'] == '8'
    
    def test_environment_validation(self):
        """Test validation of environment variables"""
        compose_content = """
version: '3.8'
services:
  app:
    environment:
      # Valid configurations
      - TELEGRAM_API_ID=12345
      - SCHEDULER_MAX_WORKERS=5
      
      # Invalid configurations (should be caught by validation)
      - INVALID_TELEGRAM_API_ID=not_a_number
      - INVALID_SCHEDULER_MAX_WORKERS=not_a_number
"""
        compose_file = Path(self.temp_dir) / "docker-compose.yml"
        compose_file.write_text(compose_content)
        
        self.extractor.load_from_compose(str(compose_file))
        env_vars = self.extractor.get_environment()
        
        # Test that we have the variables (validation would be in config classes)
        assert 'TELEGRAM_API_ID' in env_vars
        assert 'INVALID_TELEGRAM_API_ID' in env_vars
        assert 'SCHEDULER_MAX_WORKERS' in env_vars
        assert 'INVALID_SCHEDULER_MAX_WORKERS' in env_vars
        
        # Validation logic would be implemented in the config classes:
        # try:
        #     TelegramConfig.from_environment(telegram_vars)
        # except ValueError as e:
        #     assert "Invalid API ID" in str(e)
    
    def test_compose_override_files_support(self):
        """Test support for docker-compose override files"""
        # Base compose file
        base_compose = Path(self.temp_dir) / "docker-compose.yml"
        base_compose.write_text("""
version: '3.8'
services:
  app:
    environment:
      - TELEGRAM_API_ID=12345
      - DATABASE_URL=postgresql://localhost:5432/dev
      - DEBUG=true
""")
        
        # Production override
        prod_override = Path(self.temp_dir) / "docker-compose.prod.yml"
        prod_override.write_text("""
version: '3.8'
services:
  app:
    environment:
      - DATABASE_URL=postgresql://prod-db:5432/production
      - DEBUG=false
      - TELEGRAM_SESSION_NAME=production_session
""")
        
        # Load base configuration
        extractor1 = EnvironmentExtractor()
        extractor1.load_from_compose(str(base_compose))
        base_vars = extractor1.get_environment()
        
        # Load with production override
        extractor2 = EnvironmentExtractor()
        extractor2.load_from_compose(str(base_compose))
        extractor2.load_from_compose(str(prod_override))  # This should merge/override
        prod_vars = extractor2.get_environment()
        
        # Test base configuration
        assert base_vars['DATABASE_URL'] == 'postgresql://localhost:5432/dev'
        assert base_vars['DEBUG'] == 'true'
        assert 'TELEGRAM_SESSION_NAME' not in base_vars
        
        # Test production configuration (overridden)
        assert prod_vars['DATABASE_URL'] == 'postgresql://prod-db:5432/production'
        assert prod_vars['DEBUG'] == 'false'
        assert prod_vars['TELEGRAM_SESSION_NAME'] == 'production_session'
        assert prod_vars['TELEGRAM_API_ID'] == '12345'  # Should be preserved
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)