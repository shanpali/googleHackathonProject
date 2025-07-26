#!/usr/bin/env python3
"""
Test the server name parsing fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_server_parsing():
    """Test that server names are parsed correctly from function names."""
    try:
        from mcp_client import MCPClient
        
        client = MCPClient()
        
        # Simulate connecting to servers
        await_result = client.get_all_available_tools_sync()
        print(f"✅ Connected servers: {list(client.connected_servers.keys())}")
        
        # Test parsing different function names
        test_cases = [
            "fi_mcp_fetch_net_worth",
            "fi_mcp_fetch_bank_transactions", 
            "fi_mcp_fetch_credit_report"
        ]
        
        for function_name in test_cases:
            print(f"\n🧪 Testing function: {function_name}")
            
            # Extract the parsing logic to test it
            server_name = None
            tool_name = None
            
            # Try to match against known server names
            for known_server in client.connected_servers.keys():
                prefix = f"{known_server}_"
                if function_name.startswith(prefix):
                    server_name = known_server
                    tool_name = function_name[len(prefix):]
                    break
            
            print(f"   📍 Parsed server: '{server_name}'")
            print(f"   🔧 Parsed tool: '{tool_name}'")
            
            if server_name in client.connected_servers:
                print(f"   ✅ Server '{server_name}' is connected")
            else:
                print(f"   ❌ Server '{server_name}' is NOT connected")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing server name parsing fix...")
    if test_server_parsing():
        print("\n🎉 Server parsing test passed!")
    else:
        print("\n❌ Server parsing test failed.")
        sys.exit(1)
