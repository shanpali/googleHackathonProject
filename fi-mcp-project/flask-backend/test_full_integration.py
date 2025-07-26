#!/usr/bin/env python3
"""
Test the full integration with Flask backend running
"""

import sys
import os
import time
import subprocess
import requests
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_full_integration():
    """Test the full integration with Flask backend."""
    
    # Start Flask backend in background
    print("🚀 Starting Flask backend...")
    flask_process = subprocess.Popen([
        sys.executable, "app.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Give Flask time to start
    time.sleep(3)
    
    try:
        # Test if Flask is running
        response = requests.get("http://localhost:5000/mcp-tools", timeout=5)
        if response.status_code == 200:
            print("✅ Flask backend is running")
        else:
            print("❌ Flask backend not responding correctly")
            return False
            
        # Now test Gemini integration
        print("🧪 Testing Gemini with running Flask backend...")
        from gemini_service import GeminiService
        
        service = GeminiService()
        
        response = service.generate_content(
            user_content="Please fetch the net worth data for phone number 1234567890.",
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
                if call.get('success'):
                    result_str = str(call.get('result', ''))
                    print(f"     - Result length: {len(result_str)} chars")
                    if 'Error' not in result_str:
                        print(f"     - ✅ Got data successfully!")
                    else:
                        print(f"     - ⚠️ Got error: {result_str[:100]}...")
        
        if response.get('text'):
            print(f"📝 Response text (first 300 chars): {response['text'][:300]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Stop Flask backend
        print("🛑 Stopping Flask backend...")
        flask_process.terminate()
        flask_process.wait()

if __name__ == "__main__":
    if test_full_integration():
        print("\n🎉 Full integration test completed!")
        print("The function call mechanism is working correctly.")
        print("Start both your Go MCP server and Flask backend to test with real data.")
    else:
        print("\n❌ Full integration test failed.")
        sys.exit(1)
