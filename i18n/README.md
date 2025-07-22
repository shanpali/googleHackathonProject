# Internationalization (i18n) System

This directory contains the internationalization system for the application, providing localized error messages and support for multiple languages.

## Structure

```
i18n/
├── __init__.py              # Package initialization
├── error_codes.py           # Error code constants
├── service.py              # i18n service implementation
└── locales/                # Language-specific files
    ├── en/                 # English (default)
    │   └── errors.json
    ├── es/                 # Spanish
    │   └── errors.json
    └── fr/                 # French
        └── errors.json
```

## Usage

### In your Flask application:

```python
from i18n import get_localized_error, ErrorCodes

# Get localized error message (auto-detects language from Accept-Language header)
error_message = get_localized_error(ErrorCodes.AUTH_MISSING_BEARER_TOKEN)

# Or specify a specific locale
error_message = get_localized_error(ErrorCodes.AUTH_MISSING_BEARER_TOKEN, 'es')
```

### Language Detection

The system automatically detects the user's preferred language from the `Accept-Language` HTTP header. If the requested language is not available, it falls back to English.

### Adding New Languages

1. Create a new directory under `locales/` with the language code (e.g., `de` for German)
2. Add an `errors.json` file with translations for all error codes
3. The system will automatically detect and use the new language

### Adding New Error Codes

1. Add the new error code constant to `error_codes.py`
2. Add the corresponding message to all language files in `locales/*/errors.json`

## Error Code Categories

- **AUTH_xxx**: Authentication and authorization errors (1000-1099)
- **VAL_xxx**: Validation errors (2000-2099)  
- **SRV_xxx**: Server and processing errors (5000-5099)

## Example API Usage

Clients can specify their preferred language using the `Accept-Language` header:

```bash
curl -H "Accept-Language: es" \
     -H "Authorization: Bearer token" \
     -X POST /api/mcp/prompt
```

This will return error messages in Spanish if available, or fall back to English.

## Benefits

1. **Extensible**: Easy to add new languages and error messages
2. **Automatic Detection**: Uses standard HTTP Accept-Language header
3. **Fallback Support**: Graceful degradation to default language
4. **Centralized**: All error messages in one place
5. **Type Safe**: Error codes are defined as constants
6. **SEO Friendly**: Proper HTTP status codes with localized messages
