#!/usr/bin/env python3
"""
Test MCP tool execution directly
"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_direct_tool_execution():
    """Test MCP tool execution directly."""
    try:
        from mcp_client import MCPClient
        
        print("🧪 Testing direct MCP tool execution...")
        client = MCPClient()
        
        # Connect to servers
        all_tools = client.get_all_available_tools_sync()
        print(f"✅ Available tools: {list(all_tools.keys())}")
        
        # Test direct tool execution
        print("📞 Testing fi_mcp_fetch_net_worth execution...")
        
        # This should now parse correctly: fi_mcp_fetch_net_worth -> server=fi_mcp, tool=fetch_net_worth
        result = asyncio.run(client.execute_tool_for_gemini(
            "fi_mcp_fetch_net_worth", 
            {"phone": "1234567890"}
        ))
        
        print(f"✅ Tool execution completed")
        print(f"📄 Result keys: {list(result.keys())}")
        print(f"🎯 Success: {result.get('success')}")
        print(f"🏢 Server: {result.get('server')}")
        print(f"🔧 Tool: {result.get('tool')}")
        
        if not result.get('success'):
            print(f"❌ Error: {result.get('error')}")
        else:
            print(f"✅ Result preview: {str(result.get('result', ''))[:200]}...")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing direct MCP tool execution...")
    if test_direct_tool_execution():
        print("\n🎉 Direct tool execution test passed!")
        print("Server name parsing and tool execution are working correctly.")
    else:
        print("\n❌ Direct tool execution test failed.")
        sys.exit(1)
