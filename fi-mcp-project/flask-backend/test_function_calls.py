#!/usr/bin/env python3
"""
Test Gemini function call handling with explicit phone number
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_gemini_function_calls():
    """Test that Gemini can properly execute function calls and process results."""
    try:
        from gemini_service import GeminiService
        
        print("🧪 Testing Gemini function call handling...")
        service = GeminiService()
        
        # Test with very explicit instructions and phone number
        print("📞 Testing with explicit phone number...")
        
        response = service.generate_content(
            user_content="Please fetch the net worth data for phone number 1234567890 using the fi_mcp_fetch_net_worth function.",
            include_tools=True
        )
        
        print("✅ Content generation completed")
        print(f"📄 Response keys: {list(response.keys())}")
        
        if response.get('function_calls'):
            print(f"🔧 Function calls made: {len(response['function_calls'])}")
            for i, call in enumerate(response['function_calls']):
                print(f"   Call {i+1}:")
                print(f"     - Function: {call.get('function', 'unknown')}")
                print(f"     - Success: {call.get('success', False)}")
                print(f"     - Server: {call.get('server', 'unknown')}")
                print(f"     - Tool: {call.get('tool', 'unknown')}")
                if not call.get('success'):
                    print(f"     - Error: {call.get('error', 'Unknown error')}")
                else:
                    result_preview = str(call.get('result', ''))[:100]
                    print(f"     - Result preview: {result_preview}...")
        else:
            print("📝 No function calls made")
        
        if response.get('text'):
            print(f"📝 Response text: {response['text']}")
        
        if response.get('error'):
            print(f"❌ Error: {response['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_gemini_function_calls():
        print("\n🎉 Gemini function call test completed!")
    else:
        print("\n❌ Gemini function call test failed.")
        sys.exit(1)
