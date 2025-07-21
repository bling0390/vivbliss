# Telegram Bot Token Configuration

This document explains how to configure and use Telegram bot tokens with the VivBliss scraper.

## Overview

The VivBliss scraper uses Pyrogram, which supports two authentication modes:

1. **User Mode** (default): Authenticates as a regular Telegram user using phone number
2. **Bot Mode**: Authenticates as a Telegram bot using a bot token

## Bot Token Configuration

### Getting a Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. BotFather will provide you with a bot token like: `123456:ABCdefGHIjklMNOpqrSTUvwxYZ`

### Setting the Bot Token

You can configure the bot token in several ways:

#### 1. Environment Variable

```bash
export TELEGRAM_BOT_TOKEN="123456:ABCdefGHIjklMNOpqrSTUvwxYZ"
```

#### 2. .env File

Add to your `.env` file:

```env
TELEGRAM_BOT_TOKEN=123456:ABCdefGHIjklMNOpqrSTUvwxYZ
```

#### 3. Docker Compose

In your `docker-compose.yml`:

```yaml
environment:
  - TELEGRAM_BOT_TOKEN=123456:ABCdefGHIjklMNOpqrSTUvwxYZ
```

### Environment Variable Priority

The system checks for bot tokens in this order:
1. `TELEGRAM_BOT_TOKEN`
2. `BOT_TOKEN`
3. `TG_BOT_TOKEN`

## Bot Mode vs User Mode

### When to Use Bot Mode

Use bot mode when:
- You want automated uploads without phone number authentication
- You're running in a headless environment
- You need to upload to public channels
- You want simpler authentication

### When to Use User Mode

Use user mode when:
- You need full Telegram API access
- You want to upload to private chats/groups
- You need user-specific features

## Configuration Examples

### Bot Mode Configuration

```env
# Required for both modes
TELEGRAM_API_ID=12345
TELEGRAM_API_HASH=your_api_hash

# Bot token for bot mode
TELEGRAM_BOT_TOKEN=123456:ABCdefGHIjklMNOpqrSTUvwxYZ

# Target chat/channel
TELEGRAM_CHAT_ID=-1001234567890

# Optional settings
TELEGRAM_SESSION_NAME=vivbliss_bot
TELEGRAM_ENABLE_UPLOAD=True
```

### User Mode Configuration (No Bot Token)

```env
# Required for user mode
TELEGRAM_API_ID=12345
TELEGRAM_API_HASH=your_api_hash

# No bot token needed - will authenticate with phone number

# Target chat/channel
TELEGRAM_CHAT_ID=-1001234567890

# Optional settings
TELEGRAM_SESSION_NAME=vivbliss_user
TELEGRAM_ENABLE_UPLOAD=True
```

## Bot Token Validation

The system validates bot tokens to ensure they follow the correct format:
- Format: `<bot_id>:<auth_string>`
- Bot ID must be numeric
- Auth string must be at least 20 characters

Invalid tokens will raise a `ValueError` during initialization.

## Troubleshooting

### Common Issues

1. **"Invalid bot token format"**
   - Ensure your token follows the format: `123456:ABCdefGHIjklMNOpqrSTUvwxYZ`
   - Check for extra spaces or newlines

2. **Bot can't send messages**
   - Ensure the bot is added to the target chat/channel
   - For channels, bot needs admin rights to post

3. **Authentication fails**
   - Verify your `api_id` and `api_hash` are correct
   - Check that the bot token is active (not revoked)

### Testing Bot Token

You can test your bot token configuration:

```python
from vivbliss_scraper.telegram.config import TelegramConfig

# Test with environment variables
config = TelegramConfig.from_environment()
print(f"Bot token configured: {config.bot_token is not None}")

# Test with explicit values
config = TelegramConfig(
    api_id="12345",
    api_hash="your_hash",
    session_name="test",
    bot_token="123456:ABCdefGHIjklMNOpqrSTUvwxYZ"
)
```

## Security Considerations

- **Never commit bot tokens** to version control
- Use environment variables or secure secret management
- Rotate tokens regularly
- Limit bot permissions to minimum required
- Monitor bot activity for unauthorized use

## API Reference

### TelegramConfig

```python
class TelegramConfig:
    def __init__(self, api_id: str, api_hash: str, session_name: str, bot_token: Optional[str] = None):
        """
        Initialize Telegram configuration.
        
        Args:
            api_id: Telegram API ID
            api_hash: Telegram API Hash
            session_name: Session name for Pyrogram client
            bot_token: Optional bot token for bot mode authentication
        """
```

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `TELEGRAM_API_ID` | Telegram API ID from my.telegram.org | Yes | - |
| `TELEGRAM_API_HASH` | Telegram API Hash from my.telegram.org | Yes | - |
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather | No | None |
| `TELEGRAM_SESSION_NAME` | Session file name | No | vivbliss_bot |
| `TELEGRAM_CHAT_ID` | Target chat/channel ID | Yes | - |
| `TELEGRAM_ENABLE_UPLOAD` | Enable/disable uploads | No | True |