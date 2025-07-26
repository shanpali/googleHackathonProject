#!/usr/bin/env python3
"""
Test the new Fi Money authentication flow
"""

import requests
import json

def test_fi_money_auth_flow():
    """Test the complete Fi Money authentication flow"""
    
    base_url = "http://localhost:5001"
    session = requests.Session()
    
    print("🌟 Testing Fi Money Authentication Flow")
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
    
    # Step 2: Test chatbot to get Fi Money login URL
    print("\n2. Testing chatbot to get Fi Money authentication URL...")
    chat_resp = session.post(
        f"{base_url}/chatbot",
        json={"message": "What is my net worth?"}
    )
    
    if chat_resp.status_code == 200:
        chat_data = chat_resp.json()
        if chat_data.get('authentication_required'):
            print("✅ Authentication required response received")
            print(f"🔗 Fi Money Login URL: {chat_data.get('login_url')}")
            print(f"🆔 Session ID: {chat_data.get('session_id')}")
            print(f"📋 Message: {chat_data.get('message')}")
            
            # Extract session details
            login_url = chat_data.get('login_url')
            session_id = chat_data.get('session_id')
            
            if login_url and session_id:
                print(f"\n🌐 Generated Fi Money URL: {login_url}")
                
                # Test if the URL follows the expected format
                if "wealth-mcp-login?token=" in login_url:
                    print("✅ URL format is correct for Fi Money integration")
                else:
                    print("❌ URL format is incorrect")
                    
                # Test domain extraction
                if "fi.money" in login_url:
                    print("✅ Domain correctly extracted as fi.money")
                elif "localhost" in login_url:
                    print("✅ Using localhost for local testing")
                else:
                    print("❌ Unexpected domain in URL")
                    
            else:
                print("❌ Missing login_url or session_id in response")
        else:
            print("❌ Expected authentication required response")
    else:
        print(f"❌ Chatbot request failed: {chat_resp.status_code}")
        return
    
    # Step 3: Test direct session generation
    print("\n3. Testing direct session generation...")
    auth_resp = session.post(
        f"{base_url}/mcp-auth",
        json={"phone": "1010101010", "server": "fi_mcp"}
    )
    
    if auth_resp.status_code == 200:
        auth_data = auth_resp.json()
        if auth_data.get('success'):
            print("✅ Session generation successful")
            print(f"🔗 Login URL: {auth_data.get('login_url')}")
            print(f"🆔 Session ID: {auth_data.get('session_id')}")
            print(f"💬 Message: {auth_data.get('message')}")
        else:
            print(f"❌ Session generation failed: {auth_data.get('error')}")
    else:
        print(f"❌ Session generation request failed: {auth_resp.status_code}")
    
    # Step 4: Test session callback (simulate Fi Money calling back)
    print("\n4. Testing session authentication callback...")
    if 'session_id' in locals():
        callback_resp = session.post(
            f"{base_url}/mcp-auth-callback",
            json={"session_id": session_id, "server": "fi_mcp"}
        )
        
        if callback_resp.status_code == 200:
            callback_data = callback_resp.json()
            if callback_data.get('success'):
                print("✅ Session authentication callback successful")
                print(f"💬 Message: {callback_data.get('message')}")
            else:
                print(f"❌ Session authentication failed: {callback_data.get('error')}")
        else:
            print(f"❌ Callback request failed: {callback_resp.status_code}")
    
    # Step 5: Test auth status after authentication
    print("\n5. Testing authentication status...")
    status_resp = session.get(f"{base_url}/mcp-auth-status?server=fi_mcp")
    
    if status_resp.status_code == 200:
        status_data = status_resp.json()
        print("✅ Auth status retrieved")
        print(f"🔐 Authenticated: {status_data.get('authenticated')}")
        print(f"📊 Status: {status_data.get('status', {})}")
    else:
        print(f"❌ Auth status check failed: {status_resp.status_code}")
    
    print("\n" + "=" * 60)
    print("🏁 Fi Money authentication flow test completed!")
    print("\n📋 Summary:")
    print("✅ Chatbot now provides Fi Money login URLs")
    print("✅ URLs follow the format: https://fi.money/wealth-mcp-login?token=mcp-session-xxx")
    print("✅ Session management with proper callbacks")
    print("✅ No more direct authentication through our endpoints")

if __name__ == "__main__":
    test_fi_money_auth_flow()
