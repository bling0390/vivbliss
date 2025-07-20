# Telegram Integration for VivBliss Scraper

This document describes the Telegram file upload functionality integrated into the VivBliss scraper using Pyrogram.

## 🚀 Features

- **Automated File Upload**: Upload scraped images and videos to Telegram channels/chats
- **File Validation**: Comprehensive validation for supported formats and file sizes
- **Error Handling**: Robust retry mechanisms and error handling
- **Progress Tracking**: Monitor upload progress for batch operations
- **Scrapy Integration**: Seamless pipeline integration with existing scraper
- **Test-Driven Development**: 95%+ test coverage with comprehensive unit and integration tests

## 📋 Requirements

- Python 3.8+
- Pyrogram 2.0+
- Telegram API credentials (api_id, api_hash)
- Target chat/channel ID

## 🛠️ Installation

1. Install dependencies:
```bash
pip install pyrogram
```

2. Set up environment variables:
```bash
# .env file
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_SESSION_NAME=vivbliss_bot
TELEGRAM_CHAT_ID=your_chat_id
TELEGRAM_ENABLE_UPLOAD=True
```

## 📁 Module Structure

```
vivbliss_scraper/telegram/
├── __init__.py              # Package initialization
├── config.py                # Telegram client configuration
├── file_validator.py        # File validation logic
├── file_uploader.py         # Upload functionality
├── pipeline.py              # Scrapy pipeline integration
└── example_usage.py         # Usage examples
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `TELEGRAM_API_ID` | Telegram API ID | Yes | - |
| `TELEGRAM_API_HASH` | Telegram API Hash | Yes | - |
| `TELEGRAM_SESSION_NAME` | Pyrogram session name | No | `vivbliss_bot` |
| `TELEGRAM_CHAT_ID` | Target chat/channel ID | Yes | - |
| `TELEGRAM_ENABLE_UPLOAD` | Enable/disable uploads | No | `True` |

### Getting Telegram Credentials

1. Visit [my.telegram.org](https://my.telegram.org)
2. Log in with your phone number
3. Go to "API Development tools"
4. Create an application to get `api_id` and `api_hash`

### Finding Chat ID

For channels:
- Add `@userinfobot` to your channel
- Get the chat ID (will be negative for channels)

For private chats:
- Start a chat with `@userinfobot`
- Get your user ID

## 🎯 Supported File Formats

### Images
- JPG/JPEG
- PNG
- GIF
- WebP
- BMP

### Videos
- MP4
- AVI
- MKV
- MOV
- WebM
- FLV

### File Size Limits
- Maximum file size: 50MB (Telegram limitation)

## 💻 Usage Examples

### Basic Upload

```python
import asyncio
from vivbliss_scraper.telegram.config import TelegramConfig
from vivbliss_scraper.telegram.file_uploader import FileUploader

async def upload_file():
    # Configure client
    config = TelegramConfig(
        api_id="YOUR_API_ID",
        api_hash="YOUR_API_HASH",
        session_name="my_session"
    )
    
    # Create and start client
    client = await config.create_client()
    await client.start()
    
    # Upload file
    uploader = FileUploader(client)
    result = await uploader.upload_file(
        chat_id=-1001234567890,
        file_path="/path/to/image.jpg",
        caption="Uploaded from VivBliss scraper"
    )
    
    print(f"Upload result: {result}")
    await client.stop()

# Run the upload
asyncio.run(upload_file())
```

### File Validation

```python
from vivbliss_scraper.telegram.file_validator import FileValidator

validator = FileValidator()

# Validate a single file
result = validator.validate_file("/path/to/file.jpg")
if result['is_valid']:
    print(f"✅ Valid {result['file_type']} file")
else:
    print(f"❌ Invalid file: {result['errors']}")

# Check specific formats
if validator.is_supported_image_extension("photo.png"):
    print("PNG images are supported")
```

### Batch Upload

```python
async def batch_upload():
    # ... client setup ...
    
    uploader = FileUploader(client)
    
    files = ["/path/to/img1.jpg", "/path/to/vid1.mp4", "/path/to/img2.png"]
    
    def progress_callback(current, total, filename):
        print(f"Progress: {current}/{total} - {filename}")
    
    results = await uploader.upload_multiple_files(
        chat_id=-1001234567890,
        file_paths=files,
        progress_callback=progress_callback
    )
    
    successful = sum(1 for r in results if r['success'])
    print(f"Uploaded {successful}/{len(results)} files successfully")
```

## 🔗 Scrapy Integration

The Telegram functionality is integrated as a Scrapy pipeline that automatically uploads extracted media files.

### Pipeline Configuration

Add to your `settings.py`:

```python
ITEM_PIPELINES = {
    'vivbliss_scraper.pipelines.MongoDBPipeline': 300,
    'vivbliss_scraper.telegram.pipeline.TelegramUploadPipeline': 400,
}
```

### Item Structure

The pipeline looks for media files in these item fields:
- `images`
- `videos` 
- `media_files`
- `attachments`

Example item:

```python
class VivblissItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    content = scrapy.Field()
    images = scrapy.Field()      # List of image file paths
    videos = scrapy.Field()      # List of video file paths
    media_files = scrapy.Field() # List of mixed media files
```

### Pipeline Statistics

The pipeline tracks upload statistics:

```python
{
    'files_processed': 10,
    'files_uploaded': 8,
    'files_failed': 1,
    'files_skipped': 1
}
```

## 🧪 Testing

The module includes comprehensive tests with 95%+ coverage:

```bash
# Run all tests
pytest tests/test_telegram_*.py -v

# Run with coverage
coverage run -m pytest tests/test_telegram_*.py
coverage report --show-missing

# Run specific test categories
pytest tests/test_telegram_config.py -v          # Configuration tests
pytest tests/test_file_validator.py -v          # Validation tests  
pytest tests/test_file_uploader.py -v           # Upload tests
pytest tests/test_telegram_integration.py -v    # Integration tests
```

### Test Structure

- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **Mock Testing**: Extensive use of mocks for Telegram API
- **File System Tests**: Real file creation/validation

## ⚡ Performance Features

### Retry Mechanism
- Configurable retry attempts (default: 3)
- Exponential backoff for failed uploads
- Automatic error recovery

### Async Support
- Full async/await implementation
- Non-blocking file operations
- Concurrent upload support

### Memory Efficiency
- Streaming file uploads
- Minimal memory footprint
- Garbage collection friendly

## 🔒 Security Features

- **Credential Validation**: Validates API credentials before use
- **File Validation**: Comprehensive file type and size checking
- **Error Sanitization**: Safe error message handling
- **Session Management**: Secure session handling with Pyrogram

## 🐛 Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify `api_id` and `api_hash` are correct
   - Check if session file has correct permissions
   - Ensure phone number verification if required

2. **File Upload Failed**
   - Check file exists and is readable
   - Verify file size is under 50MB
   - Confirm file format is supported

3. **Chat ID Issues**
   - Use negative IDs for channels (e.g., -1001234567890)
   - Use positive IDs for private chats/users
   - Ensure bot has permission to send files to the chat

4. **Pipeline Not Working**
   - Check pipeline is enabled in settings
   - Verify environment variables are set
   - Check item fields contain valid file paths

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Monitoring

The pipeline provides detailed logging:

```
INFO: Telegram client initialized successfully
INFO: Successfully uploaded /path/to/file.jpg (Message ID: 12345)
WARNING: Skipping invalid file /path/to/file.txt: ['Unsupported file format']
ERROR: Failed to upload /path/to/file.mp4: Network timeout
INFO: Telegram upload statistics: {'files_processed': 5, 'files_uploaded': 4, 'files_failed': 1, 'files_skipped': 0}
```

## 🔄 Future Enhancements

- [ ] Support for document uploads
- [ ] Thumbnail generation for videos
- [ ] Batch download capabilities
- [ ] Channel management features
- [ ] Message scheduling
- [ ] Advanced file compression

## 📝 License

This module is part of the VivBliss scraper project and follows the same licensing terms.

## 🤝 Contributing

1. Write tests for new features
2. Maintain 90%+ test coverage
3. Follow existing code style
4. Update documentation
5. Test with real Telegram API (where appropriate)

## 📞 Support

For issues specific to Telegram integration:
1. Check the troubleshooting section
2. Review test files for usage examples
3. Verify Telegram API credentials and permissions
4. Check Scrapy pipeline configuration