"""
Internationalization service for the application.
Provides error message localization and language detection.
"""

import json
import os
from typing import Optional

try:
    from flask import request
    _flask_available = True
except ImportError:
    _flask_available = False
    request = None


class I18nService:
    def __init__(self, default_locale: str = 'en'):
        self.default_locale = default_locale
        self.locales_path = os.path.join(os.path.dirname(__file__), 'locales')
        self._error_messages = {}
        self._load_error_messages()
    
    def _load_error_messages(self):
        """Load error messages for all available locales."""
        for locale_dir in os.listdir(self.locales_path):
            locale_path = os.path.join(self.locales_path, locale_dir)
            if os.path.isdir(locale_path):
                errors_file = os.path.join(locale_path, 'errors.json')
                if os.path.exists(errors_file):
                    with open(errors_file, 'r', encoding='utf-8') as f:
                        self._error_messages[locale_dir] = json.load(f)
    
    def get_locale(self) -> str:
        """
        Determine the user's preferred locale.
        Checks Accept-Language header, falls back to default.
        """
        if _flask_available and hasattr(request, 'headers') and request:
            accept_language = request.headers.get('Accept-Language', '')
            # Simple parsing - takes the first language code
            if accept_language:
                preferred_lang = accept_language.split(',')[0].split('-')[0].lower()
                if preferred_lang in self._error_messages:
                    return preferred_lang
        
        return self.default_locale
    
    def get_error_message(self, error_code: str, locale: Optional[str] = None) -> str:
        """
        Get localized error message for the given error code.
        
        Args:
            error_code: The error code to look up
            locale: Optional locale override. If not provided, detects from request.
        
        Returns:
            Localized error message or the error code if not found.
        """
        if locale is None:
            locale = self.get_locale()
        
        # Try to get message for requested locale
        if locale in self._error_messages:
            message = self._error_messages[locale].get(error_code)
            if message:
                return message
        
        # Fallback to default locale
        if self.default_locale in self._error_messages:
            message = self._error_messages[self.default_locale].get(error_code)
            if message:
                return message
        
        # Ultimate fallback - return the error code itself
        return f"Error: {error_code}"
    
    def get_available_locales(self) -> list:
        """Get list of available locales."""
        return list(self._error_messages.keys())


# Global instance
i18n = I18nService()


def get_localized_error(error_code: str, locale: Optional[str] = None) -> str:
    """
    Convenience function to get localized error message.
    
    Args:
        error_code: The error code to look up
        locale: Optional locale override
    
    Returns:
        Localized error message
    """
    return i18n.get_error_message(error_code, locale)
