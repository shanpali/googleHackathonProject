#!/usr/bin/env python3
"""
Quick test for the async/sync fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_mcp_tool_registration():
    """Test that MCP tools can be registered without async issues."""
    try:
        from gemini_service import GeminiService
        print("✅ GeminiService import successful")
        
        # This should trigger MCP tool registration without async errors
        service = GeminiService()
        print("✅ GeminiService initialized successfully")
        
        # Check if any tools were registered
        all_tools = service.tool_registry.get_all_tool_definitions()
        print(f"✅ Total tools registered: {len(all_tools)}")
        
        # Look for MCP tools specifically
        mcp_tools = [t for t in all_tools if t.get('name', '').startswith('fi_mcp_')]
        print(f"✅ MCP tools found: {len(mcp_tools)}")
        
        if mcp_tools:
            print(f"   Tool names: {[t['name'] for t in mcp_tools]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing MCP async/sync fix...")
    if test_mcp_tool_registration():
        print("🎉 Test passed! Async/sync issue is fixed.")
    else:
        print("❌ Test failed. Check the errors above.")
        sys.exit(1)
