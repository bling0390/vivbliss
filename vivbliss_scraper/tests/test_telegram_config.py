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
        
        assert config.api_id == "12345"
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
                api_id="12345",
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