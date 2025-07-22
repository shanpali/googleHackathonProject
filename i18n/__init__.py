"""
Internationalization package for the application.
"""

from .service import i18n, get_localized_error
from .error_codes import ErrorCodes

__all__ = ['i18n', 'get_localized_error', 'ErrorCodes']
