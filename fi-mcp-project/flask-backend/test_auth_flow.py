#!/usr/bin/env python3
"""
Test the improved MCP authentication flow with session management
"""

import requests
import json
import time

def test_auth_flow():
    """Test the complete authentication flow with session management"""
    
    base_url = "http://localhost:5001"
    session = requests.Session()
    
    print("🧪 Testing Improved MCP Authentication Flow")
    print("=" * 60)
    
    # Step 1: Login to Flask
    print("\n1. Login to Flask application...")
    login_resp = session.post(
        f"{base_url}/login",
        json={"phone": "1010101010"}
    )
    
    if login_resp.status_code == 200:
        print("✅ Flask login successful")
    else:
        print(f"❌ Flask login failed: {login_resp.status_code}")
        return
    
    # Step 2: Test chatbot without MCP auth (should get auth required response)
    print("\n2. Testing chatbot before MCP authentication...")
    chat_resp = session.post(
        f"{base_url}/chatbot",
        json={"message": "What is my net worth?"}
    )
    
    if chat_resp.status_code == 200:
        chat_data = chat_resp.json()
        if chat_data.get('authentication_required'):
            print("✅ Authentication required response received")
            print(f"📋 Auth API: {chat_data.get('auth_api', {}).get('url')}")
            print(f"🔧 Curl example: {chat_data.get('curl_example', 'N/A')}")
        else:
            print("❌ Expected authentication required response")
    else:
        print(f"❌ Chatbot request failed: {chat_resp.status_code}")
        return
    
    # Step 3: Authenticate with MCP
    print("\n3. Authenticating with MCP server...")
    auth_resp = session.post(
        f"{base_url}/mcp-auth",
        json={"phone": "1010101010", "server": "fi_mcp"}
    )
    
    if auth_resp.status_code == 200:
        auth_data = auth_resp.json()
        if auth_data.get('success'):
            print("✅ MCP authentication successful")
            print(f"🔑 Session ID: {auth_data.get('session_id')}")
            print(f"⏰ Session timeout: {auth_data.get('session_timeout')} seconds")
            print(f"📅 Expires at: {auth_data.get('expires_at')}")
        else:
            print(f"❌ MCP authentication failed: {auth_data.get('error')}")
            return
    else:
        print(f"❌ MCP auth request failed: {auth_resp.status_code}")
        return
    
    # Step 4: Test auth status
    print("\n4. Checking authentication status...")
    status_resp = session.get(f"{base_url}/mcp-auth-status?server=fi_mcp")
    
    if status_resp.status_code == 200:
        status_data = status_resp.json()
        print("✅ Auth status retrieved")
        print(f"🔐 Authenticated: {status_data.get('authenticated')}")
        print(f"⏳ Remaining time: {status_data.get('status', {}).get('remaining_time', 'N/A')} seconds")
    else:
        print(f"❌ Auth status check failed: {status_resp.status_code}")
    
    # Step 5: Test chatbot with MCP auth
    print("\n5. Testing chatbot with MCP authentication...")
    chat_resp2 = session.post(
        f"{base_url}/chatbot",
        json={"message": "What is my net worth?"}
    )
    
    if chat_resp2.status_code == 200:
        chat_data2 = chat_resp2.json()
        print("✅ Chatbot request successful")
        print(f"🤖 Response: {chat_data2.get('response', 'N/A')[:100]}...")
        print(f"🔧 Function calls: {len(chat_data2.get('function_calls', []))}")
        print(f"🔐 MCP authenticated: {chat_data2.get('mcp_authenticated')}")
    else:
        print(f"❌ Chatbot request failed: {chat_resp2.status_code}")
    
    # Step 6: Test session cleanup
    print("\n6. Testing session cleanup...")
    cleanup_resp = session.post(f"{base_url}/mcp-session-cleanup")
    
    if cleanup_resp.status_code == 200:
        cleanup_data = cleanup_resp.json()
        print("✅ Session cleanup successful")
        print(f"🧹 Cleaned sessions: {cleanup_data.get('cleaned_sessions')}")
    else:
        print(f"❌ Session cleanup failed: {cleanup_resp.status_code}")
    
    print("\n" + "=" * 60)
    print("🏁 Authentication flow test completed!")

def test_session_expiry():
    """Test session expiry functionality (requires modifying session timeout)"""
    print("\n🕐 Testing Session Expiry (requires short timeout)")
    print("Note: To test this properly, temporarily set session_timeout to 10 seconds in mcp_client.py")

if __name__ == "__main__":
    test_auth_flow()
    test_session_expiry()
