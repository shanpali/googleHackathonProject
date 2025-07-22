#!/usr/bin/env python3
"""
Example API calls demonstrating i18n functionality.
This shows how to make requests with different Accept-Language headers.
"""

import requests
import json

def test_api_with_languages():
    """Test the API with different language headers."""
    base_url = "http://localhost:3000"
    
    # Test data
    test_data = {
        "mcp_server_id": "nonexistent",
        "prompt_id": "also_nonexistent"
    }
    
    # Test different languages
    languages = [
        ("en", "English"),
        ("es", "Spanish"), 
        ("fr", "French"),
        ("de", "German (fallback to English)")
    ]
    
    print("Testing API with different Accept-Language headers")
    print("=" * 55)
    print("Note: Start the Flask app with 'python3 app.py' first\n")
    
    for lang_code, lang_name in languages:
        print(f"Testing {lang_name} ({lang_code}):")
        
        headers = {
            "Accept-Language": lang_code,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                f"{base_url}/api/mcp/prompt",
                headers=headers,
                json=test_data,
                timeout=5
            )
            
            result = response.json()
            print(f"  Status: {response.status_code}")
            print(f"  Error: {result.get('error', 'No error')}")
            
        except requests.exceptions.ConnectionError:
            print(f"  Error: Could not connect to {base_url}")
            print(f"  Make sure the Flask app is running!")
        except Exception as e:
            print(f"  Error: {e}")
        
        print()

if __name__ == "__main__":
    test_api_with_languages()
