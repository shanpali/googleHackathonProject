#!/usr/bin/env python3
"""
Simple test script to demonstrate the i18n functionality.
Run this script to see how error messages are localized.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from i18n import get_localized_error, ErrorCodes

def test_i18n():
    """Test the internationalization system."""
    print("Testing Internationalization System")
    print("=" * 40)
    
    # Test different error codes
    test_codes = [
        ErrorCodes.AUTH_MISSING_BEARER_TOKEN,
        ErrorCodes.VALIDATION_MISSING_REQUIRED_FIELDS,
        ErrorCodes.VALIDATION_INVALID_MCP_SERVER,
        ErrorCodes.SERVER_PROCESSING_ERROR
    ]
    
    # Test different languages
    languages = ['en', 'es', 'fr']
    
    for code in test_codes:
        print(f"\nError Code: {code}")
        for lang in languages:
            message = get_localized_error(code, lang)
            print(f"  {lang}: {message}")

if __name__ == "__main__":
    test_i18n()
