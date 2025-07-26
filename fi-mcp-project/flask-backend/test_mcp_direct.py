#!/usr/bin/env python3
"""
Direct test of MCP client with JSON-RPC protocol
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append('/Users/sudhhegd/Projects/googleHackathonProject/fi-mcp-project/flask-backend')

async def test_mcp_direct():
    """Test MCP client directly with JSON-RPC"""
    print("🧪 Testing MCP Client with JSON-RPC Protocol")
    print("=" * 60)
    
    try:
        from mcp_client import get_mcp_client
        
        mcp_client = get_mcp_client()
        print("✅ MCP client initialized")
        
        # Connect to servers first
        print("\n1. Connecting to MCP servers...")
        await mcp_client.connect_to_all_servers()
        print("✅ Connected to servers")
        
        # First, authenticate
        print("\n2. Authenticating with MCP server...")
        auth_result = await mcp_client.authenticate_with_server("fi_mcp", "1010101010")
        print(f"Auth result: {auth_result}")
        
        if not auth_result.get('success'):
            print("❌ Authentication failed")
            return
        
        print("✅ Authentication successful")
        
        # Test tool execution
        print("\n3. Testing tool execution...")
        tool_result = await mcp_client.execute_tool_for_gemini(
            "fi_mcp_fetch_net_worth", 
            {"phone": "1010101010"}
        )
        
        print(f"Tool result: {tool_result}")
        
        if tool_result.get('success'):
            print("✅ Tool execution successful!")
            print(f"📊 Result content: {tool_result.get('result')}")
        else:
            print(f"❌ Tool execution failed: {tool_result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp_direct())
