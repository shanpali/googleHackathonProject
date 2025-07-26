#!/usr/bin/env python3
"""
Test MCP authentication and tool execution
"""

import asyncio
import requests
import json

async def test_mcp_authentication():
    """Test the complete MCP authentication and tool execution flow"""
    
    print("🚀 Testing MCP Authentication Flow")
    print("=" * 50)
    
    # Step 1: Test Flask authentication endpoint
    print("\n1. Testing Flask MCP authentication endpoint...")
    auth_data = {
        "phone": "1234567890",
        "server": "fi_mcp"
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/mcp-auth',
            json=auth_data,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Authentication successful!")
            else:
                print(f"❌ Authentication failed: {result.get('error')}")
                return
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Error testing authentication: {e}")
        return
    
    # Step 2: Test authentication status
    print("\n2. Testing authentication status...")
    try:
        response = requests.get(
            'http://localhost:5000/mcp-auth-status?server=fi_mcp',
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Auth Status: {response.json()}")
        
    except Exception as e:
        print(f"❌ Error checking auth status: {e}")
    
    # Step 3: Test MCP tool execution through chatbot
    print("\n3. Testing MCP tool execution through chatbot...")
    try:
        # First, simulate login to Flask
        login_response = requests.post(
            'http://localhost:5000/login',
            json={"phone": "1234567890"},
            timeout=10
        )
        
        if login_response.status_code == 200:
            print("✅ Flask login successful")
            
            # Now test a financial query that should trigger MCP tools
            chat_data = {
                "message": "What is my net worth?"
            }
            
            # Use the same session for continuity
            session = requests.Session()
            session.post('http://localhost:5000/login', json={"phone": "1234567890"})
            session.post('http://localhost:5000/mcp-auth', json=auth_data)
            
            chat_response = session.post(
                'http://localhost:5000/chatbot',
                json=chat_data,
                timeout=30
            )
            
            print(f"Chat Status Code: {chat_response.status_code}")
            if chat_response.status_code == 200:
                chat_result = chat_response.json()
                print(f"Chat Response: {chat_result.get('response', 'No response')}")
                print(f"Function Calls: {chat_result.get('function_calls', [])}")
                print(f"MCP Authenticated: {chat_result.get('mcp_authenticated', False)}")
            else:
                print(f"❌ Chat error: {chat_response.text}")
                
    except Exception as e:
        print(f"❌ Error testing chatbot: {e}")

def test_direct_mcp_client():
    """Test MCP client directly"""
    print("\n🔧 Testing MCP Client Directly")
    print("=" * 50)
    
    try:
        from mcp_client import get_mcp_client
        
        mcp_client = get_mcp_client()
        
        # Test authentication
        print("\n1. Testing direct MCP authentication...")
        result = asyncio.run(mcp_client.authenticate_with_server("fi_mcp", "1234567890"))
        print(f"Authentication result: {result}")
        
        if result.get('success'):
            print("✅ Direct MCP authentication successful!")
            
            # Test tool execution
            print("\n2. Testing direct tool execution...")
            tool_result = asyncio.run(mcp_client.execute_tool_for_gemini(
                "fi_mcp_fetch_net_worth", 
                {"phone": "1234567890"}
            ))
            print(f"Tool execution result: {tool_result}")
            
        else:
            print(f"❌ Direct MCP authentication failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error testing direct MCP client: {e}")

def main():
    """Main test function"""
    print("🧪 MCP Authentication Test Suite")
    print("=" * 60)
    
    # Test asyncio functionality
    asyncio.run(test_mcp_authentication())
    
    # Test direct MCP client
    test_direct_mcp_client()
    
    print("\n" + "=" * 60)
    print("🏁 Test suite completed!")

if __name__ == "__main__":
    main()
