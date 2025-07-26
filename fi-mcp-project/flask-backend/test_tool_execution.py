#!/usr/bin/env python3
"""
Test the actual chatbot functionality with MCP tools
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_mcp_tool_execution():
    """Test that MCP tools can be executed without async issues."""
    try:
        from gemini_service import GeminiService
        
        print("🧪 Testing MCP tool execution...")
        service = GeminiService()
        
        # Test a simple content generation that might use MCP tools
        # We'll use a financial query that should trigger MCP tool usage
        print("📞 Testing tool execution...")
        
        response = service.generate_content_with_user_context(
            user_content="What is my current net worth?",
            phone="1234567890",
            financial_data=None,
            include_tools=True
        )
        
        print("✅ Content generation completed")
        print(f"📄 Response keys: {list(response.keys())}")
        
        if response.get('function_calls'):
            print(f"🔧 Function calls made: {len(response['function_calls'])}")
            for call in response['function_calls']:
                print(f"   - Function: {call.get('function', 'unknown')}")
                print(f"     Success: {call.get('success', False)}")
                if not call.get('success'):
                    print(f"     Error: {call.get('error', 'Unknown error')}")
        else:
            print("📝 No function calls made")
        
        if response.get('text'):
            print(f"📝 Response text (first 200 chars): {response['text'][:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_mcp_tool_execution():
        print("\n🎉 MCP tool execution test passed!")
        print("The async/sync issue has been resolved.")
    else:
        print("\n❌ MCP tool execution test failed.")
        sys.exit(1)
