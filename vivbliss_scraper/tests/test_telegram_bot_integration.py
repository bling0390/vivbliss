import pytest
import os
from unittest.mock import Mock, patch, AsyncMock
from vivbliss_scraper.telegram.config import TelegramConfig
from vivbliss_scraper.telegram.pipeline import TelegramUploadPipeline


class TestTelegramBotIntegration:
    """Integration tests for Telegram bot token authentication."""
    
    @pytest.mark.asyncio
    async def test_bot_mode_initialization(self):
        """Test that bot mode initializes correctly with bot token."""
        with patch('vivbliss_scraper.telegram.config.Client') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value = mock_instance
            
            # Create config with bot token
            config = TelegramConfig(
                api_id="12345",
                api_hash="test_hash",
                session_name="test_bot",
                bot_token="123456:ABCdefGHIjklMNOpqrSTUvwxYZ"
            )
            
            # Create client
            client = await config.create_client()
            
            # Verify client was created with bot token
            mock_client.assert_called_once_with(
                name="test_bot",
                api_id=12345,
                api_hash="test_hash",
                bot_token="123456:ABCdefGHIjklMNOpqrSTUvwxYZ"
            )
    
    @pytest.mark.asyncio
    async def test_pipeline_with_bot_token(self):
        """Test that pipeline correctly passes bot token to config."""
        pipeline = TelegramUploadPipeline(
            api_id="12345",
            api_hash="test_hash",
            session_name="test_bot",
            chat_id=123456789,
            bot_token="123456:ABCdefGHIjklMNOpqrSTUvwxYZ"
        )
        
        assert pipeline.bot_token == "123456:ABCdefGHIjklMNOpqrSTUvwxYZ"
        
        # Mock spider
        spider = Mock()
        spider.logger = Mock()
        
        with patch('vivbliss_scraper.telegram.config.Client') as mock_client:
            mock_instance = AsyncMock()
            mock_instance.start = AsyncMock()
            mock_instance.get_me = AsyncMock(return_value=Mock(id=123456))
            mock_client.return_value = mock_instance
            
            await pipeline.open_spider(spider)
            
            # Verify config was created with bot token
            assert pipeline.config.bot_token == "123456:ABCdefGHIjklMNOpqrSTUvwxYZ"
            
            # Verify client was started
            mock_instance.start.assert_called_once()
    
    def test_environment_variables_priority(self):
        """Test that environment variables are read with correct priority."""
        # Test with TELEGRAM_BOT_TOKEN
        env_vars = {
            'TELEGRAM_API_ID': '12345',
            'TELEGRAM_API_HASH': 'test_hash',
            'TELEGRAM_BOT_TOKEN': '123456:ABCdefGHIjklMNOpqrSTUvwxYZ'
        }
        
        config = TelegramConfig.from_environment(env_vars)
        assert config.bot_token == '123456:ABCdefGHIjklMNOpqrSTUvwxYZ'
        
        # Test with BOT_TOKEN
        env_vars = {
            'TELEGRAM_API_ID': '12345',
            'TELEGRAM_API_HASH': 'test_hash',
            'BOT_TOKEN': '654321:ZYXwvuTSrqpONMlkjIHGfedCBA'
        }
        
        config = TelegramConfig.from_environment(env_vars)
        assert config.bot_token == '654321:ZYXwvuTSrqpONMlkjIHGfedCBA'
        
        # Test priority (TELEGRAM_BOT_TOKEN > BOT_TOKEN)
        env_vars = {
            'TELEGRAM_API_ID': '12345',
            'TELEGRAM_API_HASH': 'test_hash',
            'TELEGRAM_BOT_TOKEN': '111111:ABCdefGHIjklMNOpqrSTUvwxYZ_primary',
            'BOT_TOKEN': '222222:ABCdefGHIjklMNOpqrSTUvwxYZ_secondary'
        }
        
        config = TelegramConfig.from_environment(env_vars)
        assert config.bot_token == '111111:ABCdefGHIjklMNOpqrSTUvwxYZ_primary'
    
    def test_bot_token_validation_edge_cases(self):
        """Test bot token validation with edge cases."""
        # Valid tokens
        valid_tokens = [
            "123456:ABCdefGHIjklMNOpqrSTUvwxYZ",  # Standard format
            "1:ABCdefGHIjklMNOpqrSTUvwxYZ123456",  # Single digit bot ID
            "9999999999:ABCdefGHIjklMNOpqrSTUvwxYZ123456789012345",  # Long bot ID
        ]
        
        for token in valid_tokens:
            config = TelegramConfig(
                api_id="12345",
                api_hash="test_hash",
                session_name="test",
                bot_token=token
            )
            assert config.bot_token == token
        
        # Invalid tokens
        invalid_tokens = [
            "invalid_token",  # No colon
            "123456:",  # Missing auth string
            ":ABCdefGHIjklMNOpqrSTUvwxYZ",  # Missing bot ID
            "abc:ABCdefGHIjklMNOpqrSTUvwxYZ",  # Non-numeric bot ID
            "123456:short",  # Auth string too short
        ]
        
        for token in invalid_tokens:
            with pytest.raises(ValueError, match="Invalid bot token format"):
                TelegramConfig(
                    api_id="12345",
                    api_hash="test_hash",
                    session_name="test",
                    bot_token=token
                )