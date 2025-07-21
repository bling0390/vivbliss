"""
Telegram configuration module for Pyrogram client setup and validation.
"""
import asyncio
import os
from typing import Optional, Dict, Any
from pyrogram import Client


class TelegramConfig:
    """Configuration class for Telegram Pyrogram client setup."""
    
    def __init__(self, api_id: str, api_hash: str, session_name: str, bot_token: Optional[str] = None):
        """
        Initialize Telegram configuration.
        
        Args:
            api_id: Telegram API ID
            api_hash: Telegram API Hash
            session_name: Session name for Pyrogram client
            bot_token: Optional bot token for bot mode authentication
            
        Raises:
            ValueError: If any required parameter is empty or invalid
        """
        if not api_id or not api_id.strip():
            raise ValueError("api_id is required")
        if not api_hash or not api_hash.strip():
            raise ValueError("api_hash is required")
        if not session_name or not session_name.strip():
            raise ValueError("session_name is required")
            
        self.api_id = int(api_id.strip())
        self.api_hash = api_hash.strip()
        self.session_name = session_name.strip()
        
        # Validate and set bot token if provided
        if bot_token:
            bot_token = bot_token.strip()
            if bot_token and not self._is_valid_bot_token(bot_token):
                raise ValueError("Invalid bot token format")
            self.bot_token = bot_token
        else:
            self.bot_token = None
    
    def _is_valid_bot_token(self, token: str) -> bool:
        """
        Validate bot token format.
        Bot tokens have format: <bot_id>:<auth_string>
        """
        if not token:
            return False
        parts = token.split(':')
        if len(parts) != 2:
            return False
        bot_id, auth_string = parts
        return bot_id.isdigit() and len(auth_string) > 20
    
    async def create_client(self) -> Client:
        """
        Create and return a Pyrogram client instance.
        
        Returns:
            Configured Pyrogram Client instance
        """
        client_args = {
            "name": self.session_name,
            "api_id": self.api_id,
            "api_hash": self.api_hash
        }
        
        # Add bot token if available for bot mode authentication
        if self.bot_token:
            client_args["bot_token"] = self.bot_token
            
        client = Client(**client_args)
        return client
    
    async def validate_client_connection(self, client: Client) -> bool:
        """
        Validate that the client can connect to Telegram successfully.
        
        Args:
            client: Pyrogram client instance to validate
            
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            await client.get_me()
            return True
        except Exception:
            return False
    
    @classmethod
    def from_environment(cls, env_vars: Optional[Dict[str, str]] = None) -> 'TelegramConfig':
        """
        Create TelegramConfig from environment variables.
        
        Args:
            env_vars: Dictionary of environment variables. If None, uses os.environ
            
        Returns:
            TelegramConfig instance
            
        Raises:
            ValueError: If required environment variables are missing
        """
        if env_vars is None:
            env_vars = dict(os.environ)
        
        # Try different possible environment variable names
        api_id = (env_vars.get('TELEGRAM_API_ID') or 
                 env_vars.get('API_ID') or
                 env_vars.get('TG_API_ID'))
        
        api_hash = (env_vars.get('TELEGRAM_API_HASH') or
                   env_vars.get('API_HASH') or 
                   env_vars.get('TG_API_HASH'))
        
        session_name = (env_vars.get('TELEGRAM_SESSION_NAME') or
                       env_vars.get('SESSION_NAME') or
                       env_vars.get('TG_SESSION_NAME') or
                       'vivbliss_session')
        
        bot_token = (env_vars.get('TELEGRAM_BOT_TOKEN') or
                    env_vars.get('BOT_TOKEN') or
                    env_vars.get('TG_BOT_TOKEN'))
        
        if not api_id:
            raise ValueError("Missing required environment variable: TELEGRAM_API_ID (or API_ID)")
        
        if not api_hash:
            raise ValueError("Missing required environment variable: TELEGRAM_API_HASH (or API_HASH)")
        
        return cls(api_id=api_id, api_hash=api_hash, session_name=session_name, bot_token=bot_token)
    
    @classmethod 
    def from_compose_file(cls, compose_file_path: str, service_name: Optional[str] = None) -> 'TelegramConfig':
        """
        Create TelegramConfig from Docker Compose file.
        
        Args:
            compose_file_path: Path to docker-compose.yml file
            service_name: Service name to extract config from (optional)
            
        Returns:
            TelegramConfig instance
        """
        from ..config import EnvironmentExtractor
        
        extractor = EnvironmentExtractor()
        extractor.load_from_compose(compose_file_path, service_name)
        telegram_env = extractor.get_telegram_config()
        
        # Convert TELEGRAM_ prefixed variables to expected format
        env_vars = {}
        for key, value in telegram_env.items():
            # Remove TELEGRAM_ prefix for compatibility
            clean_key = key.replace('TELEGRAM_', '', 1)
            env_vars[clean_key] = value
            # Keep original key as well
            env_vars[key] = value
        
        return cls.from_environment(env_vars)