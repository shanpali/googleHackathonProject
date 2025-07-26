#!/usr/bin/env python3
"""
Test with detailed debugging
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_with_debugging():
    """Test Gemini with detailed debugging logs."""
    try:
        from gemini_service import GeminiService
        
        print("🧪 Testing with debugging enabled...")
        service = GeminiService()
        
        # Test with very explicit request for net worth
        response = service.generate_content_with_user_context(
            user_content="Please fetch my net worth data using the MCP tools.",
            phone="1234567890",
            include_tools=True
        )
        
        print("\n" + "="*50)
        print("FINAL RESULT:")
        print("="*50)
        print(f"Text: {response.get('text', 'None')}")
        print(f"Function calls: {len(response.get('function_calls', []))}")
        if response.get('function_calls'):
            for i, call in enumerate(response['function_calls']):
                print(f"  Call {i+1}: {call.get('function', 'unknown')} - Success: {call.get('success')}")
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_with_debugging()
