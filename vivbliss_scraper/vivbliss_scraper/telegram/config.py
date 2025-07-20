"""
Telegram configuration module for Pyrogram client setup and validation.
"""
import asyncio
from typing import Optional
from pyrogram import Client


class TelegramConfig:
    """Configuration class for Telegram Pyrogram client setup."""
    
    def __init__(self, api_id: str, api_hash: str, session_name: str):
        """
        Initialize Telegram configuration.
        
        Args:
            api_id: Telegram API ID
            api_hash: Telegram API Hash
            session_name: Session name for Pyrogram client
            
        Raises:
            ValueError: If any required parameter is empty
        """
        if not api_id or not api_id.strip():
            raise ValueError("api_id is required")
        if not api_hash or not api_hash.strip():
            raise ValueError("api_hash is required")
        if not session_name or not session_name.strip():
            raise ValueError("session_name is required")
            
        self.api_id = api_id.strip()
        self.api_hash = api_hash.strip()
        self.session_name = session_name.strip()
    
    async def create_client(self) -> Client:
        """
        Create and return a Pyrogram client instance.
        
        Returns:
            Configured Pyrogram Client instance
        """
        client = Client(
            name=self.session_name,
            api_id=self.api_id,
            api_hash=self.api_hash
        )
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