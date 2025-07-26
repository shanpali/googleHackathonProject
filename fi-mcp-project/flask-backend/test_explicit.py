#!/usr/bin/env python3
"""
Test with phone number explicitly in the message
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_explicit_phone():
    """Test with phone number explicitly in the user message."""
    try:
        from gemini_service import GeminiService
        
        print("🧪 Testing with explicit phone number...")
        service = GeminiService()
        
        # Test with phone number directly in the message
        response = service.generate_content(
            user_content="My phone number is 1234567890. Please fetch my net worth data using the fi_mcp_fetch_net_worth function.",
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
    test_explicit_phone()
