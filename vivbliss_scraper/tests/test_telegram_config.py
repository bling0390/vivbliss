import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from vivbliss_scraper.telegram.config import TelegramConfig


class TestTelegramConfig:
    
    def test_init_with_valid_credentials(self):
        """Test TelegramConfig initialization with valid credentials"""
        config = TelegramConfig(
            api_id="12345",
            api_hash="test_hash",
            session_name="test_session"
        )
        
        assert config.api_id == 12345
        assert config.api_hash == "test_hash"
        assert config.session_name == "test_session"
    
    def test_init_with_missing_api_id_raises_error(self):
        """Test that missing api_id raises ValueError"""
        with pytest.raises(ValueError, match="api_id is required"):
            TelegramConfig(
                api_id="",
                api_hash="test_hash",
                session_name="test_session"
            )
    
    def test_init_with_missing_api_hash_raises_error(self):
        """Test that missing api_hash raises ValueError"""
        with pytest.raises(ValueError, match="api_hash is required"):
            TelegramConfig(
                api_id="12345",
                api_hash="",
                session_name="test_session"
            )
    
    def test_init_with_missing_session_name_raises_error(self):
        """Test that missing session_name raises ValueError"""
        with pytest.raises(ValueError, match="session_name is required"):
            TelegramConfig(
                api_id="12345",
                api_hash="test_hash",
                session_name=""
            )
    
    @pytest.mark.asyncio
    async def test_create_client_returns_pyrogram_client(self):
        """Test that create_client returns a Pyrogram client instance"""
        config = TelegramConfig(
            api_id="12345",
            api_hash="test_hash",
            session_name="test_session"
        )
        
        with patch('vivbliss_scraper.telegram.config.Client') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value = mock_instance
            
            client = await config.create_client()
            
            mock_client.assert_called_once_with(
                name="test_session",
                api_id=12345,
                api_hash="test_hash"
            )
            assert client == mock_instance
    
    @pytest.mark.asyncio
    async def test_validate_client_connection_success(self):
        """Test successful client connection validation"""
        config = TelegramConfig(
            api_id="12345",
            api_hash="test_hash",
            session_name="test_session"
        )
        
        mock_client = AsyncMock()
        mock_client.get_me.return_value = Mock(id=123456, username="test_user")
        
        result = await config.validate_client_connection(mock_client)
        
        assert result is True
        mock_client.get_me.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_validate_client_connection_failure(self):
        """Test client connection validation failure"""
        config = TelegramConfig(
            api_id="12345",
            api_hash="test_hash",
            session_name="test_session"
        )
        
        mock_client = AsyncMock()
        mock_client.get_me.side_effect = Exception("Connection failed")
        
        result = await config.validate_client_connection(mock_client)
        
        assert result is False
        mock_client.get_me.assert_called_once()
    
    def test_init_with_bot_token(self):
        """Test TelegramConfig initialization with bot token"""
        config = TelegramConfig(
            api_id="12345",
            api_hash="test_hash",
            session_name="test_session",
            bot_token="123456:ABCdefGHIjklMNOpqrSTUvwxYZ"
        )
        
        assert config.api_id == 12345
        assert config.api_hash == "test_hash"
        assert config.session_name == "test_session"
        assert config.bot_token == "123456:ABCdefGHIjklMNOpqrSTUvwxYZ"
    
    def test_init_with_invalid_bot_token_raises_error(self):
        """Test that invalid bot token format raises ValueError"""
        with pytest.raises(ValueError, match="Invalid bot token format"):
            TelegramConfig(
                api_id="12345",
                api_hash="test_hash",
                session_name="test_session",
                bot_token="invalid_token"
            )
    
    @pytest.mark.asyncio
    async def test_create_client_with_bot_token(self):
        """Test that create_client uses bot token when provided"""
        config = TelegramConfig(
            api_id="12345",
            api_hash="test_hash",
            session_name="test_session",
            bot_token="123456:ABCdefGHIjklMNOpqrSTUvwxYZ"
        )
        
        with patch('vivbliss_scraper.telegram.config.Client') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value = mock_instance
            
            client = await config.create_client()
            
            mock_client.assert_called_once_with(
                name="test_session",
                api_id=12345,
                api_hash="test_hash",
                bot_token="123456:ABCdefGHIjklMNOpqrSTUvwxYZ"
            )
            assert client == mock_instance
    
    def test_from_environment_with_bot_token(self):
        """Test creating config from environment with bot token"""
        env_vars = {
            'TELEGRAM_API_ID': '12345',
            'TELEGRAM_API_HASH': 'test_hash',
            'TELEGRAM_SESSION_NAME': 'test_session',
            'TELEGRAM_BOT_TOKEN': '123456:ABCdefGHIjklMNOpqrSTUvwxYZ'
        }
        
        config = TelegramConfig.from_environment(env_vars)
        
        assert config.api_id == 12345
        assert config.api_hash == "test_hash"
        assert config.session_name == "test_session"
        assert config.bot_token == "123456:ABCdefGHIjklMNOpqrSTUvwxYZ"
    
    def test_from_environment_without_bot_token(self):
        """Test creating config from environment without bot token (user mode)"""
        env_vars = {
            'TELEGRAM_API_ID': '12345',
            'TELEGRAM_API_HASH': 'test_hash',
            'TELEGRAM_SESSION_NAME': 'test_session'
        }
        
        config = TelegramConfig.from_environment(env_vars)
        
        assert config.api_id == 12345
        assert config.api_hash == "test_hash"
        assert config.session_name == "test_session"
        assert not hasattr(config, 'bot_token') or config.bot_token is None