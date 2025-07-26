#!/usr/bin/env python3
"""
Test script to verify MCP client functionality
"""

import asyncio
import logging
from mcp_client import MCPClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_mcp_client():
    """Test the MCP client functionality."""
    try:
        # Initialize MCP client
        mcp_client = MCPClient()
        
        # Test getting all available tools
        logger.info("Testing MCP client...")
        tools = await mcp_client.get_all_available_tools()
        
        logger.info(f"Available tools: {tools}")
        
        # Test getting tools in Gemini format
        gemini_tools = mcp_client.get_tools_for_gemini()
        logger.info(f"Gemini-formatted tools: {gemini_tools}")
        
        # Cleanup
        await mcp_client.cleanup()
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing MCP client: {e}")
        return False

def test_mcp_client_sync():
    """Synchronous wrapper for testing."""
    return asyncio.run(test_mcp_client())

if __name__ == "__main__":
    success = test_mcp_client_sync()
    if success:
        print("MCP client test passed!")
    else:
        print("MCP client test failed!")
