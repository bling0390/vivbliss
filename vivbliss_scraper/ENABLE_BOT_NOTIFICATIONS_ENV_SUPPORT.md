# ENABLE_BOT_NOTIFICATIONS Environment Variable Support

## Overview

The `ENABLE_BOT_NOTIFICATIONS` environment variable support has been implemented following Test-Driven Development (TDD) methodology. This feature allows users to control bot notification behavior through environment variables, providing more flexible deployment and configuration options.

## Implementation Summary

### ✅ Core Features Implemented

1. **Environment Variable Reading**: BotNotifier now reads `ENABLE_BOT_NOTIFICATIONS` from environment variables
2. **Flexible Value Parsing**: Supports multiple formats for true/false values
3. **Priority Handling**: Settings parameters override environment variables
4. **Safe Defaults**: Invalid values default to false for security
5. **Backward Compatibility**: Existing functionality remains unchanged

### 📁 Modified Files

#### `vivbliss_scraper/utils/bot_notifier.py`
- Added `_get_enable_notifications_setting()` method
- Added `_parse_bool_value()` method
- Added `is_config_enabled()` method for testing
- Modified `create_from_settings()` to use environment variable support
- Separated configuration-level and runtime-level enable states

#### `vivbliss_scraper/spiders/vivbliss.py` 
- Updated spider initialization to better handle settings conversion

### 🧪 Test Files Created

#### Core TDD Tests
- `test_enable_bot_notifications_env_tdd.py`: RED phase failing tests
- `test_enable_bot_notifications_green.py`: GREEN phase passing tests  
- `test_debug_env_var.py`: Debug utility for environment variable parsing
- `test_debug_true_values.py`: Debug utility for true value parsing

## Usage

### Environment Variable Values

#### ✅ True Values (Enable Notifications)
```bash
export ENABLE_BOT_NOTIFICATIONS=true
export ENABLE_BOT_NOTIFICATIONS=True
export ENABLE_BOT_NOTIFICATIONS=TRUE
export ENABLE_BOT_NOTIFICATIONS=1
export ENABLE_BOT_NOTIFICATIONS=yes
export ENABLE_BOT_NOTIFICATIONS=Yes
export ENABLE_BOT_NOTIFICATIONS=YES
export ENABLE_BOT_NOTIFICATIONS=on
export ENABLE_BOT_NOTIFICATIONS=On
export ENABLE_BOT_NOTIFICATIONS=ON
export ENABLE_BOT_NOTIFICATIONS=enabled
```

#### ❌ False Values (Disable Notifications)
```bash
export ENABLE_BOT_NOTIFICATIONS=false
export ENABLE_BOT_NOTIFICATIONS=False  
export ENABLE_BOT_NOTIFICATIONS=FALSE
export ENABLE_BOT_NOTIFICATIONS=0
export ENABLE_BOT_NOTIFICATIONS=no
export ENABLE_BOT_NOTIFICATIONS=No
export ENABLE_BOT_NOTIFICATIONS=NO
export ENABLE_BOT_NOTIFICATIONS=off
export ENABLE_BOT_NOTIFICATIONS=Off
export ENABLE_BOT_NOTIFICATIONS=OFF
export ENABLE_BOT_NOTIFICATIONS=disabled
export ENABLE_BOT_NOTIFICATIONS=""  # Empty string
```

### Configuration Priority

The configuration is resolved in the following priority order:

1. **Settings Parameter** (Highest Priority)
   ```python
   BotNotifier.create_from_settings({
       'ENABLE_BOT_NOTIFICATIONS': False,  # This overrides env var
       'TELEGRAM_NOTIFICATION_CHAT_ID': '123456'
   })
   ```

2. **Environment Variable** (Medium Priority)
   ```bash
   export ENABLE_BOT_NOTIFICATIONS=true
   ```

3. **Default Value** (Lowest Priority)
   - Default is `True` when no configuration is provided

### Examples

#### Docker Compose
```yaml
services:
  vivbliss-scraper:
    environment:
      - ENABLE_BOT_NOTIFICATIONS=false
      - TELEGRAM_API_ID=your_api_id
      - TELEGRAM_API_HASH=your_api_hash
      - TELEGRAM_BOT_TOKEN=your_bot_token
      - TELEGRAM_NOTIFICATION_CHAT_ID=your_chat_id
```

#### Systemd Service
```ini
[Unit]
Description=VivBliss Scraper

[Service]
Environment=ENABLE_BOT_NOTIFICATIONS=true
Environment=TELEGRAM_API_ID=your_api_id
Environment=TELEGRAM_API_HASH=your_api_hash
ExecStart=/usr/local/bin/scrapy crawl vivbliss

[Install]
WantedBy=multi-user.target
```

#### Shell Script
```bash
#!/bin/bash
export ENABLE_BOT_NOTIFICATIONS=false
export TELEGRAM_NOTIFICATION_CHAT_ID="-1234567890"

# Run scraper with notifications disabled
scrapy crawl vivbliss
```

## Technical Details

### Method Reference

#### `BotNotifier._get_enable_notifications_setting(settings: Dict[str, Any]) -> bool`
Resolves the enable notifications setting from multiple sources:
- Checks explicit settings parameter first
- Falls back to environment variable
- Uses default value (True) if neither is available

#### `BotNotifier._parse_bool_value(value: str) -> bool`
Parses string values into boolean:
- Handles case-insensitive true/false variations
- Returns False for invalid or unknown values
- Supports common boolean representations

#### `BotNotifier.is_config_enabled() -> bool`
Returns configuration-level enabled status (used for testing):
- Ignores Pyrogram availability
- Shows pure configuration intent
- Used for environment variable validation

### Error Handling

- **Invalid Values**: Unknown values default to `False` for security
- **Missing Environment Variable**: Uses default value `True`
- **Type Errors**: Non-string values are handled gracefully
- **Chat ID Requirement**: Notifications still require a valid chat_id

### Compatibility

- **Backward Compatible**: Existing code continues to work unchanged
- **Settings Override**: Explicit settings still take precedence
- **Runtime vs Config**: Pyrogram availability still affects actual functionality

## Testing

### Running Tests

```bash
# Run RED phase tests (should fail initially)
python3 test_enable_bot_notifications_env_tdd.py

# Run GREEN phase tests (should pass after implementation)  
python3 test_enable_bot_notifications_green.py

# Run existing regression tests
python3 test_bot_notification_green.py
```

### Test Coverage

✅ **Environment Variable Reading**
✅ **True/False Value Parsing** 
✅ **Default Behavior**
✅ **Settings Priority**
✅ **Invalid Value Handling**
✅ **EnvironmentExtractor Integration**
✅ **Backward Compatibility**

## Troubleshooting

### Common Issues

#### Notifications Not Disabled
```bash
# Check if environment variable is set correctly
echo $ENABLE_BOT_NOTIFICATIONS

# Verify it's being read
python3 -c "
import os
from vivbliss_scraper.utils.bot_notifier import BotNotifier
print('Env var:', os.environ.get('ENABLE_BOT_NOTIFICATIONS'))
notifier = BotNotifier.create_from_settings({'TELEGRAM_NOTIFICATION_CHAT_ID': '123'})
print('Config enabled:', notifier.is_config_enabled())
"
```

#### Settings Override Not Working
```python
# Make sure you're passing the setting explicitly
settings = {
    'ENABLE_BOT_NOTIFICATIONS': False,  # This should override env var
    'TELEGRAM_NOTIFICATION_CHAT_ID': 'your_chat_id'
}
notifier = BotNotifier.create_from_settings(settings)
```

#### Still Getting "Pyrogram不可用"
This is expected when Pyrogram is not installed. The environment variable controls configuration-level enablement, but Pyrogram is still required for actual functionality.

## Future Enhancements

### Potential Improvements
- Support for additional environment variable names (e.g., `BOT_NOTIFICATIONS_ENABLED`)
- Integration with external configuration management systems
- Runtime environment variable reloading
- More granular notification control (per-feature toggles)

### Integration Points
- EnvironmentExtractor class for compose file support
- Spider settings integration for Scrapy environments
- Docker configuration templates
- CI/CD pipeline examples

## Implementation Notes

This feature was implemented using SPARC TDD methodology:

1. **RED Phase**: Wrote failing tests to define requirements
2. **GREEN Phase**: Implemented minimal code to pass tests
3. **REFACTOR Phase**: Cleaned up code for maintainability

The implementation maintains separation of concerns:
- Configuration parsing is separated from runtime functionality  
- Environment variable handling is isolated in dedicated methods
- Test utilities provide debugging capabilities
- Backward compatibility is preserved throughout

## Version History

- **v1.0**: Initial implementation with basic environment variable support
- **v1.1**: Added comprehensive value parsing and priority handling
- **v1.2**: Separated config-level from runtime-level enable states
- **v1.3**: Added extensive test coverage and documentation