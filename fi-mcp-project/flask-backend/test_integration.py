#!/usr/bin/env python3
"""
Simple test to verify the MCP integration works end-to-end
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from mcp_client import MCPClient
    from gemini_service import GeminiService
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure to install requirements: pip install -r requirements.txt")
    sys.exit(1)

def test_mcp_client():
    """Test MCP client functionality."""
    print("\n=== Testing MCP Client ===")
    
    try:
        client = MCPClient()
        print("✅ MCPClient initialized")
        
        # Test getting tools
        tools = client.get_all_available_tools_sync()
        print(f"✅ Available tools: {list(tools.keys())}")
        
        # Test Gemini format conversion
        gemini_tools = client.get_tools_for_gemini()
        print(f"✅ Gemini tools: {len(gemini_tools)} tools converted")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP Client test failed: {e}")
        return False

def test_gemini_integration():
    """Test Gemini service with MCP integration."""
    print("\n=== Testing Gemini Integration ===")
    
    try:
        # This will trigger MCP tool registration
        service = GeminiService()
        print("✅ GeminiService initialized with MCP integration")
        
        # Check if MCP tools were registered
        all_tools = service.tool_registry.get_all_tool_definitions()
        mcp_tools = [t for t in all_tools if 'fi_mcp_' in t.get('name', '')]
        print(f"✅ MCP tools registered: {len(mcp_tools)} tools")
        
        return True
        
    except Exception as e:
        print(f"❌ Gemini integration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing MCP Integration")
    print("=" * 40)
    
    tests = [
        test_mcp_client,
        test_gemini_integration
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! MCP integration is working.")
        print("\nNext steps:")
        print("1. Start your Go MCP server: cd ../../../fi-mcp-dev && go run main.go")
        print("2. Start Flask backend: python app.py")
        print("3. Test the /mcp-tools endpoint: curl http://localhost:5000/mcp-tools")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
